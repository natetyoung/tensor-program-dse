from full_tree_cpsat97 import Einsum, cb_full_tree
from typing import Dict, Tuple, List

def c_index(name, dims, dim_sizes):
    """
    Generate row-major 1D index expression.
    """
    idx = []
    stride = 1
    for d in reversed(dims):
        idx.append(f"{d} * {stride}")
        stride *= dim_sizes[d]
    return " + ".join(reversed(idx))

def emit_array_decl(name, dims, dim_sizes):
    size = 1
    for d in dims:
        size *= dim_sizes[d]
    # restrict is critical for Polly
    return f"float * restrict {name} = (float*)malloc(sizeof(float) * {size});"

def emit_init(name, dims, dim_sizes):
    size = 1
    for d in dims:
        size *= dim_sizes[d]
    return f"""
    for (int i = 0; i < {size}; i++)
        {name}[i] = 1.0f;
    """

def emit_fused_kernel(e: Einsum):
    out = e.output_operand
    dims = e.dim_sizes
    out_dims = e.operand_dims[out]
    in_ops = [k for k in e.operand_dims if k != out]
    red_dims = [d for d in dims if d not in out_dims]

    code = ""

    # Output loops
    for d in out_dims:
        code += f"for (int {d} = 0; {d} < {dims[d]}; {d}++) {{\n"

    # Scalar accumulator
    code += "float acc = 0.0f;\n"

    # Reduction loops
    for r in red_dims:
        code += f"for (int {r} = 0; {r} < {dims[r]}; {r}++) {{\n"

    muls = []
    for op in in_ops:
        idx = c_index(op, e.operand_dims[op], dims)
        muls.append(f"{op}[{idx}]")

    code += "acc += " + " * ".join(muls) + ";\n"

    # Close reduction loops
    for _ in red_dims:
        code += "}\n"

    out_idx = c_index(out, out_dims, dims)
    code += f"{out}[{out_idx}] = acc;\n"

    # Close output loops
    for _ in out_dims:
        code += "}\n"

    return code


def emit_einsum_function(e: Einsum, idx: int) -> str:
    args = []
    for name in e.operand_dims:
        args.append(f"float * restrict {name}")
    arglist = ", ".join(args)

    code = f"void einsum_{idx}({arglist}) {{\n"
    code += emit_fused_kernel(e)
    code += "}\n\n"
    return code

def collect_global_dim_sizes(einsums):
    dims = {}
    for e in einsums:
        for d, size in e.dim_sizes.items():
            if d in dims:
                assert dims[d] == size
            else:
                dims[d] = size
    return dims

def emit_c_program(einsums, optimized=False, capacity=None) -> str:
    headers = """
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
"""
    
    if not optimized:
        code = headers + "\n"

        # Emit einsum functions (Polly sees these!)
        for i, e in enumerate(einsums):
            code += emit_einsum_function(e, i)

        # Collect arrays
        arrays = {}
        for e in einsums:
            for name, dims in e.operand_dims.items():
                arrays[name] = dims
        
        main = "int main() {\n"

        main += """
        struct timespec start, end;
        clock_gettime(CLOCK_MONOTONIC, &start);
        """

        # Declarations
        global_dims = collect_global_dim_sizes(einsums)
        for name, dims in arrays.items():
            main += emit_array_decl(name, dims, global_dims) + "\n"
            main += emit_init(name, dims, global_dims) + "\n"

        # Call einsum kernels
        for i, e in enumerate(einsums):
            args = ", ".join(e.operand_dims.keys())
            main += f"einsum_{i}({args});\n"
        
        main += """
    clock_gettime(CLOCK_MONOTONIC, &end);
    double t = (end.tv_sec - start.tv_sec) +
               (end.tv_nsec - start.tv_nsec) * 1e-9;
    printf("Time: %f\\n", t);
    return 0;
}
"""   
    else:
        code = cb_full_tree(einsums, capacity=capacity, emit_c_code=True)
        main = ""

    return code + main