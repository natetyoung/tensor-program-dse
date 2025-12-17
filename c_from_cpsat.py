from dataclasses import dataclass
from typing import Dict, List, Union
import ast
import re

@dataclass
class Wrap:
    dim: str
    factor: int
    indent: int

@dataclass
class LoadStore:
    op: str
    dims: Dict[str, int]
    indent: int

Node = Union[Wrap, LoadStore]

WRAP_RE = re.compile(r"(\w+)\s+wrap\s+(\d+)")
LDST_RE = re.compile(r"LD/ST\s+(\w+)\s+(.+)")

def parse_indented_trace(lines: List[str]) -> List[Node]:
    nodes: List[Node] = []

    for line in lines:
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))

        stripped = line.strip()

        if m := WRAP_RE.match(stripped):
            nodes.append(Wrap(
                dim=m.group(1),
                factor=int(m.group(2)),
                indent=indent
            ))
        elif m := LDST_RE.match(stripped):
            nodes.append(LoadStore(
                op=m.group(1),
                dims=ast.literal_eval(m.group(2)),
                indent=indent
            ))
        else:
            raise ValueError(f"Unrecognized line: {line}")

    return nodes

def extract_loops_and_operands(nodes: List[Node]):
    wraps: List[Wrap] = []
    operands: Dict[str, List[str]] = {}

    for n in nodes:
        if isinstance(n, Wrap):
            wraps.append(n)
        elif isinstance(n, LoadStore):
            operands[n.op] = list(n.dims.keys())

    return wraps, operands

def infer_output_operand(operands: Dict[str, List[str]]) -> str:
    # simple, matches your trace printing order
    return list(operands.keys())[-1]

def infer_reduction_dims(operands, output, tiled_dims):
    out_dims = set(operands[output])
    all_dims = set(d for dims in operands.values() for d in dims)
    tiled_dims = set(tiled_dims)
    return sorted(all_dims - out_dims - tiled_dims), sorted(out_dims - tiled_dims)

def emit_tiled_loops(wraps, dim_sizes):
    dim_depth = {}
    tiled_dims = []
    lines = []
    indent = 1
    curr_sizes = {}

    def emit(s):
        lines.append("    " * indent + s)

    for w in wraps:
        level = dim_depth.get(w.dim, 0)
        dim_depth[w.dim] = level + 1
        base = f"{w.dim}{level}"
        size = dim_sizes[w.dim]
        curr_size = curr_sizes.get(w.dim, size)
        quotient = max(curr_size//w.factor, 1)
        curr_sizes[w.dim] = quotient

        emit(f"for (int {base} = 0; {base} < {curr_size}; {base} += {quotient}) {{")
        indent += 1

        tiled_dims.append(w.dim)
    
    for w in wraps:
        level = dim_depth.get(w.dim, 0) - 1
        base = f"{w.dim}{level}"
        size = dim_sizes[w.dim]
        curr_size = curr_sizes.get(w.dim, size)
        reassign = f"int {w.dim} = {base}"
        if level > 0:
            reassign += " + " + " + ".join([f"{w.dim}{l}" for l in range(level)])
        
        if curr_size >= 1:
            emit(
                f"for (int {base}_i = 0; "
                f"{base}_i < (({base} + {curr_size} <= {size}) ? {curr_size} : ({size} - {base})); "
                f"{base}_i++) {{"
            )
            indent += 1
            
            emit(reassign + f" + {base}_i;")
        elif curr_size == 0:
            emit(reassign + ";")
        
        curr_sizes[w.dim] = -1

    return indent, lines, tiled_dims

def strides_for(dims, dim_sizes):
    strides = {}
    stride = 1
    for d in reversed(dims):
        strides[d] = stride
        stride *= dim_sizes[d]
    return strides

def emit_compute(operands, output, dim_sizes, tiled_dims):
    inputs = [op for op in operands if op != output]
    red_dims, out_dims = infer_reduction_dims(operands, output, tiled_dims)

    lines = []
    indent = "    "

    lines.append(indent + "float acc = 0.0f;")

    # reduction loops
    for d in out_dims:
        lines.append(indent + f"for (int {d} = 0; {d} < {dim_sizes[d]}; {d}++) {{")
        indent += "    "

    for d in red_dims:
        lines.append(indent + f"for (int {d} = 0; {d} < {dim_sizes[d]}; {d}++) {{")
        indent += "    "

    # indexing
    terms = []
    for op in inputs:
        strides = strides_for(operands[op], dim_sizes)
        idx = " + ".join(f"{d} * {strides[d]}" for d in operands[op])
        terms.append(f"{op}[{idx}]")

    acc = indent + "acc += " + " * ".join(terms) + ";"
    lines.append(acc)

    # close reduction loops
    for _ in red_dims:
        indent = indent[:-4]
        lines.append(indent + "}")

    # store
    out_strides = strides_for(operands[output], dim_sizes)
    out_idx = " + ".join(f"{d} * {out_strides[d]}" for d in operands[output])
    lines.append(indent + f"{output}[{out_idx}] = acc;")

    for _ in out_dims:
        indent = indent[:-4]
        lines.append(indent + "}")

    return lines

def emit_einsum_function(
    name: str,
    nodes: List[Node],
    dim_sizes: Dict[str, int]
) -> str:
    wraps, operands = extract_loops_and_operands(nodes)
    output = infer_output_operand(operands)

    args = ", ".join(f"float * restrict {op}" for op in operands)
    lines = [f"void {name}({args}) {{"]
    indent, tiled_lines, tiled_dims = emit_tiled_loops(wraps, dim_sizes)
    lines.extend(tiled_lines)

    def emit(s):
        lines.append("    " * indent + s)

    compute = emit_compute(operands, output, dim_sizes, tiled_dims)
    lines += ["    " * indent + l.strip() for l in compute]

    # close tiled loops
    while indent > 0:
        indent -= 1
        emit("}")

    return "\n".join(lines)

def emit_c_driver(
    einsum_functions,
    tensor_sizes,
    einsum_calls,
):
    lines = []

    # ---- headers ----
    lines += [
        "#include <stdio.h>",
        "#include <stdlib.h>",
        "#include <time.h>",
        "",
    ]

    # ---- einsum functions ----
    for _, fn in einsum_functions:
        lines.append(fn.strip())
        lines.append("")

    # ---- main ----
    lines.append("int main() {")
    lines.append("")
    lines.append("        struct timespec start, end;")
    lines.append("        clock_gettime(CLOCK_MONOTONIC, &start);")

    # ---- allocations + init ----
    for name, size in tensor_sizes.items():
        lines.append(
            f"        float * restrict {name} = (float*)malloc(sizeof(float) * {size});"
        )
        lines.append("")
        lines.append(f"    for (int i = 0; i < {size}; i++)")
        lines.append(f"        {name}[i] = 1.0f;")
        lines.append("    ")

    # ---- einsum calls ----
    for fn, args in einsum_calls:
        arglist = ", ".join(args)
        lines.append(f"{fn}({arglist});")

    lines.append("")
    lines.append("        clock_gettime(CLOCK_MONOTONIC, &end);")
    lines.append(
        "        double t = (end.tv_sec - start.tv_sec) +"
    )
    lines.append(
        "                   (end.tv_nsec - start.tv_nsec) * 1e-9;"
    )
    lines.append('        printf("Time: %f\\n", t);')
    lines.append("        return 0;")
    lines.append("}")

    return "\n".join(lines)



if __name__ == '__main__':
    text = """
LD/ST L0_Y {'m': 64, 'd': 256} 
    m wrap 2 
        f wrap 1024 
            LD/ST L0_H {'m': 32, 'f': 1} 
            d wrap 256 
                LD/ST L0_W1 {'d': 1, 'f': 1}
"""

    nodes = parse_indented_trace(text.strip().splitlines())

    dim_sizes = {
        "m": "M",
        "n": "N",
        "l": "L",
    }

    print(emit_einsum_function("einsum", nodes, dim_sizes))