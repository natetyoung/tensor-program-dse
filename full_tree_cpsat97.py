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

def compute_strides(dims, all_dim_sizes):
    strides = {}
    stride = 1
    for d in reversed(dims):
        strides[d] = stride
        stride *= all_dim_sizes[d]
    return strides

def emit_c_code_section(
    einsum,
    einsum_idx,
    all_dim_sizes,
    temporal_dim,
    solver,
    op_allowed_temp_dims,
):
    """
    Emit a mathematically correct einsum kernel with wrap/temporal factors.
    """
    ops = list(einsum.operand_dims.keys())
    out = einsum.output_operand
    inputs = [o for o in ops if o != out]

    # Dimensions
    out_dims = einsum.operand_dims[out]
    in_dims = {o: einsum.operand_dims[o] for o in inputs}

    # Contracted dims = appear in inputs but not output
    contracted = sorted(
        set(d for o in inputs for d in in_dims[o]) - set(out_dims)
    )

    # Strides
    def compute_strides(dims, sizes):
        strides = {}
        stride = 1
        for d in reversed(dims):
            strides[d] = stride
            stride *= sizes[d]
        return strides

    out_strides = compute_strides(out_dims, all_dim_sizes)
    in_strides = {o: compute_strides(in_dims[o], all_dim_sizes) for o in inputs}

    code = []
    code.append(
        f"void einsum_{einsum_idx}("
        + ", ".join([f"float * restrict {o}" for o in inputs + [out]])
        + ") {"
    )

    indent = 1

    # ---- temporal wrap loops ----
    for dim in op_allowed_temp_dims[out]:
        factor = solver.Value(temporal_dim[out][dim])
        if factor > 1:
            code.append(
                "    " * indent
                + f"for (int {dim}_wrap=0; {dim}_wrap<{factor}; {dim}_wrap++) {{"
            )
            code.append(
                "    " * (indent + 1)
                + f"int {dim}_start = {dim}_wrap * ({all_dim_sizes[dim]} / {factor});"
            )
            code.append(
                "    " * (indent + 1)
                + f"int {dim}_end = ({dim}_wrap == {factor}-1 ? {all_dim_sizes[dim]} : {dim}_start + ({all_dim_sizes[dim]} / {factor}));"
            )
            indent += 1

    # ---- output loops ----
    for d in out_dims:
        if solver.Value(temporal_dim[out][d]) > 1:
            code.append(
                "    " * indent + f"for (int {d}={d}_start; {d}<{d}_end; {d}++) {{"
            )
        else:
            code.append(
                "    " * indent + f"for (int {d}=0; {d}<{all_dim_sizes[d]}; {d}++) {{"
            )
        indent += 1

    # accumulator
    code.append("    " * indent + "float acc = 0.0f;")

    # ---- reduction loops ----
    for d in contracted:
        code.append(
            "    " * indent + f"for (int {d}=0; {d}<{all_dim_sizes[d]}; {d}++) {{"
        )
        indent += 1

    # ---- load * load ----
    def index_expr(op, dims, strides):
        return " + ".join([f"{d}*{strides[d]}" for d in dims])

    mul_terms = []
    for o in inputs:
        mul_terms.append(f"{o}[{index_expr(o, in_dims[o], in_strides[o])}]")

    code.append("    " * indent + f"acc += {' * '.join(mul_terms)};")

    # close reduction loops
    for _ in contracted:
        indent -= 1
        code.append("    " * indent + "}")

    # ---- store ----
    code.append(
        "    " * indent + f"{out}[{index_expr(out, out_dims, out_strides)}] = acc;"
    )

    # close output loops
    for _ in out_dims:
        indent -= 1
        code.append("    " * indent + "}")

    # close temporal wrap loops
    for dim in op_allowed_temp_dims[out]:
        factor = solver.Value(temporal_dim[out][dim])
        if factor > 1:
            indent -= 1
            code.append("    " * indent + "}")

    code.append("}\n")
    return "\n".join(code)


def emit_c_program_chains(chains, solver, all_operands, all_operand_dims, all_dim_sizes,
                          temporal_dim, spatial_dim, same_node, parent, op_allowed_temp_dims):
    """Emit C program with separate functions for each einsum."""
    code = '#include <stdio.h>\n#include <stdlib.h>\n#include <time.h>\n\n'

    # Emit functions
    for chain_idx, chain in enumerate(chains):
        for e_idx, einsum in enumerate(chain):
            code += emit_c_code_section(
                einsum,
                einsum_idx=e_idx,
                all_dim_sizes=all_dim_sizes,
                temporal_dim=temporal_dim,
                solver=solver,
                op_allowed_temp_dims=op_allowed_temp_dims,
            )

    # Emit main
    code += 'int main() {\n'
    code += '    struct timespec start, end;\n'
    code += '    clock_gettime(CLOCK_MONOTONIC, &start);\n\n'

    # Allocate arrays
    for op in sorted(all_operands):
        dims = all_operand_dims[op]
        total_size = 1
        for d in dims:
            total_size *= all_dim_sizes[d]
        code += f'    float * restrict {op} = (float*)malloc(sizeof(float) * {total_size});\n'
        code += f'    for (int i=0;i<{total_size};i++) {op}[i] = 1.0f;\n\n'

    # Call functions
    for chain in chains:
        for e_idx, einsum in enumerate(chain):
            params = [op for op in einsum.operand_dims.keys()]
            code += f'    einsum_{e_idx}({", ".join(params)});\n'

    code += '\n    clock_gettime(CLOCK_MONOTONIC, &end);\n'
    code += '    double t = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) * 1e-9;\n'
    code += '    printf("Time: %f\\n", t);\n'
    code += '    return 0;\n'
    code += '}\n'
    return code

def cb_full_tree(
    einsums:List[Einsum],
    capacity:int,
    enforce_optimal_placement = True,
    emit_c_code:bool = False
):
    '''
    Full schedule-tree model for a chain of einsums, for fusion at various levels.
    Disallows partial spilling or spilling of any intermediate.
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
        - num_total_operands^2 booleans for "A is in the same node as B"
        - num_total_operands^2 booleans for "A is a skew-ancestor of B"
            (using n^3 booleans for "A is the same node as C which is B's ancestor", plus regular ancestor)
        - num_total_operands^2 booleans for "A is a skew-parent of B"
            (using n^3 booleans for "A is the same node as C which is B's parent", plus regular parent)
        - num_total_operands^2 booleans for "A and B must coexist in the fast memory"
    Constraints (not entirely exhaustive):
        Constraints so parent/ancestor relationships form a tree:
         - A parent of B implies A ancestor of B
         - A ancestor of B and B ancestor of C implies A ancestor of C
         - A ancestor of B implies B not ancestor of A
         - A same node as B implies B same node as A
         - A same node as B and B same node as C implies A same node as C
         - A same node as B and C parent of A implies C parent of B
         - A same node as B implies A not ancestor of B and B not ancestor of A
         - Ancestorship must be provable inductively
            (A ancestor of B implies for some C, A is an ancestor of C and C is the parent of A)
         - Each node has only one parent
        Sanity of factors in tree:
         - A same node as B implies temporal-here factors equal
         - A same node as B implies non-shared temporal-here factors all 1
         - A ancestor of B implies temporal-here factors in A which are not allowed for B are 1
         - A same node as C and C ancestor of B implies same as above
        Consistency of einsums in tree:
         - for all A, B in same einsum, either:
          - A same node as B
          - A (skew-)ancestor of B
          - B (skew-)ancestor of A
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
                assert op in einsums[i+1].operand_dims.keys()
                assert einsums[i].operand_dims[op] == einsums[i+1].operand_dims[op]
            else:
                if i < len(einsums) - 1:
                    assert op not in einsums[i+1].operand_dims.keys()
            for j in range(i, len(einsums)):
                if i != j and i+1 != j:
                    assert op not in einsums[j].operand_dims.keys()
            if op not in op_allowed_temp_dims:
                if op == einsums[i].output_operand:
                    op_allowed_temp_dims[op] = einsums[i].operand_dims[op]
                else:
                    op_allowed_temp_dims[op] = list(einsums[i].dim_sizes.keys())
            all_operand_dims[op] = einsums[i].operand_dims[op]
            if op == einsums[i].output_operand and i < len(einsums) - 1:
                fused_operands.append(op)
        for d in einsums[i].dim_sizes.keys():
            if d in all_dim_sizes:
                assert einsums[i].dim_sizes[d] == all_dim_sizes[d]
            else:
                all_dim_sizes[d] = einsums[i].dim_sizes[d]

    all_operands = list(all_operand_dims.keys())

    model = cp_model.CpModel()

    # parent, ancestor, and same-node relationship variables
    parent:Dict[str,Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}p{}'.format(i, j)) for j in all_operands if i != j
        } for i in all_operands + ['ROOT']
    } # ipj is "i is the parent of j"
    ancestor:Dict[str,Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}a{}'.format(i, j)) for j in all_operands if i != j
        } for i in all_operands
    } #iaj is "i is an ancestor of j"
    same_node:Dict[str,Dict[str,cp_model.IntVar]] = {
        i: {
            j: model.NewBoolVar('{}s{}'.format(i, j)) for j in all_operands if i != j
        } for i in all_operands
    }

    # Constraints so parent/ancestor relationships form a tree
    for i in all_operands:
        for j in all_operands:
            if i == j:
                continue
            # A parent of B implies A ancestor of B
            model.AddImplication(parent[i][j], ancestor[i][j])
            # A same node as B implies A not ancestor of B
            # (other direction will be taken care of by later iteration)
            model.AddImplication(same_node[i][j], ancestor[i][j].Not())
            # A ancestor of B implies B not ancestor of A
            # (other direction will be taken care of by later iteration)
            model.AddImplication(ancestor[i][j], ancestor[j][i].Not())
            # same-node commutativity
            model.Add(same_node[i][j] == same_node[j][i])

            ancestor_proof:Dict[str,cp_model.IntVar] = {}
            for k in all_operands:
                if i == k or j == k:
                    continue
                # A ancestor of B and B ancestor of C implies A ancestor of C
                model.AddImplication(ancestor[i][j], ancestor[i][k]).OnlyEnforceIf(ancestor[j][k])
                # A same node as B and C parent of A implies C parent of B
                model.AddImplication(parent[k][i], parent[k][j]).OnlyEnforceIf(same_node[i][j])
                # A same node as B and B same node as C implies A same node as C
                model.AddImplication(same_node[i][j], same_node[i][k]).OnlyEnforceIf(same_node[j][k])

                # variable: k proves that i ancestor of j (k is parent of j and i ancestor of k)
                ancestor_proof[k] = model.NewBoolVar('{}_pr_{}_anc_{}'.format(k, i, j))
                model.AddBoolAnd(ancestor[i][k], parent[k][j]).OnlyEnforceIf(ancestor_proof[k])
            # ancestorship must be provable
            model.AddBoolOr(
                [
                    ancestor_proof[k] for k in all_operands if k != i and k != j
                ] + [parent[i][j]]
            ).OnlyEnforceIf(ancestor[i][j])
        # Each node has only one parent
        model.AddExactlyOne([parent[x][i] for x in all_operands + ['ROOT'] if x != i])

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
            # A same node as B implies temporal-here factors equal
            for dim in op_allowed_temp_dims[i]:
                if dim in op_allowed_temp_dims[j]:
                    model.Add(temporal_dim[i][dim] == temporal_dim[j][dim]).OnlyEnforceIf(same_node[i][j])
            # A same node as B implies non-shared temporal-here factors all 1
            for dim in op_allowed_temp_dims[i]:
                if dim not in op_allowed_temp_dims[j]:
                    model.Add(temporal_dim[i][dim] == 1).OnlyEnforceIf(same_node[i][j])
            # A ancestor of B implies temporal-here factors in A which are not allowed for B are 1
            for dim in op_allowed_temp_dims[i]:
                if dim not in op_allowed_temp_dims[j]:
                    model.Add(temporal_dim[i][dim] == 1).OnlyEnforceIf(ancestor[i][j])
            # A same node as C and C ancestor of B implies same as above
            for k in all_operands:
                if i == k or j == k:
                    continue
                for dim in op_allowed_temp_dims[i]:
                    if dim not in op_allowed_temp_dims[j]:
                        model.Add(temporal_dim[i][dim] == 1).OnlyEnforceIf(
                            [same_node[i][k], ancestor[k][j]]
                        )

    # Skew-ancestry variables
    skew_anc:Dict[str,Dict[str,cp_model.IntVar]] = {}
    for op_a in all_operands:
        skew_anc[op_a] = {}
        for op_b in all_operands:
            if op_a == op_b:
                continue
            skew_components = [ancestor[op_a][op_b]]
            for op_c in all_operands:
                if op_c == op_a or op_c == op_b:
                    continue
                # c proves a in ancestor of b
                skew_a_b_c = model.NewBoolVar('skewa_{}_{}_{}'.format(op_a, op_b, op_c))
                model.AddBoolAnd(same_node[op_c][op_a], ancestor[op_c][op_b]).OnlyEnforceIf(skew_a_b_c)
                skew_components.append(skew_a_b_c)
            skew_anc[op_a][op_b] = model.NewBoolVar('{op_a}_skew_anc_{op_b}')
            model.AddBoolOr(skew_components).OnlyEnforceIf(skew_anc[op_a][op_b])
            model.AddBoolAnd([v.Not() for v in skew_components]).OnlyEnforceIf(skew_anc[op_a][op_b].Not())

    # Constraints for consistency of einsums in tree
    for e in einsums:
        ops = list(e.operand_dims.keys())
        for op_a in ops:
            for op_b in ops:
                if op_a == op_b:
                    continue
                # either A same node as B, or B skew-ancestor of A, or A skew-ancestor of B
                same_a_b = same_node[op_a][op_b]
                skew_a_b = skew_anc[op_a][op_b]
                skew_b_a = skew_anc[op_b][op_a]
                model.AddBoolOr([same_a_b, skew_a_b, skew_b_a])
    
    # Costs
    spatial_cost:Dict[str,cp_model.IntVar] = {}
    temporal_dim_contribs:Dict[str,Dict[str,Dict[str,cp_model.IntVar]]] = {}
    total_temporal_dim:Dict[str,Dict[str,cp_model.IntVar]] = {}
    total_temporal_cost:Dict[str,cp_model.IntVar] = {}
    for op in all_operands:
        op_size = 1
        for d in all_operand_dims[op]:
            op_size *= all_dim_sizes[d]
        # Product of own factors is spatial cost
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
        max_temporal_cost = allowed_dim_product * (2**len(all_operands))
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

        if op in fused_operands:
            total_temporal_cost[op] = model.NewIntVar(0, 0, 'total_temporal_cost_'+op)
        else:
            total_temporal_cost[op] = add_mul_chain(
                model,
                list(total_temporal_dim[op].values()),
                1, max_temporal_cost,
                'total_temporal_cost_'+op
            )
    
    # Capacity
    # when don't two buffers A and B need to coexist?
    # 1. neither is a (skew-)ancestor of the other OR
    # 2. A is an ancestor of B, but:
    #   all A's producers (if it is an output) or its consumers (if it is an input)
    #   have the A node or further out as the least common ancestor with B
    # so they do need to coexist if:
    # 1. A is a (skew-)ancestor of B AND
    # 2. at least one of A's fellow operands in an einsum has a LCA with B which is (skew-)descended from A
    # 2 in other words: some C exists where A ancestor of C, C ancestor of both B and some other operand with A
    coexist_vars:Dict[str,Dict[str,cp_model.IntVar]] = {}
    for op_a in all_operands:
        coexist_vars[op_a] = {}
        for op_b in all_operands:
            if op_a == op_b:
                continue
            coexist_var = model.NewBoolVar('coexist_{}_{}'.format(op_a, op_b))
            coexist_vars[op_a][op_b] = coexist_var
            for e in einsums:
                if op_a in e.operand_dims.keys() and op_b in e.operand_dims.keys():
                    model.Add(coexist_var == 1)
            for e in einsums:
                if op_a not in e.operand_dims.keys():
                    continue
                problematic_operands = []
                if op_a == e.output_operand:
                    problematic_operands = [o for o in e.operand_dims.keys() if o != op_a and o != op_b]
                else:
                    problematic_operands = [e.output_operand]
                for op_d in problematic_operands:
                    if op_a == op_d or op_b == op_d:
                        continue
                    for op_c in all_operands:
                        if op_c == op_d:
                            continue
                        if op_c == op_b:
                            model.AddBoolOr(
                                skew_anc[op_b][op_d].Not(), skew_anc[op_a][op_b].Not()
                            ).OnlyEnforceIf(
                                coexist_var.Not()
                            )
                        elif op_c != op_a:
                            anc_a_c = skew_anc[op_a][op_c]
                            anc_c_b = skew_anc[op_c][op_b]
                            anc_c_d = skew_anc[op_c][op_d]
                            # none of B's skew-ancestors before A are skew-ancestors of D
                            model.AddBoolOr(
                                anc_a_c.Not(), anc_c_b.Not(), anc_c_d.Not(), skew_anc[op_a][op_b].Not()
                            ).OnlyEnforceIf(
                                coexist_var.Not()
                            )
                        # B is not itself a skew-ancestor of D
                        model.AddBoolOr(
                            skew_anc[op_b][op_d].Not(), skew_anc[op_a][op_b].Not()
                        ).OnlyEnforceIf(
                            coexist_var.Not()
                        )
                        # D is not itself a skew-ancestor of B before A
                        model.AddBoolOr(
                            skew_anc[op_a][op_d].Not(), skew_anc[op_d][op_b].Not(), skew_anc[op_a][op_b].Not()
                        ).OnlyEnforceIf(
                            coexist_var.Not()
                        )
                    # B is not colocated with D
                    model.AddBoolOr(
                        same_node[op_b][op_d].Not(), skew_anc[op_a][op_b].Not()
                    ).OnlyEnforceIf(
                        coexist_var.Not()
                    )
    for op_a in all_operands:
        for op_b in all_operands:
            if op_a == op_b:
                continue
            model.Add(coexist_vars[op_a][op_b] == coexist_vars[op_b][op_a])
    
    total_coexist_space:Dict[str,cp_model.IntVar] = {}
    for op in all_operands:
        total_coexist_space[op] = model.NewIntVar(1, capacity, 'total_space_used_{op}')
        contrib_vars = []
        for op2 in all_operands:
            if op == op2:
                continue
            contrib_var = model.NewIntVar(1, capacity, 'space_contrib_{}_{}'.format(op, op2))
            contrib_vars.append(contrib_var)
            model.Add(contrib_var == spatial_cost[op2]).OnlyEnforceIf(coexist_vars[op][op2])
            model.Add(contrib_var == 1).OnlyEnforceIf(coexist_vars[op][op2].Not())
        # Real capacity constraint
        model.Add(cp_model.LinearExpr.Sum(contrib_vars) + spatial_cost[op] <= capacity)

    if enforce_optimal_placement:
        # Optional optimality sanity constraints
        for op in all_operands:
            for dim in op_allowed_temp_dims[op]:
                # temporal factor is 1 if dim does not participate in this tensor or any assigned to same node
                if dim not in all_operand_dims[op]:
                    model.Add(temporal_dim[op][dim] == 1).OnlyEnforceIf(
                        *[
                            same_node[op][other_op].Not() 
                            for other_op in all_operands 
                            if dim in all_operand_dims[other_op] and other_op != op
                        ]
                    )
                # spatial factor is 1 if dim does participate in this and any same node or skew-descendants
                if dim in all_operand_dims[op]:
                    model.Add(spatial_dim[op][dim] == 1).OnlyEnforceIf(
                        *([
                            same_node[op][other_op].Not()
                            for other_op in all_operands
                            if dim not in all_operand_dims[other_op] and other_op != op
                        ] + [
                            skew_anc[op][other_op].Not()
                            for other_op in all_operands
                            if dim not in all_operand_dims[other_op] and other_op != op
                        ])
                    )

    # total cost vars
    total_cost_vars:Dict[str,cp_model.IntVar] = {}
    for op in all_operands:
        op_size = 1
        for d in all_operand_dims[op]:
            op_size *= all_dim_sizes[d]
        allowed_dim_product = 1
        for d in op_allowed_temp_dims[op]:
            allowed_dim_product *= all_dim_sizes[d]
        if op in fused_operands:
            total_cost_vars[op] = model.NewIntVar(0, 0, 'total_cost_'+op)
        else:
            total_cost_vars[op] = model.NewIntVar(op_size, allowed_dim_product * (2**len(all_operands)), 'total_cost_'+op)
            model.AddMultiplicationEquality(
                total_cost_vars[op],
                (spatial_cost[op], total_temporal_cost[op])
            )

    model.Minimize(cp_model.LinearExpr.Sum(list(total_cost_vars.values())))

    print("MODEL WRITING DONE")

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 300.0
    solver.Solve(model)
    print(solver.ResponseStats())

    for op in all_operands + ['ROOT']:
        for op2 in all_operands:
            if op == op2:
                continue
            if solver.BooleanValue(parent[op][op2]):
                print(op, 'is the parent of', op2)

    for op in all_operands:
        for op2 in all_operands:
            if op == op2:
                continue
            if solver.BooleanValue(same_node[op][op2]):
                print(op, 'same node as', op2)
        print(op, 'must coexist with', [
            op2 for op2 in all_operands if op != op2 and solver.BooleanValue(coexist_vars[op][op2])
        ])

    # print tree structure
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
                    if solver.BooleanValue(same_node[current][op2]):
                        path[-1].append(op2)
                for potential_parent in all_operands + ['ROOT']:
                    if potential_parent == current:
                        continue
                    if solver.BooleanValue(parent[potential_parent][current]):
                        if potential_parent == 'ROOT':
                            current = potential_parent
                            break
                        path.append([potential_parent])
                        current = potential_parent
                        break
            if len(path) > len(full_path):
                full_path = path
        full_path = list(reversed(full_path))
        print('Einsum operands path:', ' -> '.join([str(n) for n in full_path]))
        indent_level = 0
        for level in full_path:
            # print temporal dims here if >1, indenting after each, then print all participating ops in level
            for dim in op_allowed_temp_dims[level[0]]:
                dim_factor = solver.Value(temporal_dim[level[0]][dim])
                if dim_factor > 1:
                    print(' ' * indent_level + dim + ' wrap', dim_factor)
                    indent_level += 1
            for op in level:
                if op in e.operand_dims.keys():
                    print(' ' * indent_level + 'LD/ST ' + op + ' ' + str({
                        d: solver.Value(spatial_dim[op][d]) for d in spatial_dim[op].keys()
                    }))
    
    # print per-einsum costs
    for e_num in range(len(einsums)):
        print(f"Einsum {e_num} spatial costs:", [(o, solver.Value(spatial_cost[o])) for o in einsums[e_num].operand_dims])
        print(f"Einsum {e_num} temporal costs:", [(o, solver.Value(total_temporal_cost[o])) for o in einsums[e_num].operand_dims])
    
    if emit_c_code:
        code = emit_c_program_chains(
            [einsums],
            solver,
            all_operands,
            all_operand_dims,
            all_dim_sizes,
            temporal_dim,
            spatial_dim,
            same_node,
            parent,
            op_allowed_temp_dims
        )
        return code

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
    # cb_full_tree(
    #     [
    #         Einsum(
    #             {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
    #             'C',
    #             {'m': 32 * 1024, 'k': 4 * 1024, 'n': 16 * 1024}
    #         ),
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
    cb_full_tree(
        [
            Einsum(
                {'A': ('m', 'k'), 'B': ('k', 'n'), 'C': ('m', 'n')},
                'C',
                {'m': 32 * 1024, 'k': 4 * 1024, 'n': 16 * 1024}
            ),
            Einsum(
                {'C': ('m', 'n'), 'D': ('m', 'n')},
                'D',
                {'m': 32 * 1024, 'n': 16 * 1024}
            ),
            Einsum(
                {'D': ('m', 'n'), 'E': ('n', 'l'), 'F': ('m', 'l')},
                'F',
                {'m': 32 * 1024, 'n': 16 * 1024, 'l': 4 * 1024}
            )
        ],
        512 * 1024
    )

