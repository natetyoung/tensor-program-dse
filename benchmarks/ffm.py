'''Run AccelForge's FFM mapper (default optimization level, O3) on a case's
workload on the snowcat arch at the case's capacity.

Usage: python ffm.py [--threads N] [--force] CASE ...
Writes results/<case>/ffm.{json,txt} (an existing ffm.json is kept unless
--force). Exports the case's einsums first if needed.

Snowcat: MainMemory (1 J per bit read or written, so energy = off-chip bits)
above one GlobalBuffer that may keep every tensor, above a free MAC.
MainMemory keeps everything except intermediates, so an intermediate is
fused iff it never touches MainMemory. The GlobalBuffer's size is set to the
case's capacity in bits; with metrics = ENERGY alone FFM returns a single
minimum-traffic mapping.

The reported time is FFM's mapping search (map_workload_to_arch with
eval_in_detail=False), after an untimed warm-up search on a tiny workload
that absorbs the process's one-time start-up cost (about 3 s). The chosen mapping is then evaluated in detail, untimed,
for per-tensor traffic and buffer usage, as FFM's own eval_in_detail would
(minus its mapping.svg rendering, which needs Graphviz). If that evaluation
fails (it does on some workloads, e.g. kda_batched: "No mappings found for
..."), the search's own total is reported without the breakdown.'''
import argparse, copy, logging, os, tempfile, time, traceback

import accelforge as af
from accelforge.mapper.FFM.main import map_workload_to_arch
from accelforge.model.main import evaluate_mapping
from accelforge.util import _fillna_and__numeric_cast
from accelforge._accelerated_imports import pd
from accelforge.frontend.mapping.mapping import (Compute, Nested, Sequential, Spatial,
                                                 Storage, Temporal)

from common import available_cores, load, machine_info, result_path, save
from cases import CASES
from export import export, load_spec


def tree_lines(node, indent=0):
    '''The mapping tree, one node per line; loops show the tile after them.'''
    pad = ' ' * indent
    if isinstance(node, Temporal):
        return [pad + f'for {node.rank_variable} -> tile {node.tile_shape}']
    if isinstance(node, Spatial):
        return [pad + f'parfor {node.rank_variable} -> tile {node.tile_shape} '
                f'({node.component}.{node.name})']
    if isinstance(node, Storage):
        return [pad + f'store {", ".join(map(str, node.tensors))} @{node.component}']
    if isinstance(node, Compute):
        return [pad + f'compute {node.einsum}']
    if isinstance(node, Sequential):
        lines = [pad + 'sequential:']
        for child in node.nodes:
            lines += [pad + ' -'] + tree_lines(child, indent + 2)
        return lines
    if isinstance(node, Nested):
        return [l for child in node.nodes for l in tree_lines(child, indent)]
    return [pad + type(node).__name__]


# FFM may write files to the working directory, so searches run in this one.
# It lasts as long as the process: FFM's worker processes are reused across
# searches and keep the directory they started in as their working directory,
# so deleting it (as a per-search temporary directory would) makes any
# os.getcwd() in them fail (e.g. in numba's error formatting).
WORKDIR = tempfile.TemporaryDirectory()


def search(spec, einsum_names):
    '''FFM's mapping search: (result, wall s).'''
    cwd = os.getcwd()
    os.chdir(WORKDIR.name)
    try:
        t0 = time.perf_counter()
        result = map_workload_to_arch(spec, einsum_names=einsum_names,
                                      print_progress=False, eval_in_detail=False)
        return result, time.perf_counter() - t0
    finally:
        os.chdir(cwd)


def warm_up(threads):
    '''An untimed search on a tiny workload, so start-up costs (worker
    processes, compilation) are not charged to the first timed case.'''
    af.set_n_parallel_jobs(threads)
    spec = af.Spec.from_yaml(af.examples.arches.snowcat, af.examples.workloads.basic.matvecs)
    spec.arch.nodes['GlobalBuffer'].size = 8 * 32
    spec.mapper.metrics = af.Metrics.ENERGY
    search(spec, None)


def evaluate_in_detail(spec, result):
    '''What map_workload_to_arch(eval_in_detail=True) does after the search,
    without rendering the mapping: replace result.data with the detailed
    evaluation of the chosen mapping.'''
    local = copy.deepcopy(spec)
    local.model.metrics = local.mapper.info_metrics
    local.mapping = result.data.iloc[0]['Total<SEP>mapping'](_for_model=True)
    data = evaluate_mapping(local, flattened_arches=result.flattened_arches,
                            evaluated_specs=result.evaluated_specs).data
    result.data = _fillna_and__numeric_cast(pd.concat([data]), 0)


def run(name, threads):
    case = CASES[name]
    ex = load(result_path(name, 'einsums.json'))
    if ex is None:
        export(name)
        ex = load(result_path(name, 'einsums.json'))
    bpv = ex['bits_per_value']
    produced = {e['output'] for e in ex['einsums']}
    consumed = {t for e in ex['einsums'] for t in e['operand_dims'] if t != e['output']}
    intermediates = sorted(produced & consumed)

    af.set_n_parallel_jobs(threads)
    spec = load_spec(case)
    spec.arch.nodes['GlobalBuffer'].size = case['capacity'] * bpv
    spec.mapper.metrics = af.Metrics.ENERGY
    result, wall = search(spec, case['einsums'])
    mapping = result.mapping()
    search_traffic_bits = float(result.data.iloc[0]['Total<SEP>energy'])
    detail_error = None
    try:
        evaluate_in_detail(spec, result)
        detail = True
    except Exception:
        detail_error = traceback.format_exc(limit=1).strip().splitlines()[-1]
        print(f'{name}: FFM detailed evaluation failed ({detail_error}); '
              "reporting the search's total", flush=True)
        detail = False

    if detail:
        traffic_bits = float(result.energy())
        per_tensor = {}  # tensor -> {action: elements}
        for (t, action), v in result.energy(per_tensor=True, per_action=True).items():
            if t not in (None, 'None') and action in ('read', 'write'):
                per_tensor.setdefault(str(t), {})[action] = float(v) / bpv
        usage = float(result.resource_usage()['GlobalBuffer']) * case['capacity']
        in_main = {c.split('<SEP>')[-1] for c in result.data.columns
                   if '<SEP>usage<SEP>memory<SEP>MainMemory<SEP>' in c}
    else:  # the search keeps only the total and the mapping
        traffic_bits = search_traffic_bits
        per_tensor, usage = None, None
        in_main = {str(t) for n in mapping.get_nodes_of_type(Storage)
                   if n.component == 'MainMemory' for t in n.tensors}
    fused = [t for t in intermediates if t not in in_main]
    traffic = traffic_bits / bpv

    summary = {'case': name, 'tool': 'ffm', 'optimization_level': 'O3 (default)',
               'wall_s': wall, 'capacity': case['capacity'], 'bits_per_value': bpv,
               'traffic': traffic, 'glb_usage': usage, 'fused': fused,
               'intermediates': intermediates, 'per_tensor': per_tensor,
               'search_traffic': search_traffic_bits / bpv,
               'eval_in_detail': detail, 'detail_error': detail_error,
               'machine': machine_info(threads)}
    save(result_path(name, 'ffm.json'), summary)
    result_path(name, 'ffm.txt').write_text('\n'.join(
        [f'# {name} (FFM): wall {wall:.2f} s, {threads} processes', *tree_lines(mapping),
         f'Per tensor (elements): {per_tensor}',
         f'Fused intermediates: {fused} of {intermediates}',
         f'GlobalBuffer usage: {usage} of {case["capacity"]} elements',
         f'Off-chip traffic: {traffic:.0f} elements']) + '\n')
    print(f'{name} (FFM): {wall:.1f} s, traffic {traffic:.0f} elements, fused {fused}',
          flush=True)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--threads', type=int, default=available_cores(),
                   help='FFM worker processes (default: all available cores). Fewer '
                        'processes use less memory.')
    p.add_argument('--force', action='store_true', help='rerun even if ffm.json exists')
    p.add_argument('cases', nargs='+', choices=CASES, metavar='CASE')
    args = p.parse_args()
    todo = [n for n in args.cases if args.force or not result_path(n, 'ffm.json').exists()]
    for name in sorted(set(args.cases) - set(todo)):
        print(f'{name} (FFM): already done, skipping (--force to rerun)')
    if todo:
        warm_up(args.threads)
    for name in todo:
        run(name, args.threads)
