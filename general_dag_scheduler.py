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

    # ── Tree-structure variables (_build_tree_structure) ──────────────────────
    # ancestor[i][j]: the node containing i is a (non-strict) ancestor of the node containing j
    ancestor: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    # same_node[i][j]: the node containing i is the same as the node containing j
    same_node: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    # is_anchor[i]: i is the first (anchor) operand in its node; its temporal factors count for the node
    is_anchor: Dict[str, cp_model.IntVar] = field(default_factory=dict)

    # ── Timeline variables (_build_timeline) ──────────────────────────────────
    # time_start[i] / time_end[i]: unique integer timestamps for buffer lifetime of i
    time_start: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    time_end: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # contains[i][j]: time interval for i strictly contains that of j
    contains: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    # totally_after[i][j]: time interval for i is entirely after that of j
    totally_after: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    starts_after: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    ends_after: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)

    # ── Factor variables (_build_factor_vars) ─────────────────────────────────
    # spatial_dim[op][dim]: spatial tiling factor for operand op along dim
    spatial_dim: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)
    # temporal_dim[op][dim]: loop-count factor introduced at op's node along dim
    temporal_dim: Dict[str, Dict[str, cp_model.IntVar]] = field(default_factory=dict)

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
    # temporal_if_not_fused_cost[op]: product of total_temporal_dim values for op (ignoring fusion)
    temporal_if_not_fused_cost: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # total_temporal_cost[op]: temporal_if_not_fused_cost[op] if op is not fused, else 0
    total_temporal_cost: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # total_cost_vars[op]: spatial_cost * total_temporal_cost (= memory traffic cost for op)
    total_cost_vars: Dict[str, cp_model.IntVar] = field(default_factory=dict)
    # all_compute_iters[i]: total compute iterations for uniquified einsum i (or 0 if no compute cost)
    all_compute_iters: List = field(default_factory=list)


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
    Create per-operand start/end time variables and the interval-relationship
    auxiliary booleans (contains, totally_after, starts_after, ends_after).

    Constraints enforce:
    - start < end for every operand
    - all start/end timestamps are globally distinct (total order)
    - if i is a strict ancestor of j, j's interval is contained in i's or
      completely separate from it
    - incomparable buffers (neither is ancestor of the other) never overlap
    - hierarchical consistency: a strict ancestor relates to all its subtree
      members identically (no subtree-splitting)
    - all operands of the same einsum overlap in time
    - if i is the unique producer of an original operand, every reader of that
      operand is totally after i
    """
    model = sm.model
    ops = sm.all_operands
    N = len(ops)

    sm.time_start = {i: model.NewIntVar(0, 2*N - 1, f'{i}_start') for i in ops}
    sm.time_end   = {i: model.NewIntVar(0, 2*N - 1, f'{i}_end')   for i in ops}

    for i in ops:
        model.Add(sm.time_start[i] < sm.time_end[i])

    model.AddAllDifferent(
        [sm.time_start[i] for i in ops] + [sm.time_end[i] for i in ops])

    sm.contains     = {i: {j: model.NewBoolVar(f'{i}_contains_{j}')     for j in ops if i != j} for i in ops}
    sm.totally_after = {i: {j: model.NewBoolVar(f'{i}_totally_after_{j}') for j in ops if i != j} for i in ops}
    sm.starts_after  = {i: {j: model.NewBoolVar(f'{i}_starts_after_{j}')  for j in ops if i != j} for i in ops}
    sm.ends_after    = {i: {j: model.NewBoolVar(f'{i}_ends_after_{j}')    for j in ops if i != j} for i in ops}

    for i in ops:
        for j in ops:
            if i == j:
                continue

            # Define starts_after / ends_after via time comparisons
            model.Add(sm.time_start[i] > sm.time_start[j]).OnlyEnforceIf(sm.starts_after[i][j])
            model.Add(sm.time_start[i] < sm.time_start[j]).OnlyEnforceIf(sm.starts_after[i][j].Not())
            model.Add(sm.time_end[i]   > sm.time_end[j]).OnlyEnforceIf(sm.ends_after[i][j])
            model.Add(sm.time_end[i]   < sm.time_end[j]).OnlyEnforceIf(sm.ends_after[i][j].Not())
            model.Add(sm.starts_after[i][j] == sm.starts_after[j][i].Not())
            model.Add(sm.ends_after[i][j]   == sm.ends_after[j][i].Not())

            # Define contains
            model.Add(sm.time_start[i] < sm.time_start[j]).OnlyEnforceIf(sm.contains[i][j])
            model.Add(sm.time_end[i]   > sm.time_end[j]).OnlyEnforceIf(sm.contains[i][j])
            model.AddBoolOr(sm.starts_after[i][j], sm.ends_after[j][i]).OnlyEnforceIf(
                sm.contains[i][j].Not())

            # Define totally_after
            model.Add(sm.time_start[i] > sm.time_end[j]).OnlyEnforceIf(sm.totally_after[i][j])
            model.Add(sm.time_start[i] < sm.time_end[j]).OnlyEnforceIf(sm.totally_after[i][j].Not())

            # Strict ancestor implies interval containment or total separation
            model.AddBoolOr(
                [sm.totally_after[i][j], sm.totally_after[j][i], sm.contains[i][j]]
            ).OnlyEnforceIf(sm.ancestor[i][j], sm.ancestor[j][i].Not())

            # Producer must precede all readers of the same original operand
            if (sm.original_names[i] == sm.original_names[j]
                    and sm.operand_groups[sm.original_names[i]]["producer"] == i):
                model.Add(sm.totally_after[j][i] == 1)

    # Tree-incomparable buffers must not overlap
    for i in ops:
        for j in ops:
            if i == j:
                continue
            model.AddBoolOr(
                [sm.totally_after[i][j], sm.totally_after[j][i]]
            ).OnlyEnforceIf(sm.ancestor[i][j].Not(), sm.ancestor[j][i].Not())

    # Hierarchical timeline consistency: if p is a strict ancestor of q, and q
    # is an ancestor of r, then p must relate to q and r identically in timesteps
    # (no splitting a subtree by timestep).
    for p in ops:
        for q in ops:
            if p == q:
                continue
            p_strict_anc_q = model.NewBoolVar(f'{p}_strict_anc_{q}')
            model.AddBoolAnd([sm.ancestor[p][q], sm.ancestor[q][p].Not()]).OnlyEnforceIf(p_strict_anc_q)
            model.AddBoolOr([sm.ancestor[p][q].Not(), sm.ancestor[q][p]]).OnlyEnforceIf(p_strict_anc_q.Not())

            for r in ops:
                if p == r or q == r:
                    continue
                cond = model.NewBoolVar(f'cond_match_rel_{p}_{q}_{r}')
                model.AddBoolAnd([p_strict_anc_q, sm.ancestor[q][r]]).OnlyEnforceIf(cond)
                model.AddBoolOr([p_strict_anc_q.Not(), sm.ancestor[q][r].Not()]).OnlyEnforceIf(cond.Not())

                model.Add(sm.totally_after[p][q] == sm.totally_after[p][r]).OnlyEnforceIf(cond)
                model.Add(sm.totally_after[q][p] == sm.totally_after[r][p]).OnlyEnforceIf(cond)
                model.Add(sm.contains[p][q] == sm.contains[p][r]).OnlyEnforceIf(cond)

    # All operands in the same einsum must have overlapping lifetimes and be
    # comparable in the tree (one must be an ancestor of the other).
    for e in sm.einsums:
        for op1 in e.operand_dims:
            for op2 in e.operand_dims:
                if op1 == op2:
                    continue
                model.Add(sm.time_start[op1] < sm.time_end[op2])
                model.Add(sm.time_start[op2] < sm.time_end[op1])
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


def _build_fusion(sm: SchedulerModel, allow_spilling: bool) -> None:
    """
    Create must_write / must_read / fused variables and their defining
    constraints.

    An operand need not be transferred to/from memory if it is fused with an
    adjacent occurrence of the same original operand.  Fusion requires the two
    occurrences to be in the same node and to have back-to-back time intervals.
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
    sm.fused = {
        op: {
            consumer: model.NewBoolVar(f'fused_{op}_{consumer}')
            for consumer in sm.operand_groups[sm.original_names[op]]["consumers"]
            if consumer != op
        }
        for op in ops
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
                # Consumers are sequenced after the producer
                for consumer in consumers:
                    model.Add(sm.totally_after[consumer][op] == 1)

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

        # Fusion definition: same node and back-to-back intervals.
        # Consistent spatial factors along shared dimensions enforced for efficiency
        for consumer in consumers:
            if consumer == op:
                continue
            model.Add(sm.time_end[op] + 1 == sm.time_start[consumer]).OnlyEnforceIf(
                sm.fused[op][consumer])
            model.Add(sm.same_node[op][consumer] == 1).OnlyEnforceIf(
                sm.fused[op][consumer])
            # If not fused, the intervals must be fully separated.
            model.AddBoolOr(sm.totally_after[op][consumer], sm.totally_after[consumer][op])
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
      in j's, then i's temporal factor for that dim must be 1 (it can't be
      tiled at a level that j doesn't see).
    - Non-anchor operands must have all temporal factors equal to 1 (only the
      anchor's factors count for the node).
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
        for dim in sm.op_allowed_temp_dims[i]:
            model.Add(sm.temporal_dim[i][dim] == 1).OnlyEnforceIf(sm.is_anchor[i].Not())

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

        # total_temporal_dim[op][d] = product of contributions over all operands
        sm.total_temporal_dim[op] = {}
        for d in sm.op_allowed_temp_dims[op]:
            sm.total_temporal_dim[op][d] = add_mul_chain(
                model,
                [sm.temporal_dim_contribs[op][other_op][d] for other_op in ops],
                1, sm.all_dim_sizes[d] * (2 ** len(ops)),
                f'total_temporal_dim_{op}_{d}'
            )
            # Dim fidelity: spatial[op][d] × total_temporal[op][d] ≥ dim_size[d]
            # Equivalently: spatial[op][d] = ⌈dim_size[d] / total_temporal[op][d]⌉
            if d in sm.all_operand_dims[op]:
                total_size = model.NewIntVar(
                    1, sm.all_dim_sizes[d] * (2 ** len(ops)),
                    f'total_dim_size_{op}_{d}')
                model.AddMultiplicationEquality(
                    total_size, [sm.spatial_dim[op][d], sm.total_temporal_dim[op][d]])
                model.Add(total_size >= sm.all_dim_sizes[d])
                model.AddDivisionEquality(
                    sm.spatial_dim[op][d],
                    sm.all_dim_sizes[d] + sm.total_temporal_dim[op][d] - 1,
                    sm.total_temporal_dim[op][d])

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
            model.Add(sm.total_cost_vars[op] >= op_size).OnlyEnforceIf(sm.must_write[op])
            model.Add(sm.total_cost_vars[op] == 0).OnlyEnforceIf(sm.must_write[op].Not())
        elif op in sm.must_read:
            model.Add(sm.total_cost_vars[op] >= op_size).OnlyEnforceIf(sm.must_read[op])
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
    - Different occurrences of the same original operand must not overlap in
      time and must not be strict ancestors of each other.
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

    # No overlap and no strict ancestorship between different occurrences of the
    # same original operand.
    for e in sm.einsums:
        for op in e.operand_dims:
            other_names = [op2 for op2 in ops
                        if sm.original_names[op2] == sm.original_names[op] and op2 != op]
            for op2 in other_names:
                model.AddBoolOr(sm.totally_after[op][op2], sm.totally_after[op2][op])
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

    Since all start/end times are distinct integers, peak memory occurs at the
    moment each buffer is initialized (time_start[i]).  We therefore check the
    constraint at every time_start[i]: buffer j is live at that moment iff j
    started before i (starts_after[i][j]) and has not yet ended (not
    totally_after[i][j]).
    """
    model = sm.model
    ops = sm.all_operands

    for i in ops:
        active_costs = []
        for j in ops:
            if i == j:
                active_costs.append(sm.spatial_cost[i])
            else:
                is_active = model.NewBoolVar(f'active_at_start_{i}_{j}')
                model.AddBoolAnd(
                    [sm.starts_after[i][j], sm.totally_after[i][j].Not()]
                ).OnlyEnforceIf(is_active)
                model.AddBoolOr(
                    [sm.starts_after[i][j].Not(), sm.totally_after[i][j]]
                ).OnlyEnforceIf(is_active.Not())

                active_cost_ij = model.NewIntVar(0, sm.capacity, f'active_cost_{i}_{j}')
                model.Add(active_cost_ij == sm.spatial_cost[j]).OnlyEnforceIf(is_active)
                model.Add(active_cost_ij == 0).OnlyEnforceIf(is_active.Not())
                active_costs.append(active_cost_ij)

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
                    tmp = model.NewIntVar(1, sm.all_dim_sizes[d], f'tmp_{i}_{d}')
                    model.Add(tmp == min_sp + e.accel_gran[d] - 1)
                    model.AddDivisionEquality(repetitions, tmp, e.accel_gran[d])
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
                min_possible_total_iters, max_iterations, f'total_compute_iters_{i}')
            model.AddMultiplicationEquality(
                total_compute_iters, [total_repetitions, max_op_temporal])
            sm.all_compute_iters.append(total_compute_iters)
        else:
            sm.all_compute_iters.append(0)

    model.Minimize(
        sum(sm.all_compute_iters[i] * sm.einsums[i].compute_cost
            for i in range(len(sm.einsums)))
        + sum(sm.total_cost_vars[op] for op in ops)
    )


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
        # Per-operand summary
        for i in ops:
            print(f"Operand {i} (original name {sm.original_names[i]}):")
            print(f"  Time interval: [{solver.Value(sm.time_start[i])}, {solver.Value(sm.time_end[i])})")
            print(f"  Spatial factors: {{", end="")
            for d in sm.all_operand_dims[i]:
                print(f"{d}: {solver.Value(sm.spatial_dim[i][d])}, ", end="")
            print("}")
            print(f"  Temporal factors: {{", end="")
            for d in sm.op_allowed_temp_dims[i]:
                print(f"{d}: {solver.Value(sm.temporal_dim[i][d])}, ", end="")
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
            return min(solver.Value(sm.time_start[op]) for op in n)

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

        # Map the latest init-time of each einsum's operands to a compute event
        compute_events: Dict[int, tuple] = {}
        for idx, e in enumerate(sm.einsums):
            einsum_ops = [
                k for k in ops
                if k.endswith(f"_read_{idx}") or k.endswith(f"_write_{idx}")
            ]
            if einsum_ops:
                latest_init = max(solver.Value(sm.time_start[op]) for op in einsum_ops)
                out_op = next((k for k in einsum_ops if k.endswith(f"_write_{idx}")), None)
                in_ops = [k for k in einsum_ops if k != out_op]
                if out_op:
                    compute_events[latest_init] = (idx, out_op, in_ops)

        def print_tree(n: tuple, indent_level: int = 0,
                       dim_counts: Optional[Dict[str, int]] = None) -> None:
            if dim_counts is None:
                dim_counts = {}
            indent = "  " * indent_level
            anchor = next(
                (op for op in n if solver.Value(sm.is_anchor[op]) == 1), n[0])

            # Emit for-loops for non-trivial temporal factors at this node
            temporal_str = []
            new_dim_counts = dim_counts.copy()
            for d in sm.op_allowed_temp_dims[anchor]:
                val = solver.Value(sm.temporal_dim[anchor][d])
                if val > 1:
                    count = new_dim_counts.get(d, 0)
                    temporal_str.append((f"{d}{count}", val))
                    new_dim_counts[d] = count + 1

            inner_indent = indent
            for loop_var, val in temporal_str:
                print(f"{inner_indent}for {loop_var} in range({val}):")
                inner_indent += "  "
                indent_level += 1

            child_indent = indent_level

            # Collect all events in this node (inits, frees, child subtrees)
            events = []
            for op in n:
                events.append((solver.Value(sm.time_start[op]), 'init', op))
                events.append((solver.Value(sm.time_end[op]),   'free', op))
            for c in children[n]:
                events.append((node_start_time(c), 'child', c))
            events.sort(key=lambda x: x[0])

            for t, ev_type, item in events:
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

                    # Emit any compute event triggered at this time
                    if t in compute_events:
                        idx, write_op, in_ops = compute_events[t]
                        operands_str = ", ".join(in_ops)
                        op_type_str = (
                            f" [{sm.einsums[idx].operation}]"
                            if sm.einsums[idx].operation else ""
                        )
                        print(f"{inner_indent}{write_op} += compute_einsum_{idx}{op_type_str}({operands_str})")

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


# ─── 5. Orchestrator ─────────────────────────────────────────────────────────

def scheduler(
    einsums: List[Einsum],
    capacity: int,
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
    scheduler(
        [
            Einsum(
                {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
                'C',
                {'m': 32 * 1024, 'k': 4 * 1024, 'n': 16 * 1024},
                accel_gran={'m': 1, 'k': 128, 'n': 128},
                compute_cost=100,
                operation='matmul'
            ),
            Einsum(
                {'C': ('m', 'n'), 'D': ('n', 'l'), 'E': ('m', 'l')},
                'E',
                {'m': 32 * 1024, 'n': 16 * 1024, 'l': 4 * 1024},
                accel_gran={'m': 1, 'n': 128, 'l': 128},
                compute_cost=100,
                operation='matmul'
            )
        ],
        32 * 1024 * 1024,
        allow_spilling=False
    )