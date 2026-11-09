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
the same time. Timed results are only comparable within one machine.'''
import argparse, subprocess, sys

from common import HERE, available_cores, result_path
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

    common = ['--threads', str(args.threads)] + ['--force'] * args.force
    hint = ['--no-hint'] * args.no_hint
    commands = {
        'export': lambda c: ['export.py', c],
        'ffm': lambda c: ['ffm.py', *common, c],
        'dag': lambda c: ['dag.py', '--time-limit', str(args.dag_time_limit), *common, *hint, c],
        'capped': lambda c: ['dag.py', '--cap-at-ffm', *common, *hint, c],
    }
    failed = []
    for case in args.cases or CASES:
        for step in steps:
            if step == 'export' and result_path(case, 'einsums.json').exists() and not args.force:
                continue
            print(f'== {case}: {step}', flush=True)
            r = subprocess.run([sys.executable, *commands[step](case)], cwd=HERE)
            if r.returncode:
                print(f'== {case}: {step} FAILED (exit {r.returncode})', flush=True)
                failed.append(f'{case} {step}')
                if step == 'export':
                    break
    print()
    summarize.main()
    if failed:
        print('\nFailed steps: ' + ', '.join(failed))
        sys.exit(1)


if __name__ == '__main__':
    main()
