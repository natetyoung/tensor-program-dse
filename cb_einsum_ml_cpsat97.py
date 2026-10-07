from math import prod
from typing import Dict, FrozenSet, List, NamedTuple, Tuple, Union
from ortools.sat.python import cp_model

class MemCosts(NamedTuple):
    '''Integer per-element access costs of one memory.'''
    read_energy: int = 1
    write_energy: int = 1
    read_time: int = 1
    write_time: int = 1

class Memory(NamedTuple):
    cap: int
    ops: Tuple[str, ...]
    costs: MemCosts

class Unit(NamedTuple):
    '''An operand's copy at one level; owns one LD/ST slot.'''
    op: str
    lvl: int

MemKey = Tuple[int, int]  # (level, memory index); DRAM is (num_levels, 0)

class Problem(NamedTuple):
    '''Parsed inputs plus derived structure, shared by model and evaluator.'''
    operand_dims: Dict[str, Tuple[str, ...]]
    output: str
    dim_sizes: Dict[str, int]
    memories: List[List[Memory]]           # per level, excluding DRAM
    mem_costs: Dict[MemKey, MemCosts]      # every memory, including DRAM
    fanouts: List[Tuple[int, ...]]         # per level, one size per array dim
    mc_ops: List[List[FrozenSet[str]]]     # per level and array dim: multicast operands
    units: List[Unit]                      # outermost level first
    op_levels: Dict[str, List[int]]        # levels holding each operand, innermost first
    unit_mem: Dict[Unit, MemKey]           # the unit's own memory
    unit_src: Dict[Unit, MemKey]           # its parent: next memory up holding op, or DRAM
    comp_mem: Dict[str, MemKey]            # where compute accesses op (innermost, or DRAM)
    compute_time: int
    compute_energy: int
    compute_accesses: bool

    def endpoints(self, u):
        '''(memory read, memory written) by u's transfers.'''
        if u.op == self.output:
            return self.unit_mem[u], self.unit_src[u]
        return self.unit_src[u], self.unit_mem[u]

    def crossed(self, op, lo, hi):
        '''(level, array dim) pairs of the fanouts at levels [lo, hi) that
        multicast op; an access from below lo to a memory at level hi
        crosses them.'''
        return [(l, s) for l in range(lo, hi)
                for s in range(len(self.fanouts[l])) if op in self.mc_ops[l][s]]

    def label(self, key):
        lvl, m = key
        if lvl == len(self.memories):
            return 'DRAM'
        if len(self.memories[lvl]) == 1:
            return 'L'+str(lvl)
        return 'L'+str(lvl)+'.m'+str(m)+' {'+','.join(self.memories[lvl][m].ops)+'}'

class Schedule(NamedTuple):
    objective: int
    order: List[Unit]                      # unit per slot, outermost first
    factors: Dict[str, List[int]]          # temporal factor per dim per bucket
    energy: int
    delay: int
    parallel: Dict[int, Dict[str, int]]    # level -> dim -> parallel factor
    par_rows: Dict[int, List[Dict[str, int]]]  # level -> per array dim: dim -> factor

def add_mul_chain(model:cp_model.CpModel, components, lb, ub, pfx):
    var = components[0]
    for i, c in enumerate(components[1:]):
        new_var = model.NewIntVar(lb, ub, pfx+'_mul_chain'+str(i))
        model.AddMultiplicationEquality(new_var, (var, c))
        var = new_var
    return var

def make_problem(operand_dims, output_operand, dim_sizes, capacities, level_costs=None,
                 dram_costs=MemCosts(), fanouts=None, multicast=False,
                 compute_time=0, compute_energy=0, compute_accesses=True):
    '''Validate and normalize cb_einsum_ml's architecture arguments.'''
    operands = list(operand_dims)
    if isinstance(capacities, int):
        capacities = [capacities]
    num_levels = len(capacities)
    if level_costs is None:
        level_costs = [MemCosts()] * num_levels
    if fanouts is None:
        fanouts = [1] * num_levels
    fanouts = [f if isinstance(f, tuple) else (f,) for f in fanouts]
    if isinstance(multicast, bool):
        multicast = [multicast] * num_levels
    if len(fanouts) != num_levels or len(multicast) != num_levels:
        raise ValueError('fanouts and multicast need one entry per level')

    def check_ops(ops, where):
        for op in ops:
            if op not in operand_dims:
                raise ValueError('unknown operand '+str(op)+' in '+where)

    memories, unit_mem = [], {}
    for lvl, spec in enumerate(capacities):
        if isinstance(spec, int):
            spec = [(spec, operands)]
        mems = []
        for m, mem in enumerate(spec):
            ops = tuple(mem[1])
            check_ops(ops, 'L'+str(lvl)+' memory '+str(m))
            for op in ops:
                if Unit(op, lvl) in unit_mem:
                    raise ValueError('operand '+op+' in multiple L'+str(lvl)+' memories')
                unit_mem[Unit(op, lvl)] = (lvl, m)
            mems.append(Memory(mem[0], ops, mem[2] if len(mem) > 2 else level_costs[lvl]))
        memories.append(mems)
    dram = (num_levels, 0)
    mem_costs = {(lvl, m): mem.costs for lvl in range(num_levels)
                 for m, mem in enumerate(memories[lvl])}
    mem_costs[dram] = dram_costs

    mc_ops = []
    for l, entry in enumerate(multicast):
        if isinstance(entry, bool):
            entry = [entry] * len(fanouts[l])
        elif any(isinstance(e, str) for e in entry):
            # a flat operand list is only unambiguous for a 1-D fanout
            if len(fanouts[l]) > 1:
                raise ValueError('multicast['+str(l)+'] must give one entry per array dim of '
                                 'fanouts['+str(l)+'], e.g. (('+repr(entry[0])+',), ...)')
            entry = [entry]
        elif len(entry) != len(fanouts[l]):
            raise ValueError('multicast['+str(l)+'] needs one entry per array dim of fanouts['+str(l)+']')
        row = []
        for e in entry:
            if isinstance(e, bool):
                e = operands if e else ()
            check_ops(e, 'multicast')
            row.append(frozenset(e))
        mc_ops.append(row)

    units = [Unit(op, lvl) for lvl in range(num_levels) for op in operands if Unit(op, lvl) in unit_mem]
    op_levels = {op: [lvl for lvl in range(num_levels) if Unit(op, lvl) in unit_mem] for op in operands}
    unit_src = {}
    for u in units:
        outer = [l for l in op_levels[u.op] if l > u.lvl]
        unit_src[u] = unit_mem[Unit(u.op, outer[0])] if outer else dram
    comp_mem = {op: unit_mem[Unit(op, op_levels[op][0])] if op_levels[op] else dram
                for op in operands}
    return Problem(operand_dims, output_operand, dim_sizes, memories, mem_costs, fanouts,
                   mc_ops, units, op_levels, unit_mem, unit_src, comp_mem,
                   compute_time, compute_energy, compute_accesses)

def evaluate_schedule(p:Problem, order, factors, par_rows):
    '''
    Independent plain-Python validity check and cost of a schedule.
    order: Unit per slot, outermost first. factors: dim -> temporal factor
    per bucket (len(order) + 1). par_rows: level -> per array dim
    {dim: parallel factor}. Returns dict with per-unit 'spatial' (tile per
    instance) and 'traffic' (elements moved, summed over instances), and
    'energy', 'delay', 'ports' ((memory, 'read'/'write') -> time per instance).
    '''
    num_levels = len(p.memories)
    iters = prod(p.dim_sizes.values())

    # Level l's parallel loops sit just outside its first slot; if used, every
    # slot above level l comes first.
    eff = {d: list(fs) for d, fs in factors.items()}
    par_tot = {}
    for l, rows in par_rows.items():
        b = sum(1 for u in order if u.lvl > l)
        par_tot[l] = prod(f for row in rows for f in row.values())
        for row in rows:
            for d, f in row.items():
                eff[d][b] *= f
        if par_tot[l] > 1:
            assert all(u.lvl > l for u in order[:b]), ('parallel level not blocked', l, order)
    instances = [prod(par_tot.get(l, 1) for l in range(lvl, num_levels)) for lvl in range(num_levels + 1)]
    for d, size in p.dim_sizes.items():
        assert prod(eff[d]) >= size, ('dim not covered', d)

    def shared(op, lo, hi):
        # instances that differ only in parallel dims op lacks share one access
        return prod(f for l, s in p.crossed(op, lo, hi) if l in par_rows
                    for d, f in par_rows[l][s].items() if d not in p.operand_dims[op])

    spatial, traffic = {}, {}
    reads = {k: 0 for k in p.mem_costs}
    writes = {k: 0 for k in p.mem_costs}
    for g, u in enumerate(order):
        sp = prod(eff[d][b] for b in range(g + 1, len(order) + 1) for d in p.operand_dims[u.op])
        tp = prod(eff[d][b] for b in range(g + 1) for d in p.dim_sizes)
        spatial[u], traffic[u] = sp, sp * tp
        mc = shared(u.op, u.lvl, p.unit_src[u][0])
        assert traffic[u] % mc == 0, (u, mc)
        rd, wr = p.endpoints(u)
        reads[rd] += traffic[u] if u.op == p.output else traffic[u] // mc
        writes[wr] += traffic[u] // mc if u.op == p.output else traffic[u]
    for lvl, mems in enumerate(p.memories):
        for mem in mems:
            assert sum(spatial[Unit(op, lvl)] for op in mem.ops) <= mem.cap, ('over capacity', lvl, mem)

    # compute reads each input and read-modify-writes the output every
    # iteration (no read for an element's first write); padding ignored
    if p.compute_accesses:
        for op, key in p.comp_mem.items():
            accesses = -(-iters // shared(op, 0, key[0]))
            if op == p.output:
                out_size = prod(p.dim_sizes[d] for d in p.operand_dims[op])
                assert accesses >= out_size, (op, accesses)
                writes[key] += accesses
                reads[key] += accesses - out_size
            else:
                reads[key] += accesses

    energy = (sum(p.mem_costs[k].read_energy * n for k, n in reads.items())
              + sum(p.mem_costs[k].write_energy * n for k, n in writes.items())
              + p.compute_energy * iters)
    ports = {}
    for k in p.mem_costs:
        ports[(k, 'read')] = -(-p.mem_costs[k].read_time * reads[k] // instances[k[0]])
        ports[(k, 'write')] = -(-p.mem_costs[k].write_time * writes[k] // instances[k[0]])
    delay = max(ports.values(), default=0)
    if p.compute_time > 0:
        delay = max(delay, p.compute_time * -(-iters // instances[0]))
    return {'spatial': spatial, 'traffic': traffic, 'energy': energy, 'delay': delay, 'ports': ports}

def cb_einsum_ml(
    operand_dims:Dict[str,Tuple[str]],
    output_operand:str,
    dim_sizes:Dict[str,int],
    capacities:Union[int,List[Union[int,List[Tuple]]]],
    level_costs:List[MemCosts] = None,
    dram_costs:MemCosts = MemCosts(),
    objective:str = 'edp',
    fanouts:List[Union[int,Tuple[int,...]]] = None,
    multicast:Union[bool,List[Union[bool,Tuple]]] = False,
    compute_time:int = 0,
    compute_energy:int = 0,
    compute_accesses:bool = True,
    enforce_optimal_placement = True,
    blocked = False,
    break_ties = True,
    perfect_division = False,
    verbose = True,
    time_limit = 120.0
):
    '''
    Multi-level constrained-buckets model for a single einsum: chooses tiling
    factors, loop order, parallel factors and placement on a memory hierarchy.

    Structure: each (operand, level) pair is a Unit with one LD/ST slot in a
    single global order (outermost first); buckets of tiling factors sit
    between consecutive slots. A unit's tile is the product of the factors
    inside its slot over its operand's dims; its traffic is that tile times
    every factor outside its slot. An operand's outer slot precedes its inner
    slot (inclusive hierarchy).

    Arguments:
    - capacities: per level, innermost first. An int is one memory shared by
      all operands; a list of (capacity, ops) or (capacity, ops, MemCosts)
      splits the level into separate memories. An operand in no memory at a
      level bypasses it. DRAM sits above the outermost level.
    - level_costs / dram_costs: MemCosts for memories without explicit costs,
      and for DRAM.
    - objective: 'edp' (energy x delay, each scaled below 2^30 to avoid
      overflow), 'energy' or 'delay'.
    - fanouts[l]: replicates level l (its memories and the compute below)
      per parent instance; a tuple is a multi-dimensional array. Each array
      dim holds a product of parallel factors at most its size, placed in
      the bucket just outside level l's first slot. If level l uses any
      parallelism, every slot of the levels above l comes first.
    - multicast[l]: a bool, or one entry per array dim of fanouts[l] (a flat
      operand list only for a 1-D fanout), each a bool or a collection of
      operands (True = every operand). For an input, instances that differ
      only in parallel dims it lacks share one parent read; for the output,
      their partial sums are reduced on the way up (the parent is written
      once). An array dim may be parallel over reduction dims if it
      multicasts the output, and over output dims if it multicasts an input
      or nothing.
    - compute_time: cycles per iteration per compute unit; adds a compute
      port of compute_time x ceil(iterations / total parallelism).
    - compute_energy: energy per iteration.
    - compute_accesses: charge compute's own accesses to each operand's
      innermost memory (or DRAM): one read per iteration per input, a
      read-modify-write per iteration for the output (no read for an
      element's first write), shared along multicasting array dims crossed.
    - blocked: force all slots of level l+1 before all of level l.
    - break_ties: fix the order of adjacent slots with no loops between them.
    - perfect_division: factors must multiply to exactly each dim size
      (otherwise at least, i.e. padding allowed).

    Cost model: traffic of unit (op, l) moves data between level l and its
    parent (next level up holding op, or DRAM): inputs are read from the
    parent and written to l, the output the reverse. Energy is the sum of
    read_energy + write_energy over every access. Delay is the busiest port:
    every memory has separate read and write ports running in parallel,
    each busy for elements x its time, split over the memory's instances.
    Capacities are per instance; traffic and energy sum over instances.
    Padding is ignored for compute.

    Returns a Schedule, or None if no solution was found. The solution is
    asserted against evaluate_schedule.
    '''
    if objective not in ('edp', 'energy', 'delay'):
        raise ValueError('unknown objective '+objective)
    p = make_problem(operand_dims, output_operand, dim_sizes, capacities, level_costs,
                     dram_costs, fanouts, multicast, compute_time, compute_energy,
                     compute_accesses)
    model = cp_model.CpModel()
    operands = list(operand_dims)
    units = p.units
    num_levels = len(p.memories)
    num_slots = len(units)
    num_buckets = num_slots + 1
    max_iters = prod(dim_sizes.values())
    total_fan = prod(prod(f) for f in p.fanouts)
    op_size = {op: prod(dim_sizes[d] for d in operand_dims[op]) for op in operands}
    name = {u: u.op+'_L'+str(u.lvl) for u in units}

    # placement_vars[u][g]: unit u occupies slot g (permutation)
    placement_vars = {u: [model.NewBoolVar(name[u]+'_pl_'+str(g)) for g in range(num_slots)]
                      for u in units}
    for u in units:
        model.AddExactlyOne(placement_vars[u])
    for g in range(num_slots):
        model.AddExactlyOne([placement_vars[u][g] for u in units])

    pos_vars = {}
    for u in units:
        pos_vars[u] = model.NewIntVar(0, num_slots - 1, name[u]+'_pos')
        model.Add(pos_vars[u] == sum(g * placement_vars[u][g] for g in range(num_slots)))

    # inclusion: outer level loaded before inner level
    for op in operands:
        lvls = p.op_levels[op]
        for inner, outer in zip(lvls, lvls[1:]):
            model.Add(pos_vars[Unit(op, outer)] < pos_vars[Unit(op, inner)])

    if blocked:
        for u in units:
            base = sum(1 for v in units if v.lvl > u.lvl)
            n = sum(1 for v in units if v.lvl == u.lvl)
            model.Add(pos_vars[u] >= base)
            model.Add(pos_vars[u] < base + n)

    # inner_vars[u][b]: unit u's slot is above bucket b (bucket b is inside u's tile)
    inner_vars = {}
    for u in units:
        inner_vars[u] = []
        for b in range(num_buckets):
            v = model.NewBoolVar(name[u]+'_inner_'+str(b))
            model.Add(v == sum(placement_vars[u][g] for g in range(b)))
            inner_vars[u].append(v)

    # Parallel factors. Level l's parallel loops sit in bucket par_bucket[l]
    # (fixed, since used parallelism forces outer levels' slots before it).
    # An array dim may be parallel over reduction dims if it multicasts the
    # output, and over output dims if it multicasts an input or nothing.
    reduction_dims = [d for d in dim_sizes if d not in operand_dims[output_operand]]
    def allowed_dims(l, s):
        ops = p.mc_ops[l][s]
        dims = reduction_dims if output_operand in ops else []
        if not ops or ops - {output_operand}:
            dims = dims + list(operand_dims[output_operand])
        return dims
    par_levels = [l for l in range(num_levels)
                  if any(size > 1 and allowed_dims(l, s) for s, size in enumerate(p.fanouts[l]))]
    par_bucket = {l: sum(1 for u in units if u.lvl > l) for l in par_levels}
    par_rows = {}  # level -> per array dim: {dim: factor var}
    par_dims = {}  # level -> {dim: product over array dims}
    par_tot = {}   # level -> product over dims
    for l in par_levels:
        rows = []
        for s, size in enumerate(p.fanouts[l]):
            row = {d: model.NewIntVar(1, min(size, dim_sizes[d]), 'par_L'+str(l)+'_'+str(s)+'_'+d)
                   for d in allowed_dims(l, s)}
            if row:
                model.Add(add_mul_chain(model, list(row.values()), 1, size,
                                        'par_L'+str(l)+'_'+str(s)) <= size)
            rows.append(row)
        par_rows[l] = rows
        fan = prod(p.fanouts[l])
        par_dims[l] = {
            d: add_mul_chain(model, [row[d] for row in rows if d in row], 1, fan, 'par_L'+str(l)+'_'+d)
            for d in dim_sizes if any(d in row for row in rows)
        }
        par_tot[l] = add_mul_chain(model, list(par_dims[l].values()), 1, fan, 'par_tot_L'+str(l))
        used = model.NewBoolVar('par_used_L'+str(l))
        model.Add(par_tot[l] >= 2).OnlyEnforceIf(used)
        model.Add(par_tot[l] == 1).OnlyEnforceIf(used.Not())
        for u in units:
            if u.lvl > l:
                model.Add(pos_vars[u] < par_bucket[l]).OnlyEnforceIf(used)

    # instances[lvl]: copies of a level-lvl memory (product of parallelism at
    # or above it); instances[num_levels] = 1 is DRAM
    instances = []
    for lvl in range(num_levels + 1):
        above = [par_tot[l] for l in par_levels if l >= lvl]
        instances.append(add_mul_chain(model, above, 1, total_fan, 'instances_L'+str(lvl)) if above else 1)

    def shared_factor_vars(op, lo, hi):
        # parallel factors over dims op lacks, along crossed array dims that multicast op
        return [par_rows[l][s][d] for l, s in p.crossed(op, lo, hi) if l in par_rows
                for d in par_rows[l][s] if d not in operand_dims[op]]

    # Factor variables (temporal); eff_vars adds parallel factors in their buckets
    factor_vars = {}
    eff_vars = {}
    for dim in dim_sizes:
        factor_vars[dim] = []
        for b in range(num_buckets):
            factor_vars[dim].append(model.NewIntVar(1, dim_sizes[dim], dim+'_'+str(b)+'_factor'))
            if enforce_optimal_placement:
                for u in units:
                    # dim participates in unit just above bucket b (move out for free)
                    if b > 0 and dim in operand_dims[u.op]:
                        model.Add(factor_vars[dim][b] == 1).OnlyEnforceIf(placement_vars[u][b-1])
                    # dim does not participate in unit just below bucket b (move in)
                    if b < num_slots and dim not in operand_dims[u.op]:
                        model.Add(factor_vars[dim][b] == 1).OnlyEnforceIf(placement_vars[u][b])

            # forbid temporal reduction (no partial spilling); innermost output
            # slot is the deepest, so this implies the rule for all levels.
            # An output in no memory accumulates in DRAM, so no rule applies.
            if dim in reduction_dims and p.op_levels[output_operand]:
                model.Add(factor_vars[dim][b] == 1).OnlyEnforceIf(
                    inner_vars[Unit(output_operand, p.op_levels[output_operand][0])][b].Not()
                )
        eff_vars[dim] = []
        for b in range(num_buckets):
            pars = [par_dims[l][dim] for l in par_levels if par_bucket[l] == b and dim in par_dims[l]]
            if pars:
                eff_vars[dim].append(add_mul_chain(model, [factor_vars[dim][b]] + pars,
                                                   1, dim_sizes[dim] * total_fan, dim+'_'+str(b)+'_eff'))
            else:
                eff_vars[dim].append(factor_vars[dim][b])
        # Product of factors (incl. parallel) for this dim is at least dim size
        factor_product = add_mul_chain(model, eff_vars[dim],
                                       1, dim_sizes[dim] * 2**(num_buckets-1) * total_fan,
                                       dim+'_factor_prod')
        if perfect_division:
            model.Add(factor_product == dim_sizes[dim])
        else:
            model.Add(factor_product >= dim_sizes[dim])

    # Tie-breaking: adjacent slots separated by an all-ones bucket can be
    # swapped without changing any cost, so require them in canonical rank
    # order. Rank puts outer levels before inner ones, so the inclusion
    # constraint never forbids the canonical order. Safe alongside the
    # placement rules: an optimum minimizing (cost, total traffic, total
    # spatial) satisfies those rules in any order (a violation would strictly
    # improve traffic or spatial without worsening the others, and energy and
    # delay never increase with less traffic), and swaps keep all unchanged.
    if break_ties:
        ranked = sorted(units, key=lambda u: (-u.lvl, operands.index(u.op)))
        rank = {u: i for i, u in enumerate(ranked)}
        rank_at = []
        for g in range(num_slots):
            r = model.NewIntVar(0, num_slots - 1, 'rank_at_'+str(g))
            model.Add(r == sum(rank[u] * placement_vars[u][g] for u in units))
            rank_at.append(r)
        for b in range(1, num_slots):
            nonempty = model.NewBoolVar('nonempty_'+str(b))
            model.Add(
                sum(factor_vars[d][b] for d in dim_sizes) >= len(dim_sizes) + 1
            ).OnlyEnforceIf(nonempty)
            model.Add(rank_at[b-1] < rank_at[b]).OnlyEnforceIf(nonempty.Not())

    # Per-bucket products, shared across units
    sp_prods = {
        op: [add_mul_chain(model, [eff_vars[d][b] for d in operand_dims[op]],
                           1, max_iters, 'sp_prod_'+op+'_'+str(b))
             for b in range(num_buckets)]
        for op in operands
    }
    tp_prods = [add_mul_chain(model, [eff_vars[d][b] for d in dim_sizes],
                              1, max_iters, 'tp_prod_'+str(b))
                for b in range(num_buckets)]

    # spatial_vars[u]: tile per instance; traffic_vars[u]: elements moved,
    # summed over instances
    spatial_vars, traffic_vars = {}, {}
    for u in units:
        cap = p.memories[u.lvl][p.unit_mem[u][1]].cap
        sp_contribs, tp_contribs = [], []
        for b in range(num_buckets):
            sc = model.NewIntVar(1, cap, name[u]+'_spatial_contrib_'+str(b))
            model.Add(sc == sp_prods[u.op][b]).OnlyEnforceIf(inner_vars[u][b])
            model.Add(sc == 1).OnlyEnforceIf(inner_vars[u][b].Not())
            sp_contribs.append(sc)
            tc = model.NewIntVar(1, max_iters, name[u]+'_temporal_contrib_'+str(b))
            model.Add(tc == tp_prods[b]).OnlyEnforceIf(inner_vars[u][b].Not())
            model.Add(tc == 1).OnlyEnforceIf(inner_vars[u][b])
            tp_contribs.append(tc)
        spatial_vars[u] = add_mul_chain(model, sp_contribs, 1, cap, 'spatial_cost_'+name[u])
        temporal = add_mul_chain(model, tp_contribs, 1, max_iters, 'temporal_cost_'+name[u])
        traffic_vars[u] = model.NewIntVar(op_size[u.op], max_iters, 'total_cost_'+name[u])
        model.AddMultiplicationEquality(traffic_vars[u], (spatial_vars[u], temporal))

    # capacity constraint per memory
    for lvl, mems in enumerate(p.memories):
        for mem in mems:
            model.Add(sum(spatial_vars[Unit(op, lvl)] for op in mem.ops) <= mem.cap)

    # reads[k] / writes[k]: expressions for elements read from / written to
    # memory k, summed over instances.
    reads = {k: [] for k in p.mem_costs}
    writes = {k: [] for k in p.mem_costs}

    # Transfers. Instances that differ only in parallel dims the operand lacks
    # share one parent access: a multicast read for inputs, a reduced write
    # for the output. Those parallel factors are part of the unit's temporal
    # product, so this divides exactly.
    parent_traffic = {}
    for u in units:
        shared = shared_factor_vars(u.op, u.lvl, p.unit_src[u][0])
        if shared:
            mc = add_mul_chain(model, shared, 1, total_fan, 'multicast_'+name[u])
            parent_traffic[u] = model.NewIntVar(1, max_iters, 'parent_traffic_'+name[u])
            model.AddMultiplicationEquality(traffic_vars[u], (parent_traffic[u], mc))
        else:
            parent_traffic[u] = traffic_vars[u]
        rd, wr = p.endpoints(u)
        if u.op == output_operand:
            reads[rd].append(traffic_vars[u])
            writes[wr].append(parent_traffic[u])
        else:
            reads[rd].append(parent_traffic[u])
            writes[wr].append(traffic_vars[u])

    # Compute accesses: every iteration reads each input and read-modify-
    # writes the output in the operand's innermost memory (or DRAM). Compute
    # units sit below every fanout, so accesses to a memory at level li cross
    # the fanouts below li, sharing accesses as transfers do. The first write
    # of each output element needs no read. Padding is ignored.
    comp_accesses = {}
    if compute_accesses:
        for op, key in p.comp_mem.items():
            shared = shared_factor_vars(op, 0, key[0])
            if shared:
                mc = add_mul_chain(model, shared, 1, total_fan, 'comp_multicast_'+op)
                accesses = model.NewIntVar(1, max_iters, 'comp_accesses_'+op)
                model.AddDivisionEquality(accesses, max_iters + mc - 1, mc)
            else:
                accesses = max_iters
            comp_accesses[op] = accesses
            if op == output_operand:
                # no more reduction parallelism than there are reduction iterations
                model.Add(accesses >= op_size[op])
                writes[key].append(accesses)
                reads[key].append(accesses - op_size[op])
            else:
                reads[key].append(accesses)

    # Energy: every access to every memory, plus the compute itself
    energy_ub = max(1, sum(p.mem_costs[k].read_energy * len(reads[k])
                           + p.mem_costs[k].write_energy * len(writes[k]) for k in p.mem_costs)
                    * max_iters + compute_energy * max_iters)
    energy = model.NewIntVar(0, energy_ub, 'energy')
    model.Add(energy == sum(p.mem_costs[k].read_energy * sum(reads[k])
                            + p.mem_costs[k].write_energy * sum(writes[k]) for k in p.mem_costs)
              + compute_energy * max_iters)

    # Delay: each memory's read and write ports work in parallel with all
    # other ports; delay is the busiest port. Replicated memories split
    # their accesses evenly over their instances.
    ports = []  # (memory key, 'read'/'write', time var per instance)
    delay_ub = 1
    for k, costs in p.mem_costs.items():
        for kind, terms, t in (('read', reads[k], costs.read_time),
                               ('write', writes[k], costs.write_time)):
            if not terms or t == 0:
                continue
            pfx = p.label(k)+'_'+kind
            port_ub = t * max_iters * len(terms)
            delay_ub = max(delay_ub, port_ub)
            # per-instance time = ceil(busy / instances)
            rounded_up = model.NewIntVar(0, port_ub + total_fan, pfx+'_total_time')
            model.Add(rounded_up == t * sum(terms) + instances[k[0]] - 1)
            pv = model.NewIntVar(0, port_ub, pfx+'_time')
            model.AddDivisionEquality(pv, rounded_up, instances[k[0]])
            ports.append((k, kind, pv))
    delay_terms = [pv for _, _, pv in ports]

    # Compute: each compute unit runs its share of the iterations
    compute_var = None
    if compute_time > 0:
        iters_per_unit = model.NewIntVar(1, max_iters, 'iters_per_unit')
        model.AddDivisionEquality(iters_per_unit, max_iters + instances[0] - 1, instances[0])
        compute_var = model.NewIntVar(0, compute_time * max_iters, 'compute_time')
        model.Add(compute_var == compute_time * iters_per_unit)
        delay_terms.append(compute_var)
        delay_ub = max(delay_ub, compute_time * max_iters)

    delay = model.NewIntVar(0, delay_ub, 'delay')
    if delay_terms:
        model.AddMaxEquality(delay, delay_terms)
    else:
        model.Add(delay == 0)

    if objective == 'energy':
        model.Minimize(energy)
    elif objective == 'delay':
        model.Minimize(delay)
    else:
        # E * D overflows int64, so scale each to <= 2^30 before multiplying
        # (rounding error relative to the bounds, not the values)
        e_scale = -(-energy_ub // 2**30)
        d_scale = -(-delay_ub // 2**30)
        energy_s = model.NewIntVar(0, energy_ub // e_scale, 'energy_scaled')
        delay_s = model.NewIntVar(0, delay_ub // d_scale, 'delay_scaled')
        model.AddDivisionEquality(energy_s, energy, e_scale)
        model.AddDivisionEquality(delay_s, delay, d_scale)
        edp_s = model.NewIntVar(0, (energy_ub // e_scale) * (delay_ub // d_scale), 'edp_scaled')
        model.AddMultiplicationEquality(edp_s, (energy_s, delay_s))
        model.Minimize(edp_s)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)
    if verbose:
        print(solver.ResponseStats())
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    order = sorted(units, key=lambda u: solver.Value(pos_vars[u]))
    factors = {d: [solver.Value(f) for f in factor_vars[d]] for d in dim_sizes}
    parallel = {l: {d: solver.Value(v) for d, v in par_dims[l].items()} for l in par_levels}
    par_vals = {l: [{d: solver.Value(v) for d, v in row.items()} for row in par_rows[l]]
                for l in par_levels}

    if verbose:
        indent = 0
        for b in range(num_buckets):
            for dim in dim_sizes:
                if factors[dim][b] > 1:
                    print(' ' * indent + dim + ' wrap', factors[dim][b])
                    indent += 1
            for l in par_levels:
                if par_bucket[l] == b:
                    for s, row in enumerate(par_vals[l]):
                        tag = '(L'+str(l)+(('.s'+str(s)) if len(par_vals[l]) > 1 else '')+')'
                        for dim, f in row.items():
                            if f > 1:
                                print(' ' * indent + dim + ' parfor', f, tag)
                                indent += 1
            if b < num_slots:
                print(' ' * indent + 'LD/ST ' + order[b].op + ' @L' + str(order[b].lvl))
        for lvl, mems in enumerate(p.memories):
            for m, mem in enumerate(mems):
                print(p.label((lvl, m))+' Spatial Costs:',
                      [(o, solver.Value(spatial_vars[Unit(o, lvl)])) for o in mem.ops])
                print(p.label((lvl, m))+' Traffic:',
                      [(o, solver.Value(traffic_vars[Unit(o, lvl)])) for o in mem.ops])
        shared_acc = [(u.op+'@L'+str(u.lvl), solver.Value(parent_traffic[u])) for u in units
                      if solver.Value(parent_traffic[u]) != solver.Value(traffic_vars[u])]
        if shared_acc:
            print('Multicast Reads / Reduced Writes at Parent:', shared_acc)
        if comp_accesses:
            print('Compute Accesses:', [(op+' @'+p.label(p.comp_mem[op]), solver.Value(n))
                                        for op, n in comp_accesses.items()])
        print('Port Times (per instance):', [(p.label(k)+' '+kind, solver.Value(pv))
                                             for k, kind, pv in ports])
        if compute_var is not None:
            print('Compute Time:', solver.Value(compute_var))

    # cross-check against the independent evaluator
    ev = evaluate_schedule(p, order, factors, par_vals)
    for u in units:
        assert ev['spatial'][u] == solver.Value(spatial_vars[u]), (u, ev['spatial'][u])
        assert ev['traffic'][u] == solver.Value(traffic_vars[u]), (u, ev['traffic'][u])
    e_val, d_val = ev['energy'], ev['delay']
    assert e_val == solver.Value(energy) and d_val == solver.Value(delay), (e_val, d_val)
    obj_val = {'energy': e_val, 'delay': d_val, 'edp': e_val * d_val}[objective]
    if verbose:
        print('Energy:', e_val, 'Delay:', d_val, 'EDP:', e_val * d_val)

    return Schedule(obj_val, order, factors, e_val, d_val, parallel, par_vals)

if __name__ == '__main__':
    # Regression examples (see cb_einsum_ml_NOTES.md):
    # mm = {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')}
    # cb_einsum_ml(mm, 'C', {'m': 4096, 'k': 65536, 'n': 4096}, [4096, 524288], objective='energy')
    # cb_einsum_ml(mm, 'C', {'m': 4096, 'k': 65536, 'n': 4096}, [4096, 524288], objective='energy', blocked=True)

    # Q einsum from TCM paper
    cb_einsum_ml(
        {'I': ('b', 'm', 'd'), 'WQ': ('h', 'e', 'd'), 'Q': ('b', 'm', 'h', 'e')},
        'Q',
        {'b': 64, 'm': 64 * 1024, 'h': 32, 'e': 128, 'd': 4096},
        [[(1, ('WQ',))], [(4 * 1024 * 1024, ('I', 'Q'))], 128 * 1024 * 1024],
        level_costs=[MemCosts(0, 0, 0, 0), MemCosts(read_energy=3, write_energy=3, read_time=0, write_time=0), MemCosts(read_energy=22, write_energy=28, read_time=1, write_time=2)],
        dram_costs=MemCosts(83, 83, 3, 3),
        objective='edp',
        fanouts=[(128, 128), 4, 1],
        multicast=[(('I',), ('Q',)), ('I', 'WQ'), False],
        compute_time=8 * 2048,
        compute_energy=1,
        perfect_division=True
    )
