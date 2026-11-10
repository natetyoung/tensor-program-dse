'''Run the whole DAG-scheduler-vs-FFM comparison for some cases, then write
results/summary.md.

Usage:
    python run.py [options] [CASE ...]      (default: all cases)
    python run.py --list

For each case, in order: export its einsums (export.py), run FFM (ffm.py),
run the DAG scheduler with a fixed time limit (dag.py), and run it again
capped at FFM's time (dag.py --cap-at-ffm). Each step runs in its own
process, so one failing (e.g. FFM running out of memory) does not stop the
others. Steps whose results exist are skipped unless --force.

FFM and CP-SAT get the same number of threads (--threads, default: every
available core), so the capped comparison gives both the same machine for
the same time. Timed results are only comparable within one machine.

With --measure-memory, each ffm/dag/capped step runs in its own systemd scope
and its whole process tree's peak memory is added to its result
(peak_memory; see common.run_step).'''
import argparse, sys

from common import available_cores, check_memory_measurement, result_path, run_step
from cases import CASES
import summarize

STEPS = ['export', 'ffm', 'dag', 'capped']


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog='\n\n'.join(__doc__.split('\n\n')[1:]))
    p.add_argument('cases', nargs='*', metavar='CASE', help='cases to run (default: all)')
    p.add_argument('--list', action='store_true', help='list the cases and exit')
    p.add_argument('--steps', default=','.join(STEPS),
                   help=f'comma-separated subset of {",".join(STEPS)} (default: all)')
    p.add_argument('--threads', type=int, default=available_cores(),
                   help='FFM processes and CP-SAT workers (default: all available cores, '
                        f'{available_cores()} here). Fewer FFM processes use less memory.')
    p.add_argument('--dag-time-limit', type=float, default=600,
                   help="seconds for the DAG scheduler's fixed-limit run (default 600)")
    p.add_argument('--no-hint', action='store_true',
                   help='do not hint CP-SAT with single-einsum tilings')
    p.add_argument('--force', action='store_true', help='rerun steps whose results exist')
    p.add_argument('--measure-memory', action='store_true',
                   help="record each step's peak memory (needs a systemd user session "
                        'with cgroup v2 memory accounting)')
    args = p.parse_args()
    if args.list:
        for name, c in CASES.items():
            print(f"{name:24s} {c['workload']:40s} capacity {c['capacity']}")
        return
    unknown = [c for c in args.cases if c not in CASES]
    if unknown:
        p.error(f'unknown cases {unknown}; see --list')
    steps = args.steps.split(',')
    if not set(steps) <= set(STEPS):
        p.error(f'--steps must be a subset of {STEPS}')
    if args.measure_memory and (why := check_memory_measurement()):
        p.error(f'--measure-memory: {why}')

    common = ['--threads', str(args.threads)] + ['--force'] * args.force
    hint = ['--no-hint'] * args.no_hint
    commands = {
        'export': lambda c: ['export.py', c],
        'ffm': lambda c: ['ffm.py', *common, c],
        'dag': lambda c: ['dag.py', '--time-limit', str(args.dag_time_limit), *common, *hint, c],
        'capped': lambda c: ['dag.py', '--cap-at-ffm', *common, *hint, c],
    }
    results = {'ffm': 'ffm.json', 'dag': 'dag.json', 'capped': 'dag_capped.json'}
    failed = []
    for case in args.cases or CASES:
        for step in steps:
            if step == 'export' and result_path(case, 'einsums.json').exists() and not args.force:
                continue
            print(f'== {case}: {step}', flush=True)
            code, mem = run_step(commands[step](case),
                                 result_path(case, results[step]) if step in results else None,
                                 args.measure_memory and step in results)
            if code:
                peak = f", peak memory {mem['mb']:.0f} MB" if mem else ''
                oom = ', OOM-killed' if mem and mem['oom_kills'] else ''
                print(f'== {case}: {step} FAILED (exit {code}{oom}{peak})', flush=True)
                failed.append(f'{case} {step}{oom}{peak}')
                if step == 'export':
                    break
    print()
    summarize.main()
    if failed:
        print('\nFailed steps: ' + ', '.join(failed))
        sys.exit(1)


if __name__ == '__main__':
    main()
