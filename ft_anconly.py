from dataclasses import dataclass
from typing import Dict, List, Tuple
from ortools.sat.python import cp_model
from c_from_cpsat import emit_c_driver, emit_einsum_function, parse_indented_trace, extract_loops_and_operands

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
    operation: str = None


def cb_full_tree(
    einsums:List[Einsum],
    capacity:int,
    enforce_optimal_placement = True,
    emit_c_code:bool = False,
    allow_spilling = False,
    debug:bool = True,
    return_fused:str = None
):
    '''
    Full schedule-tree model for a chain of einsums, for fusion at various levels.
    Disallows partial spilling.
    Use unique names for operands except when they are being passed.
    '''
    '''
    We only represent sequence nodes.
    Each tensor is identified with the node at which it is sequenced with its consumer,
      so many tensors may have the same node.
    Variables (not entirely exhaustive):
        - integer temporal-right-here factors for each allowed-temporal dim for each operand
        - integer spatial factors for each participating dim for each operand
        - num_operands integer spatial costs
        - integer total temporal factors for each allowed-temporal dim for each operand
        - num_operands total temporal * spatial costs
        - num_operands integer combined-for-all-resident spatial costs
        - num_total_operands^2 booleans for "A is parent of B"
        - num_total_operands^2 booleans for "A is ancestor of B"
        - num_total_operands^2 booleans for "A and B must coexist in the fast memory"
    Constraints (not entirely exhaustive):
        Constraints so parent/ancestor relationships form a tree:
         - A parent of B implies A ancestor of B
         - A ancestor of B and B ancestor of C implies A ancestor of C
         - A ancestor of B implies B not ancestor of A
         - Each node has only one parent
        Sanity of factors in tree:
         - A ancestor of B implies temporal-here factors in A which are not allowed for B are 1
        Consistency of einsums in tree:
         - for all A, B in same einsum, either A ancestor B or B ancestor A
        Costs:
         - Product of own factors is spatial cost
         - Product of temporal-here factors is local temporal cost
         - Product of local temporal costs of ancestors is overall temporal cost
            (uses temporal_contrib vars which are local temporal or 1 depending if ancestor)
        Dim fidelity:
        - product of spatial and ancestor temporal factors of dim is at least dim size
        Simultaneous buffers:
        - A's total spatial cost includes B's spatial cost if they are in the same einsum OR:
          - B is an input: A, B, and B's consumer share a single lowest common ancestor
          - B is an output: A, B, and all of B's inputs share a single LCA
        Capacity:
        - max total spatial cost is at most capacity
        Optional optimality sanity:
        - factor is 1 if:
            - dim does not participate in this tensor or any assigned to same node OR
            - dim does participate in all parent tensors

    Minimize:
        - sum of products of spatial and temporal
    '''

    all_operand_dims = {}
    op_allowed_temp_dims = {}
    all_dim_sizes = {}
    fused_operands = []
    # check consistency of chain
    for i in range(len(einsums)):
        for op in einsums[i].operand_dims.keys():
            if op == einsums[i].output_operand and i < len(einsums) - 1:
                assert op[-6:] == '_spill'
                assert op[:-6] in einsums[i+1].operand_dims.keys()
                assert einsums[i].operand_dims[op] == einsums[i+1].operand_dims[op[:-6]]
                fused_operands.append(op[:-6])
            for j in range(i+1, len(einsums)):
                assert op not in einsums[j].operand_dims.keys()
            if op == einsums[i].output_operand:
                op_allowed_temp_dims[op] = list(einsums[i].operand_dims[op])
            else:
                op_allowed_temp_dims[op] = list(einsums[i].dim_sizes.keys())
            all_operand_dims[op] = einsums[i].operand_dims[op]
        for d in einsums[i].dim_sizes.keys():
            if d in all_dim_sizes:
                assert einsums[i].dim_sizes[d] == all_dim_sizes[d]
            else:
                all_dim_sizes[d] = einsums[i].dim_sizes[d]

    all_operands = list(all_operand_dims.keys())
    if debug: print(all_operands)

    model = cp_model.CpModel()

    # ancestor relationship variables
    ancestor_overlap:Dict[str,Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}_ao_{}'.format(i, j)) for j in all_operands if i != j
        } for i in all_operands
    } # i_ao_j is "i is an ancestor of j and the subtree rooted at j must happen while buffer i exists"
    ancestor_not_overlap:Dict[str,Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}_ano_{}'.format(i, j)) for j in all_operands if i != j
        } for i in all_operands
    } # i_ano_j is "i is an ancestor of j and the subtree rooted at j does not happen while buffer i exists"
    ancestor:Dict[str,Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}_a_{}'.format(i, j)) for j in all_operands if i != j
        } for i in all_operands
    } # i_a_j is "i is an ancestor of j"
    # i_p_j = i_po_j OR i_pno_j
    # i_a_j = i_ao_j OR i_ano_j
    for i in all_operands + ['ROOT']:
        for j in all_operands:
            if i == j:
                continue
            if i != 'ROOT':
                model.AddBoolOr(ancestor_overlap[i][j], ancestor_not_overlap[i][j]).OnlyEnforceIf(ancestor[i][j])
                model.AddBoolAnd(ancestor_overlap[i][j].Not(), ancestor_not_overlap[i][j].Not()).OnlyEnforceIf(ancestor[i][j].Not())


    # Constraints so ancestor relationships form a tree
    for i in all_operands:
        for j in all_operands:
            if i == j:
                continue
            # A ancestor of B implies B not ancestor of A
            model.AddAtMostOne([
                ancestor_overlap[i][j], ancestor_not_overlap[i][j], ancestor_overlap[j][i], ancestor_not_overlap[j][i]
            ])
            for k in all_operands:
                if i == k or j == k:
                    continue
                # A ancestor (overlap/not-overlap) of B and B ancestor (any kind) of C implies A ancestor (overlap/not-overlap) of C
                model.Add(ancestor_overlap[i][k] == 1).OnlyEnforceIf(ancestor_overlap[i][j], ancestor[j][k])
                model.Add(ancestor_not_overlap[i][k] == 1).OnlyEnforceIf(ancestor_not_overlap[i][j], ancestor[j][k])

                # Consistency of ancestorship
                model.AddBoolOr(ancestor[i][j], ancestor[j][i]).OnlyEnforceIf(ancestor[i][k], ancestor[j][k])

    # Spatial dim vars: operand to dim to var
    spatial_dim:Dict[str,Dict[str,cp_model.IntVar]] = {
        op: {
            dim: model.NewIntVar(1, all_dim_sizes[dim], '{}_sp_{}'.format(op, dim)) for dim in all_operand_dims[op]
        } for op in all_operands
    }
    # Temporal-here dim vars: operand to dim to var
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

    # Constraints for consistency of einsums in tree
    for i, e in enumerate(einsums):
        ops = list(e.operand_dims.keys())
        for op_a in ops:
            for op_b in ops:
                if op_a == op_b:
                    continue
                # either B is ancestor of A, or A is ancestor of B (OVERLAP)
                model.AddBoolOr([ancestor_overlap[op_b][op_a], ancestor_overlap[op_a][op_b]])
    
    # Bool variables for whether we are fusing a particular operand
    fuse_op:Dict[str,cp_model.BoolVar] = {}
    for op in fused_operands:
        fuse_op[op] = model.NewBoolVar('fuse_'+op)
        # 1. Neither is an ancestor of the other
        model.Add(ancestor[op][op+'_spill'] == 0)
        model.Add(ancestor[op+'_spill'][op] == 0)
        # 2. They have exactly the same ancestors with other nodes if fused
        for other_op in all_operands:
            if other_op == op or other_op == op+'_spill':
                continue
            model.Add(ancestor[other_op][op] == ancestor[other_op][op+'_spill']).OnlyEnforceIf(fuse_op[op])
            # If they differ in ancestor_overlap, all temporal dims must be 1
            for dim in op_allowed_temp_dims[op]:
                model.Add(temporal_dim[op][dim] == 1).OnlyEnforceIf(
                    fuse_op[op], ancestor_overlap[other_op][op], ancestor_overlap[other_op][op+'_spill'].Not())
                model.Add(temporal_dim[op][dim] == 1).OnlyEnforceIf(
                    fuse_op[op], ancestor_overlap[other_op][op].Not(), ancestor_overlap[other_op][op+'_spill'])
            for dim in op_allowed_temp_dims[op+'_spill']:
                model.Add(temporal_dim[op+'_spill'][dim] == 1).OnlyEnforceIf(
                    fuse_op[op], ancestor_overlap[other_op][op], ancestor_overlap[other_op][op+'_spill'].Not())
                model.Add(temporal_dim[op+'_spill'][dim] == 1).OnlyEnforceIf(
                    fuse_op[op], ancestor_overlap[other_op][op].Not(), ancestor_overlap[other_op][op+'_spill'])
        # 3. They have exactly the same temporal dim factors if fused
        for dim in op_allowed_temp_dims[op]:
            if dim in op_allowed_temp_dims[op+'_spill']:
                model.Add(temporal_dim[op][dim] == temporal_dim[op+'_spill'][dim]).OnlyEnforceIf(fuse_op[op])
            else:
                model.Add(temporal_dim[op][dim] == 1).OnlyEnforceIf(fuse_op[op])
        for dim in op_allowed_temp_dims[op+'_spill']:
            if dim not in op_allowed_temp_dims[op]:
                model.Add(temporal_dim[op+'_spill'][dim] == 1).OnlyEnforceIf(fuse_op[op])

        if not allow_spilling:
            model.Add(fuse_op[op] == 1)
            if debug: print(f'Forced fuse for {op}')
    
    # Costs
    spatial_cost:Dict[str,cp_model.IntVar] = {}
    temporal_dim_contribs:Dict[str,Dict[str,Dict[str,cp_model.IntVar]]] = {}
    total_temporal_dim:Dict[str,Dict[str,cp_model.IntVar]] = {}
    total_temporal_cost:Dict[str,cp_model.IntVar] = {}
    temporal_if_not_fused_cost:Dict[str,cp_model.IntVar] = {}
    for op in all_operands:
        op_size = 1
        for d in all_operand_dims[op]:
            op_size *= all_dim_sizes[d]
        # Fused operand non-spatial-doublecounting should be taken care of by new coexistence constraints
        spatial_cost[op] = add_mul_chain(
            model,
            [spatial_dim[op][d] for d in all_operand_dims[op]],
            1,
            op_size,
            'spatial_cost_'+op
        )

    # Total temporal dim calculation
    for op in all_operands:
        allowed_dim_product = 1
        for d in op_allowed_temp_dims[op]:
            allowed_dim_product *= all_dim_sizes[d]
        max_temporal_cost = allowed_dim_product * (2**len(op_allowed_temp_dims[op]))
        temporal_dim_contribs[op] = {}
        for other_op in all_operands:
            if op == other_op:
                continue
            temporal_dim_contribs[op][other_op] = {}
            for d in op_allowed_temp_dims[op]:
                temporal_dim_contribs[op][other_op][d] = model.NewIntVar(
                    1, all_dim_sizes[d], f'temp_contrib_{op}_{other_op}_{d}'
                )
                if d in temporal_dim[other_op]:
                    model.Add(
                        temporal_dim_contribs[op][other_op][d] == temporal_dim[other_op][d]
                    ).OnlyEnforceIf(ancestor[other_op][op])
                    model.Add(
                        temporal_dim_contribs[op][other_op][d] == 1
                    ).OnlyEnforceIf(ancestor[other_op][op].Not())
                else:
                    model.Add(temporal_dim_contribs[op][other_op][d] == 1)
        total_temporal_dim[op] = {}
        for d in op_allowed_temp_dims[op]:
            total_temporal_dim[op][d] = add_mul_chain(
                model,
                [
                    temporal_dim_contribs[op][other_op][d] for other_op in all_operands if other_op != op
                ] + [temporal_dim[op][d]],
                1, all_dim_sizes[d] * (2**len(all_operands)),
                'total_temporal_dim_'+op+'_'+d
            )
            # Dim fidelity
            if d in all_operand_dims[op]:
                total_size = model.NewIntVar(1, all_dim_sizes[d] * (2**len(all_operands)), 'total_dim_size_{op}_{d}')
                model.AddMultiplicationEquality(total_size, [spatial_dim[op][d], total_temporal_dim[op][d]])
                model.Add(total_size >= all_dim_sizes[d])
                model.AddDivisionEquality(spatial_dim[op][d], all_dim_sizes[d] + total_temporal_dim[op][d] - 1, total_temporal_dim[op][d])

        temporal_if_not_fused_cost[op] = add_mul_chain(
            model,
            list(total_temporal_dim[op].values()),
            1, max_temporal_cost,
            'temporal_if_not_fused_'+op
        )
        if op in fused_operands or op.endswith('_spill'):
            total_temporal_cost[op] = model.NewIntVar(0, max_temporal_cost, 'total_temporal_cost_'+op)
            restore_op_name = op if op in fused_operands else op.replace('_spill', '')
            model.Add(total_temporal_cost[op] == 0).OnlyEnforceIf(fuse_op[restore_op_name])
            model.Add(total_temporal_cost[op] == temporal_if_not_fused_cost[op]).OnlyEnforceIf(fuse_op[restore_op_name].Not())
        else:
            total_temporal_cost[op] = temporal_if_not_fused_cost[op]
    
    # Capacity
    coexist_vars:Dict[str,Dict[str,cp_model.IntVar]] = {}
    for op_a in all_operands:
        coexist_vars[op_a] = {}
        for op_b in all_operands:
            if op_a == op_b:
                continue
            coexist_var = model.NewBoolVar('coexist_{}_{}'.format(op_a, op_b))
            coexist_vars[op_a][op_b] = coexist_var
            model.Add(ancestor_overlap[op_b][op_a] == coexist_var)
    
    for op in all_operands:
        contrib_vars = []
        for op2 in all_operands:
            if op == op2:
                continue
            contrib_var = model.NewIntVar(0, capacity, 'space_contrib_{}_{}'.format(op, op2))
            contrib_vars.append(contrib_var)
            model.Add(contrib_var == spatial_cost[op2]).OnlyEnforceIf(coexist_vars[op][op2])
            model.Add(contrib_var == 0).OnlyEnforceIf(coexist_vars[op][op2].Not())
        # Real capacity constraint
        model.Add(cp_model.LinearExpr.Sum(contrib_vars) + spatial_cost[op] <= capacity)

    if enforce_optimal_placement:
        max_useful_granularity = {}
        for e in einsums:
            for d in e.dim_sizes.keys():
                if d not in max_useful_granularity:
                    max_useful_granularity[d] = 1
                if e.accel_gran and e.compute_cost > 0:
                    if d in e.accel_gran:
                        max_useful_granularity[d] = max(max_useful_granularity[d], e.accel_gran[d])
                    elif 'PRODUCT' in e.accel_gran:
                        max_useful_granularity[d] = max(max_useful_granularity[d], e.accel_gran['PRODUCT'])

        # Optional optimality sanity constraints
        for op in all_operands:
            for dim in op_allowed_temp_dims[op]:
                # temporal factor is 1 if dim does not participate in this tensor
                if dim not in all_operand_dims[op]:
                    model.Add(temporal_dim[op][dim] == 1)
                # spatial factor is at most the maximum useful spatial granularity if dim does participate in this and any descendants
                if op not in fused_operands and dim in all_operand_dims[op]:
                    model.Add(spatial_dim[op][dim] <= max_useful_granularity[dim]).OnlyEnforceIf(
                        *([
                            ancestor[op][other_op].Not()
                            for other_op in all_operands
                            if dim not in all_operand_dims[other_op] and other_op != op
                        ])
                    )

        for i in range(len(einsums)-1):
            for k in range(i+1):
                for op in einsums[k].operand_dims.keys():
                    for j in range(i+1, len(einsums)):
                        for op2 in einsums[j].operand_dims.keys():
                            if op == op2:
                                continue
                            model.Add(ancestor[op][op2] == 0).OnlyEnforceIf(fuse_op[fused_operands[i]].Not())
                            model.Add(ancestor[op2][op] == 0).OnlyEnforceIf(fuse_op[fused_operands[i]].Not())
                            model.Add(ancestor_overlap[fused_operands[i]+'_spill'][op2] == 0)
                            model.Add(ancestor_not_overlap[fused_operands[i]+'_spill'][op2] == 0).OnlyEnforceIf(fuse_op[fused_operands[i]].Not())

            for j in range(i):
                for op2 in einsums[j].operand_dims.keys():
                    if op == op2:
                        continue
                    model.Add(ancestor[fused_operands[i]][op2] == 0)
                        

    # total cost vars
    total_cost_vars:Dict[str,cp_model.IntVar] = {}
    for op in all_operands:
        op_size = 1
        for d in all_operand_dims[op]:
            op_size *= all_dim_sizes[d]
        allowed_dim_product = 1
        for d in op_allowed_temp_dims[op]:
            allowed_dim_product *= all_dim_sizes[d]
        if op in fused_operands or op.endswith('_spill'):
            total_cost_vars[op] = model.NewIntVar(0, allowed_dim_product * (2**len(op_allowed_temp_dims[op])), 'total_cost_'+op)
        else:
            total_cost_vars[op] = model.NewIntVar(op_size, allowed_dim_product * (2**len(op_allowed_temp_dims[op])), 'total_cost_'+op)
        model.AddMultiplicationEquality(
            total_cost_vars[op],
            (spatial_cost[op], total_temporal_cost[op])
        )
        if op in fused_operands or op.endswith('_spill'):
            restore_op_name = op if op in fused_operands else op.replace('_spill', '')
            model.Add(total_cost_vars[op] >= op_size).OnlyEnforceIf(fuse_op[restore_op_name].Not())
            model.Add(total_cost_vars[op] == 0).OnlyEnforceIf(fuse_op[restore_op_name])

    # Compute cost
    all_compute_iters = []
    # for all einsums:
    for i, e in enumerate(einsums):
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

    model.Minimize(sum([all_compute_iters[i] * einsums[i].compute_cost for i in range(len(einsums))]) + cp_model.LinearExpr.Sum(list(total_cost_vars.values())))

    if debug: print("MODEL WRITING DONE")

    solver = cp_model.CpSolver()
    # solver.parameters.max_time_in_seconds = 300.0
    # model.AddAssumptions([parent['C_spill']['A']])
    solver.Solve(model)
    if debug:
        print(solver.ResponseStats())
        assumptions = solver.SufficientAssumptionsForInfeasibility()
        print(len(assumptions))
        for var_index in assumptions:
            print(var_index, f"{var_index}: '{model.proto.variables[var_index].name}'")

    implicit_parents:Dict[str,str] = {op: 'ROOT' for op in all_operands}
    for op in all_operands:
        for op2 in all_operands:
            if op == op2:
                continue
            if solver.BooleanValue(ancestor[op][op2]):
                nearest_ancestor = True
                for op3 in all_operands:
                    if op3 == op or op3 == op2:
                        continue
                    if solver.BooleanValue(ancestor[op][op3]) and solver.BooleanValue(ancestor[op3][op2]):
                        nearest_ancestor = False
                        break
                if nearest_ancestor:
                    implicit_parents[op2] = op

    if debug:
        for op in all_operands + ['ROOT']:
            for op2 in all_operands:
                if op == op2:
                    continue
                if implicit_parents[op2] == op: #solver.BooleanValue(parent[op][op2]):
                    print(op, 'is the parent of', op2, 'overlap:', 
                        solver.BooleanValue(ancestor_overlap[op][op2]) if op != 'ROOT' else False)
                # if op != 'ROOT' and solver.BooleanValue(ancestor[op][op2]):
                #     print(op, 'is an ancestor of', op2, 'overlap:', solver.BooleanValue(ancestor_overlap[op][op2]))

        # for op in all_operands:
        #     print(op, 'must coexist with', [
        #         op2 for op2 in all_operands if op != op2 and solver.BooleanValue(coexist_vars[op][op2])
        #     ])
        # for op2 in all_operands:
        #     if op == op2: continue
        #     if not solver.BooleanValue(coexist_vars[op][op2]):
        #         print(op, 'does not coexist with', op2)
        #         if op2 not in equal_temporal_dims[op]:
        #             continue
        #         print(op, 'has equal temporal dims with', op2, '?', solver.BooleanValue(equal_temporal_dims[op][op2]))
        #         print(op, 'ancestor of', op2, '?', solver.BooleanValue(ancestor[op][op2]))
        #         print(op2, 'ancestor of', op, '?', solver.BooleanValue(ancestor[op2][op]))

    # print tree structure
    traces = []
    for e in einsums:
        # find path of operands
        full_path = []
        for op in e.operand_dims.keys():
            path = [[op]]
            current = op
            while True:
                if current == 'ROOT':
                    break
                # find all participating same-node operands
                for op2 in e.operand_dims.keys():
                    if current == op2:
                        continue
                for potential_parent in all_operands + ['ROOT']:
                    if potential_parent == current:
                        continue
                    if implicit_parents[current] == potential_parent: #solver.BooleanValue(parent[potential_parent][current]):
                        if potential_parent == 'ROOT':
                            current = potential_parent
                            break
                        path.append([potential_parent])
                        current = potential_parent
                        break
            if len(path) > len(full_path):
                full_path = path
        full_path = list(reversed(full_path))
        if debug: print('Einsum operands path:', ' -> '.join([str(n) for n in full_path]))
        indent_level = 0
        trace = []
        for level in full_path:
            # print temporal dims here if >1, indenting after each, then print all participating ops in level
            for dim in op_allowed_temp_dims[level[0]]:
                dim_factor = solver.Value(temporal_dim[level[0]][dim])
                if dim_factor > 1:
                    if debug: print(' ' * indent_level + dim + ' wrap', dim_factor)
                    trace.append(' ' * indent_level + dim + ' wrap ' + str(dim_factor))
                    indent_level += 1
            for op in level:
                if op in e.operand_dims.keys():
                    if debug: print(' ' * indent_level + 'LD/ST ' + op + ' ' + str({
                        d: solver.Value(spatial_dim[op][d]) for d in spatial_dim[op].keys()
                    }))
                    trace.append(' ' * indent_level + 'LD/ST ' + op + ' ' + str({
                        d: solver.Value(spatial_dim[op][d]) for d in spatial_dim[op].keys()
                    }))
        traces.append(trace)
    
    if debug:
        for e_num in range(len(einsums)):
            print(f"Einsum {e_num} spatial costs:", [(o, solver.Value(spatial_cost[o])) for o in einsums[e_num].operand_dims])
            print(f"Einsum {e_num} temporal costs:", [(o, solver.Value(total_temporal_cost[o])) for o in einsums[e_num].operand_dims])
            if einsums[e_num].compute_cost > 0:
                print(f"Einsum {e_num} compute iterations:", solver.Value(all_compute_iters[e_num]))
    
    if emit_c_code:
        einsum_functions = []
        einsum_calls = []
        tensor_sizes = {}
        for i, e in enumerate(einsums):
            name = f"einsum_{i}"
            nodes = parse_indented_trace(traces[i])
            _, operands = extract_loops_and_operands(nodes)
            einsum_functions.append((name, emit_einsum_function(name, nodes, all_dim_sizes)))
            einsum_calls.append((name, operands.keys()))
        for op, dims in all_operand_dims.items():
            tensor_sizes[op] = 1
            for d in dims:
                tensor_sizes[op] *= all_dim_sizes[d]
        #print("einsum_functions", einsum_functions)
        #print("einsum_calls", einsum_calls)
        #print("tensor_sizes", tensor_sizes)
        return emit_c_driver(einsum_functions, tensor_sizes, einsum_calls)

    if return_fused:
        return solver.Value(fuse_op[return_fused])
    return solver.ObjectiveValue(), solver.ResponseProto().wall_time
        

if __name__ == '__main__':
    # cb_full_tree(
    #     [Einsum(
    #         {'X': ('n', 'k', 'm'), 'A': ('m', 'k', 'h'), 'B': ('n', 'h'), 'C': ('m', 'n')},
    #         'C',
    #         {'m': 32 * 1024, 'k': 2 * 1024, 'n': 10283, 'h': 8}
    #     )],
    #     128 * 1024
    # )
    # cb_full_tree(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 4 * 1024, 'k': 8 * 1024, 'n': 4 * 1024}
    #         ),
    #         Einsum(
    #             {'C': ('m', 'n'), 'E': ('m', 'n')},
    #             'E',
    #             {'m': 4 * 1024, 'n': 4 * 1024}
    #         )
    #     ],
    #     512 * 1024
    # )
    # import time
    # start = time.time()
    # cb_full_tree(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C_spill': ('m', 'n')},
    #             'C_spill',
    #             {'m': 32 * 1024, 'k': 4 * 1024, 'n': 16 * 1024}
    #         ),
    #         Einsum(
    #             {'C': ('m', 'n'), 'D': ('n', 'l'), 'E': ('m', 'l')},
    #             'E',
    #             {'m': 32 * 1024, 'n': 16 * 1024, 'l': 4 * 1024}
    #         )
    #     ],
    #     512 * 1024,
    #     allow_spilling=True
    # )
    # cb_full_tree(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C_spill': ('m', 'n')},
    #             'C_spill',
    #             {'m': 32 * 1024, 'k': 4 * 1024, 'n': 16 * 1024}
    #         ),
    #         Einsum(
    #             {'C': ('m', 'n'), 'D': ('n', 'l'), 'E': ('m', 'l')},
    #             'E',
    #             {'m': 32 * 1024, 'n': 16 * 1024, 'l': 4 * 1024}
    #         )
    #     ],
    #     32 * 1024 * 1024,
    #     allow_spilling=True
    # )
    # end = time.time()
    # print("Total time:", end - start)
    # cb_full_tree(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 32 * 1024, 'k': 4 * 1024, 'n': 16 * 1024}
    #         )
    #     ],
    #     512 * 1024
    # )
    # cb_full_tree(
    #     [
    #         Einsum(
    #             {'C': ('m', 'n'), 'D': ('n', 'l'), 'E': ('m', 'l')},
    #             'E',
    #             {'m': 32 * 1024, 'n': 16 * 1024, 'l': 4 * 1024}
    #         )
    #     ],
    #     512 * 1024
    # )
    # cb_full_tree(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 4 * 1024, 'k': 8 * 1024, 'n': 4 * 1024}
    #         ),
    #         Einsum(
    #             {'C': ('m', 'n'), 'D': ('m', 'n')},
    #             'D',
    #             {'m': 4 * 1024, 'n': 4 * 1024}
    #         ),
    #         Einsum(
    #             {'D': ('m', 'n'), 'E': ('m', 'n')},
    #             'E',
    #             {'m': 4 * 1024, 'n': 4 * 1024}
    #         )
    #     ],
    #     512 * 1024
    # )
    # cb_full_tree(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 32 * 1024, 'k': 4 * 1024, 'n': 16 * 1024}
    #         ),
    #         Einsum(
    #             {'C': ('m', 'n'), 'D': ('m', 'n')},
    #             'D',
    #             {'m': 32 * 1024, 'n': 16 * 1024}
    #         ),
    #         Einsum(
    #             {'D': ('m', 'n'), 'E': ('n', 'l'), 'F': ('m', 'l')},
    #             'F',
    #             {'m': 32 * 1024, 'n': 16 * 1024, 'l': 4 * 1024}
    #         )
    #     ],
    #     512 * 1024
    # )
    # cb_full_tree(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 1 * 1024, 'k': 4 * 1024, 'n': 1 * 1024}
    #         ),
    #         Einsum(
    #             {'C': ('m', 'n'), 'D': ('n', 'l'), 'E': ('m', 'l')},
    #             'E',
    #             {'m': 1 * 1024, 'n': 1 * 1024, 'l': 2 * 1024}
    #         ),
    #         Einsum(
    #             {'E': ('m', 'l'), 'F': ('m', 'l')},
    #             'F',
    #             {'m': 1 * 1024, 'l': 2 * 1024}
    #         )
    #     ],
    #     32 * 1024
    # )
    # cb_full_tree(
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
    #             {'L0_S': ('m', 'n'), 'L0_V': ('n', 'k'), 'L0_O_spill': ('m', 'k')},
    #             'L0_O_spill', 
    #             {'m': 2048, 'n': 2048, 'k': 4096}
    #         ), 
    #         Einsum(
    #             {'L0_O': ('m', 'k'), 'L0_Wo': ('k', 'd'), 'L0_Y': ('m', 'd')},
    #             'L0_Y',
    #             {'m': 2048, 'k': 4096, 'd': 4096}
    #         ), 
    #     ],
    #     4 * 1024 * 1024,
    #     allow_spilling=True
    # )
    cb_full_tree( #FULL SIX EINSUM GPT
        [
            Einsum(
                {'L0_X': ('m', 'd'), 'L0_WQ': ('d', 'k'), 'L0_Q_spill': ('m', 'k')}, 
                'L0_Q_spill', 
                {'m': 2048, 'd': 4096, 'k': 4096}
            ),
            Einsum(
                {'L0_Q': ('m', 'k'), 'L0_K': ('n', 'k'), 'L0_S_spill': ('m', 'n')},
                'L0_S_spill', 
                {'m': 2048, 'n': 2048, 'k': 4096}
            ), 
            Einsum(
                {'L0_S': ('m', 'n'), 'L0_V': ('n', 'k1'), 'L0_O_spill': ('m', 'k1')},
                'L0_O_spill', 
                {'m': 2048, 'n': 2048, 'k1': 4096}
            ), 
            Einsum(
                {'L0_O': ('m', 'k1'), 'L0_Wo': ('k1', 'd1'), 'L0_Y_spill': ('m', 'd1')},
                'L0_Y_spill',
                {'m': 2048, 'k1': 4096, 'd1': 4096}
            ), 
            Einsum(
                {'L0_Y': ('m', 'd1'), 'L0_W1': ('d1', 'f1'), 'L0_H_spill': ('m', 'f1')},
                'L0_H_spill',
                {'m': 2048, 'd1': 4096, 'f1': 16384}
            ),
            Einsum(
                {'L0_H': ('m', 'f1'), 'L0_W2': ('f1', 'd2'), 'L0_Z': ('m', 'd2')},
                'L0_Z',
                {'m': 2048, 'f1': 16384, 'd2': 4096}
            )
        ],
        8 * 1024 * 1024,
        allow_spilling=True
    )
    # def generate_matmul_chain(num_einsums, m, k_n_seq):
    #     ret = []
    #     dim_names = ('m', 'k', 'n0')
    #     op_names = ('A', 'B0', 'C0')
    #     for i in range(num_einsums):
    #         sizes = (m, k_n_seq[i % len(k_n_seq)][0], k_n_seq[i % len(k_n_seq)][1])
    #         dim_sizes = {dim_names[j]: sizes[j] for j in range(3)}
    #         output_name = op_names[2]
    #         if i < num_einsums - 1:
    #             output_name = output_name + '_spill'
    #         ret.append(Einsum(
    #             {op_names[0]: (dim_names[0], dim_names[1]), op_names[1]: (dim_names[1], dim_names[2]), output_name: (dim_names[0], dim_names[2])}, 
    #             output_name, 
    #             dim_sizes
    #         ))
    #         dim_names = (dim_names[0], dim_names[2], 'n' + str(i+1))
    #         op_names = (op_names[2], 'B' + str(i+1), 'C' + str(i+1))
    #     return ret
    # # print(generate_matmul_chain(2, 1024, [(4096, 4096)]))
    # # print(generate_matmul_chain(2, 32*1024, [(4*1024, 16*1024), (16*1024, 4*1024)]))
    # # cb_full_tree(
    # #     generate_matmul_chain(2, 32*1024, [(4*1024, 16*1024), (16*1024, 4*1024)]),
    # #     512 * 1024
    # # )
    # cb_full_tree(
    #     generate_matmul_chain(4, 8*1024, [(16*1024, 16*1024), (16*1024, 4*1024), (4*1024, 4*1024), (4*1024, 16*1024)]),
    #     512 * 1024,
    #     allow_spilling=True
    # )

