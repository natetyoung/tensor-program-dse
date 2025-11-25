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

def cb_einsum(
    operand_dims:Dict[str,Tuple[str]],
    output_operand:str,
    dim_sizes:Dict[str,int],
    capacity:int,
    enforce_optimal_placement = True
):
    '''
    Constrained Buckets model for a single einsum.
    Should be extremely low-symmetry; disallows partial spilling.
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

    model = cp_model.CpModel()
    operands = list(operand_dims.keys())
    num_buckets = len(operands) + 1

    # vars indicating order of blocking levels
    placement_vars:Dict[str,List[cp_model.IntVar]] = {
        op: [model.NewBoolVar(op+'_pl_'+str(i)) for i in range(len(operands))] for op in operands
    }
    for op in operands:
        model.AddExactlyOne(placement_vars[op])
    for i in range(len(operands)):
        model.AddExactlyOne([placement_vars[op][i] for op in operands])

    dim_to_participating_ops_map = {
        d: [op for op in operands if d in operand_dims[op]] for d in dim_sizes.keys()
    }

    # Factor variables
    factor_vars:Dict[str,List[cp_model.IntVar]] = {}
    for dim in dim_sizes.keys():
        factor_vars[dim] = []
        for i in range(num_buckets):
            factor_vars[dim].append(model.NewIntVar(
                1, dim_sizes[dim], dim+'_'+str(i)+'_factor'
            ))
            # Optimal placement constraint
            if enforce_optimal_placement:
                if i > 0:
                    # dim participates in op at outer blocking level (move out for free)
                    model.Add(factor_vars[dim][i] == 1).OnlyEnforceIf(
                        *[
                            placement_vars[op][i-1].Not() 
                            for op in operands if dim not in operand_dims[op]
                        ]
                    ) 
                    # enforced if, for all op where dim does not participate, op is not placed i-1
                elif i < len(operand_dims.keys()):
                    # dim does not participate in inner blocking level (move in)
                    model.Add(factor_vars[dim][-1] == 1).OnlyEnforceIf(
                        *[
                            placement_vars[op][i].Not() 
                            for op in operands if dim in operand_dims[op]
                        ]
                    )
                    # enforced if, for all op where dim does participate, op is not placed i
            
            # forbid temporal reduction
            if dim not in operand_dims[output_operand]:
                # dim is reduction and would be temporal for output
                model.Add(factor_vars[dim][-1] == 1).OnlyEnforceIf(
                    *[
                        placement_vars[output_operand][j].Not()
                        for j in range(i)
                    ]
                )
                # enforced if, for all indices j outside of i, output is not placed j
        # Product of factors for this dim is at least dim size
        factor_product = add_mul_chain(
            model,
            factor_vars[dim],
            1, dim_sizes[dim] * 2**(num_buckets-1),
            dim+'_'+str(i)+'_factor'
        )
        model.Add(factor_product >= dim_sizes[dim])
    
    # Cost vars
    spatial_cost_vars:Dict[str,cp_model.IntVar] = {}
    temporal_cost_vars:Dict[str,cp_model.IntVar] = {}
    total_cost_vars:Dict[str,cp_model.IntVar] = {}
    max_iters = 1
    for s in dim_sizes.values():
        max_iters *= s

    # Spatial and temporal contribution vars
    spatial_contrib_vars:Dict[str,List[cp_model.IntVar]] = {
        op: [] for op in operands
    }
    temporal_contrib_vars:Dict[str,List[cp_model.IntVar]] = {
        op: [] for op in operands
    }
    for op, dims in operand_dims.items():
        for i in range(num_buckets):
            spatial_contrib_vars[op].append(model.NewIntVar(
                1, capacity, op+'_spatial_contrib_'+str(i)
            ))
            sp_prod = add_mul_chain(
                model,
                [factor_vars[dim][i] for dim in dims],
                1,
                max_iters,
                'spatial_contrib_'+op+'_'+str(i)
            )
            model.Add(spatial_contrib_vars[op][i] == sp_prod).OnlyEnforceIf(
                *[placement_vars[op][j].Not() for j in range(i, len(operands))]
            )
            model.Add(spatial_contrib_vars[op][i] == 1).OnlyEnforceIf(
                *[placement_vars[op][j].Not() for j in range(i)]
            )
            temporal_contrib_vars[op].append(model.NewIntVar(
                1, max_iters, op+'_temporal_contrib_'+str(i)
            ))
            tp_prod = add_mul_chain(
                model,
                [factor_vars[dim][i] for dim in dim_sizes.keys()],
                1,
                max_iters,
                'temporal_contrib_'+op+'_'+str(i)
            )
            model.Add(temporal_contrib_vars[op][i] == tp_prod).OnlyEnforceIf(
                *[placement_vars[op][j].Not() for j in range(i)]
            )
            model.Add(temporal_contrib_vars[op][i] == 1).OnlyEnforceIf(
                *[placement_vars[op][j].Not() for j in range(i, len(operands))]
            )
        
        op_size = 1
        for d in dims:
            op_size *= dim_sizes[d]
        spatial_cost_vars[op] = add_mul_chain(
            model,
            spatial_contrib_vars[op],
            1, capacity,
            'spatial_cost_'+op
        )
        temporal_cost_vars[op] = add_mul_chain(
            model,
            temporal_contrib_vars[op],
            1, max_iters,
            'temporal_cost_'+op
        )
        total_cost_vars[op] = model.NewIntVar(op_size, max_iters, 'total_cost_'+op)
        model.AddMultiplicationEquality(
            total_cost_vars[op],
            (spatial_cost_vars[op], temporal_cost_vars[op])
        )

    # capacity constraint
    model.Add(cp_model.LinearExpr.Sum(list(spatial_cost_vars.values())) <= capacity)

    model.Minimize(cp_model.LinearExpr.Sum(list(total_cost_vars.values())))

    print("MODEL WRITING DONE")

    solver = cp_model.CpSolver()
    solver.Solve(model)
    print(solver.ResponseStats())

    indent_level = 0
    for i in range(num_buckets):
        for dim in dim_sizes.keys():
            if solver.Value(factor_vars[dim][i]) > 1:
                print(' ' * indent_level + dim + ' wrap', solver.Value(factor_vars[dim][i]))
                indent_level += 1
        if i < len(operands):
            for op in operands:
                if solver.Value(placement_vars[op][i]) == 1:
                    print(' ' * indent_level + 'LD/ST ' + op)
    
    print('Spatial Costs:')
    print([(o, solver.Value(spatial_cost_vars[o])) for o in operand_dims.keys()])
    print('Temporal Costs:')
    print([(o, solver.Value(temporal_cost_vars[o])) for o in operand_dims.keys()])

if __name__ == '__main__':
    # cb_einsum(
    #     {'X': ('n', 'k', 'm'), 'A': ('m', 'k', 'h'), 'B': ('n', 'h'), 'C': ('m', 'n')},
    #     'C',
    #     {'m': 32 * 1024, 'k': 2 * 1024, 'n': 10283, 'h': 8},
    #     128 * 1024
    # )
    cb_einsum(
        {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
        'C',
        {'m': 4 * 1024, 'k': 8 * 1024, 'n': 4 * 1024},
        512 * 1024
    )
    # cb_einsum(
    #     {'A': ('m', 'n'), 'B': ('m', 'n')},
    #     'B',
    #     {'m': 4 * 1024, 'n': 4 * 1024},
    #     512 * 1024
    # )

