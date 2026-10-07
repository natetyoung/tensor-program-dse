from typing import Dict, List, NamedTuple, Tuple, Union
from ortools.sat.python import cp_model

class MemCosts(NamedTuple):
    '''Integer per-element access costs of one memory.'''
    read_energy: int = 1
    write_energy: int = 1
    read_time: int = 1
    write_time: int = 1

def add_mul_chain(model:cp_model.CpModel, components, lb, ub, pfx):
    old_var = components[0]
    new_var = components[0]
    for i in range(len(components) - 1):
        old_var = new_var
        new_var = model.NewIntVar(lb, ub, pfx+'_mul_chain'+str(i))
        constr = model.AddMultiplicationEquality(new_var, (old_var, components[i+1]))
    return new_var

def evaluate_schedule(operand_dims, dim_sizes, num_levels, order, factors):
    '''
    Independent cost evaluator.
    order: list of (op, level) per slot, outermost first.
    factors: dict dim -> list of factors per bucket (len(order) + 1).
    Returns (spatial, traffic) dicts keyed by (op, level).
    '''
    spatial, traffic = {}, {}
    for g, (op, lvl) in enumerate(order):
        sp, tp = 1, 1
        for b in range(len(order) + 1):
            for d in dim_sizes:
                if b > g and d in operand_dims[op]:
                    sp *= factors[d][b]
                elif b <= g:
                    tp *= factors[d][b]
        spatial[(op, lvl)] = sp
        traffic[(op, lvl)] = sp * tp
    return spatial, traffic

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
    Multi-level constrained buckets model for a single einsum.
    capacities[0] is the innermost (smallest) fast memory; data above the
    outermost level lives in DRAM. Each (operand, level) pair is a "unit"
    with one LD/ST slot in a single global order of slots; buckets of
    tiling factors sit between consecutive slots. Each operand's outer
    slot must precede its inner slot (inclusive hierarchy).
    Each entry of capacities is either an int (one memory shared by all
    operands at that level) or a list of memory specs (capacity, ops) or
    (capacity, ops, costs), which splits the level into separate memories.
    An operand belongs to at most one memory per level; an operand in no
    memory at a level bypasses it (no unit at that level). Memories without
    explicit costs use level_costs[lvl] (a MemCosts). DRAM, above the
    outermost level, has dram_costs.
    Traffic of unit (op, l) = data moved between level l and op's next
    present outer level (its "source", or DRAM). For inputs it is read
    from the source and written to l; for the output it is read from l and
    written to the source.
    Energy = sum over transfers of read_energy + write_energy per element.
    Delay = busiest port: memories (incl. DRAM) run in parallel with
    separate read and write ports, each busy for (elements x its time).
    objective: 'edp' (energy x delay), 'energy' or 'delay'.
    compute_accesses=True also charges compute's own accesses to each
    operand's innermost memory (or DRAM) to energy and that memory's ports:
    one read per iteration per input, and a read-modify-write per iteration
    for the output (no read for an element's first write). Along array dims
    that multicast an operand stored above them, instances that differ only
    in dims the operand lacks share one access (broadcast reads; reduced
    output writes). Padding is ignored.
    fanouts[l] replicates level l (all its memories and the compute below)
    fanouts[l] times per parent instance; a tuple is a multi-dimensional
    array, each array dimension holding a product of factors at most its
    size. The solver picks parallel factors over the dims each array dim
    allows (see multicast below), placed in the bucket just outside level l's
    outermost slot. If level l uses parallelism, all slots of levels above l
    precede all slots at or below l. Capacities are per instance; traffic
    and energy are totals over instances; port times are per instance.
    multicast[l] (or one bool for all levels): fills from a parent above
    level l into level-l instances read the parent once per distinct tile
    (instances that differ only in parallel dims the operand lacks share
    one read); writes still go to every instance. Without it, every
    instance's fill reads the parent separately. Each entry is a bool (all
    operands, every array dim), or one entry per array dimension of
    fanouts[l], each a bool or a collection of operand names, e.g.
    (('A',), ('B',)) for a 2-D array multicasting A along dim 0 and B along
    dim 1. A flat collection of operand names is accepted only for a 1-D
    fanout.
    Multicasting the output means the reverse: partial sums from instances
    that differ only in reduction dims are combined on the way to the parent
    (each instance's write-back is read; the parent is written once). An
    array dim may be parallel over reduction dims if it multicasts the
    output, and over output dims if it multicasts an input or nothing; True
    is the same as listing every operand.
    compute_time > 0 adds a compute port to delay: compute_time x
    ceil(iterations / total parallelism), ignoring padding.
    compute_energy adds compute_energy per iteration to energy (a constant
    for a given einsum, ignoring padding).
    blocked=True restricts to per-level blocks (all level l+1 slots before
    all level l slots), for comparison.
    break_ties=True fixes the order of adjacent slots with no loops between
    them.
    Returns (objective value, order, temporal factors, energy, delay,
    parallel factors {lvl: {dim: P}}).
    '''
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

    # mc_ops[l][s]: operands multicast along array dim s of level l's fanout
    def mc_set(entry):
        if isinstance(entry, bool):
            return frozenset(operand_dims) if entry else frozenset()
        for op in entry:
            if op not in operand_dims:
                raise ValueError('unknown operand '+str(op)+' in multicast')
        return frozenset(entry)
    mc_ops:List[List[frozenset]] = []
    for l, entry in enumerate(multicast):
        if isinstance(entry, bool):
            mc_ops.append([mc_set(entry)] * len(fanouts[l]))
        elif any(isinstance(e, str) for e in entry):
            # a flat operand list is only unambiguous for a 1-D fanout
            if len(fanouts[l]) > 1:
                raise ValueError('multicast['+str(l)+'] must give one entry per array dim of '
                                 'fanouts['+str(l)+'], e.g. (('+repr(entry[0])+',), ...)')
            mc_ops.append([mc_set(entry)])
        elif len(entry) == len(fanouts[l]):
            mc_ops.append([mc_set(e) for e in entry])
        else:
            raise ValueError('multicast['+str(l)+'] needs one entry per array dim of fanouts['+str(l)+']')
    if objective not in ('edp', 'energy', 'delay'):
        raise ValueError('unknown objective '+objective)

    model = cp_model.CpModel()
    operands = list(operand_dims.keys())

    # memories[lvl]: list of (capacity, ops, costs)
    memories:List[List[Tuple[int,Tuple[str],MemCosts]]] = []
    unit_mem:Dict[Tuple[str,int],int] = {}
    for lvl, spec in enumerate(capacities):
        if isinstance(spec, int):
            spec = [(spec, operands)]
        mems = []
        for m, mem in enumerate(spec):
            cap, ops = mem[0], tuple(mem[1])
            costs = mem[2] if len(mem) > 2 else level_costs[lvl]
            for op in ops:
                if op not in operand_dims:
                    raise ValueError('unknown operand '+op+' in L'+str(lvl)+' memory '+str(m))
                if (op, lvl) in unit_mem:
                    raise ValueError('operand '+op+' in multiple L'+str(lvl)+' memories')
                unit_mem[(op, lvl)] = m
            mems.append((cap, ops, costs))
        memories.append(mems)

    # memory keys: (lvl, m), plus 'DRAM'
    mem_costs = {(lvl, m): memories[lvl][m][2]
                 for lvl in range(num_levels) for m in range(len(memories[lvl]))}
    mem_costs['DRAM'] = dram_costs

    # units present, outermost level first; op_levels[op]: op's levels, innermost first
    units = [(op, lvl) for lvl in range(num_levels) for op in operands if (op, lvl) in unit_mem]
    op_levels = {op: [lvl for lvl in range(num_levels) if (op, lvl) in unit_mem] for op in operands}
    unit_cap = {u: memories[u[1]][unit_mem[u]][0] for u in units}

    # transfer endpoints: read from where the data is, write to where it goes
    unit_rd, unit_wr = {}, {}
    unit_src_lvl = {}  # source level (num_levels for DRAM)
    for op, lvl in units:
        here = (lvl, unit_mem[(op, lvl)])
        outer = [l for l in op_levels[op] if l > lvl]
        src = (outer[0], unit_mem[(op, outer[0])]) if outer else 'DRAM'
        unit_src_lvl[(op, lvl)] = outer[0] if outer else num_levels
        if op == output_operand:
            unit_rd[(op, lvl)], unit_wr[(op, lvl)] = here, src
        else:
            unit_rd[(op, lvl)], unit_wr[(op, lvl)] = src, here
    unit_rd_energy = {u: mem_costs[unit_rd[u]].read_energy for u in units}
    unit_wr_energy = {u: mem_costs[unit_wr[u]].write_energy for u in units}

    def multicast_dims(u):
        # (level, array dim) pairs crossed by u's transfer to/from a shared
        # parent that multicast (inputs) or reduce (output) u's operand
        return [(l, s) for l in range(u[1], unit_src_lvl[u])
                for s in range(len(fanouts[l])) if u[0] in mc_ops[l][s]]

    def mem_label(key):
        if key == 'DRAM':
            return 'DRAM'
        lvl, m = key
        if len(memories[lvl]) == 1:
            return 'L'+str(lvl)
        return 'L'+str(lvl)+'.m'+str(m)+' {'+','.join(memories[lvl][m][1])+'}'
    num_slots = len(units)
    num_buckets = num_slots + 1

    max_iters = 1
    for s in dim_sizes.values():
        max_iters *= s

    # placement_vars[u][g]: unit u occupies slot g (permutation)
    placement_vars:Dict[Tuple[str,int],List[cp_model.IntVar]] = {
        u: [model.NewBoolVar(u[0]+'_L'+str(u[1])+'_pl_'+str(g)) for g in range(num_slots)]
        for u in units
    }
    for u in units:
        model.AddExactlyOne(placement_vars[u])
    for g in range(num_slots):
        model.AddExactlyOne([placement_vars[u][g] for u in units])

    pos_vars = {}
    for u in units:
        pos_vars[u] = model.NewIntVar(0, num_slots - 1, u[0]+'_L'+str(u[1])+'_pos')
        model.Add(pos_vars[u] == sum(g * placement_vars[u][g] for g in range(num_slots)))

    # inclusion: outer level loaded before inner level
    for op in operands:
        lvls = op_levels[op]
        for inner, outer in zip(lvls, lvls[1:]):
            model.Add(pos_vars[(op, outer)] < pos_vars[(op, inner)])

    if blocked:
        for op, lvl in units:
            base = sum(1 for u in units if u[1] > lvl)
            n = sum(1 for u in units if u[1] == lvl)
            model.Add(pos_vars[(op, lvl)] >= base)
            model.Add(pos_vars[(op, lvl)] < base + n)

    # inner_vars[u][b]: unit u's slot is above bucket b (bucket b is inside u's tile)
    inner_vars:Dict[Tuple[str,int],List[cp_model.IntVar]] = {}
    for u in units:
        inner_vars[u] = []
        for b in range(num_buckets):
            v = model.NewBoolVar(u[0]+'_L'+str(u[1])+'_inner_'+str(b))
            model.Add(v == sum(placement_vars[u][g] for g in range(b)))
            inner_vars[u].append(v)

    # Parallel factors: level l's parallel loop sits in bucket n_out[l]
    # (fixed, since used parallelism forces outer levels' slots before it).
    # An array dim may be parallel over reduction dims if it multicasts the
    # output, and over output dims if it multicasts an input or nothing.
    reduction_dims = [d for d in dim_sizes if d not in operand_dims[output_operand]]
    def par_row_dims(l, s):
        ops = mc_ops[l][s]
        dims = reduction_dims if output_operand in ops else []
        if not ops or ops - {output_operand}:
            dims = dims + list(operand_dims[output_operand])
        return dims
    par_levels = [l for l in range(num_levels)
                  if any(size > 1 and par_row_dims(l, s) for s, size in enumerate(fanouts[l]))]
    total_fan = 1
    for f in fanouts:
        for size in f:
            total_fan *= size
    n_out = {l: sum(1 for u in units if u[1] > l) for l in par_levels}
    par_vars:Dict[int,Dict[str,cp_model.IntVar]] = {}
    par_slot_vars:Dict[int,List[Dict[str,cp_model.IntVar]]] = {}  # per array dim
    par_tot:Dict[int,cp_model.IntVar] = {}
    for l in par_levels:
        slots = []
        for s, size in enumerate(fanouts[l]):
            row = {d: model.NewIntVar(1, min(size, dim_sizes[d]), 'par_L'+str(l)+'_'+str(s)+'_'+d)
                   for d in par_row_dims(l, s)}
            if row:
                prod = add_mul_chain(model, list(row.values()), 1, size, 'par_L'+str(l)+'_'+str(s))
                model.Add(prod <= size)
            slots.append(row)
        par_slot_vars[l] = slots
        fan_tot = 1
        for size in fanouts[l]:
            fan_tot *= size
        par_vars[l] = {
            d: add_mul_chain(model, [row[d] for row in slots if d in row], 1, fan_tot,
                             'par_L'+str(l)+'_'+d)
            for d in dim_sizes if any(d in row for row in slots)
        }
        par_tot[l] = add_mul_chain(model, list(par_vars[l].values()), 1, fan_tot,
                                   'par_tot_L'+str(l))
        used = model.NewBoolVar('par_used_L'+str(l))
        model.Add(par_tot[l] >= 2).OnlyEnforceIf(used)
        model.Add(par_tot[l] == 1).OnlyEnforceIf(used.Not())
        for u in units:
            if u[1] > l:
                model.Add(pos_vars[u] < n_out[l]).OnlyEnforceIf(used)

    # rep[lvl]: instances of a level-lvl memory (product of fanouts at or above)
    rep:Dict[int,Union[int,cp_model.IntVar]] = {}
    for lvl in range(num_levels):
        above = [par_tot[l] for l in par_levels if l >= lvl]
        rep[lvl] = add_mul_chain(model, above, 1, total_fan, 'rep_L'+str(lvl)) if above else 1

    # Factor variables (temporal); eff_vars adds parallel factors in their buckets
    factor_vars:Dict[str,List[cp_model.IntVar]] = {}
    eff_vars:Dict[str,List[cp_model.IntVar]] = {}
    for dim in dim_sizes.keys():
        factor_vars[dim] = []
        for b in range(num_buckets):
            factor_vars[dim].append(model.NewIntVar(
                1, dim_sizes[dim], dim+'_'+str(b)+'_factor'
            ))
            if enforce_optimal_placement:
                for u in units:
                    # dim participates in unit just above bucket b (move out for free)
                    if b > 0 and dim in operand_dims[u[0]]:
                        model.Add(factor_vars[dim][b] == 1).OnlyEnforceIf(placement_vars[u][b-1])
                    # dim does not participate in unit just below bucket b (move in)
                    if b < num_slots and dim not in operand_dims[u[0]]:
                        model.Add(factor_vars[dim][b] == 1).OnlyEnforceIf(placement_vars[u][b])

            # forbid temporal reduction (no partial spilling); innermost output
            # slot is the deepest, so this implies the rule for all levels.
            # An output in no memory accumulates in DRAM, so no rule applies.
            if dim not in operand_dims[output_operand] and op_levels[output_operand]:
                model.Add(factor_vars[dim][b] == 1).OnlyEnforceIf(
                    inner_vars[(output_operand, op_levels[output_operand][0])][b].Not()
                )
        eff_vars[dim] = []
        for b in range(num_buckets):
            pars = [par_vars[l][dim] for l in par_levels if n_out[l] == b and dim in par_vars[l]]
            if pars:
                eff_vars[dim].append(add_mul_chain(
                    model, [factor_vars[dim][b]] + pars,
                    1, dim_sizes[dim] * total_fan, dim+'_'+str(b)+'_eff'))
            else:
                eff_vars[dim].append(factor_vars[dim][b])
        # Product of factors (incl. parallel) for this dim is at least dim size
        factor_product = add_mul_chain(
            model,
            eff_vars[dim],
            1, dim_sizes[dim] * 2**(num_buckets-1) * total_fan,
            dim+'_factor_prod'
        )
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
        ranked = sorted(units, key=lambda u: (-u[1], operands.index(u[0])))
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
        op: [
            add_mul_chain(model, [eff_vars[d][b] for d in operand_dims[op]],
                          1, max_iters, 'sp_prod_'+op+'_'+str(b))
            for b in range(num_buckets)
        ] for op in operands
    }
    tp_prods = [
        add_mul_chain(model, [eff_vars[d][b] for d in dim_sizes.keys()],
                      1, max_iters, 'tp_prod_'+str(b))
        for b in range(num_buckets)
    ]

    # Cost vars
    spatial_cost_vars:Dict[Tuple[str,int],cp_model.IntVar] = {}
    temporal_cost_vars:Dict[Tuple[str,int],cp_model.IntVar] = {}
    total_cost_vars:Dict[Tuple[str,int],cp_model.IntVar] = {}
    for u in units:
        op, lvl = u
        cap = unit_cap[u]
        pfx = op+'_L'+str(lvl)
        sp_contribs, tp_contribs = [], []
        for b in range(num_buckets):
            sc = model.NewIntVar(1, cap, pfx+'_spatial_contrib_'+str(b))
            model.Add(sc == sp_prods[op][b]).OnlyEnforceIf(inner_vars[u][b])
            model.Add(sc == 1).OnlyEnforceIf(inner_vars[u][b].Not())
            sp_contribs.append(sc)
            tc = model.NewIntVar(1, max_iters, pfx+'_temporal_contrib_'+str(b))
            model.Add(tc == tp_prods[b]).OnlyEnforceIf(inner_vars[u][b].Not())
            model.Add(tc == 1).OnlyEnforceIf(inner_vars[u][b])
            tp_contribs.append(tc)

        op_size = 1
        for d in operand_dims[op]:
            op_size *= dim_sizes[d]
        spatial_cost_vars[u] = add_mul_chain(model, sp_contribs, 1, cap, 'spatial_cost_'+pfx)
        temporal_cost_vars[u] = add_mul_chain(model, tp_contribs, 1, max_iters, 'temporal_cost_'+pfx)
        total_cost_vars[u] = model.NewIntVar(op_size, max_iters, 'total_cost_'+pfx)
        model.AddMultiplicationEquality(
            total_cost_vars[u],
            (spatial_cost_vars[u], temporal_cost_vars[u])
        )

    # capacity constraint per memory
    for lvl in range(num_levels):
        for cap, ops, _ in memories[lvl]:
            model.Add(cp_model.LinearExpr.Sum(
                [spatial_cost_vars[(op, lvl)] for op in ops]
            ) <= cap)

    # Traffic at the parent: instances that differ only in parallel dims the
    # operand lacks share one parent access, a multicast read for inputs or
    # a reduced write for the output. Those parallel factors are part of the
    # unit's temporal product, so this divides exactly.
    parent_traffic:Dict[Tuple[str,int],cp_model.IntVar] = {}
    for u in units:
        shared = [par_slot_vars[l][s][d] for l, s in multicast_dims(u) if l in par_slot_vars
                  for d in par_slot_vars[l][s] if d not in operand_dims[u[0]]]
        if shared:
            pfx = u[0]+'_L'+str(u[1])
            mc = add_mul_chain(model, shared, 1, total_fan, 'multicast_'+pfx)
            parent_traffic[u] = model.NewIntVar(1, max_iters, 'parent_traffic_'+pfx)
            model.AddMultiplicationEquality(total_cost_vars[u], (parent_traffic[u], mc))
        else:
            parent_traffic[u] = total_cost_vars[u]
    out_units = [u for u in units if u[0] == output_operand]
    read_traffic = {u: total_cost_vars[u] if u in out_units else parent_traffic[u] for u in units}
    write_traffic = {u: parent_traffic[u] if u in out_units else total_cost_vars[u] for u in units}

    # Compute accesses: every iteration reads each input and read-modify-
    # writes the output in the operand's innermost memory (or DRAM). Compute
    # units sit below every fanout, so accesses to a memory at level li cross
    # the fanouts below li; along array dims that multicast the operand,
    # instances differing only in dims it lacks share one access (a
    # broadcast read, or a reduced output write). The first write of each
    # output element needs no read. Padding is ignored.
    comp_mem, comp_rd, comp_wr = {}, {}, {}
    if compute_accesses:
        for op in operands:
            li = op_levels[op][0] if op_levels[op] else num_levels
            comp_mem[op] = (li, unit_mem[(op, li)]) if op_levels[op] else 'DRAM'
            shared = [par_slot_vars[l][s][d] for l in range(li) if l in par_slot_vars
                      for s in range(len(fanouts[l])) if op in mc_ops[l][s]
                      for d in par_slot_vars[l][s] if d not in operand_dims[op]]
            if shared:
                mc = add_mul_chain(model, shared, 1, total_fan, 'comp_multicast_'+op)
                accesses = model.NewIntVar(1, max_iters, 'comp_accesses_'+op)
                model.AddDivisionEquality(accesses, max_iters + mc - 1, mc)
            else:
                accesses = max_iters
            if op == output_operand:
                out_size = 1
                for d in operand_dims[op]:
                    out_size *= dim_sizes[d]
                # no more reduction parallelism than there are reduction iterations
                model.Add(accesses >= out_size)
                comp_wr[op], comp_rd[op] = accesses, accesses - out_size
            else:
                comp_rd[op] = accesses

    # Energy: every transfer reads one memory and writes another, plus the
    # compute itself
    energy_ub = max(1, sum((unit_rd_energy[u] + unit_wr_energy[u]) * max_iters for u in units)
                    + sum((mem_costs[comp_mem[op]].read_energy + mem_costs[comp_mem[op]].write_energy)
                          * max_iters for op in comp_mem)
                    + compute_energy * max_iters)
    energy = model.NewIntVar(0, energy_ub, 'energy')
    model.Add(energy == sum(unit_rd_energy[u] * read_traffic[u]
                            + unit_wr_energy[u] * write_traffic[u] for u in units)
              + sum(mem_costs[comp_mem[op]].read_energy * comp_rd[op] for op in comp_rd)
              + sum(mem_costs[comp_mem[op]].write_energy * comp_wr[op] for op in comp_wr)
              + compute_energy * max_iters)

    # Delay: each memory's read and write ports work in parallel with all
    # other ports; delay is the busiest port. Replicated memories split
    # their total traffic evenly over their instances.
    # ports: (memory key, 'read'/'write', time per element, units using it,
    #         operands whose compute accesses use it)
    ports = []
    for key, costs in mem_costs.items():
        for kind, ends, comp, t in (('read', unit_rd, comp_rd, costs.read_time),
                                    ('write', unit_wr, comp_wr, costs.write_time)):
            us = [u for u in units if ends[u] == key]
            cs = [op for op in comp if comp_mem[op] == key]
            if (us or cs) and t > 0:
                ports.append((key, kind, t, us, cs))
    port_vars = []
    for key, kind, t, us, cs in ports:
        pfx = mem_label(key)+'_'+kind
        port_ub = t * max_iters * (len(us) + len(cs))
        pv = model.NewIntVar(0, port_ub, pfx+'_time')
        key_rep = 1 if key == 'DRAM' else rep[key[0]]
        moved = read_traffic if kind == 'read' else write_traffic
        comp = comp_rd if kind == 'read' else comp_wr
        busy = t * sum(moved[u] for u in us) + t * sum(comp[op] for op in cs)
        if isinstance(key_rep, int):
            model.Add(pv == busy)
        else:
            # per-instance time = ceil(busy / instances)
            total = model.NewIntVar(0, port_ub + total_fan, pfx+'_total_time')
            model.Add(total == busy + key_rep - 1)
            model.AddDivisionEquality(pv, total, key_rep)
        port_vars.append(pv)
    delay_terms = list(port_vars)
    delay_ub = max([1] + [t * max_iters * (len(us) + len(cs)) for _, _, t, us, cs in ports])

    # Compute: each compute unit runs its share of the iterations
    compute_var = None
    if compute_time > 0:
        iters_per_unit = model.NewIntVar(1, max_iters, 'iters_per_unit')
        model.AddDivisionEquality(iters_per_unit, max_iters + rep[0] - 1, rep[0])
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

    order = [None] * num_slots
    for u in units:
        order[solver.Value(pos_vars[u])] = u
    factors = {d: [solver.Value(f) for f in factor_vars[d]] for d in dim_sizes}
    parallel = {l: {d: solver.Value(v) for d, v in par_vars[l].items()} for l in par_levels}
    par_slots = {l: [{d: solver.Value(v) for d, v in row.items()} for row in par_slot_vars[l]]
                 for l in par_levels}

    if verbose:
        indent_level = 0
        for b in range(num_buckets):
            for dim in dim_sizes.keys():
                if factors[dim][b] > 1:
                    print(' ' * indent_level + dim + ' wrap', factors[dim][b])
                    indent_level += 1
            for l in par_levels:
                if n_out[l] == b:
                    for s, row in enumerate(par_slots[l]):
                        tag = '(L'+str(l)+(('.s'+str(s)) if len(par_slots[l]) > 1 else '')+')'
                        for dim, p in row.items():
                            if p > 1:
                                print(' ' * indent_level + dim + ' parfor', p, tag)
                                indent_level += 1
            if b < num_slots:
                print(' ' * indent_level + 'LD/ST ' + order[b][0] + ' @L' + str(order[b][1]))
        for lvl in range(num_levels):
            for m, (_, ops, _) in enumerate(memories[lvl]):
                print(mem_label((lvl, m))+' Spatial Costs:',
                      [(o, solver.Value(spatial_cost_vars[(o, lvl)])) for o in ops])
                print(mem_label((lvl, m))+' Traffic:',
                      [(o, solver.Value(total_cost_vars[(o, lvl)])) for o in ops])
        mc_reads = [(u[0]+'@L'+str(u[1]), solver.Value(parent_traffic[u])) for u in units
                    if u not in out_units
                    and solver.Value(parent_traffic[u]) != solver.Value(total_cost_vars[u])]
        if mc_reads:
            print('Multicast Source Reads:', mc_reads)
        red_writes = [(u[0]+'@L'+str(u[1]), solver.Value(parent_traffic[u])) for u in out_units
                      if solver.Value(parent_traffic[u]) != solver.Value(total_cost_vars[u])]
        if red_writes:
            print('Reduced Parent Writes:', red_writes)
        if comp_mem:
            print('Compute Accesses:', [(op+' @'+mem_label(comp_mem[op]),
                                         solver.Value(comp_rd[op]) if op in comp_rd else 0,
                                         solver.Value(comp_wr[op]) if op in comp_wr else 0)
                                        for op in operands], '(reads, writes)')
        print('Port Times (per instance):', [(mem_label(key)+' '+kind, solver.Value(pv))
                              for (key, kind, _, _, _), pv in zip(ports, port_vars)])
        if compute_var is not None:
            print('Compute Time:', solver.Value(compute_var))

    # cross-check against independent evaluator, with parallel factors
    # folded into their buckets
    eff = {d: list(factors[d]) for d in dim_sizes}
    rep_py = {lvl: 1 for lvl in range(num_levels)}
    for l in par_levels:
        p_tot = 1
        for d, p in parallel[l].items():
            eff[d][n_out[l]] *= p
            p_tot *= p
        for lvl in range(l + 1):
            rep_py[lvl] *= p_tot
        if p_tot > 1:
            assert all(order[g][1] > l for g in range(n_out[l])), (l, order)
    spatial, traffic = evaluate_schedule(operand_dims, dim_sizes, num_levels, order, eff)
    for u in units:
        assert spatial[u] == solver.Value(spatial_cost_vars[u]), (u, spatial[u])
        assert traffic[u] == solver.Value(total_cost_vars[u]), (u, traffic[u])
    for lvl in range(num_levels):
        for cap, ops, _ in memories[lvl]:
            assert sum(spatial[(o, lvl)] for o in ops) <= cap
    reads, writes = {}, {}
    for u in units:
        mc = 1
        for l, s in multicast_dims(u):
            if l in par_slots:
                for d, p in par_slots[l][s].items():
                    if d not in operand_dims[u[0]]:
                        mc *= p
        assert traffic[u] % mc == 0, (u, mc)
        if u[0] == output_operand:
            reads[u], writes[u] = traffic[u], traffic[u] // mc
        else:
            reads[u], writes[u] = traffic[u] // mc, traffic[u]
    c_reads, c_writes = {}, {}
    for op in comp_mem:
        li = op_levels[op][0] if op_levels[op] else num_levels
        mc = 1
        for l in range(min(li, num_levels)):
            if l in par_slots:
                for s in range(len(fanouts[l])):
                    if op in mc_ops[l][s]:
                        for d, p in par_slots[l][s].items():
                            if d not in operand_dims[op]:
                                mc *= p
        accesses = -(-max_iters // mc)
        if op == output_operand:
            out_size = 1
            for d in operand_dims[op]:
                out_size *= dim_sizes[d]
            assert accesses >= out_size, (op, accesses)
            c_reads[op], c_writes[op] = accesses - out_size, accesses
        else:
            c_reads[op] = accesses
    e_val = (sum(unit_rd_energy[u] * reads[u] + unit_wr_energy[u] * writes[u] for u in units)
             + sum(mem_costs[comp_mem[op]].read_energy * c_reads[op] for op in c_reads)
             + sum(mem_costs[comp_mem[op]].write_energy * c_writes[op] for op in c_writes)
             + compute_energy * max_iters)
    port_times = []
    for key, kind, t, us, cs in ports:
        key_rep = 1 if key == 'DRAM' else rep_py[key[0]]
        moved = sum((reads if kind == 'read' else writes)[u] for u in us)
        assert t * moved % key_rep == 0
        comp = sum((c_reads if kind == 'read' else c_writes)[op] for op in cs)
        port_times.append(-(-t * (moved + comp) // key_rep))
    if compute_time > 0:
        port_times.append(compute_time * -(-max_iters // rep_py[0]))
    d_val = max([0] + port_times)
    assert e_val == solver.Value(energy) and d_val == solver.Value(delay), (e_val, d_val)
    obj_val = {'energy': e_val, 'delay': d_val, 'edp': e_val * d_val}[objective]
    if verbose:
        print('Energy:', e_val, 'Delay:', d_val, 'EDP:', e_val * d_val)

    return obj_val, order, factors, e_val, d_val, parallel

if __name__ == '__main__':
    mm = {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')}
    # print('=== single level ===')
    # cb_einsum_ml(mm, 'C', {'m': 4 * 1024, 'k': 8 * 1024, 'n': 4 * 1024}, [512 * 1024])

    # sizes = {'m': 4 * 1024, 'k': 64 * 1024, 'n': 4 * 1024}
    # caps = [4 * 1024, 512 * 1024]
    # print('=== two levels, general ordering ===')
    # gen = cb_einsum_ml(mm, 'C', sizes, caps)
    # print('=== two levels, per-level blocks ===')
    # blk = cb_einsum_ml(mm, 'C', sizes, caps, blocked=True)
    # print('general objective:', gen[0] if gen else None)
    # print('blocked objective:', blk[0] if blk else 'infeasible')

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
