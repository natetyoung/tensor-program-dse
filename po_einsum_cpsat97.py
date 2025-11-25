# %%
from typing import Dict, Tuple
from ortools.sat.python import cp_model

# %%
def add_mul_chain(model, components, lb, ub, pfx):
    old_var = components[0]
    new_var = components[0]
    for i in range(len(components) - 1):
        old_var = new_var
        new_var = model.NewIntVar(lb, ub, pfx+'_mul_chain'+str(i))
        constr = model.AddMultiplicationEquality(new_var, (old_var, components[i+1]))
    return new_var


# %%
# Einsum description: 
# dict mapping operand names to tuples of coordinate names for operands
# tuple of coordinate names for outputs
# dict mapping coordinate names to sizes

# %%
def po_einsum(
    operand_dims:Dict[str,Tuple[str]],
    output_operand:str,
    dim_sizes:Dict[str,int],
    capacity:int,
    num_levels:int = 2,
    disambiguate_inner_outer = True,
    forbid_reduction_splitting = True,
    enforce_incomparable_nondivision = True
):
    '''
    Partial Order (with somewhat explicit data schedules) model for a single einsum.
    Should be very low-symmetry; disallows partial spilling.
    '''
    '''
    Variables:
        - num_levels sizes for each coord
        - booleans indicating whether each is temporal or spatial for each operand
        - booleans indicating whether each pair of factors is comparable in the partial order, and which way
        - integer contributions to spatial cost for each factor
        - integer contributions to temporal cost  for each factor
        - integer total spatial costs of each operand
        - integer total temporal costs of each operand
    Constraints:
        - Valid partial order (Transitivity, noncontradiction)
        - Partial order obeys temporal / spatial divides
        (a temporal and b spatial for any operand implies a > b)
        - nonparticipating factors spatial for outputs
        - n_inner ordered before n_outer, similar for m
        - m_inner * m_outer >= m, n_inner * n_outer >= n
        - spatial contributions are full size if participating and spatial,
        1 otherwise
        - temporal contributions are full if temporal, 1 otherwise
        - product of each type of contribution is total
        - sum of total spatial contributions <= capacity
    Minimize:
        - sum of products of spatial and temporal
    '''
    model = cp_model.CpModel()
    factors = [dim+'_'+str(lvl) for dim in dim_sizes.keys() for lvl in range(num_levels)]
    # Spatial variables
    spatial_vars = {}
    for v in factors:
        for operand in operand_dims.keys():
            spatial_vars[operand+'_'+v] = model.NewBoolVar(operand+'_'+v+'_spatial')
    # Partial order variables
    po_vars = {}
    for i in range(len(factors)):
        for j in range(i):
            f1 = factors[i]
            f2 = factors[j]
            po_vars[f1+'_lt_'+f2] = model.NewBoolVar(f1+'_lt_'+f2)
            po_vars[f2+'_lt_'+f1] = model.NewBoolVar(f2+'_lt_'+f1)
            # Noncontradiction
            model.Add(po_vars[f1+'_lt_'+f2] + po_vars[f2+'_lt_'+f1] <= 1)
    # Transitivity constraints
    for f1 in factors:
        for f2 in factors:
            for f3 in factors:
                if f1==f2 or f2==f3 or f1==f3:
                    continue
                model.AddImplication(
                    po_vars[f1+'_lt_'+f2],
                    po_vars[f1+'_lt_'+f3]
                ).OnlyEnforceIf(po_vars[f2+'_lt_'+f3])
    # Consistency with spatial constraints
    for operand in operand_dims.keys():
        for f1 in factors:
            for f2 in factors:
                if f1 != f2:
                    # If f1 is temporal and f2 is spatial for this operand, then f1 < f2
                    # model.Add(po_vars[f1+'_lt_'+f2] >= spatial_vars[operand+'_'+f2] - spatial_vars[operand+'_'+f1])
                    model.AddImplication(
                        spatial_vars[operand+'_'+f2],
                        po_vars[f1+'_lt_'+f2]
                    ).OnlyEnforceIf(
                        spatial_vars[operand+'_'+f1].Not()
                    )
    for dim in dim_sizes.keys():
        if dim not in operand_dims[output_operand]:
            for i in range(num_levels):
                model.Add(spatial_vars[output_operand + '_' + dim + '_' + str(i)] == 1)
    if disambiguate_inner_outer:
        # outer before inner
        for dim in dim_sizes.keys():
            for i in range(num_levels):
                for j in range(i):
                    # enforce i not before j, rather than j before i (minimal comparability)
                    model.Add(po_vars['{}_{}_lt_{}_{}'.format(dim, i, dim, j)] == 0)

    # Size variables
    size_vars = {}
    for dim in dim_sizes.keys():
        for i in range(num_levels):
            size_vars[dim+'_'+str(i)] = model.NewIntVar(1, dim_sizes[dim], dim+'_'+str(i))
        total_size_here = add_mul_chain(model,
                                        [size_vars[dim+'_'+str(i)] for i in range(num_levels)],
                                        1,
                                        dim_sizes[dim] * (2**(num_levels - 1)),
                                        dim+'_total')
        model.Add(total_size_here >= dim_sizes[dim])

    if forbid_reduction_splitting:
        for dim in dim_sizes.keys():
            if dim not in operand_dims[output_operand]:
                for i in range(num_levels-1):
                    model.Add(size_vars[dim+'_'+str(i)] == 1)

    if enforce_incomparable_nondivision:
        for dim in dim_sizes.keys():
            for i in range(num_levels):
                for j in range(i):
                    # if we have neither dim_i lt dim_j nor dim_j lt dim_i, dim_i must be 1
                    # (do not split dimensions when it doesn't matter)
                    model.Add(size_vars[dim+'_'+str(i)] == 1).OnlyEnforceIf(
                        po_vars[dim+'_'+str(i)+'_lt_'+dim+'_'+str(j)].Not(),
                        po_vars[dim+'_'+str(j)+'_lt_'+dim+'_'+str(i)].Not()
                    )

    # Spatial contributions
    spatial_contrib_vars = {}
    for operand in operand_dims.keys():
        for dim in dim_sizes.keys():
            for i in range(num_levels):
                v = dim + '_' + str(i)
                spatial_contrib_vars[operand+'_'+v] = model.NewIntVar(
                    1, dim_sizes[dim], operand+'_'+v+'_spatial_contrib'
                )
                # Constrain to factor size if participating and spatial, 1 otherwise
                if (dim in operand_dims[operand]):
                    model.Add(spatial_contrib_vars[operand+'_'+v] == size_vars[v]).OnlyEnforceIf(
                        spatial_vars[operand+'_'+v]
                    )
                    model.Add(spatial_contrib_vars[operand+'_'+v] == 1).OnlyEnforceIf(
                        spatial_vars[operand+'_'+v].Not()
                    )
                else:
                    model.Add(spatial_contrib_vars[operand+'_'+v] == 1)
    # Temporal contributions
    temporal_contrib_vars = {}
    for operand in operand_dims.keys():
        for dim in dim_sizes.keys():
            for i in range(num_levels):
                v = dim + '_' + str(i)
                temporal_contrib_vars[operand+'_'+v] = model.NewIntVar(
                    1, dim_sizes[dim], operand+'_'+v+'_temporal_contrib'
                )
                # Constrain to factor size if temporal, 1 otherwise
                model.Add(temporal_contrib_vars[operand+'_'+v] == size_vars[v]).OnlyEnforceIf(
                    spatial_vars[operand+'_'+v].Not()
                )
                model.Add(temporal_contrib_vars[operand+'_'+v] == 1).OnlyEnforceIf(
                    spatial_vars[operand+'_'+v]
                )
    
    total_iters = 1
    for d, s in dim_sizes.items():
        total_iters *= s
    # total spatial and temporal vars
    total_temporal_vars = {}
    total_spatial_vars = {}
    for operand in operand_dims.keys():
        # this spatial bound is slightly loose
        total_spatial_vars[operand] = model.NewIntVar(1, capacity, operand+'_total_spatial')
        total_temporal_vars[operand] = model.NewIntVar(1, total_iters, operand+'_total_temporal')
        
        total_spatial_vars[operand] = add_mul_chain(
            model,
            tuple(spatial_contrib_vars[operand+'_'+v] for v in factors), 
            1, total_iters,
            operand+'_total_spatial' 
        )
        total_temporal_vars[operand] = add_mul_chain(
            model,
            tuple(temporal_contrib_vars[operand+'_'+v] for v in factors), 
            1, total_iters,
            operand+'_total_temporal'
        )
    # capacity constraint
    model.Add(
        cp_model.LinearExpr.Sum(list(total_spatial_vars.values())) <= capacity
    )

    # Minimize sum of spatial times temporal
    total_cost_vars = {}
    for operand in operand_dims.keys():
        min_cost = 1
        for d in operand_dims[operand]:
            min_cost *= dim_sizes[d]
        total_cost_vars[operand] = model.NewIntVar(min_cost, total_iters, operand+'_total_cost')
        model.AddMultiplicationEquality(
            total_cost_vars[operand],
            (total_spatial_vars[operand], total_temporal_vars[operand])
        )
        # FAKE CONSTRAINT FOR TESTING
        # model.add(total_spatial_vars[operand] + total_temporal_vars[operand] == total_cost_vars[operand])
    model.Minimize(
        cp_model.LinearExpr.Sum(list(total_cost_vars.values()))
    )
    print("MODEL WRITING DONE")

    solver = cp_model.CpSolver()
    solver.Solve(model)
    print(solver.ResponseStats())

    # reconstruct loop nest and blocking levels consistent with partial order and spatial vars
    # toposort factors based on po_vars
    def toposort_factors(po_vars):
        visited = []
        def visit(f):
            if f in visited:
                return []
            visited.append(f)
            ret = []
            for c in factors:
                if f != c and solver.BooleanValue(po_vars[f+'_lt_'+c]):
                    ret = visit(c) + ret
            return [f] + ret
        full_sorted_list = []
        for f in factors:
            full_sorted_list = visit(f) + full_sorted_list
        return full_sorted_list

    sf = toposort_factors(po_vars)
    print(sf)
    spatial_hit = []
    for i in range(len(sf)):
        f = sf[i]
        for operand in operand_dims.keys():
            if operand not in spatial_hit and solver.BooleanValue(spatial_vars[operand+'_'+f]):
                print(' '*i + f'Load/Store {operand}')
                spatial_hit.append(operand)
        print(' '*i + f[0], 'wrap', solver.Value(size_vars[f]))
    print('Spatial Costs:')
    print([(o, solver.Value(total_spatial_vars[o])) for o in operand_dims.keys()])
    print('Temporal Costs:')
    print([(o, solver.Value(total_temporal_vars[o])) for o in operand_dims.keys()])

if __name__ == '__main__':
    # po_einsum(
    #     {'A': ('m', 'k', 'h'), 'B': ('n', 'h'), 'C': ('m', 'n')},
    #     'C',
    #     {'m': 32 * 1024, 'k': 2 * 1024, 'n': 10283, 'h': 8},
    #     16 * 1024,
    #     num_levels=3,
    #     forbid_reduction_splitting=True
    # )
    po_einsum(
        {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
        'C',
        {'m': 4 * 1024, 'k': 8 * 1024, 'n': 4 * 1024},
        128 * 1024
    )
    # po_einsum(
    #     {'A': ('m', 'n'), 'B': ('m', 'n')},
    #     'B',
    #     {'m': 4 * 1024, 'n': 4 * 1024},
    #     512 * 1024
    # )