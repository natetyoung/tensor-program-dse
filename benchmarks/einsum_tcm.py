'''Run TCM (AccelForge's FFM mapper, default optimization level O3) on
single-einsum cases (einsum_cases.py) on TPU-v4i.

Usage: python einsum_tcm.py [--threads N] [--force] EINSUM ...
Writes results/<einsum>/tcm.{json,txt} (an existing tcm.json is kept unless
--force).

The spec (spec_for, shared with einsum_cpsat.py's evaluation) is AccelForge's
tpu_v4i arch with the constraints of the TCM paper's artifact (qk_spec()):
the PE array and the LocalBuffer's fanout need not be fully used, the
LocalBuffer keeps the input and output and may multicast anything, the
GlobalBuffer keeps the input and output and may keep the weight, and
MainMemory keeps everything. Metrics are energy and latency.

As in ffm.py, the reported time is the mapping search alone, after an
untimed warm-up search; the chosen mapping (the lowest-EDP one) is then
evaluated in detail, untimed.'''
import argparse, logging

import accelforge as af

from common import available_cores, machine_info, result_path, save
from einsum_cases import EINSUM_CASES
from export import workload_yaml
from ffm import evaluate_in_detail, search, tree_lines, warm_up


def spec_for(case):
    spec = af.Spec.from_yaml(af.examples.arches.tpu_v4i, workload_yaml(case),
                             jinja_parse_data=case['jinja'])
    spec.arch['ProcessingElement'].spatial['reuse_input'].min_usage = 0
    spec.arch['ProcessingElement'].spatial['reuse_output'].min_usage = 0
    spec.arch['LocalBuffer'].tensors.keep = 'input | output'
    spec.arch['LocalBuffer'].spatial['Z'].may_reuse = 'All'
    spec.arch['LocalBuffer'].spatial['Z'].min_usage = 0
    spec.arch['GlobalBuffer'].tensors.keep = 'input | output'
    spec.arch['GlobalBuffer'].tensors.may_keep = 'All'
    spec.arch['MainMemory'].tensors.keep = 'All'
    spec.mapper.metrics = af.Metrics.ENERGY | af.Metrics.LATENCY
    return spec


def breakdown(result):
    '''Energy per (component, tensor, action) and latency per component.'''
    energy = {'/'.join(map(str, k)): float(v) for k, v in result.energy(
        per_component=True, per_tensor=True, per_action=True).items() if v}
    latency = {k: float(v) for k, v in result.latency(per_component=True).items()}
    return energy, latency


def run(name, threads):
    af.set_n_parallel_jobs(threads)
    spec = spec_for(EINSUM_CASES[name])
    result, wall = search(spec, [name])
    # the search returns the energy-latency Pareto front; keep the lowest EDP
    edp = result.data['Total<SEP>energy'] * result.data['Total<SEP>latency']
    result.data = result.data.iloc[[int(edp.to_numpy().argmin())]]
    evaluate_in_detail(spec, result)
    energy, latency = float(result.energy()), float(result.latency())
    energy_parts, latency_parts = breakdown(result)
    save(result_path(name, 'tcm.json'), {
        'case': name, 'tool': 'tcm', 'optimization_level': 'O3 (default)', 'wall_s': wall,
        'pareto_mappings': len(edp), 'energy_J': energy, 'latency_s': latency,
        'edp_Js': energy * latency, 'energy_parts_J': energy_parts,
        'latency_parts_s': latency_parts, 'machine': machine_info(threads)})
    result_path(name, 'tcm.txt').write_text('\n'.join(
        [f'# {name} (TCM): wall {wall:.2f} s, {threads} processes',
         *tree_lines(result.mapping()),
         f'Energy by component/tensor/action (J): {energy_parts}',
         f'Latency by component (s): {latency_parts}',
         f'Energy {energy} J, latency {latency} s, EDP {energy * latency} J*s']) + '\n')
    print(f'{name} (TCM): {wall:.1f} s, EDP {energy * latency:.6g} J*s', flush=True)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--threads', type=int, default=available_cores(),
                   help='FFM worker processes (default: all available cores)')
    p.add_argument('--force', action='store_true', help='rerun even if tcm.json exists')
    p.add_argument('einsums', nargs='+', choices=EINSUM_CASES, metavar='EINSUM')
    args = p.parse_args()
    todo = [n for n in args.einsums if args.force or not result_path(n, 'tcm.json').exists()]
    for name in sorted(set(args.einsums) - set(todo)):
        print(f'{name} (TCM): already done, skipping (--force to rerun)')
    if todo:
        warm_up(args.threads)
    for name in todo:
        run(name, args.threads)
