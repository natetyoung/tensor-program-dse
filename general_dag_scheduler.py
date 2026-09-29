"""
general_dag_scheduler.py

Synthesizes a schedule-tree / loop-tree structure for a DAG of einsums via
CP-SAT.  The top-level entry point is `scheduler()`.

Internal organisation
─────────────────────
  UniqueDAG / uniquify_einsums   Pre-processing: rename operands so every
                                 occurrence is unique across the DAG.

  SchedulerModel                 Context object that owns the CP-SAT model and
                                 every variable dict built during model
                                 construction.  After solving, the same object
                                 (together with the CpSolver) is sufficient for
                                 downstream consumers to query any solved value.

  _build_*                       Private helpers, each responsible for one
                                 logical phase of model construction.  They
                                 accept a SchedulerModel and mutate it in-place.

  print_schedule                 Standalone result-printing function; takes a
                                 solved SchedulerModel + CpSolver.

  scheduler                      Orchestrator: calls uniquify → build phases →
                                 solve → print_schedule, returns (sm, solver).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ortools.sat.python import cp_model

# Re-export Einsum so callers that do `from general_dag_scheduler import Einsum`
# continue to work unchanged.
from scheduler_utils import Einsum, add_mul_chain


# ─── 1. Pre-processing ────────────────────────────────────────────────────────

@dataclass
class UniqueDAG:
    """
    Result of uniquifying operand names across a DAG of einsums.

    Each occurrence of an operand in the original list is renamed so that, e.g.,
    the 'C' written by Einsum 0 becomes 'C_write_0' and the same 'C' read by
    Einsum 1 becomes 'C_read_1'.  This uniquification is needed to represent
    shared operands (fusion edges) explicitly in the tree model.
    """
    einsums: List[Einsum]                          # uniquified einsums
    original_names: Dict[str, str]                 # unique_name -> original_name
    operand_groups: Dict[str, dict]                # original_name -> {producer, consumers}
    all_operands: List[str]                        # ordered list of all unique operand names
    all_operand_dims: Dict[str, Tuple[str, ...]]   # unique_name -> dim tuple
    op_allowed_temp_dims: Dict[str, List[str]]     # unique_name -> dims allowed to have temporal factors
    all_dim_sizes: Dict[str, int]                  # dim_name -> size


def uniquify_einsums(einsums: List[Einsum]) -> UniqueDAG:
    """
    Rename operand occurrences to be unique across the DAG and return the
    resulting UniqueDAG.  No CP-SAT objects are created here.

    Raises ValueError if any output operand name is produced by more than one
    einsum.
    """
    uniquified_einsums = []
    original_names: Dict[str, str] = {}
    operand_groups: Dict[str, dict] = {}
    all_operand_dims: Dict[str, Tuple] = {}
    op_allowed_temp_dims: Dict[str, List[str]] = {}
    all_dim_sizes: Dict[str, int] = {}

    # Pass 1 – classify each occurrence as producer or consumer.
    for idx, e in enumerate(einsums):
        out_op = e.output_operand
        if out_op not in operand_groups:
            operand_groups[out_op] = {"producer": None, "consumers": []}
        else:
            if operand_groups[out_op]["producer"] is not None:
                raise ValueError(
                    f"Duplicate output operand name '{out_op}' found in Einsum index {idx}. "
                    "Output operand names must be unique across all Einsums."
                )
        operand_groups[out_op]["producer"] = f"{out_op}_write_{idx}"

        for op in e.operand_dims:
            if op == out_op:
                continue
            if op not in operand_groups:
                operand_groups[op] = {"producer": None, "consumers": []}
            operand_groups[op]["consumers"].append(f"{op}_read_{idx}")

    # Pass 2 – build uniquified Einsum objects and populate lookup dicts.
    for idx, e in enumerate(einsums):
        new_operand_dims: Dict[str, Tuple] = {}
        new_output = f"{e.output_operand}_write_{idx}"

        for op, dims in e.operand_dims.items():
            new_op = new_output if op == e.output_operand else f"{op}_read_{idx}"

            new_operand_dims[new_op] = dims
            original_names[new_op] = op
            all_operand_dims[new_op] = dims
            # Outputs may only be tiled in their own dims; inputs can be tiled
            # in any dim of the enclosing einsum (reduction dims included).
            op_allowed_temp_dims[new_op] = (
                list(dims) if op == e.output_operand else list(e.dim_sizes.keys())
            )
            for d in dims:
                if d not in all_dim_sizes:
                    all_dim_sizes[d] = e.dim_sizes[d]

        new_e = Einsum(new_operand_dims, new_output, e.dim_sizes,
                       e.accel_gran, e.compute_cost, e.operation)
        uniquified_einsums.append(new_e)

    all_operands = list(all_operand_dims.keys())

    return UniqueDAG(
        einsums=uniquified_einsums,
        original_names=original_names,
        operand_groups=operand_groups,
        all_operands=all_operands,
        all_operand_dims=all_operand_dims,
        op_allowed_temp_dims=op_allowed_temp_dims,
        all_dim_sizes=all_dim_sizes,
    )


# ─── 2. Model context ─────────────────────────────────────────────────────────

@dataclass
class SchedulerModel:
    """
    Owns the CP-SAT model and every variable dictionary built during model
    construction.

    An instance is created at the start of `scheduler()` and passed through each
    `_build_*` helper.  After `solver.Solve(sm.model)`, the same instance plus
    the solver are sufficient to extract any result; pass them to
    `print_schedule()` or query variable values directly for downstream use.

    Fields are grouped by the phase that creates them; see the _build_* helpers
    for the constraints that govern each group.
    """

    # ── Core model ────────────────────────────────────────────────────────────
    model: cp_model.CpModel

    # ── Problem data (read-only after construction; copied from UniqueDAG) ────
    einsums: List[Einsum]
    original_names: Dict[str, str]
    operand_groups: Dict[str, dict]
    all_operands: List[str]
    all_operand_dims: Dict[str, Tuple]
    op_allowed_temp_dims: Dict[str, List]
    all_dim_sizes: Dict[str, int]
    capacity: int
    num_cores: int

    # ── Tree-structure variables (_build_tree_structure) ──────────────────────
    # ancestor[i][j]: the node containing i is a (non-strict) ancestor of the node containing j
    ancestor: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    # same_node[i][j]: the node containing i is the same as the node containing j
    same_node: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    # is_anchor[i]: i is the first (anchor) operand in its node; its temporal factors count for the node
    is_anchor: Dict[str, cp_model.IntVar] = field(default_factory=dict)

    # ── Timeline variables (_build_timeline) ──────────────────────────────────
    # Time is measured in einsum steps: each einsum executes at one step, and
    # buffers are allocated/freed in the gaps between steps.
    # pos[k]: step at which einsum k executes (a permutation of [0, E))
    pos: List[cp_model.IntVar] = field(default_factory=list)
    # time_start[i] / time_end[i]: first / last step (inclusive) at which buffer i is live
    time_start: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    time_end: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # win_start[x] / win_end[x]: step range enclosing every buffer in the subtree rooted at x's node
    win_start: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    win_end: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # totally_after[i][j]: (half-reified) buffer i is live only at steps after buffer j is freed.
    # Only defined for pairs of occurrences of the same original operand.
    totally_after: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)

    # ── Factor variables (_build_factor_vars) ─────────────────────────────────
    # spatial_dim[op][dim]: spatial tiling factor for operand op along dim
    spatial_dim: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    # temporal_dim[op][dim]: loop-count factor introduced at op's node along dim
    temporal_dim: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    # parallel_dim[op][dim]: parallelization factor at op's node along dim (1 if not parallelized)
    parallel_dim: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)

    # ── Fusion variables (_build_fusion) ──────────────────────────────────────
    # must_write[op]: op must be written to off-chip memory
    must_write: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # must_read[op]: op must be loaded from off-chip memory
    must_read: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # fused[i][j]: operand i (a write) is fused with operand j (the matching read)
    fused: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)

    # ── Cost variables (_build_cost_vars) ─────────────────────────────────────
    # spatial_cost[op]: product of spatial_dim values for op (= buffer element count)
    spatial_cost: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # temporal_dim_contribs[op][other_op][dim]: contribution of other_op's temporal factor to op's total
    temporal_dim_contribs: Dict[str, Dict[str, Dict[str, cp_model.IntVar]]] = field(default_factory=dict)
    # total_temporal_dim[op][dim]: product of all ancestors' temporal factors for op along dim
    total_temporal_dim: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    # parallel_dim_contribs[op][other_op][dim]: contribution of other_op's parallel factor to op's total
    parallel_dim_contribs: Dict[str, Dict[str, Dict[str, cp_model.IntVar]]] = field(default_factory=dict)
    # total_parallel_dim[op][dim]: product of all ancestors' parallel factors for op along dim
    total_parallel_dim: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    # temporal_if_not_fused_cost[op]: product of total_temporal_dim values for op (ignoring fusion)
    temporal_if_not_fused_cost: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # total_temporal_cost[op]: temporal_if_not_fused_cost[op] if op is not fused, else 0
    total_temporal_cost: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # total_cost_vars[op]: spatial_cost * total_temporal_cost (= memory traffic cost for op)
    total_cost_vars: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # all_compute_iters[i]: total compute iterations for uniquified einsum i (or 0 if no compute cost)
    all_compute_iters: List = field(default_factory=list)
    final_compute_cost: Optional[cp_model.IntVar] = None
    final_communication_cost: Optional[cp_model.IntVar] = None


# ─── 3. Model-building helpers ────────────────────────────────────────────────

def _build_tree_structure(sm: SchedulerModel) -> None:
    """
    Create ancestor/same_node/is_anchor variables and the constraints that
    force them to represent a valid tree of nodes.

    Variables
    ─────────
    ancestor[i][j]   BoolVar: node(i) is a (non-strict) ancestor of node(j)
    same_node[i][j]  BoolVar: node(i) == node(j)   (iff ancestor both ways)
    is_anchor[i]     BoolVar: i is the lexicographically-first operand in its node
    """
    model = sm.model
    ops = sm.all_operands

    sm.ancestor  = {i: {j: model.NewBoolVar(f'{i}_a_{j}')   for j in ops} for i in ops}
    sm.same_node = {i: {j: model.NewBoolVar(f'{i}_s_{j}')   for j in ops} for i in ops}
    sm.is_anchor = {i:     model.NewBoolVar(f'{i}_is_anchor')               for i in ops}

    # Transitivity: i ancestor of j and j ancestor of k  =>  i ancestor of k
    # Consistency:  i and j share a descendant k  =>  one is an ancestor of the other
    for i in ops:
        for j in ops:
            if i == j:
                continue
            for k in ops:
                if i == k or j == k:
                    continue
                model.Add(sm.ancestor[i][k] == 1).OnlyEnforceIf(sm.ancestor[i][j], sm.ancestor[j][k])
                model.AddBoolOr(sm.ancestor[i][j], sm.ancestor[j][i]).OnlyEnforceIf(
                    sm.ancestor[i][k], sm.ancestor[j][k])

    # same_node[i][j]  iff  ancestor[i][j] AND ancestor[j][i]
    for i in ops:
        for j in ops:
            if i == j:
                model.Add(sm.same_node[i][j] == 1)
                model.Add(sm.ancestor[i][j] == 1)
                continue
            model.Add(sm.same_node[i][j] == 1).OnlyEnforceIf(sm.ancestor[i][j], sm.ancestor[j][i])
            model.Add(sm.same_node[i][j] == 0).OnlyEnforceIf(sm.ancestor[i][j].Not())
            model.Add(sm.same_node[i][j] == 0).OnlyEnforceIf(sm.ancestor[j][i].Not())

    # is_anchor[i]  iff  no earlier operand (by list index) shares the same node
    for i in range(len(ops)):
        for j in range(i):
            model.Add(sm.is_anchor[ops[i]] == 0).OnlyEnforceIf(sm.same_node[ops[i]][ops[j]])
        model.Add(sm.is_anchor[ops[i]] == 1).OnlyEnforceIf(
            [sm.same_node[ops[i]][ops[j]].Not() for j in range(i)])


def _build_timeline(sm: SchedulerModel) -> None:
    """
    Create the einsum step order, per-operand live ranges, per-operand subtree
    windows, and the totally_after auxiliary booleans.

    Time is measured in einsum steps: pos[k] is a permutation of [0, E), and
    each buffer i is live over the inclusive step range
    [time_start[i], time_end[i]].  Buffers are allocated and freed in the gaps
    between steps, so two ranges overlap iff they share a step.

    Constraints enforce:
    - every buffer is live at its own einsum's step (so all operands of an
      einsum overlap)
    - every producer einsum executes before each of its consumer einsums
    - x's window [win_start[x], win_end[x]] encloses the range of every
      buffer in the subtree rooted at x's node; same-node operands share a
      window
    - if p is a strict ancestor of x, p's range either encloses x's whole
      window or is completely separate from it (no subtree-splitting)
    - windows of incomparable operands (neither is ancestor of the other) never
      overlap, so each subtree occupies one contiguous block of steps
    - an einsum's step lies outside the window of any subtree that contains
      none of its operands (it cannot execute inside another subtree's loops)
    - all operands of the same einsum are comparable in the tree
    """
    model = sm.model
    ops = sm.all_operands
    E = len(sm.einsums)
    op_einsum = {op: k for k, e in enumerate(sm.einsums) for op in e.operand_dims}

    sm.pos = [model.NewIntVar(0, E - 1, f'einsum_{k}_pos') for k in range(E)]
    model.AddAllDifferent(sm.pos)

    # Producers execute before consumers
    for group in sm.operand_groups.values():
        if group["producer"] is None:
            continue
        for consumer in group["consumers"]:
            model.Add(sm.pos[op_einsum[group["producer"]]] < sm.pos[op_einsum[consumer]])

    sm.time_start = {i: model.NewIntVar(0, E - 1, f'{i}_start') for i in ops}
    sm.time_end   = {i: model.NewIntVar(0, E - 1, f'{i}_end')   for i in ops}
    sm.win_start  = {x: model.NewIntVar(0, E - 1, f'{x}_win_start') for x in ops}
    sm.win_end    = {x: model.NewIntVar(0, E - 1, f'{x}_win_end')   for x in ops}

    # Each buffer is live at its own einsum's step
    for i in ops:
        model.Add(sm.time_start[i] <= sm.pos[op_einsum[i]])
        model.Add(sm.pos[op_einsum[i]] <= sm.time_end[i])

    # totally_after is only needed between occurrences of the same original
    # operand (fusion / spilling), and only in the positive direction.
    sm.totally_after = {
        i: {j: model.NewBoolVar(f'{i}_totally_after_{j}')
            for j in ops if i != j and sm.original_names[i] == sm.original_names[j]}
        for i in ops
    }
    for i in ops:
        for j, lit in sm.totally_after[i].items():
            model.Add(sm.time_start[i] > sm.time_end[j]).OnlyEnforceIf(lit)

    # Subtree windows.  Windows need only be outer bounds: a loose window can
    # only force ancestors to live longer, so the solver prefers tight ones.
    for x in ops:
        for y in ops:
            # x's window encloses every buffer in x's subtree (including x)
            model.Add(sm.win_start[x] <= sm.time_start[y]).OnlyEnforceIf(sm.ancestor[x][y])
            model.Add(sm.time_end[y] <= sm.win_end[x]).OnlyEnforceIf(sm.ancestor[x][y])
            # Same-node operands share a subtree, so share a window (redundant
            # but safe: the intersection of their windows is always valid)
            if x < y:
                model.Add(sm.win_start[x] == sm.win_start[y]).OnlyEnforceIf(sm.same_node[x][y])
                model.Add(sm.win_end[x] == sm.win_end[y]).OnlyEnforceIf(sm.same_node[x][y])

    for p in ops:
        for x in ops:
            if p == x:
                continue
            # Strict ancestor p encloses x's whole window, or is entirely
            # before or after it.  This implies p relates identically to every
            # buffer in x's subtree.
            p_encloses = model.NewBoolVar(f'{p}_encloses_win_{x}')
            p_before   = model.NewBoolVar(f'{p}_before_win_{x}')
            p_after    = model.NewBoolVar(f'{p}_after_win_{x}')
            model.Add(sm.time_start[p] <= sm.win_start[x]).OnlyEnforceIf(p_encloses)
            model.Add(sm.win_end[x] <= sm.time_end[p]).OnlyEnforceIf(p_encloses)
            model.Add(sm.time_end[p] < sm.win_start[x]).OnlyEnforceIf(p_before)
            model.Add(sm.win_end[x] < sm.time_start[p]).OnlyEnforceIf(p_after)
            model.AddBoolOr([p_encloses, p_before, p_after]).OnlyEnforceIf(
                sm.ancestor[p][x], sm.ancestor[x][p].Not())

    for idx, x in enumerate(ops):
        for z in ops[idx + 1:]:
            # Incomparable subtrees occupy disjoint windows.  Since each
            # buffer's range lies within its own window, this also keeps
            # incomparable buffers from overlapping.
            x_first = model.NewBoolVar(f'win_{x}_before_win_{z}')
            z_first = model.NewBoolVar(f'win_{z}_before_win_{x}')
            model.Add(sm.win_end[x] < sm.win_start[z]).OnlyEnforceIf(x_first)
            model.Add(sm.win_end[z] < sm.win_start[x]).OnlyEnforceIf(z_first)
            model.AddBoolOr([x_first, z_first]).OnlyEnforceIf(
                sm.ancestor[x][z].Not(), sm.ancestor[z][x].Not())

    # An einsum executes outside the window of any subtree containing none of
    # its operands.  (If x is an ancestor of any operand of k, it is an
    # ancestor of k's deepest operand, since k's operands form a chain.)
    for x in ops:
        for k, e in enumerate(sm.einsums):
            if x in e.operand_dims:
                continue
            k_before = model.NewBoolVar(f'einsum_{k}_before_win_{x}')
            k_after  = model.NewBoolVar(f'einsum_{k}_after_win_{x}')
            model.Add(sm.pos[k] < sm.win_start[x]).OnlyEnforceIf(k_before)
            model.Add(sm.win_end[x] < sm.pos[k]).OnlyEnforceIf(k_after)
            model.AddBoolOr(
                [sm.ancestor[x][o] for o in e.operand_dims] + [k_before, k_after])

    # All operands in the same einsum must be comparable in the tree (one must
    # be an ancestor of the other).
    for e in sm.einsums:
        for op1 in e.operand_dims:
            for op2 in e.operand_dims:
                if op1 == op2:
                    continue
                model.AddBoolOr(sm.ancestor[op1][op2], sm.ancestor[op2][op1])


def _build_factor_vars(sm: SchedulerModel) -> None:
    """
    Create the spatial and temporal factor variables.

    spatial_dim[op][dim]  in [1, dim_size]  — number of elements tiled in dim
    temporal_dim[op][dim] in [1, dim_size]  — loop-count factor at op's node

    Constraints on these variables are added separately by _build_fusion (for
    spatial consistency across fused pairs) and _build_factor_constraints (for
    temporal ancestor/anchor constraints).
    """
    model = sm.model
    sm.spatial_dim = {
        op: {
            dim: model.NewIntVar(1, sm.all_dim_sizes[dim], f'{op}_sp_{dim}')
            for dim in sm.all_operand_dims[op]
        }
        for op in sm.all_operands
    }
    sm.temporal_dim = {
        op: {
            dim: model.NewIntVar(1, sm.all_dim_sizes[dim], f'{op}_tp_{dim}')
            for dim in sm.op_allowed_temp_dims[op]
        }
        for op in sm.all_operands
    }
    sm.parallel_dim = {
        op: {
            dim: model.NewIntVar(1, min(sm.num_cores, sm.all_dim_sizes[dim]), f'{op}_par_{dim}')
            for dim in sm.op_allowed_temp_dims[op]
        }
        for op in sm.all_operands
    }


def _build_fusion(sm: SchedulerModel, allow_spilling: bool) -> None:
    """
    Create must_write / must_read / fused variables and their defining
    constraints.

    An operand need not be transferred to/from memory if it is fused with an
    adjacent occurrence of the same original operand.  Fusion requires the two
    occurrences to be in the same node and to have effectively-identical time intervals.
    Fused operands must share spatial factors along shared dimensions.
    """
    model = sm.model
    ops = sm.all_operands

    sm.must_write = {
        e.output_operand: model.NewBoolVar(f'must_write_{e.output_operand}')
        for e in sm.einsums
    }
    sm.must_read = {
        op: model.NewBoolVar(f'must_read_{op}')
        for op in ops
        if sm.operand_groups[sm.original_names[op]]["producer"] != op
    }
    all_names = {}
    for op in sm.must_write:
        orig = sm.original_names[op]
        if orig not in all_names:
            all_names[orig] = [op]
    for op in sm.must_read:
        orig = sm.original_names[op]
        if orig not in all_names:
            all_names[orig] = [op]
        else:
            all_names[orig].append(op)
    # We do it this way to break symmetry on fusion (only one way needs to be expressible)
    sm.fused = {
        names[i]: {
            names[j]: model.NewBoolVar(f'fused_{names[i]}_{names[j]}')
            for j in range(i + 1, len(names))
        }
        for names in all_names.values() for i in range(len(names)) 
    }

    for op in ops:
        orig = sm.original_names[op]
        consumers = sm.operand_groups[orig]["consumers"]

        if op in sm.must_write:
            if len(consumers) == 0:
                # No consumers: this is a global output, must always be stored.
                model.Add(sm.must_write[op] == 1)
            else:
                # must_write iff at least one consumer must_read
                for consumer in consumers:
                    model.Add(sm.must_read[consumer] == 0).OnlyEnforceIf(sm.must_write[op].Not())
                model.AddBoolOr(
                    [sm.must_read[consumer] for consumer in consumers]
                ).OnlyEnforceIf(sm.must_write[op])
                # Consumers which must read are sequenced after the producer
                for consumer in consumers:
                    model.Add(sm.totally_after[consumer][op] == 1).OnlyEnforceIf(sm.must_read[consumer])

        if op in sm.must_read:
            possibly_fused_predecessors = [i for i in sm.fused if op in sm.fused[i]]
            if len(possibly_fused_predecessors) == 0:
                # No possible fusion source: this is a global input, must always be loaded.
                model.Add(sm.must_read[op] == 1)
            # must_read[op] == 0  iff  some fused[i][op] is true
            model.AddBoolOr(
                [sm.fused[i][op] for i in sm.fused if op in sm.fused[i]]
            ).OnlyEnforceIf(sm.must_read[op].Not())
            model.AddBoolAnd(
                [sm.fused[i][op].Not() for i in sm.fused if op in sm.fused[i]]
            ).OnlyEnforceIf(sm.must_read[op])

        # Fusion happens in chains, not trees: only one fusion partner in each direction
        for i1 in sm.fused:
            model.AddAtMostOne([
                sm.fused[i1][consumer] for consumer in sm.fused[i1]
            ])
        for i2 in ops:
            model.AddAtMostOne([
                sm.fused[i1][i2] for i1 in sm.fused if i2 in sm.fused[i1]
            ])

        # Fusion definition: same node and identical live ranges (so the shared
        # buffer is live at both einsums' steps).
        # Consistent spatial factors along shared dimensions enforced for efficiency
        for consumer in sm.fused[op] if op in sm.fused else []:
            if consumer == op:
                continue
            model.Add(sm.time_start[op] == sm.time_start[consumer]).OnlyEnforceIf(
                sm.fused[op][consumer])
            model.Add(sm.time_end[op] == sm.time_end[consumer]).OnlyEnforceIf(
                sm.fused[op][consumer])
            model.Add(sm.same_node[op][consumer] == 1).OnlyEnforceIf(
                sm.fused[op][consumer])
            # If not fused, the intervals must be fully separated.
            if op in sm.fused[consumer]:
                model.AddBoolOr(sm.totally_after[op][consumer], sm.totally_after[consumer][op]).OnlyEnforceIf(sm.fused[op][consumer].Not(), sm.fused[consumer][op].Not())
            else:
                model.AddBoolOr(sm.totally_after[op][consumer], sm.totally_after[consumer][op]).OnlyEnforceIf(sm.fused[op][consumer].Not())
            # Spatial factors must agree along any shared dimension.
            for dim in sm.all_operand_dims[op]:
                if dim in sm.spatial_dim[consumer]:
                    model.Add(
                        sm.spatial_dim[op][dim] == sm.spatial_dim[consumer][dim]
                    ).OnlyEnforceIf(sm.fused[op][consumer])

    if not allow_spilling:
        for op in sm.must_write:
            if len(sm.operand_groups[sm.original_names[op]]["consumers"]) > 0:
                model.Add(sm.must_write[op] == 0)


def _build_factor_constraints(sm: SchedulerModel) -> None:
    """
    Add constraints on temporal_dim variables that reflect tree-structure rules.

    - If i is an ancestor of j and a dim in i's allowed temporal dims is NOT
      in j's, then i's temporal and parallel factors for that dim must be 1 
      (we would introduce recompute for j's einsum otherwise).
    - Non-anchor operands must have all temporal and parallel factors equal 
      to 1 (only the anchor's factors count for the node).
    - Reinterpreted dimensions (a dimension present in one occurrence but not
      another of the same original operand) must have temporal factor 1 in any
      ancestor of the occurrence that lacks the dimension.
    """
    model = sm.model
    ops = sm.all_operands

    for i in ops:
        for j in ops:
            if i == j:
                continue
            for dim in sm.op_allowed_temp_dims[i]:
                if dim not in sm.op_allowed_temp_dims[j]:
                    model.Add(sm.temporal_dim[i][dim] == 1).OnlyEnforceIf(sm.ancestor[i][j])
                    model.Add(sm.parallel_dim[i][dim] == 1).OnlyEnforceIf(sm.ancestor[i][j])
        for dim in sm.op_allowed_temp_dims[i]:
            model.Add(sm.temporal_dim[i][dim] == 1).OnlyEnforceIf(sm.is_anchor[i].Not())
            model.Add(sm.parallel_dim[i][dim] == 1).OnlyEnforceIf(sm.is_anchor[i].Not())

    # Reinterpreted dimensions: if a dimension appears in one occurrence of an
    # original operand but not another, any ancestor of the occurrence that
    # lacks it must have temporal factor 1 for that dimension.
    for orig_name, group in sm.operand_groups.items():
        instances = []
        if group["producer"] is not None:
            instances.append(group["producer"])
        instances.extend(group["consumers"])

        for u1 in instances:
            for u2 in instances:
                if u1 == u2:
                    continue
                dims1 = set(sm.all_operand_dims[u1])
                dims2 = set(sm.all_operand_dims[u2])
                for dim in dims1 - dims2:
                    for op in ops:
                        if dim in sm.op_allowed_temp_dims[op]:
                            model.Add(sm.temporal_dim[op][dim] == 1).OnlyEnforceIf(
                                sm.ancestor[op][u2])
                            model.Add(sm.parallel_dim[op][dim] == 1).OnlyEnforceIf(
                                sm.ancestor[op][u2])

    # Hierarchical spatial bounds: if i is an ancestor of j, then i's spatial tile
    # must physically contain j's spatial tile for any shared dimension.
    for i in ops:
        for j in ops:
            if i == j:
                continue
            for dim in sm.all_operand_dims[i]:
                if dim in sm.all_operand_dims[j]:
                    model.Add(sm.spatial_dim[i][dim] >= sm.spatial_dim[j][dim]).OnlyEnforceIf(sm.ancestor[i][j])

    # No reduction across cores: Operands which are einsum outputs should have no ancestors (strict or otherwise) 
    # with a parallel factor in any dimension which is not in all_operand_dims for that operand.
    einsum_outputs = [e.output_operand for e in sm.einsums]
    for o in einsum_outputs:
        for a in ops:
            for dim in sm.op_allowed_temp_dims[a]:
                if dim not in sm.all_operand_dims[o]:
                    model.Add(sm.parallel_dim[a][dim] == 1).OnlyEnforceIf(sm.ancestor[a][o])
                    model.Add(sm.parallel_dim[a][dim] == 1).OnlyEnforceIf(sm.ancestor[o][a])

def _build_cost_vars(sm: SchedulerModel) -> None:
    """
    Build all cost-related variables:

    spatial_cost[op]              product of spatial_dim values  (buffer size)
    temporal_dim_contribs         per-ancestor, per-dim contributions
    total_temporal_dim[op][dim]   product of ancestor contributions for dim
    temporal_if_not_fused_cost    product of total_temporal_dim values
    total_temporal_cost           temporal cost gated by must_write/must_read
    total_cost_vars               spatial * temporal  (memory traffic)

    Also adds the dim-fidelity constraints:
      spatial[op][d] * total_temporal[op][d] ≥ dim_size[d]
    using ceiling-division to force the spatial factor up to cover all elements.
    """
    model = sm.model
    ops = sm.all_operands

    # Spatial cost = product of spatial_dim values for each operand
    for op in ops:
        op_size = 1
        for d in sm.all_operand_dims[op]:
            op_size *= sm.all_dim_sizes[d]
        sm.spatial_cost[op] = add_mul_chain(
            model,
            [sm.spatial_dim[op][d] for d in sm.all_operand_dims[op]],
            1, min(op_size, sm.capacity),
            f'spatial_cost_{op}'
        )

    # Temporal costs
    for op in ops:
        allowed_dim_product = 1
        for d in sm.op_allowed_temp_dims[op]:
            allowed_dim_product *= sm.all_dim_sizes[d]
        max_temporal_cost = allowed_dim_product * (2 ** len(sm.op_allowed_temp_dims[op]))

        # temporal_dim_contribs[op][other_op][d]: the factor that other_op
        # contributes to op's total temporal iteration count along dim d.
        # It equals other_op's temporal_dim[d] iff other_op is an ancestor of
        # op and is the anchor of its node; otherwise it equals 1.
        sm.temporal_dim_contribs[op] = {}
        for other_op in ops:
            sm.temporal_dim_contribs[op][other_op] = {}
            for d in sm.op_allowed_temp_dims[op]:
                contrib = model.NewIntVar(1, sm.all_dim_sizes[d],
                                         f'temp_contrib_{op}_{other_op}_{d}')
                sm.temporal_dim_contribs[op][other_op][d] = contrib
                if d in sm.temporal_dim[other_op]:
                    model.Add(contrib == sm.temporal_dim[other_op][d]).OnlyEnforceIf(
                        sm.ancestor[other_op][op], sm.is_anchor[other_op])
                    model.Add(contrib == 1).OnlyEnforceIf(sm.ancestor[other_op][op].Not())
                    model.Add(contrib == 1).OnlyEnforceIf(sm.is_anchor[other_op].Not())
                else:
                    model.Add(contrib == 1)
        
        # same for parallel_dim_contribs
        sm.parallel_dim_contribs[op] = {}
        for other_op in ops:
            sm.parallel_dim_contribs[op][other_op] = {}
            for d in sm.op_allowed_temp_dims[op]:
                contrib = model.NewIntVar(1, min(sm.num_cores, sm.all_dim_sizes[d]),
                                         f'par_contrib_{op}_{other_op}_{d}')
                sm.parallel_dim_contribs[op][other_op][d] = contrib
                if d in sm.parallel_dim[other_op]:
                    model.Add(contrib == sm.parallel_dim[other_op][d]).OnlyEnforceIf(
                        sm.ancestor[other_op][op], sm.is_anchor[other_op])
                    model.Add(contrib == 1).OnlyEnforceIf(sm.ancestor[other_op][op].Not())
                    model.Add(contrib == 1).OnlyEnforceIf(sm.is_anchor[other_op].Not())
                else:
                    model.Add(contrib == 1)

        # total_temporal_dim[op][d] = product of contributions over all operands
        sm.total_temporal_dim[op] = {}
        # total_parallel_dim[op][d] same
        sm.total_parallel_dim[op] = {}
        for d in sm.op_allowed_temp_dims[op]:
            sm.total_temporal_dim[op][d] = add_mul_chain(
                model,
                [sm.temporal_dim_contribs[op][other_op][d] for other_op in ops],
                1, sm.all_dim_sizes[d] * 4, # can overshoot via imperfect tiling but not by much
                f'total_temporal_dim_{op}_{d}'
            )
            sm.total_parallel_dim[op][d] = add_mul_chain(
                model,
                [sm.parallel_dim_contribs[op][other_op][d] for other_op in ops],
                1, sm.num_cores,
                f'total_parallel_dim_{op}_{d}'
            )
            # Dim fidelity: spatial[op][d] * total_temporal[op][d] * total_parallel[op][d] >= dim_size[d]
            # Equivalently: spatial[op][d] = ceil(dim_size[d] / (total_temporal[op][d] * total_parallel[op][d]))
            if d in sm.all_operand_dims[op]:
                total_size = model.NewIntVar(
                    1, sm.all_dim_sizes[d] * 4,
                    f'total_dim_size_{op}_{d}')
                total_except_spatial = model.NewIntVar(
                    1, sm.all_dim_sizes[d] * 4,
                    f'total_except_spatial_{op}_{d}')
                model.AddMultiplicationEquality(
                    total_except_spatial, [sm.total_temporal_dim[op][d], sm.total_parallel_dim[op][d]])
                model.AddMultiplicationEquality(
                    total_size, [sm.spatial_dim[op][d], total_except_spatial])
                model.Add(total_size >= sm.all_dim_sizes[d])
                model.AddDivisionEquality(
                    sm.spatial_dim[op][d],
                    sm.all_dim_sizes[d] + total_except_spatial - 1,
                    total_except_spatial)

        # Constrain the product of all parallel factors along the path to this operand to be at most num_cores
        path_parallel_dims = [sm.total_parallel_dim[op][d] for d in sm.op_allowed_temp_dims[op]]
        total_path_parallel = add_mul_chain(
            model,
            path_parallel_dims,
            1, sm.num_cores,
            f'total_path_parallel_{op}'
        )
        model.Add(total_path_parallel <= sm.num_cores)

        # temporal_if_not_fused_cost = product of total_temporal_dim values
        sm.temporal_if_not_fused_cost[op] = add_mul_chain(
            model,
            list(sm.total_temporal_dim[op].values()),
            1, max_temporal_cost,
            f'temporal_if_not_fused_{op}'
        )

        # total_temporal_cost is gated by the fusion decision
        sm.total_temporal_cost[op] = model.NewIntVar(0, max_temporal_cost,
                                                     f'total_temporal_cost_{op}')
        if op in sm.must_write:
            model.Add(sm.total_temporal_cost[op] == 0).OnlyEnforceIf(sm.must_write[op].Not())
            model.Add(sm.total_temporal_cost[op] == sm.temporal_if_not_fused_cost[op]).OnlyEnforceIf(
                sm.must_write[op])
        elif op in sm.must_read:
            model.Add(sm.total_temporal_cost[op] == 0).OnlyEnforceIf(sm.must_read[op].Not())
            model.Add(sm.total_temporal_cost[op] == sm.temporal_if_not_fused_cost[op]).OnlyEnforceIf(
                sm.must_read[op])
        else:
            assert False, "Internal error: all operands must be in must_write or must_read"

    # Total cost = spatial × temporal for each operand
    for op in ops:
        op_size = 1
        for d in sm.all_operand_dims[op]:
            op_size *= sm.all_dim_sizes[d]
        allowed_dim_product = 1
        for d in sm.op_allowed_temp_dims[op]:
            allowed_dim_product *= sm.all_dim_sizes[d]

        sm.total_cost_vars[op] = model.NewIntVar(
            0, allowed_dim_product * (2 ** len(sm.op_allowed_temp_dims[op])),
            f'total_cost_{op}'
        )
        model.AddMultiplicationEquality(
            sm.total_cost_vars[op],
            (sm.spatial_cost[op], sm.total_temporal_cost[op])
        )
        # If an operand is not fused, its total cost must be at least its full size.
        if op in sm.must_write:
            model.Add(sm.total_cost_vars[op] >= op_size // sm.num_cores).OnlyEnforceIf(sm.must_write[op])
            model.Add(sm.total_cost_vars[op] == 0).OnlyEnforceIf(sm.must_write[op].Not())
        elif op in sm.must_read:
            model.Add(sm.total_cost_vars[op] >= op_size // sm.num_cores).OnlyEnforceIf(sm.must_read[op])
            model.Add(sm.total_cost_vars[op] == 0).OnlyEnforceIf(sm.must_read[op].Not())


def _build_optimality_constraints(sm: SchedulerModel) -> None:
    """
    Add optional pruning / optimality constraints that eliminate symmetry and
    obviously suboptimal solutions without changing the feasible set of truly
    optimal schedules.

    - Temporal factors for dimensions that do not appear in the current node's
      operand (and no same-node operand) are forced to 1.
    - Spatial factors for a dimension are bounded by the maximum accelerator
      granularity for that dimension across all einsums.
    - Temporal factors are similarly bounded when all strict ancestors of an
      operand share that dimension.
    - Different occurrences of the same original operand must not be strict 
      ancestors of each other.
    - When there is no fusion at all, operands belonging to different einsums 
      must not be in an ancestor relationship.
    """
    model = sm.model
    ops = sm.all_operands

    # Compute max useful accelerator granularity per dimension
    max_useful_granularity: Dict[str, int] = {}
    for e in sm.einsums:
        for d in e.dim_sizes:
            if d not in max_useful_granularity:
                max_useful_granularity[d] = 1
            if e.accel_gran and e.compute_cost > 0:
                if d in e.accel_gran:
                    max_useful_granularity[d] = max(max_useful_granularity[d], e.accel_gran[d])
                elif 'PRODUCT' in e.accel_gran:
                    max_useful_granularity[d] = max(
                        max_useful_granularity[d], e.accel_gran['PRODUCT'])

    for op in ops:
        for dim in sm.op_allowed_temp_dims[op]:
            # Temporal factor is 1 if dim does not appear in this operand or
            # any same-node operand (always better to move to inner loop).
            if dim not in sm.all_operand_dims[op]:
                same_node_users = [
                    other for other in ops
                    if dim in sm.all_operand_dims[other] and other != op
                ]
                model.Add(sm.temporal_dim[op][dim] == 1).OnlyEnforceIf(
                    *([sm.same_node[op][other].Not() for other in same_node_users]))
            # Spatial factor is at most the max useful granularity when all
            # descendants use this dimension.
            if dim in sm.all_operand_dims[op]:
                non_users = [
                    other for other in ops
                    if dim not in sm.all_operand_dims[other] and other != op
                ]
                model.Add(sm.spatial_dim[op][dim] <= max_useful_granularity[dim]).OnlyEnforceIf(
                    *([sm.ancestor[op][other].Not() for other in non_users]))

    # Bound temporal factors when all strict ancestors share the dimension.
    for c in ops:
        c_has_strict_anc = model.NewBoolVar(f'{c}_has_strict_anc')
        is_strict_anc: Dict[str, cp_model.IntVar] = {}
        for a in ops:
            if a == c:
                continue
            var = model.NewBoolVar(f'{a}_is_strict_anc_of_{c}')
            model.AddBoolAnd([sm.ancestor[a][c], sm.ancestor[c][a].Not()]).OnlyEnforceIf(var)
            model.AddBoolOr([sm.ancestor[a][c].Not(), sm.ancestor[c][a]]).OnlyEnforceIf(var.Not())
            is_strict_anc[a] = var

        model.AddBoolOr(list(is_strict_anc.values())).OnlyEnforceIf(c_has_strict_anc)
        model.AddBoolAnd([v.Not() for v in is_strict_anc.values()]).OnlyEnforceIf(
            c_has_strict_anc.Not())

        for dim in sm.op_allowed_temp_dims[c]:
            bad_bs = [b for b in ops if dim not in sm.all_operand_dims[b] and b != c]
            bad_b_exists = model.NewBoolVar(f'bad_b_exists_{c}_{dim}')
            if not bad_bs:
                model.Add(bad_b_exists == 0)
            else:
                model.AddBoolOr([is_strict_anc[b] for b in bad_bs]).OnlyEnforceIf(bad_b_exists)
                model.AddBoolAnd(
                    [is_strict_anc[b].Not() for b in bad_bs]
                ).OnlyEnforceIf(bad_b_exists.Not())
            model.Add(
                sm.temporal_dim[c][dim] <= max_useful_granularity[dim]
            ).OnlyEnforceIf([c_has_strict_anc, bad_b_exists.Not()])

    # No strict ancestorship between different occurrences of the
    # same original operand.
    for e in sm.einsums:
        for op in e.operand_dims:
            other_names = [op2 for op2 in ops
                        if sm.original_names[op2] == sm.original_names[op] and op2 != op]
            for op2 in other_names:
                # same_node is allowed; strict ancestorship is not
                model.Add(sm.ancestor[op][op2] == sm.ancestor[op2][op])

    # When there is no fusion at all, operands from different einsums must not be
    # in any ancestor relationship.
    for i in range(len(sm.einsums)):
        for j in range(i + 1, len(sm.einsums)):
            e1, e2 = sm.einsums[i], sm.einsums[j]
            no_fusion_conds = [
                sm.fused[op][consumer].Not()
                for op in sm.fused
                for consumer in sm.fused[op]
            ]
            for op1 in e1.operand_dims:
                for op2 in e2.operand_dims:
                    model.AddBoolAnd(
                        [sm.ancestor[op1][op2].Not(), sm.ancestor[op2][op1].Not()]
                    ).OnlyEnforceIf(*no_fusion_conds)


def _build_capacity_constraint(sm: SchedulerModel) -> None:
    """
    At any point in time the sum of spatial costs of all live buffers must not
    exceed the capacity limit.

    Buffers are only allocated and freed between einsum steps, so it suffices
    to check the constraint at each einsum's step pos[k].  Buffer j is live at
    that step iff time_start[j] <= pos[k] <= time_end[j].  Read buffers only
    occupy memory if they must be loaded (fused reads alias their producer's
    buffer).

    Only one direction is encoded (live => cost counted): the capacity sum
    pushes the counted costs down on its own.
    """
    model = sm.model
    ops = sm.all_operands

    for k, e in enumerate(sm.einsums):
        active_costs = []
        for j in ops:
            if j in e.operand_dims:
                # Operands of einsum k are always live at its step
                if j not in sm.must_read:
                    active_costs.append(sm.spatial_cost[j])
                    continue
                live_conds = []
            else:
                # j is live at step k unless k is before or after j's range
                k_before = model.NewBoolVar(f'einsum_{k}_before_{j}')
                k_after  = model.NewBoolVar(f'einsum_{k}_after_{j}')
                model.Add(sm.pos[k] < sm.time_start[j]).OnlyEnforceIf(k_before)
                model.Add(sm.time_end[j] < sm.pos[k]).OnlyEnforceIf(k_after)
                live_conds = [k_before.Not(), k_after.Not()]
            if j in sm.must_read:
                live_conds.append(sm.must_read[j])

            active_cost = model.NewIntVar(0, sm.capacity, f'active_cost_{k}_{j}')
            model.Add(active_cost >= sm.spatial_cost[j]).OnlyEnforceIf(live_conds)
            active_costs.append(active_cost)

        model.Add(sum(active_costs) <= sm.capacity)


def _build_compute_cost_and_objective(sm: SchedulerModel) -> None:
    """
    Build per-einsum compute iteration count variables and set the minimisation
    objective.

    For einsums with compute_cost > 0, the number of iterations is determined
    by dividing spatial dimensions by the accelerator granularity (either per-
    dim or as a product), then multiplying by the maximum temporal cost of any
    operand in the einsum (reflecting the innermost loop depth).

    Objective: minimise   Σ_e  compute_cost_e × iters_e
                        + Σ_op total_cost_vars_op
    """
    model = sm.model
    ops = sm.all_operands

    sm.all_compute_iters = []
    for i, e in enumerate(sm.einsums):
        max_iterations = 1
        for d in e.dim_sizes:
            max_iterations *= e.dim_sizes[d] * 2

        if e.compute_cost > 0:
            min_possible_total_iters = 1

            if len(e.accel_gran) == 1 and 'PRODUCT' in e.accel_gran:
                # Special case: only the product of all spatial dims matters.
                for d in e.dim_sizes:
                    min_possible_total_iters *= sm.all_dim_sizes[d]
                min_possible_total_iters //= e.accel_gran['PRODUCT']

                min_spatial_dims = []
                for d in e.dim_sizes:
                    min_sp = model.NewIntVar(1, sm.all_dim_sizes[d], f'min_spatial_{i}_{d}')
                    candidates = [sm.spatial_dim[op][d]
                                  for op in e.operand_dims if d in sm.all_operand_dims[op]]
                    model.AddMinEquality(min_sp, candidates)
                    min_spatial_dims.append(min_sp)

                spatial_product = add_mul_chain(
                    model, min_spatial_dims,
                    1, sm.capacity * len(e.dim_sizes),
                    f'spatial_dim_product_{i}'
                )
                total_repetitions = model.NewIntVar(
                    1, max_iterations // e.accel_gran['PRODUCT'] + 1, f'repetitions_{i}')
                model.AddDivisionEquality(
                    total_repetitions,
                    spatial_product + e.accel_gran['PRODUCT'] - 1,
                    e.accel_gran['PRODUCT']
                )
            else:
                # General case: ceildiv per dimension, then multiply.
                for d in e.dim_sizes:
                    if d in e.accel_gran:
                        min_possible_total_iters *= sm.all_dim_sizes[d] // e.accel_gran[d]
                    else:
                        min_possible_total_iters *= sm.all_dim_sizes[d]

                inner_loop_repetitions: List[cp_model.IntVar] = []
                for d in e.accel_gran:
                    min_sp = model.NewIntVar(1, sm.all_dim_sizes[d], f'min_spatial_{i}_{d}')
                    candidates = [sm.spatial_dim[op][d]
                                  for op in e.operand_dims if d in sm.all_operand_dims[op]]
                    model.AddMinEquality(min_sp, candidates)
                    repetitions = model.NewIntVar(
                        1, sm.all_dim_sizes[d] // e.accel_gran[d] + 1, f'repetitions_{i}_{d}')
                    model.AddDivisionEquality(repetitions, min_sp + e.accel_gran[d] - 1, e.accel_gran[d])
                    inner_loop_repetitions.append(repetitions)

                total_repetitions = add_mul_chain(
                    model, inner_loop_repetitions,
                    1, max_iterations,
                    f'total_repetitions_{i}'
                )

            # Multiply by the maximum temporal cost of any operand in this einsum
            # (the innermost operand's loop depth).
            max_op_temporal = model.NewIntVar(1, max_iterations, f'max_temporal_cost_{i}')
            model.AddMaxEquality(
                max_op_temporal,
                [sm.temporal_if_not_fused_cost[op] for op in e.operand_dims]
            )
            total_compute_iters = model.NewIntVar(
                min_possible_total_iters // sm.num_cores, max_iterations, f'total_compute_iters_{i}')
            model.AddMultiplicationEquality(
                total_compute_iters, [total_repetitions, max_op_temporal])
            sm.all_compute_iters.append(total_compute_iters)
        else:
            sm.all_compute_iters.append(0)

    min_compute_cost = 0
    max_compute_cost = 0
    for i in range(len(sm.einsums)):
        if sm.einsums[i].compute_cost == 0:
            continue
        else:
            min_compute_cost += sm.einsums[i].compute_cost * sm.all_compute_iters[i].Proto().domain[0]
            max_compute_cost += sm.einsums[i].compute_cost * sm.all_compute_iters[i].Proto().domain[1]

    min_communication_cost = 0
    max_communication_cost = 0
    for op in ops:
        min_communication_cost += sm.total_cost_vars[op].Proto().domain[0]
        max_communication_cost += sm.total_cost_vars[op].Proto().domain[1]
    
    sm.final_compute_cost = model.NewIntVar(min_compute_cost, max_compute_cost, 'final_compute_cost')
    model.Add(sm.final_compute_cost == sum(sm.all_compute_iters[i] * sm.einsums[i].compute_cost
                                        for i in range(len(sm.einsums))))
    sm.final_communication_cost = model.NewIntVar(min_communication_cost, max_communication_cost, 'final_communication_cost')
    model.Add(sm.final_communication_cost == sum(sm.total_cost_vars[op] for op in ops))

    final_cost = model.NewIntVar(
        max(min_compute_cost, min_communication_cost),
        max(max_compute_cost, max_communication_cost), 
        'final_cost'
    )
    model.Add(
        final_cost >= sm.final_compute_cost
    )
    model.Add(
        final_cost >= sm.final_communication_cost
    )

    model.Minimize(final_cost*5 + sm.final_compute_cost + sm.final_communication_cost)


# ─── 4. Result extraction and printing ───────────────────────────────────────

def print_schedule(sm: SchedulerModel, solver: cp_model.CpSolver, status: int) -> None:
    """
    Print the solved schedule to stdout.

    If a solution was found (OPTIMAL or FEASIBLE), prints:
      - Per-operand time intervals, spatial factors, temporal factors, and
        must_write / must_read flags.
      - A loop-nest representation of the synthesized schedule tree.

    Always prints a per-operand and per-einsum cost breakdown at the end.

    Parameters
    ──────────
    sm      : SchedulerModel populated by the _build_* helpers
    solver  : CpSolver after calling solver.Solve(sm.model)
    status  : return value of solver.Solve (cp_model.OPTIMAL, FEASIBLE, etc.)
    """
    ops = sm.all_operands

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        einsum_order = sorted(range(len(sm.einsums)), key=lambda k: solver.Value(sm.pos[k]))
        print(f"Einsum order: {einsum_order}")

        # Per-operand summary
        for i in ops:
            print(f"Operand {i} (original name {sm.original_names[i]}):")
            print(f"  Live steps: [{solver.Value(sm.time_start[i])}, {solver.Value(sm.time_end[i])}]")
            print(f"  Spatial factors: {{", end="")
            for d in sm.all_operand_dims[i]:
                print(f"{d}: {solver.Value(sm.spatial_dim[i][d])}, ", end="")
            print("}")
            print(f"  Temporal factors: {{", end="")
            for d in sm.op_allowed_temp_dims[i]:
                print(f"{d}: {solver.Value(sm.temporal_dim[i][d])}, ", end="")
            print("}")
            print(f"  Parallel factors: {{", end="")
            for d in sm.op_allowed_temp_dims[i]:
                print(f"{d}: {solver.Value(sm.parallel_dim[i][d])}, ", end="")
            print("}")
            if i in sm.must_write:
                print(f"  Must write: {solver.Value(sm.must_write[i])}")
            if i in sm.must_read:
                print(f"  Must read: {solver.Value(sm.must_read[i])}")

        # ── Build the schedule-tree ───────────────────────────────────────────
        print("\n=== Synthesized Loop Nest ===")

        # Identify nodes (groups of same-node operands)
        nodes = []
        processed: set = set()
        for i in ops:
            if i in processed:
                continue
            node_ops = [j for j in ops if solver.Value(sm.same_node[i][j]) == 1]
            nodes.append(node_ops)
            processed.update(node_ops)

        # For each node, collect all descendants (including non-direct ones)
        strict_ancestor = {
            tuple(n1): [
                tuple(n2) for n2 in nodes
                if n1 != n2 and solver.Value(sm.ancestor[n1[0]][n2[0]]) == 1
            ]
            for n1 in nodes
        }

        roots = [
            tuple(n) for n in nodes
            if not any(tuple(n) in desc for desc in strict_ancestor.values())
        ]

        def node_start_time(n):
            # A subtree may start before any of its root node's own buffers
            subtree = [n] + strict_ancestor[n]
            return min(solver.Value(sm.time_start[op]) for m in subtree for op in m)

        # Build direct-children mapping (descendants without an intermediate)
        children: Dict[tuple, list] = {tuple(n): [] for n in nodes}
        for n in nodes:
            n_desc = strict_ancestor[tuple(n)]
            for d in n_desc:
                has_intermediate = any(
                    d in strict_ancestor[inter]
                    for inter in n_desc if inter != d
                )
                if not has_intermediate:
                    children[tuple(n)].append(d)

        for n in children:
            children[n].sort(key=node_start_time)
        roots.sort(key=node_start_time)

        # Each einsum computes at its step, in the node of its deepest operand
        # (the operand that every other operand of the einsum is an ancestor of)
        node_of = {op: tuple(n) for n in nodes for op in n}
        compute_events: Dict[tuple, list] = {tuple(n): [] for n in nodes}
        for idx, e in enumerate(sm.einsums):
            einsum_ops = list(e.operand_dims)
            deepest = next(
                o for o in einsum_ops
                if all(solver.Value(sm.ancestor[x][o]) for x in einsum_ops))
            in_ops = [o for o in einsum_ops if o != e.output_operand]
            compute_events[node_of[deepest]].append(
                (solver.Value(sm.pos[idx]), idx, e.output_operand, in_ops))

        def fused_depth(op):
            # Number of fusion hops back to the buffer's root, so aliases are
            # printed after the buffer they alias when allocated at the same step
            depth = 0
            while True:
                src = next((s for s in sm.fused
                            if op in sm.fused[s] and solver.Value(sm.fused[s][op])), None)
                if src is None:
                    return depth
                op, depth = src, depth + 1

        def print_tree(n: tuple, indent_level: int = 0,
                       dim_counts: Optional[Dict[str, int]] = None) -> None:
            if dim_counts is None:
                dim_counts = {}
            indent = "  " * indent_level
            anchor = next(
                (op for op in n if solver.Value(sm.is_anchor[op]) == 1), n[0])

            # Emit parallel loops / for-loops for non-trivial parallel and temporal factors at this node
            parallel_str = []
            temporal_str = []
            new_dim_counts = dim_counts.copy()
            for d in sm.op_allowed_temp_dims[anchor]:
                val = solver.Value(sm.parallel_dim[anchor][d])
                if val > 1:
                    count = new_dim_counts.get(d, 0)
                    parallel_str.append((f"{d}{count}", val))
                    new_dim_counts[d] = count + 1
            for d in sm.op_allowed_temp_dims[anchor]:
                val = solver.Value(sm.temporal_dim[anchor][d])
                if val > 1:
                    count = new_dim_counts.get(d, 0)
                    temporal_str.append((f"{d}{count}", val))
                    new_dim_counts[d] = count + 1

            inner_indent = indent
            for loop_var, val in parallel_str:
                print(f"{inner_indent}par {loop_var} in range({val}):")
                inner_indent += "  "
                indent_level += 1

            for loop_var, val in temporal_str:
                print(f"{inner_indent}for {loop_var} in range({val}):")
                inner_indent += "  "
                indent_level += 1

            child_indent = indent_level

            # Collect all events in this node (inits, computes, child subtrees,
            # frees).  Several events can share a step: allocations come
            # before the step's compute/child subtree, and frees after it.
            events = []
            for op in n:
                events.append((solver.Value(sm.time_start[op]), 0, fused_depth(op), 'init', op))
                events.append((solver.Value(sm.time_end[op]),   2, 0, 'free', op))
            for c in children[n]:
                events.append((node_start_time(c), 1, 0, 'child', c))
            for ev in compute_events[n]:
                events.append((ev[0], 1, 0, 'compute', ev[1:]))
            events.sort(key=lambda x: x[:3])

            for t, _, _, ev_type, item in events:
                if ev_type == 'init':
                    op = item
                    orig = sm.original_names[op]
                    shape_strs = [
                        str(solver.Value(sm.spatial_dim[op][d]))
                        for d in sm.all_operand_dims[op]
                    ]
                    if not shape_strs:
                        shape_tuple = "()"
                    elif len(shape_strs) == 1:
                        shape_tuple = f"({shape_strs[0]},)"
                    else:
                        shape_tuple = f"({', '.join(shape_strs)})"

                    is_read  = op in sm.must_read  and solver.Value(sm.must_read[op])
                    is_write = op in sm.must_write and solver.Value(sm.must_write[op])
                    is_fused = not is_read and not is_write

                    if is_fused:
                        fused_producer = next(
                            (src for src in sm.fused
                             if op in sm.fused[src] and solver.Value(sm.fused[src][op])),
                            None
                        )
                        if fused_producer:
                            print(f"{inner_indent}{op} = {fused_producer} # Fused alias time {t}")
                        else:
                            print(f"{inner_indent}{op} = zeros({shape_tuple}) # Fused root time {t}")
                    else:
                        if "_read_" in op:
                            print(f"{inner_indent}{op} = load({orig}, size={shape_tuple}) # time {t}")
                        else:
                            print(f"{inner_indent}{op} = zeros({shape_tuple}) # time {t}")

                elif ev_type == 'compute':
                    idx, write_op, in_ops = item
                    operands_str = ", ".join(in_ops)
                    op_type_str = (
                        f" [{sm.einsums[idx].operation}]"
                        if sm.einsums[idx].operation else ""
                    )
                    print(f"{inner_indent}{write_op} += compute_einsum_{idx}{op_type_str}({operands_str}) # time {t}")

                elif ev_type == 'free':
                    op = item
                    orig = sm.original_names[op]
                    is_write = op in sm.must_write and solver.Value(sm.must_write[op])
                    has_fused_consumer = any(
                        solver.Value(sm.fused[op][c]) for c in sm.fused.get(op, {}))
                    if not has_fused_consumer:
                        if is_write:
                            print(f"{inner_indent}store({orig}) = {op}")
                        print(f"{inner_indent}free({op}) # time {t}")

                elif ev_type == 'child':
                    print_tree(item, child_indent, new_dim_counts)

        for r in roots:
            print_tree(r)
        print("=============================\n")

    else:
        print(f"Solver did not find an optimal or feasible solution. Status: {status}")

    # Cost summary (printed regardless of solution status)
    print("COSTS:")
    for i, e in enumerate(sm.einsums):
        if e.compute_cost > 0:
            print(f"Einsum {i} (compute cost {e.compute_cost}): "
                  f"{solver.Value(sm.all_compute_iters[i])} iterations")
    for op in ops:
        print(
            f"Operand {op} (original name {sm.original_names[op]}): "
            f"total cost {solver.Value(sm.total_cost_vars[op])} "
            f"(spatial {solver.Value(sm.spatial_cost[op])}, "
            f"temporal {solver.Value(sm.total_temporal_cost[op])})"
        )
    if solver.Value(sm.final_compute_cost) > solver.Value(sm.final_communication_cost):
        print(f"Final cost = {solver.Value(sm.final_compute_cost)} (compute dominated vs {solver.Value(sm.final_communication_cost)})")
    elif solver.Value(sm.final_compute_cost) < solver.Value(sm.final_communication_cost):
        print(f"Final cost = {solver.Value(sm.final_communication_cost)} (communication dominated vs {solver.Value(sm.final_compute_cost)})")
    else:
        print(f"Final cost = {solver.Value(sm.final_compute_cost)} (compute and communication equal)")


# ─── 5. Orchestrator ─────────────────────────────────────────────────────────

def scheduler(
    einsums: List[Einsum],
    capacity: int,
    num_cores: int = 1,
    enforce_optimal_placement: bool = True,
    allow_spilling: bool = False,
    debug: bool = True,
) -> Tuple['SchedulerModel', cp_model.CpSolver]:
    """
    Synthesize a schedule-tree / loop-tree structure for a DAG of einsums.

    We view the tree as being built out of twigs like so: o--(o,o).
    The input DAG uses repeated operand names to represent dataflow; names are
    uniquified internally for the tree model.

    Parameters
    ──────────
    einsums                  : List of Einsum objects describing the DAG.
    capacity                 : On-chip memory capacity (element count).
    enforce_optimal_placement: If True, add pruning constraints that eliminate
                               obviously suboptimal solutions.
    allow_spilling           : If True, allow intermediate operands to be
                               written to and read from off-chip memory.
    debug                    : If True, print model-building progress.

    Returns
    ───────
    (sm, solver) where sm is the populated SchedulerModel and solver is the
    CpSolver after solving.  Callers can query any variable value via
    solver.Value(sm.<variable>[...]).
    """
    # ── Step 1: Pre-process ───────────────────────────────────────────────────
    dag = uniquify_einsums(einsums)

    if debug:
        print("Operand Name Uniquification Results:")
        print("  Uniquified Einsums:")
        for ue in dag.einsums:
            print("    ", ue)
        print("  Operand Groups (Original -> Unique Producer & Consumers):")
        for orig_name, group in dag.operand_groups.items():
            print(f"    {orig_name}:")
            print(f"      Producer:  {group['producer']}")
            print(f"      Consumers: {group['consumers']}")
        print()

    # ── Step 2: Create model context ──────────────────────────────────────────
    sm = SchedulerModel(
        model=cp_model.CpModel(),
        einsums=dag.einsums,
        original_names=dag.original_names,
        operand_groups=dag.operand_groups,
        all_operands=dag.all_operands,
        all_operand_dims=dag.all_operand_dims,
        op_allowed_temp_dims=dag.op_allowed_temp_dims,
        all_dim_sizes=dag.all_dim_sizes,
        capacity=capacity,
        num_cores=num_cores
    )

    # ── Step 3: Build model phases in dependency order ────────────────────────
    _build_tree_structure(sm)
    _build_timeline(sm)
    _build_factor_vars(sm)           # must come before _build_fusion (spatial_dim used there)
    _build_fusion(sm, allow_spilling)
    _build_factor_constraints(sm)    # must come after _build_fusion (uses is_anchor, ancestor)
    _build_cost_vars(sm)             # must come after both factor and fusion phases
    if enforce_optimal_placement:
        _build_optimality_constraints(sm)
    _build_capacity_constraint(sm)   # uses spatial_cost from _build_cost_vars
    _build_compute_cost_and_objective(sm)

    if debug:
        print("MODEL WRITING DONE")

    # ── Step 4: Solve ─────────────────────────────────────────────────────────
    solver = cp_model.CpSolver()
    status = solver.Solve(sm.model)
    if debug:
        print(solver.SolutionInfo())
        print(solver.ResponseStats())

    # ── Step 5: Print results ─────────────────────────────────────────────────
    print_schedule(sm, solver, status)

    return sm, solver


# ─── 6. Example usage ────────────────────────────────────────────────────────

if __name__ == '__main__':
    # scheduler(
    #     [Einsum(
    #         {'X': ('n', 'k', 'm'), 'A': ('m', 'k', 'h'), 'B': ('n', 'h'), 'C': ('m', 'n')},
    #         'C',
    #         {'m': 32 * 1024, 'k': 2 * 1024, 'n': 10283, 'h': 8}
    #     )],
    #     128 * 1024
    # )
    # scheduler(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 4 * 1024, 'k': 8 * 1024, 'n': 4 * 1024},
    #             accel_gran={'m': 32, 'n': 32},
    #             compute_cost=100
    #         ),
    #         Einsum(
    #             {'C': ('m', 'n'), 'E': ('m', 'n')},
    #             'E',
    #             {'m': 4 * 1024, 'n': 4 * 1024},
    #             accel_gran={'PRODUCT': 32 * 32},
    #             compute_cost=100
    #         )
    #     ],
    #     512 * 1024,
    #     allow_spilling=True,
    #     debug=True
    # )
    # scheduler(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 32 * 1024, 'k': 4 * 1024, 'n': 16 * 1024},
    #             accel_gran={'m': 512, 'k': 128, 'n': 128},
    #             compute_cost=100,
    #             operation='matmul'
    #         ),
    #         Einsum(
    #             {'C': ('m', 'n'), 'D': ('n', 'l'), 'E': ('m', 'l')},
    #             'E',
    #             {'m': 32 * 1024, 'n': 16 * 1024, 'l': 4 * 1024},
    #             accel_gran={'m': 128, 'n': 128, 'l': 512},
    #             compute_cost=100,
    #             operation='matmul'
    #         )
    #     ],
    #     7 * 1024 * 1024,
    #     allow_spilling=True,
    #     num_cores=2
    # )
    scheduler(
        [
            Einsum(
                {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
                'C',
                {'m': 64 * 1024, 'k': 128, 'n': 16 * 1024},
                accel_gran={'m': 512, 'k': 128, 'n': 128},
                compute_cost=70710,
                operation='matmul'
            ),
            Einsum(
                {'C': ('m', 'n'), 'D': ('n', 'l'), 'E': ('m', 'l')},
                'E',
                {'m': 64 * 1024, 'n': 16 * 1024, 'l': 1},
                accel_gran={'PRODUCT': 128},  #{'m': 128, 'n': 128, 'l': 512},
                compute_cost=22,
                operation='matmul'
            )
        ],
        3 * 1024 * 1024,
        allow_spilling=True,
        num_cores=2
    )
    # scheduler(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 165, 'k': 4, 'n': 90},
    #             accel_gran={'m': 16},
    #             compute_cost=1,
    #             operation='matmul'
    #         ),
    #         Einsum(
    #             {'C': ('m', 'n'), 'D': ('n', 'l'), 'E': ('m', 'l')},
    #             'E',
    #             {'m': 165, 'n': 90, 'l': 16},
    #             accel_gran={'l': 16},
    #             compute_cost=1,
    #             operation='matmul'
    #         )
    #     ],
    #     512,
    #     allow_spilling=True,
    #     num_cores=1
    # )
    # scheduler(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 16 * 1024, 'k': 1024, 'n': 4 * 1024}
    #         ),
    #         Einsum(
    #             {'C': ('m', 'n'), 'D': ('n', 'l'), 'E': ('m', 'l')},
    #             'E',
    #             {'m': 16 * 1024, 'n': 4 * 1024, 'l': 1024}
    #         )
    #     ],
    #     8 * 1024 * 1024,
    #     allow_spilling=True
    # )
    # scheduler( #FULL SIX EINSUM GPT
    #     [
    #         Einsum(
    #             {'L0_X': ('m', 'd'), 'L0_WQ': ('d', 'k'), 'L0_Q_spill': ('m', 'k')}, 
    #             'L0_Q_spill', 
    #             {'m': 2048, 'd': 4096, 'k': 4096}
    #         ),
    #         Einsum(
    #             {'L0_Q': ('m', 'k'), 'L0_K': ('n', 'k'), 'L0_S_spill': ('m', 'n')},
    #             'L0_S_spill', 
    #             {'m': 2048, 'n': 2048, 'k': 4096}
    #         ), 
    #         Einsum(
    #             {'L0_S': ('m', 'n'), 'L0_V': ('n', 'k1'), 'L0_O_spill': ('m', 'k1')},
    #             'L0_O_spill', 
    #             {'m': 2048, 'n': 2048, 'k1': 4096}
    #         ), 
    #         Einsum(
    #             {'L0_O': ('m', 'k1'), 'L0_Wo': ('k1', 'd1'), 'L0_Y_spill': ('m', 'd1')},
    #             'L0_Y_spill',
    #             {'m': 2048, 'k1': 4096, 'd1': 4096}
    #         ), 
    #         Einsum(
    #             {'L0_Y': ('m', 'd1'), 'L0_W1': ('d1', 'f1'), 'L0_H_spill': ('m', 'f1')},
    #             'L0_H_spill',
    #             {'m': 2048, 'd1': 4096, 'f1': 16384}
    #         ),
    #         Einsum(
    #             {'L0_H': ('m', 'f1'), 'L0_W2': ('f1', 'd2'), 'L0_Z': ('m', 'd2')},
    #             'L0_Z',
    #             {'m': 2048, 'f1': 16384, 'd2': 4096}
    #         )
    #     ],
    #     8 * 1024 * 1024,
    #     allow_spilling=True
    # )