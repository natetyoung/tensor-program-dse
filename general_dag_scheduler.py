from dataclasses import dataclass
from typing import Dict, List, Tuple
from ortools.sat.python import cp_model

def add_mul_chain(model:cp_model.CpModel, components, lb, ub, pfx):
    old_var = components[0]
    new_var = components[0]
    for i in range(len(components) - 1):
        old_var = new_var
        new_var = model.NewIntVar(lb, ub, pfx+'_mul_chain'+str(i))
        constr = model.AddMultiplicationEquality(new_var, (old_var, components[i+1]))
    return new_var

# Einsum description: 
# dict mapping operand names to tuples of coordinate names for operands
# tuple of coordinate names for outputs
# dict mapping coordinate names to sizes

@dataclass
class Einsum:
    operand_dims: Dict[str, Tuple[str]]
    output_operand: str
    dim_sizes: Dict[str, int]
    accel_gran: Dict[str, int] = None
    compute_cost: int = 0


def scheduler(
    einsums:List[Einsum],
    capacity:int,
    enforce_optimal_placement = True,
    allow_spilling = False,
    debug:bool = True
):
    '''
    Solver program which synthesizes a schedule-tree / loop-tree structure for a DAG of einsums
    We view the tree as being built out of twigs like so: o--(o,o)
    The input DAG has repeated operand names to represent dataflow, but the names are uniquified for the tree
    '''
    # 1. Uniquify operand names for the general DAG representation.
    uniquified_einsums = []
    original_names = {}  # unique_name -> original_name
    operand_groups = {}  # original_name -> {"producer": unique_name_or_None, "consumers": [unique_names]}
    all_operand_dims = {}
    op_allowed_temp_dims = {}
    all_dim_sizes = {}

    # Initialize operand groups to classify each unique name as producer or consumer
    for idx, e in enumerate(einsums):
        # Output/Producer
        out_op = e.output_operand
        if out_op not in operand_groups:
            operand_groups[out_op] = {"producer": None, "consumers": []}
        else:
            if operand_groups[out_op]["producer"] is not None:
                raise ValueError(f"Duplicate output operand name '{out_op}' found in Einsum index {idx}. Output operand names must be unique across all Einsums.")
        operand_groups[out_op]["producer"] = f"{out_op}_write_{idx}"

        # Inputs/Consumers
        for op in e.operand_dims:
            if op == out_op:
                continue
            if op not in operand_groups:
                operand_groups[op] = {"producer": None, "consumers": []}
            operand_groups[op]["consumers"].append(f"{op}_read_{idx}")

    for idx, e in enumerate(einsums):
        new_operand_dims = {}
        new_output = f"{e.output_operand}_write_{idx}"
        
        for op, dims in e.operand_dims.items():
            if op == e.output_operand:
                new_op = new_output
            else:
                new_op = f"{op}_read_{idx}"
            
            new_operand_dims[new_op] = dims
            original_names[new_op] = op

            all_operand_dims[new_op] = dims
            op_allowed_temp_dims[new_op] = dims if op == e.output_operand else list(e.dim_sizes.keys())
            for d in dims:
                if d not in all_dim_sizes:
                    all_dim_sizes[d] = e.dim_sizes[d]
            
        new_e = Einsum(new_operand_dims, new_output, e.dim_sizes, e.accel_gran, e.compute_cost)
        uniquified_einsums.append(new_e)

    all_operands = list(all_operand_dims.keys())

    if debug:
        print("Operand Name Uniquification Results:")
        print("  Uniquified Einsums:")
        for ue in uniquified_einsums:
            print("    ", ue)
        print("  Operand Groups (Original -> Unique Producer & Consumers):")
        for orig_name, group in operand_groups.items():
            print(f"    {orig_name}:")
            print(f"      Producer:  {group['producer']}")
            print(f"      Consumers: {group['consumers']}")
        print()

    '''
    Variables:
    Boolean:
    - "Operand A is in a (non-strict) ancestor node of operand B"
    - "Operand A is in the same node as operand B"
    - "Operand A is an anchor operand for its node" (meaning its temporal factors will count; first operand in node is anchor)
    - "Buffer A exists when buffer B is initialized and therefore they overlap"
    Integer:
    - (unique) start and end times for operand A's buffer
    - temporal factor of dim d for operand A (constrained to be 0 if A is not an anchor operand)
    - spatial factor of dim d for operand A
    - spatial and temporal costs
    '''
    model = cp_model.CpModel()
    ancestor:Dict[str,Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}_a_{}'.format(i, j)) for j in all_operands
        } for i in all_operands
    } # i_a_j is "the node containing i is a (not necessarily strict) ancestor of the node containing j"
    same_node:Dict[str,Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}_s_{}'.format(i, j)) for j in all_operands
        } for i in all_operands
    } # i_s_j is "the node containing i is the same as the node containing j"
    is_anchor:Dict[str,cp_model.IntVar] = {
        i: model.NewBoolVar('{}_is_anchor'.format(i)) for i in all_operands
    } # i_is_anchor is "i is an anchor operand for its node (its temporal factors are counted as those of the node)"

    # Constraints so ancestor relationships form a tree
    for i in all_operands:
        for j in all_operands:
            if i == j:
                continue
            for k in all_operands:
                if i == k or j == k:
                    continue
                # A ancestor of B and B ancestor of C implies A ancestor of C
                model.Add(ancestor[i][k] == 1).OnlyEnforceIf(ancestor[i][j], ancestor[j][k])
                # Consistency of ancestorship
                model.AddBoolOr(ancestor[i][j], ancestor[j][i]).OnlyEnforceIf(ancestor[i][k], ancestor[j][k])

    # Definition of same-node relationship in terms of ancestor relationships: a_s_b if and only if a_a_b and b_a_a
    for i in all_operands:
        for j in all_operands:
            if i == j:
                model.Add(same_node[i][j] == 1) # same node with self
                continue
            model.Add(same_node[i][j] == 1).OnlyEnforceIf(ancestor[i][j], ancestor[j][i])
            model.Add(same_node[i][j] == 0).OnlyEnforceIf(ancestor[i][j].Not())
            model.Add(same_node[i][j] == 0).OnlyEnforceIf(ancestor[j][i].Not())

    # Anchor constraints: i is an anchor if and only if none of the operands earlier in the list are in the same node
    for i in range(len(all_operands)):
        for j in range(i):
            model.Add(is_anchor[all_operands[i]] == 0).OnlyEnforceIf(same_node[all_operands[i]][all_operands[j]])
        model.Add(is_anchor[all_operands[i]] == 1).OnlyEnforceIf([same_node[all_operands[i]][all_operands[j]].Not() for j in range(i)])

    time_start:Dict[str,cp_model.IntVar] = {
        i: model.NewIntVar(0, 2*len(all_operands) - 1, '{}_start'.format(i)) for i in all_operands
    } # i_start is the time at which the buffer for operand i is initialized
    time_end:Dict[str,cp_model.IntVar] = {
        i: model.NewIntVar(0, 2*len(all_operands) - 1, '{}_end'.format(i)) for i in all_operands
    } # i_end is the time at which the buffer for operand i is deallocated
    # Explicitly constrain time_start < time_end since we no longer use IntervalVars with duration >= 1
    for i in all_operands:
        model.Add(time_start[i] < time_end[i])
    
    # timestep uniqueness constraints (buffers are initialized and deallocated in a total order)
    model.AddAllDifferent([time_start[i] for i in all_operands] + [time_end[i] for i in all_operands])

    # interval containment (enforced for strict ancestor relationships): if i is a strict ancestor of j, i's interval must contain that of j or not overlap at all
    contains:Dict[str, Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}_contains_{}'.format(i, j)) for j in all_operands if i != j
        } for i in all_operands
    } # i_contains_j is "the time interval for i strictly contains that of j"
    totally_after:Dict[str, Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}_totally_after_{}'.format(i, j)) for j in all_operands if i != j
        } for i in all_operands
    } # i_totally_after_j is "the time interval for i is totally after that of j"
    starts_after:Dict[str, Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}_starts_after_{}'.format(i, j)) for j in all_operands if i != j
        } for i in all_operands
    } # i_starts_after_j is "the time interval for i starts after that of j"
    ends_after:Dict[str, Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}_ends_after_{}'.format(i, j)) for j in all_operands if i != j
        } for i in all_operands
    } # i_ends_after_j is "the time interval for i ends after that of j"
    for i in all_operands:
        for j in all_operands:
            if i == j:
                continue
            model.Add(time_start[i] > time_start[j]).OnlyEnforceIf(starts_after[i][j])
            model.Add(time_start[i] < time_start[j]).OnlyEnforceIf(starts_after[i][j].Not())
            model.Add(time_end[i] > time_end[j]).OnlyEnforceIf(ends_after[i][j])
            model.Add(time_end[i] < time_end[j]).OnlyEnforceIf(ends_after[i][j].Not())
            model.Add(starts_after[i][j] == starts_after[j][i].Not())
            model.Add(ends_after[i][j] == ends_after[j][i].Not())

            model.Add(time_start[i] < time_start[j]).OnlyEnforceIf(contains[i][j])
            model.Add(time_end[i] > time_end[j]).OnlyEnforceIf(contains[i][j])
            model.AddBoolOr(starts_after[i][j], ends_after[j][i]).OnlyEnforceIf(contains[i][j].Not())

            model.Add(time_start[i] > time_end[j]).OnlyEnforceIf(totally_after[i][j])
            model.Add(time_start[i] < time_end[j]).OnlyEnforceIf(totally_after[i][j].Not())
    
            model.AddBoolOr([totally_after[i][j], totally_after[j][i], contains[i][j]]).OnlyEnforceIf(ancestor[i][j], ancestor[j][i].Not())

            # if i and j are the same operand and i is a write, j must be totally after i
            if original_names[i] == original_names[j] and operand_groups[original_names[i]]["producer"] == i:
                model.Add(totally_after[j][i] == 1)
    
    # non-overlap of tree-incomparable buffers: if neither i nor j is an ancestor of the other, their buffers cannot overlap in time
    for i in all_operands:
        for j in all_operands:
            if i == j:
                continue
            model.AddBoolOr([totally_after[i][j], totally_after[j][i]]).OnlyEnforceIf(ancestor[i][j].Not(), ancestor[j][i].Not())

    # Hierarchical timeline consistency: if P is a strict ancestor of Q, and Q is an ancestor of R,
    # then P must have the identical temporal relationship with Q and R, preventing P from splitting a child subtree.
    for p in all_operands:
        for q in all_operands:
            if p == q:
                continue
            
            p_strict_anc_q = model.NewBoolVar(f'{p}_strict_anc_{q}')
            model.AddBoolAnd([ancestor[p][q], ancestor[q][p].Not()]).OnlyEnforceIf(p_strict_anc_q)
            model.AddBoolOr([ancestor[p][q].Not(), ancestor[q][p]]).OnlyEnforceIf(p_strict_anc_q.Not())

            for r in all_operands:
                if p == r or q == r:
                    continue
                
                cond = model.NewBoolVar(f'cond_match_rel_{p}_{q}_{r}')
                model.AddBoolAnd([p_strict_anc_q, ancestor[q][r]]).OnlyEnforceIf(cond)
                model.AddBoolOr([p_strict_anc_q.Not(), ancestor[q][r].Not()]).OnlyEnforceIf(cond.Not())
                
                model.Add(totally_after[p][q] == totally_after[p][r]).OnlyEnforceIf(cond)
                model.Add(totally_after[q][p] == totally_after[r][p]).OnlyEnforceIf(cond)
                model.Add(contains[p][q] == contains[p][r]).OnlyEnforceIf(cond)


    # Einsum consistency: interval overlap for every pair of operands in the same Einsum
    for e in uniquified_einsums:
        for op1 in e.operand_dims.keys():
            for op2 in e.operand_dims.keys():
                if op1 == op2:
                    continue
                model.Add(time_start[op1] < time_end[op2])
                model.Add(time_start[op2] < time_end[op1])
                model.AddBoolOr(ancestor[op1][op2], ancestor[op2][op1])

    # Spatial dim vars: operand to dim to var
    spatial_dim:Dict[str,Dict[str,cp_model.IntVar]] = {
        op: {
            dim: model.NewIntVar(1, all_dim_sizes[dim], '{}_sp_{}'.format(op, dim)) for dim in all_operand_dims[op]
        } for op in all_operands
    }

    # Fusion vars
    must_write:Dict[str,cp_model.IntVar] = {
        e.output_operand: model.NewBoolVar('must_write_{}'.format(e.output_operand)) for e in uniquified_einsums
    } # must_write[op] is true if op must be written to memory (i.e. not all consumers are fused)
    must_read:Dict[str,cp_model.IntVar] = {
        op: model.NewBoolVar('must_read_{}'.format(op)) for op in all_operands if operand_groups[original_names[op]]["producer"] != op
    } # must_read[op] is true if op must be read from memory (i.e. not fused with any previous version of the same original operand)
    fused:Dict[str,Dict[str,cp_model.IntVar]] = {
        op: {
            consumer: model.NewBoolVar('fused_{}_{}'.format(op, consumer)) for consumer in operand_groups[original_names[op]]["consumers"] if consumer != op
        } for op in all_operands
    } # fused[i][j] is true if operand i is fused with operand j (i.e. same orig operand, same node, time_end[i] + 1 == time_start[j])
    # Fusion sanity / definition constraints
    for op in all_operands:
        if op in must_write:
            if len(operand_groups[original_names[op]]["consumers"]) == 0:
                model.Add(must_write[op] == 1) # If no consumers, must write since it's a global output
            else:
                # An operand need not be written if and only if no consumer needs to read it
                for consumer in operand_groups[original_names[op]]["consumers"]:
                    model.Add(must_read[consumer] == 0).OnlyEnforceIf(must_write[op].Not())
                model.AddBoolOr([must_read[consumer] for consumer in operand_groups[original_names[op]]["consumers"]]).OnlyEnforceIf(must_write[op])
                # The consumers must be sequenced after the producer
                for consumer in operand_groups[original_names[op]]["consumers"]:
                    model.Add(totally_after[consumer][op] == 1)
        if op in must_read:
            if len([i for i in fused if op in fused[i]]) == 0:
                model.Add(must_read[op] == 1) # If no other versions, must read since it's a global input and is only read this time
            # j need not be read if and only if fused[i][j] for some i is true
            model.AddBoolOr([fused[i][op] for i in fused if op in fused[i]]).OnlyEnforceIf(must_read[op].Not())
            model.AddBoolAnd([fused[i][op].Not() for i in fused if op in fused[i]]).OnlyEnforceIf(must_read[op])
        for consumer in operand_groups[original_names[op]]["consumers"]:
            if consumer == op:
                continue
            # op and consumer can only be fused if they are in the same node and time_end[op] + 1 == time_start[consumer]
            model.Add(time_end[op] + 1 == time_start[consumer]).OnlyEnforceIf(fused[op][consumer])
            model.Add(same_node[op][consumer] == 1).OnlyEnforceIf(fused[op][consumer])
            # converse: if not fused, totally before or totally after (will take care of not same node)
            model.AddBoolOr(totally_after[op][consumer], totally_after[consumer][op])
            # Same spatial dims for fused ops
            for dim in all_operand_dims[op]:
                if dim in spatial_dim[consumer]:
                    model.Add(spatial_dim[op][dim] == spatial_dim[consumer][dim]).OnlyEnforceIf(fused[op][consumer])
            
    # Temporal-here dim vars: operand to dim to var (constrain to 1 if not anchor or if not in allowed temp dims for descendant)
    temporal_dim:Dict[str,Dict[str,cp_model.IntVar]] = {
        op: {
            dim: model.NewIntVar(1, all_dim_sizes[dim], '{}_sp_{}'.format(op, dim)) for dim in op_allowed_temp_dims[op]
        } for op in all_operands
    }

    # Constraints for sanity of factors in tree
    for i in all_operands:
        for j in all_operands:
            if i == j:
                continue
            # A ancestor of B implies temporal-here factors in A which are not allowed for B are 1
            for dim in op_allowed_temp_dims[i]:
                if dim not in op_allowed_temp_dims[j]:
                    model.Add(temporal_dim[i][dim] == 1).OnlyEnforceIf(ancestor[i][j])
        # i not an anchor implies all temporal-here factors are 1
        for dim in op_allowed_temp_dims[i]:
            model.Add(temporal_dim[i][dim] == 1).OnlyEnforceIf(is_anchor[i].Not())

    if not allow_spilling:
        for op in must_write:
            if len(operand_groups[original_names[op]]["consumers"]) > 0:
                model.Add(must_write[op] == 0)
    
    # Costs
    spatial_cost:Dict[str,cp_model.IntVar] = {}
    for op in all_operands:
        op_size = 1
        for d in all_operand_dims[op]:
            op_size *= all_dim_sizes[d]
        spatial_cost[op] = add_mul_chain(
            model,
            [spatial_dim[op][d] for d in all_operand_dims[op]],
            1,
            min(op_size, capacity),
            'spatial_cost_'+op
        )
    
    temporal_dim_contribs:Dict[str,Dict[str,Dict[str,cp_model.IntVar]]] = {}
    total_temporal_dim:Dict[str,Dict[str,cp_model.IntVar]] = {}
    total_temporal_cost:Dict[str,cp_model.IntVar] = {}
    temporal_if_not_fused_cost:Dict[str,cp_model.IntVar] = {}

    # Total temporal dim calculation
    for op in all_operands:
        allowed_dim_product = 1
        for d in op_allowed_temp_dims[op]:
            allowed_dim_product *= all_dim_sizes[d]
        max_temporal_cost = allowed_dim_product * (2**len(op_allowed_temp_dims[op]))
        temporal_dim_contribs[op] = {}
        for other_op in all_operands:
            temporal_dim_contribs[op][other_op] = {}
            for d in op_allowed_temp_dims[op]:
                temporal_dim_contribs[op][other_op][d] = model.NewIntVar(
                    1, all_dim_sizes[d], f'temp_contrib_{op}_{other_op}_{d}'
                )
                if d in temporal_dim[other_op]:
                    model.Add(
                        temporal_dim_contribs[op][other_op][d] == temporal_dim[other_op][d]
                    ).OnlyEnforceIf(ancestor[other_op][op], is_anchor[other_op])
                    model.Add(
                        temporal_dim_contribs[op][other_op][d] == 1
                    ).OnlyEnforceIf(ancestor[other_op][op].Not())
                    model.Add(
                        temporal_dim_contribs[op][other_op][d] == 1
                    ).OnlyEnforceIf(is_anchor[other_op].Not())
                else:
                    model.Add(temporal_dim_contribs[op][other_op][d] == 1)
        total_temporal_dim[op] = {}
        for d in op_allowed_temp_dims[op]:
            total_temporal_dim[op][d] = add_mul_chain(
                model,
                [
                    temporal_dim_contribs[op][other_op][d] for other_op in all_operands
                ],
                1, all_dim_sizes[d] * (2**len(all_operands)),
                'total_temporal_dim_'+op+'_'+d
            )
            # Dim fidelity
            if d in all_operand_dims[op]:
                total_size = model.NewIntVar(1, all_dim_sizes[d] * (2**len(all_operands)), 'total_dim_size_{op}_{d}')
                model.AddMultiplicationEquality(total_size, [spatial_dim[op][d], total_temporal_dim[op][d]])
                model.Add(total_size >= all_dim_sizes[d])
                model.AddDivisionEquality(spatial_dim[op][d], all_dim_sizes[d] + total_temporal_dim[op][d] - 1, total_temporal_dim[op][d])

        total_temporal_cost[op] = model.NewIntVar(0, max_temporal_cost, 'total_temporal_cost_'+op)
        temporal_if_not_fused_cost[op] = add_mul_chain(
            model,
            list(total_temporal_dim[op].values()),
            1, max_temporal_cost,
            'temporal_if_not_fused_'+op
        )
        if op in must_write:
            model.Add(total_temporal_cost[op] == 0).OnlyEnforceIf(must_write[op].Not())
            model.Add(total_temporal_cost[op] == temporal_if_not_fused_cost[op]).OnlyEnforceIf(must_write[op])
        elif op in must_read:
            model.Add(total_temporal_cost[op] == 0).OnlyEnforceIf(must_read[op].Not())
            model.Add(total_temporal_cost[op] == temporal_if_not_fused_cost[op]).OnlyEnforceIf(must_read[op])
        else:
            assert False, "Internal error: all operands should be in either must_write or must_read"

    # total cost vars
    total_cost_vars:Dict[str,cp_model.IntVar] = {}
    for op in all_operands:
        op_size = 1
        for d in all_operand_dims[op]:
            op_size *= all_dim_sizes[d]
        allowed_dim_product = 1
        for d in op_allowed_temp_dims[op]:
            allowed_dim_product *= all_dim_sizes[d]
        total_cost_vars[op] = model.NewIntVar(0, allowed_dim_product * (2**len(op_allowed_temp_dims[op])), 'total_cost_'+op)
        model.AddMultiplicationEquality(
            total_cost_vars[op],
            (spatial_cost[op], total_temporal_cost[op])
        )
        # If an operand is not fused, its total cost must be at least its size
        if op in must_write:
            model.Add(total_cost_vars[op] >= op_size).OnlyEnforceIf(must_write[op])
            model.Add(total_cost_vars[op] == 0).OnlyEnforceIf(must_write[op].Not())
        elif op in must_read:
            model.Add(total_cost_vars[op] >= op_size).OnlyEnforceIf(must_read[op])
            model.Add(total_cost_vars[op] == 0).OnlyEnforceIf(must_read[op].Not())

    
    # Optional optimality sanity constraints
    if enforce_optimal_placement:
        max_useful_granularity = {}
        for e in uniquified_einsums:
            for d in e.dim_sizes.keys():
                if d not in max_useful_granularity:
                    max_useful_granularity[d] = 1
                if e.accel_gran and e.compute_cost > 0:
                    if d in e.accel_gran:
                        max_useful_granularity[d] = max(max_useful_granularity[d], e.accel_gran[d])
                    elif 'PRODUCT' in e.accel_gran:
                        max_useful_granularity[d] = max(max_useful_granularity[d], e.accel_gran['PRODUCT'])
        for op in all_operands:
            for dim in op_allowed_temp_dims[op]:
                # temporal factor is 1 if dim does not participate in this tensor or any same_node tensor (since if it did, we could just make this an inner loop and save the cost)
                if dim not in all_operand_dims[op]:
                    model.Add(temporal_dim[op][dim] == 1).OnlyEnforceIf(
                        *([
                            same_node[op][other_op].Not()
                            for other_op in all_operands
                            if dim in all_operand_dims[other_op] and other_op != op
                        ])
                    )
                # spatial factor is at most the maximum useful spatial granularity if dim does participate in this and any descendants
                if dim in all_operand_dims[op]:
                    model.Add(spatial_dim[op][dim] <= max_useful_granularity[dim]).OnlyEnforceIf(
                        *([
                            ancestor[op][other_op].Not()
                            for other_op in all_operands
                            if dim not in all_operand_dims[other_op] and other_op != op
                        ])
                    )

        # Ensure temporal_dim[C][dim] is at most the maximum useful spatial granularity if C has at least one strict ancestor
        # and dim participates in ALL strict ancestors of C.
        for c in all_operands:
            c_has_strict_anc = model.NewBoolVar(f'{c}_has_strict_anc')
            is_strict_anc = {}
            for a in all_operands:
                if a == c:
                    continue
                var = model.NewBoolVar(f'{a}_is_strict_anc_of_{c}')
                model.AddBoolAnd([ancestor[a][c], ancestor[c][a].Not()]).OnlyEnforceIf(var)
                model.AddBoolOr([ancestor[a][c].Not(), ancestor[c][a]]).OnlyEnforceIf(var.Not())
                is_strict_anc[a] = var
                
            model.AddBoolOr(list(is_strict_anc.values())).OnlyEnforceIf(c_has_strict_anc)
            model.AddBoolAnd([v.Not() for v in is_strict_anc.values()]).OnlyEnforceIf(c_has_strict_anc.Not())
            
            for dim in op_allowed_temp_dims[c]:
                bad_bs = [b for b in all_operands if dim not in all_operand_dims[b] and b != c]
                bad_b_exists = model.NewBoolVar(f'bad_b_exists_{c}_{dim}')
                if not bad_bs:
                    model.Add(bad_b_exists == 0)
                else:
                    model.AddBoolOr([is_strict_anc[b] for b in bad_bs]).OnlyEnforceIf(bad_b_exists)
                    model.AddBoolAnd([is_strict_anc[b].Not() for b in bad_bs]).OnlyEnforceIf(bad_b_exists.Not())
                
                model.Add(temporal_dim[c][dim] <= max_useful_granularity[dim]).OnlyEnforceIf([c_has_strict_anc, bad_b_exists.Not()])

        # No overlap and no strict ancestorship between different versions of the same operand
        for e in uniquified_einsums:
            for op in e.operand_dims.keys():
                other_names = [op2 for op2 in all_operands if original_names[op2] == original_names[op] and op2 != op]
                for op2 in other_names:
                    model.AddBoolOr(totally_after[op][op2], totally_after[op2][op])
                    model.Add(ancestor[op][op2] == ancestor[op2][op]) # same_node allowed, strict ancestorship not allowed
        # If no fusion at all, no ancestorship between any operands in different einsums
        for i in range(len(uniquified_einsums)):
            for j in range(i+1, len(uniquified_einsums)):
                e1 = uniquified_einsums[i]
                e2 = uniquified_einsums[j]
                for op1 in e1.operand_dims.keys():
                    for op2 in e2.operand_dims.keys():
                        model.AddBoolAnd([ancestor[op1][op2].Not(), ancestor[op2][op1].Not()]).OnlyEnforceIf(
                            *([
                                fused[op][consumer].Not() for op in fused for consumer in fused[op]
                            ])
                        )

    # Constraint for reinterpreted dimensions:
    # For any two instances of the same original operand, if a dimension appears in one but not the other,
    # it must have a temporal factor of 1 in any ancestor of the other instance.
    for orig_name, group in operand_groups.items():
        instances = []
        if group["producer"] is not None:
            instances.append(group["producer"])
        instances.extend(group["consumers"])
        
        for u1 in instances:
            for u2 in instances:
                if u1 == u2:
                    continue
                dims1 = set(all_operand_dims[u1])
                dims2 = set(all_operand_dims[u2])
                
                for dim in dims1 - dims2:
                    for op in all_operands:
                        if dim in op_allowed_temp_dims[op]:
                            model.Add(temporal_dim[op][dim] == 1).OnlyEnforceIf(ancestor[op][u2])

    # Capacity constraint
    # At any point in time, the sum of spatial_cost of all active buffers must be <= capacity.
    # Since all start and end times are distinct, peak memory must occur at some time_start[i].
    for i in all_operands:
        active_costs = []
        for j in all_operands:
            if i == j:
                active_costs.append(spatial_cost[i])
            else:
                is_active = model.NewBoolVar(f'active_at_start_{i}_{j}')
                # Buffer j is active at time_start[i] iff j starts before i and j does not end before i starts.
                model.AddBoolAnd([starts_after[i][j], totally_after[i][j].Not()]).OnlyEnforceIf(is_active)
                model.AddBoolOr([starts_after[i][j].Not(), totally_after[i][j]]).OnlyEnforceIf(is_active.Not())
                
                active_cost_i_j = model.NewIntVar(0, capacity, f'active_cost_{i}_{j}')
                model.Add(active_cost_i_j == spatial_cost[j]).OnlyEnforceIf(is_active)
                model.Add(active_cost_i_j == 0).OnlyEnforceIf(is_active.Not())
                
                active_costs.append(active_cost_i_j)
                
        model.Add(sum(active_costs) <= capacity)

    # Compute cost
    all_compute_iters = []
    # for all einsums:
    for i, e in enumerate(uniquified_einsums):
        max_iterations = 1
        for d in e.dim_sizes.keys():
            max_iterations *= e.dim_sizes[d] * 2
        # if it has a cost:
        if e.compute_cost > 0:
            # for each dim:
            if len(e.accel_gran) == 1 and 'PRODUCT' in e.accel_gran:
                # special case where only the product of the spatial dims matters. We can just multiply them together and then ceildiv by the granularity.
                min_spatial_dims = []
                for d in e.dim_sizes.keys():
                    min_spatial_dim = model.NewIntVar(1, all_dim_sizes[d], f'min_spatial_{i}_{d}')
                    spatial_dim_candidates = [spatial_dim[op][d] for op in e.operand_dims if d in all_operand_dims[op]]
                    model.AddMinEquality(min_spatial_dim, spatial_dim_candidates)
                    min_spatial_dims.append(min_spatial_dim)
                spatial_dim_product = add_mul_chain(
                    model,
                    min_spatial_dims,
                    1, capacity * len(e.dim_sizes), # upper bound on product of all spatial dims
                    f'spatial_dim_product_{i}'
                )
                total_repetitions = model.NewIntVar(1, max_iterations // e.accel_gran['PRODUCT'] + 1, f'repetitions_{i}')
                model.AddDivisionEquality(total_repetitions, spatial_dim_product + e.accel_gran['PRODUCT'] - 1, e.accel_gran['PRODUCT'])
            else:
                inner_loop_repetitions:List[cp_model.IntVar] = []
                for d in e.accel_gran.keys():
                    # find the smallest spatial value of each dim
                    min_spatial_dim = model.NewIntVar(1, all_dim_sizes[d], f'min_spatial_{i}_{d}')
                    spatial_dim_candidates = [spatial_dim[op][d] for op in e.operand_dims if d in all_operand_dims[op]]
                    model.AddMinEquality(min_spatial_dim, spatial_dim_candidates)
                    # ceildiv by granularity
                    repetitions = model.NewIntVar(1, all_dim_sizes[d] // e.accel_gran[d] + 1, f'repetitions_{i}_{d}')
                    tmp = model.NewIntVar(1, all_dim_sizes[d], f'tmp_{i}_{d}')
                    model.Add(tmp == min_spatial_dim + e.accel_gran[d] - 1)
                    model.AddDivisionEquality(repetitions, tmp, e.accel_gran[d])
                    inner_loop_repetitions.append(repetitions)
                # multiply all those
                total_repetitions = add_mul_chain(
                    model,
                    inner_loop_repetitions,
                    1, max_iterations,
                    f'total_repetitions_{i}'
                )
            # multiply by max temporal cost of any operand (i.e. innermost operand temporal cost)
            max_op_temporal_cost = model.NewIntVar(1, max_iterations, f'max_temporal_cost_{i}')
            model.AddMaxEquality(max_op_temporal_cost, [temporal_if_not_fused_cost[op] for op in e.operand_dims.keys()])
            total_compute_iters = model.NewIntVar(1, max_iterations, f'total_compute_iters_{i}')
            model.AddMultiplicationEquality(total_compute_iters, [total_repetitions, max_op_temporal_cost])
            all_compute_iters.append(total_compute_iters)
        else:
            all_compute_iters.append(0)

    # Objective: minimize total cost
    model.Minimize(sum([all_compute_iters[i] * uniquified_einsums[i].compute_cost for i in range(len(uniquified_einsums))]) + sum(total_cost_vars[op] for op in all_operands))

    if debug: print("MODEL WRITING DONE")

    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if debug:
        print(solver.SolutionInfo())
        print(solver.ResponseStats())

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for i in all_operands:
            print(f"Operand {i} (original name {original_names[i]}):")
            print(f"  Time interval: [{solver.Value(time_start[i])}, {solver.Value(time_end[i])})")
            print(f"  Spatial factors: {{", end="")
            for d in all_operand_dims[i]:
                print(f"{d}: {solver.Value(spatial_dim[i][d])}, ", end="")
            print("}")
            print(f"  Temporal factors: {{", end="")
            for d in op_allowed_temp_dims[i]:
                print(f"{d}: {solver.Value(temporal_dim[i][d])}, ", end="")
            print("}")
            if i in must_write:
                print(f"  Must write: {solver.Value(must_write[i])}")
            if i in must_read:
                print(f"  Must read: {solver.Value(must_read[i])}")

        print("\n=== Synthesized Loop Nest ===")
        nodes = []
        processed = set()
        for i in all_operands:
            if i in processed: continue
            node_ops = [j for j in all_operands if solver.Value(same_node[i][j]) == 1]
            nodes.append(node_ops)
            processed.update(node_ops)
            
        strict_ancestor = {
            tuple(n1): [tuple(n2) for n2 in nodes if n1 != n2 and solver.Value(ancestor[n1[0]][n2[0]]) == 1]
            for n1 in nodes
        }
        
        roots = [tuple(n) for n in nodes if not any(tuple(n) in desc for desc in strict_ancestor.values())]
        
        def node_start_time(n):
            return min(solver.Value(time_start[op]) for op in n)
            
        children = {tuple(n): [] for n in nodes}
        for n in nodes:
            n_desc = strict_ancestor[tuple(n)]
            for d in n_desc:
                has_intermediate = any(d in strict_ancestor[inter] for inter in n_desc if inter != d)
                if not has_intermediate:
                    children[tuple(n)].append(d)
                    
        for n in children:
            children[n].sort(key=node_start_time)
            
        roots.sort(key=node_start_time)
        
        # Track which einsums are computed and when, using the global uniquified_einsums
        compute_events = {}
        for idx, e in enumerate(uniquified_einsums):
            ops = [k for k in all_operands if k.endswith(f"_read_{idx}") or k.endswith(f"_write_{idx}")]
            if ops:
                latest_init_time = max(solver.Value(time_start[op]) for op in ops)
                out_op = next((k for k in ops if k.endswith(f"_write_{idx}")), None)
                in_ops = [k for k in ops if k != out_op]
                if out_op:
                    compute_events[latest_init_time] = (idx, out_op, in_ops)
        
        def print_tree(n, indent_level=0, dim_counts=None):
            if dim_counts is None:
                dim_counts = {}
            indent = "  " * indent_level
            anchor = next((op for op in n if solver.Value(is_anchor[op]) == 1), n[0])
            
            temporal_str = []
            new_dim_counts = dim_counts.copy()
            for d in op_allowed_temp_dims[anchor]:
                val = solver.Value(temporal_dim[anchor][d])
                if val > 1:
                    count = new_dim_counts.get(d, 0)
                    loop_var = f"{d}{count}"
                    temporal_str.append((loop_var, val))
                    new_dim_counts[d] = count + 1
            
            inner_indent = indent
            for loop_var, val in temporal_str:
                print(f"{inner_indent}for {loop_var} in range({val}):")
                inner_indent += "  "
                indent_level += 1
                
            child_indent = indent_level
                
            events = []
            for op in n:
                events.append((solver.Value(time_start[op]), 'init', op))
                events.append((solver.Value(time_end[op]), 'free', op))
            for c in children[n]:
                events.append((node_start_time(c), 'child', c))
                
            events.sort(key=lambda x: x[0])
            
            for t, ev_type, item in events:
                if ev_type == 'init':
                    op = item
                    orig = original_names[op]
                    shape_strs = [str(solver.Value(spatial_dim[op][d])) for d in all_operand_dims[op]]
                    if not shape_strs:
                        shape_tuple = "()"
                    elif len(shape_strs) == 1:
                        shape_tuple = f"({shape_strs[0]},)"
                    else:
                        shape_tuple = f"({', '.join(shape_strs)})"
                    
                    is_read = op in must_read and solver.Value(must_read[op])
                    is_write = op in must_write and solver.Value(must_write[op])
                    is_fused = not is_read and not is_write
                    
                    if is_fused:
                        fused_producer = next((i for i in fused if op in fused[i] and solver.Value(fused[i][op])), None)
                        if fused_producer:
                            print(f"{inner_indent}{op} = {fused_producer} # Fused alias time {t}")
                        else:
                            print(f"{inner_indent}{op} = zeros({shape_tuple}) # Fused root time {t}")
                    else:
                        if "_read_" in op:
                            print(f"{inner_indent}{op} = load({orig}, size={shape_tuple}) # time {t}")
                        else:
                            print(f"{inner_indent}{op} = zeros({shape_tuple}) # time {t}")
                    
                    # Print any computations that trigger at this time
                    if t in compute_events:
                        idx, write_op, ops = compute_events[t]
                        operands_str = ", ".join(ops)
                        print(f"{inner_indent}{write_op} += compute_einsum_{idx}({operands_str})")
                
                elif ev_type == 'free':
                    op = item
                    orig = original_names[op]
                    is_read = op in must_read and solver.Value(must_read[op])
                    is_write = op in must_write and solver.Value(must_write[op])
                    
                    has_fused_consumer = any(solver.Value(fused[op][c]) for c in fused.get(op, {}))
                    if has_fused_consumer:
                        pass # Memory ownership transferred to consumer
                    else:
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

    print("COSTS:")
    for i, e in enumerate(uniquified_einsums):
        if e.compute_cost > 0:
            print(f"Einsum {i} (compute cost {e.compute_cost}): {solver.Value(all_compute_iters[i])} iterations")
    for op in all_operands:
        print(f"Operand {op} (original name {original_names[op]}): total cost {solver.Value(total_cost_vars[op])} (spatial {solver.Value(spatial_cost[op])}, temporal {solver.Value(total_temporal_cost[op])})")

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
                accel_gran={'m': 32, 'n': 32},
                compute_cost=32
            ),
            Einsum(
                {'C': ('m', 'n'), 'D': ('n', 'l'), 'E': ('m', 'l')},
                'E',
                {'m': 32 * 1024, 'n': 16 * 1024, 'l': 4 * 1024},
                accel_gran={'m': 32, 'l': 32},
                compute_cost=32
            )
        ],
        32 * 1024 * 1024,
        allow_spilling=False
    )