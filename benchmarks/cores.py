'''Run the DAG scheduler with compute costs on some workloads with 1 and with
8 hardware cores (the scheduler's num_cores: parallel units that split loops
across cores), each with the same time limit, and report the schedules. No
FFM comparison.

Usage:
    python cores.py [--time-limit S] [--cores 1,8] [--threads N] [--no-hint]
                    [--force] [CASE ...]
Default cases: swiglu, kda_batched, gdn_decode, siso_k128, gqa_llama3_8b,
kimi_k3_mla; default limit 1800 s per run (up to 6 hours for all twelve runs).

The workloads are this repository's Python descriptions, with their
compute_cost, accel_gran and operation (compute_workloads.py), not the
compute-free AccelForge exports of the FFM comparison. The objective is then
the scheduler's 5 x max(compute, traffic) + compute + traffic. Settings are
otherwise dag.py's; CP-SAT gets --threads workers (default: all available
cores) whatever num_cores is.

Writes results/<case>/compute_cores<N>.{json,txt} (separate from the FFM
comparison's dag*.json; existing results are kept unless --force) and
results/compute_cores_report.md: a table of every run, then each run's loop
nest. Traffic and compute are per core (what each core moves off-chip, and
its compute time), so both fall roughly with the core count.'''
import argparse

from common import RESULTS, available_cores, load, result_path
from compute_workloads import WORKLOADS
import dag

DEFAULT_CASES = ['swiglu', 'kda_batched', 'gdn_decode', 'siso_k128', 'gqa_llama3_8b',
                 'kimi_k3_mla']
REPORT = RESULTS / 'compute_cores_report.md'


def stem(n):
    return f'compute_cores{n}'


def loop_nest(case, n):
    '''The schedule's loop nest from the run's text output.'''
    text = result_path(case, stem(n) + '.txt').read_text()
    marker = '=== Synthesized Loop Nest ==='
    return text[text.index(marker) + len(marker):].strip() if marker in text else text.strip()


def num(v):
    return '' if v is None else f'{v:.0f}'


def report(cases, cores):
    rows, nests = [], []
    for case in cases:
        for n in cores:
            r = load(result_path(case, stem(n) + '.json'))
            if r is None:
                continue
            if r.get('objective_at_limit') is None:
                state = 'no solution by limit' if r['status'] in ('OPTIMAL', 'FEASIBLE') \
                    else r['status']
            elif r['proved_optimal_by_limit']:
                state = 'optimal'
            elif r['status'] == 'OPTIMAL':
                state = 'optimal (proved after limit)'
            else:
                state = f"feasible (objective bound {r['objective_bound']:.0f})"
            rows.append(f"| {case} | {n} | {num(r.get('objective_at_limit'))} | "
                        f"{num(r.get('traffic_at_limit'))} | {num(r.get('compute_at_limit'))} | "
                        f"{state} | {r['wall_s']:.1f} | {r['time_limit_s']:.0f} | "
                        f"{r['machine']['threads']} |")
            nests += [f'## {case}, {n} core{"s" * (n > 1)}', '',
                      f"{state}; objective {num(r.get('objective_at_limit'))}, traffic per "
                      f"core {num(r.get('traffic_at_limit'))}, compute per core "
                      f"{num(r.get('compute_at_limit'))}; fused {r.get('fused')}",
                      '', '```', loop_nest(case, n), '```', '']
    out = ['# DAG scheduler with compute costs at different core counts', '',
           "- `cores`: the scheduler's `num_cores` (hardware cores the schedule may split "
           "loops across, as `par` loops). `threads`: CP-SAT workers.",
           "- Workloads from this repository's Python descriptions, with compute costs "
           "(compute_workloads.py). Objective: 5 x max(compute, traffic) + compute + "
           'traffic, with traffic (off-chip elements read + written) and compute per core.',
           '', '| case | cores | objective | traffic per core | compute per core | status | '
           'wall s | limit s | threads |', '|---|---|---|---|---|---|---|---|---|',
           *rows, '', *nests]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(out) + '\n')
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog='\n\n'.join(__doc__.split('\n\n')[1:]))
    p.add_argument('cases', nargs='*', metavar='CASE',
                   help=f'cases (default: {" ".join(DEFAULT_CASES)}; any of '
                        f'{", ".join(WORKLOADS)})')
    p.add_argument('--time-limit', type=float, default=1800,
                   help='seconds per run, for every core count (default 1800)')
    p.add_argument('--cores', default='1,8', help='comma-separated core counts (default 1,8)')
    p.add_argument('--threads', type=int, default=available_cores(),
                   help='CP-SAT workers (default: all available cores)')
    p.add_argument('--no-hint', action='store_true',
                   help='do not hint CP-SAT with single-einsum tilings')
    p.add_argument('--force', action='store_true', help='rerun runs whose results exist')
    args = p.parse_args()
    cases = args.cases or DEFAULT_CASES
    unknown = [c for c in cases if c not in WORKLOADS]
    if unknown:
        p.error(f'unknown cases {unknown}; choose from {", ".join(WORKLOADS)}')
    cores = [int(n) for n in args.cores.split(',')]
    for case in cases:
        for n in cores:
            if not args.force and result_path(case, stem(n) + '.json').exists():
                print(f'{case} ({stem(n)}): already done, skipping (--force to rerun)')
                continue
            dag.run(case, args.time_limit, args.threads, not args.no_hint, False,
                    num_cores=n, stem=stem(n), compare_ffm=False, workload=WORKLOADS[case]())
    print('\n'.join(report(cases, cores)))
    print(f'Written to {REPORT}')


if __name__ == '__main__':
    main()
