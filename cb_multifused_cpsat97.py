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

class Einsum:
    def __init__(self, operand_dims, output_operand, dim_sizes):
        self.operand_dims:Dict[str,Tuple[str]] = operand_dims
        self.output_operand:str = output_operand
        self.dim_sizes:Dict[str,int] = dim_sizes

def cb_fused(
    einsums:List[Einsum],
    passed_operands:List[str],
    capacity:int,
    enforce_optimal_placement = True
):
    '''
    Constrained Buckets model for a chain of einsums, all fused at the same level.
    Should be extremely low-symmetry; disallows partial spilling.
    Also disallows any spilling of any intermediate.
    Requires that intermediates have outermost blocking (no factors between 2 intermediates)
     which means no other operand has to be stored between einsums
    '''
    '''
    Variables:
        - num_operands + 1 integer factors for each dim
        - num_operands * (num_operands + 1) integer spatial and temporal contributions
        - boolean placement in order for each operand
        - integer total spatial costs of each operand
        - integer total temporal costs of each operand
    Constraints:
        - optionally, factor is 1 if:
            - dim participates in outer blocking level of bucket OR
            - dim does not participate in inner blocking level
        - factor is 1 if:
            - bucket is outside output blocking level and dim does not participate in output
        - product of factors of dim is at least dim size
        - For each operand:
            - Product of participating factors in higher-indexed buckets is spatial cost
            - Product of participating factors in lower-indexed buckets is temporal cost
        - sum of total spatial contributions <= capacity
    Minimize:
        - sum of products of spatial and temporal
    '''

    assert len(einsums) == len(passed_operands) + 1

    # check consistency of passed operand
    for i in range(len(passed_operands)):
        e1_, e2_ = einsums[i], einsums[i+1]
        passed_op = passed_operands[i]
        assert len(e1_.operand_dims[e1_.output_operand]) == len(e2_.operand_dims[passed_op])
        for i in range(len(e2_.operand_dims[passed_op])):
            assert (
                e2_.dim_sizes[e2_.operand_dims[passed_op][i]]
                == e1_.dim_sizes[e1_.operand_dims[e1_.output_operand][i]]
            )

    model = cp_model.CpModel()

    # Cost vars (now as lists of dicts, one per einsum)
    spatial_cost_vars: List[Dict[str, cp_model.IntVar]] = [{} for _ in range(len(einsums))]
    temporal_cost_vars: List[Dict[str, cp_model.IntVar]] = [{} for _ in range(len(einsums))]
    total_cost_vars: List[Dict[str, cp_model.IntVar]] = [{} for _ in range(len(einsums))]

    # Factor vars per einsum: factor_vars[e_num][dim] -> List[IntVar]
    factor_vars: List[Dict[str, List[cp_model.IntVar]]] = [{} for _ in range(len(einsums))]

    # Placement vars per einsum: placement_vars[e_num][op] -> List[BoolVar]
    placement_vars: List[Dict[str, List[cp_model.IntVar]]] = [{} for _ in range(len(einsums))]

    for e_num in range(len(einsums)):
        e = einsums[e_num]
        operands = list(e.operand_dims.keys())
        num_buckets = len(operands) + 1

        # vars indicating order of blocking levels
        for op in operands:
            placement_vars[e_num][op] = [model.NewBoolVar(str(e_num)+op+'_pl_'+str(i)) for i in range(len(operands))]
            model.AddExactlyOne(placement_vars[e_num][op])
        for i in range(len(operands)):
            model.AddExactlyOne([placement_vars[e_num][op][i] for op in operands])
        
        # passed op must be outermost
        if e_num == 0:
            model.Add(placement_vars[e_num][e.output_operand][0] == 1)
        elif e_num == len(einsums) - 1:
            model.Add(placement_vars[e_num][passed_operands[e_num - 1]][0] == 1)
        else:
            model.Add(placement_vars[e_num][passed_operands[e_num - 1]][0] == 1)
            model.Add(placement_vars[e_num][e.output_operand][1] == 1)
        

        # Factor variables
        for dim in e.dim_sizes.keys():
            factor_vars[e_num][dim] = []
            for i in range(num_buckets):
                factor_vars[e_num][dim].append(model.NewIntVar(
                    1, e.dim_sizes[dim], str(e_num)+dim+'_'+str(i)+'_factor'
                ))
                # Optimal placement constraint
                if enforce_optimal_placement:
                    if i > 2 or ((e_num == 0 or e_num == len(einsums) - 1) and i > 1): # instead of i > 0
                        # We allow suboptimal spatial cost for outermost op because of fusion
                        # dim participates in op at outer blocking level (move out for free)
                        model.Add(factor_vars[e_num][dim][i] == 1).OnlyEnforceIf(
                            *[
                                placement_vars[e_num][op][i-1].Not() 
                                for op in operands if dim not in e.operand_dims[op]
                            ]
                        ) 
                        # enforced if, for all op where dim does not participate, op is not placed i-1
                    elif i < len(e.operand_dims.keys()):
                        # dim does not participate in inner blocking level (move in)
                        model.Add(factor_vars[e_num][dim][-1] == 1).OnlyEnforceIf(
                            *[
                                placement_vars[e_num][op][i].Not() 
                                for op in operands if dim in e.operand_dims[op]
                            ]
                        )
                        # enforced if, for all op where dim does participate, op is not placed i
                
                # forbid temporal reduction
                if dim not in e.operand_dims[e.output_operand]:
                    # dim is reduction and would be temporal for output
                    model.Add(factor_vars[e_num][dim][-1] == 1).OnlyEnforceIf(
                        *[
                            placement_vars[e_num][e.output_operand][j].Not()
                            for j in range(i)
                        ]
                    )
                    # enforced if, for all indices j outside of i, output is not placed j
                
            # no factors between input and output in fusion
            if e_num > 0 and e_num < len(einsums) - 1:
                model.Add(factor_vars[e_num][dim][1] == 1)
            
            # Product of factors for this dim is at least dim size
            factor_product = add_mul_chain(
                model,
                factor_vars[e_num][dim],
                1, e.dim_sizes[dim] * 2**(num_buckets-1),
                str(e_num)+dim+'_'+str(i)+'_factor'
            )
            model.Add(factor_product >= e.dim_sizes[dim])
        
        max_iters = 1
        for s in e.dim_sizes.values():
            max_iters *= s

        # Spatial and temporal contribution vars
        spatial_contrib_vars:Dict[str,List[cp_model.IntVar]] = {
            op: [] for op in operands
        }
        temporal_contrib_vars:Dict[str,List[cp_model.IntVar]] = {
            op: [] for op in operands
        }
        for op, dims in e.operand_dims.items():
            for i in range(num_buckets):
                spatial_contrib_vars[op].append(model.NewIntVar(
                    1, capacity, str(e_num)+op+'_spatial_contrib_'+str(i)
                ))
                sp_prod = add_mul_chain(
                    model,
                    [factor_vars[e_num][dim][i] for dim in dims],
                    1,
                    max_iters,
                    str(e_num)+'spatial_contrib_'+op+'_'+str(i)
                )
                model.Add(spatial_contrib_vars[op][i] == sp_prod).OnlyEnforceIf(
                    *[placement_vars[e_num][op][j].Not() for j in range(i, len(operands))]
                )
                model.Add(spatial_contrib_vars[op][i] == 1).OnlyEnforceIf(
                    *[placement_vars[e_num][op][j].Not() for j in range(i)]
                )
                temporal_contrib_vars[op].append(model.NewIntVar(
                    1, max_iters, str(e_num)+op+'_temporal_contrib_'+str(i)
                ))
                tp_prod = add_mul_chain(
                    model,
                    [factor_vars[e_num][dim][i] for dim in e.dim_sizes.keys()],
                    1,
                    max_iters,
                    str(e_num)+'temporal_contrib_'+op+'_'+str(i)
                )
                model.Add(temporal_contrib_vars[op][i] == tp_prod).OnlyEnforceIf(
                    *[placement_vars[e_num][op][j].Not() for j in range(i)]
                )
                model.Add(temporal_contrib_vars[op][i] == 1).OnlyEnforceIf(
                    *[placement_vars[e_num][op][j].Not() for j in range(i, len(operands))]
                )
            
            op_size = 1
            for d in dims:
                op_size *= e.dim_sizes[d]
            spatial_cost_vars[e_num][op] = add_mul_chain(
                model,
                spatial_contrib_vars[op],
                1, capacity,
                str(e_num)+'spatial_cost_'+op
            )
            if (e_num > 0 and op == passed_operands[e_num - 1]) or (e_num < len(einsums) - 1 and op == e.output_operand):
                temporal_cost_vars[e_num][op] = model.NewIntVar(0, 0, str(e_num)+'_temp_'+op)
                total_cost_vars[e_num][op] = model.NewIntVar(0, 0, str(e_num)+'_total_'+op)
            else:
                temporal_cost_vars[e_num][op] = add_mul_chain(
                    model,
                    temporal_contrib_vars[op],
                    1, max_iters * 2 ** (num_buckets - 1),
                    str(e_num)+'temporal_cost_'+op
                )
                total_cost_vars[e_num][op] = model.NewIntVar(
                    op_size,
                    max_iters * 2 ** (num_buckets - 1),
                    str(e_num)+'total_cost_'+op
                )
                model.AddMultiplicationEquality(
                    total_cost_vars[e_num][op],
                    (spatial_cost_vars[e_num][op], temporal_cost_vars[e_num][op])
                )

    # capacity constraints
    for e_num, e in enumerate(einsums):
        ops_here = [op for op in e.operand_dims.keys()]
        model.Add(cp_model.LinearExpr.Sum([spatial_cost_vars[e_num][op] for op in ops_here]) <= capacity)

    for op_num, op in enumerate(passed_operands):
        for i in range(len(einsums[op_num + 1].operand_dims[op])):
            # outermost factor of participating dims must be equal
            e2_dim = einsums[op_num + 1].operand_dims[op][i]
            e1_dim = einsums[op_num].operand_dims[einsums[op_num].output_operand][i]
            model.Add(factor_vars[op_num + 1][e2_dim][0] == factor_vars[op_num][e1_dim][0])

    # flatten total_cost_vars from both einsums for objective
    all_cost_vars = [v for d in total_cost_vars for v in d.values()]
    model.Minimize(cp_model.LinearExpr.Sum(all_cost_vars))

    print("MODEL WRITING DONE")

    solver = cp_model.CpSolver()
    solver.Solve(model)
    print(solver.ResponseStats())

    for e_num, e in enumerate(einsums):
        indent_level = 0
        for i in range(len(e.operand_dims.keys()) + 1):
            for dim in e.dim_sizes.keys():
                if solver.Value(factor_vars[e_num][dim][i]) > 1:
                    print(' ' * indent_level + dim + ' wrap', solver.Value(factor_vars[e_num][dim][i]))
                    indent_level += 1
            if i < len(e.operand_dims.keys()):
                for op in e.operand_dims.keys():
                    if solver.Value(placement_vars[e_num][op][i]) == 1:
                        print(' ' * indent_level + 'LD/ST ' + op)
    
    # print per-einsum costs
    for e_num in range(len(einsums)):
        print(f"Einsum {e_num} spatial costs:", [(o, solver.Value(s)) for o, s in spatial_cost_vars[e_num].items()])
        print(f"Einsum {e_num} temporal costs:", [(o, solver.Value(s)) for o, s in temporal_cost_vars[e_num].items()])

if __name__ == '__main__':
    # cb_fused(
    #     [Einsum(
    #         {'X': ('n', 'k', 'm'), 'A': ('m', 'k', 'h'), 'B': ('n', 'h'), 'C': ('m', 'n')},
    #         'C',
    #         {'m': 32 * 1024, 'k': 2 * 1024, 'n': 10283, 'h': 8}
    #     )],
    #     [],
    #     128 * 1024
    # )
    # cb_fused(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 4 * 1024, 'k': 8 * 1024, 'n': 4 * 1024}
    #         ),
    #         Einsum(
    #             {'D': ('m1', 'n1'), 'E': ('m1', 'n1')},
    #             'E',
    #             {'m1': 4 * 1024, 'n1': 4 * 1024}
    #         )
    #     ],
    #     ['D'],
    #     512 * 1024,
    #     True
    # )
    # cb_fused(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 32 * 1024, 'k': 4 * 1024, 'n': 16 * 1024}
    #         ),
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 32 * 1024, 'k': 16 * 1024, 'n': 4 * 1024}
    #         )
    #     ],
    #     ['A'],
    #     512 * 1024,
    #     True
    # )
    # cb_fused(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 4 * 1024, 'k': 8 * 1024, 'n': 4 * 1024}
    #         ),
    #         Einsum(
    #             {'D': ('m', 'n'), 'E': ('m', 'n')},
    #             'E',
    #             {'m': 4 * 1024, 'n': 4 * 1024}
    #         ),
    #         Einsum(
    #             {'D': ('m', 'n'), 'E': ('m', 'n')},
    #             'E',
    #             {'m': 4 * 1024, 'n': 4 * 1024}
    #         )
    #     ],
    #     ['D', 'D'],
    #     512 * 1024,
    #     True
    # )
    cb_fused(
        [
            Einsum(
                {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
                'C',
                {'m': 32 * 1024, 'k': 4 * 1024, 'n': 16 * 1024}
            ),
            Einsum(
                {'D': ('m', 'n'), 'E': ('m', 'n')},
                'E',
                {'m': 32 * 1024, 'n': 16 * 1024}
            ),
            Einsum(
                {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
                'C',
                {'m': 32 * 1024, 'k': 16 * 1024, 'n': 4 * 1024}
            )
        ],
        ['D', 'A'],
        512 * 1024,
        True
    )

