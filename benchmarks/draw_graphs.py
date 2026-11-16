'''Draw each case in cases.py as a dataflow graph: one node per einsum,
edges labelled with the tensor passed between them. Sizes are not shown;
a node's shape says what kind of einsum it is:

    box             contraction (matmul-like): >= 2 inputs share a summed dim
    invtriangle     reduction: dims summed out of a single input
    triangle        elementwise (incl. broadcast of a lower-rank operand)
    diamond         outer product: no reduction, output dims not all
                    present in any one input
    plaintext       workload inputs (weights, activations) -- not einsums
    double border   global output (written off-chip)

--no-labels drops the title and all node and edge labels (inputs become dots), leaving
just the graph's shape.

Einsums come from the case's workloads/*.yaml (rendered with its jinja
data) or, for AccelForge example workloads, from results/<case>/einsums.json
(written by export.py).

Usage: python3 draw_graphs.py [CASE ...] [--out DIR] [--format svg|png|pdf]
       [--no-inputs] [--no-labels]
Writes DIR/<case>.dot, plus DIR/<case>.<format> if Graphviz's `dot` is on
PATH, else DIR/<case>.html, which renders the graph in a browser (viz.js).
Needs jinja2 and PyYAML.'''
import argparse, json, re, shutil, subprocess
from pathlib import Path

import jinja2, yaml

from cases import CASES

HERE = Path(__file__).resolve().parent
REF = re.compile(r'(\w+)\[([^\]]*)\]')

SHAPES = {  # kind -> (graphviz shape, fill colour)
    'contraction': ('box', '#9ecae1'),
    'reduction': ('invtriangle', '#fdae6b'),
    'elementwise': ('triangle', '#a1d99b'),
    'outer': ('diamond', '#bcbddc'),
}


def parse_einsum(text):
    '''"Out[a, b] = X[a, k] * W[M: k, b]" -> (name, {tensor: dims}, output).
    A reinterpreted dim "M: k" is the rank variable k.'''
    refs = [(t, tuple(d.split(':')[-1].strip() for d in dims.split(',') if d.strip()))
            for t, dims in REF.findall(text)]
    out = refs[0][0]
    return out, dict(refs), out


def load_einsums(name, case):
    '''[(einsum name, {tensor: dims}, output tensor)] for a case.'''
    if case['workload'].endswith('.yaml'):
        src = (HERE / case['workload']).read_text()
        w = yaml.safe_load(jinja2.Template(src).render(**case['jinja']))['workload']
        einsums = [parse_einsum(e if isinstance(e, str) else e['einsum'])
                   for e in w['einsums']]
    else:
        path = HERE / 'results' / name / 'einsums.json'
        if not path.exists():
            raise SystemExit(f'{name}: {path} missing; run export.py {name} first')
        einsums = [(e['name'], {t: tuple(d) for t, d in e['operand_dims'].items()},
                    e['output']) for e in json.loads(path.read_text())['einsums']]
    if case.get('einsums'):
        einsums = [e for e in einsums if e[0] in case['einsums']]
    return einsums


def classify(operands, output):
    out_dims = set(operands[output])
    inputs = [set(d) for t, d in operands.items() if t != output]
    summed = set().union(*inputs) - out_dims
    if summed:
        shared = any(sum(d in i for i in inputs) >= 2 for d in summed)
        return 'contraction' if shared else 'reduction'
    if inputs and not any(out_dims <= i for i in inputs):
        return 'outer'
    return 'elementwise'


def to_dot(name, einsums, global_outputs=(), show_inputs=True, labels=True):
    producer = {out: ename for ename, _, out in einsums}
    consumed = {t for _, ops, out in einsums for t in ops if t != out}
    q = json.dumps  # DOT accepts JSON-style quoted strings
    lbl = (lambda s: q(s)) if labels else (lambda s: '""')
    lines = [f'digraph {q(name)} {{', '  rankdir=TB; nodesep=0.3; ranksep=0.4;',
             f'  labelloc=t; label={lbl(name)}; fontname="Helvetica";',
             '  node [fontname="Helvetica", fontsize=11, style=filled, penwidth=1.2];',
             '  edge [fontname="Helvetica", fontsize=9, color="#555555"];']
    for ename, ops, out in einsums:
        kind = classify(ops, out)
        shape, fill = SHAPES[kind]
        extra = ', peripheries=2' if out in global_outputs or out not in consumed else ''
        size = (', width=1.0, height=0.8' if shape in ('triangle', 'invtriangle') else '') \
            if labels else ', width=0.45, height=0.45, fixedsize=true'
        tip = f'{out}[{", ".join(ops[out])}] = ' + ' * '.join(
            f'{t}[{", ".join(d)}]' for t, d in ops.items() if t != out)
        lines.append(f'  {q("e:" + ename)} [label={lbl(ename)}, shape={shape}, '
                     f'fillcolor={q(fill)}, tooltip={q(tip + "  (" + kind + ")")}{size}{extra}];')
    for ename, ops, out in einsums:
        for t in ops:
            if t == out:
                continue
            if t in producer:
                lines.append(f'  {q("e:" + producer[t])} -> {q("e:" + ename)} [label={lbl(t)}];')
            elif show_inputs:
                lines.append(f'  {q("t:" + t)} [label={q(t)}, shape=plaintext, style="", '
                             'fontcolor="#666666", fontsize=10];' if labels else
                             f'  {q("t:" + t)} [label="", shape=point, width=0.08, '
                             'color="#999999"];')
                lines.append(f'  {q("t:" + t)} -> {q("e:" + ename)} [color="#bbbbbb"];')
    lines.append('}')
    return '\n'.join(dict.fromkeys(lines))  # drop repeated input-node lines


HTML = '''<!doctype html><meta charset="utf-8"><title>{name}</title>
<style>body{{margin:16px;font-family:sans-serif;background:#fff}}svg{{max-width:100%;height:auto}}</style>
<div id="g">Rendering…</div>
<script src="https://cdn.jsdelivr.net/npm/@viz-js/viz@3.11.0/lib/viz-standalone.js"></script>
<script>Viz.instance().then(v => {{ const g = document.getElementById('g');
g.replaceChildren(v.renderSVGElement({dot})); }});</script>
'''


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('cases', nargs='*', metavar='CASE', help='default: all cases')
    p.add_argument('--out', default=str(HERE / 'results' / 'graphs'))
    p.add_argument('--format', default='svg', choices=['svg', 'png', 'pdf'])
    p.add_argument('--no-inputs', action='store_true', help='hide workload input tensors')
    p.add_argument('--no-labels', action='store_true',
                   help='no node or edge labels: just the shape of the graph')
    args = p.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    dot = shutil.which('dot')
    for name in args.cases or CASES:
        case = CASES[name]
        try:
            einsums = load_einsums(name, case)
        except SystemExit as e:
            print(e)
            continue
        src = to_dot(name, einsums, case.get('global_outputs', ()), not args.no_inputs,
                     not args.no_labels)
        (out / f'{name}.dot').write_text(src)
        if dot:
            target = out / f'{name}.{args.format}'
            subprocess.run([dot, f'-T{args.format}', '-o', target, out / f'{name}.dot'],
                           check=True)
        else:
            target = out / f'{name}.html'
            target.write_text(HTML.format(name=name, dot=json.dumps(src)))
        print(f'{name}: {len(einsums)} einsums -> {target}')


if __name__ == '__main__':
    main()
