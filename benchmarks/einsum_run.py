'''Run the single-einsum comparison of cb_einsum_ml_cpsat97 with TCM on
TPU-v4i for some einsums, then write results/einsum_summary.md.

Usage:
    python einsum_run.py [options] [EINSUM ...]   (default: all but SKIP_BY_DEFAULT)
    python einsum_run.py --list
    python einsum_run.py --summarize               (only rewrite the summary)

For each einsum: TCM (einsum_tcm.py), then CP-SAT (einsum_cpsat.py), each in
its own process, so one failing (e.g. TCM running out of memory) does not
stop the other. Steps whose results exist are skipped unless --force. Both
tools get the same number of threads (--threads).

With --measure-memory, each step runs in its own systemd scope and its whole
process tree's peak memory is added to its result (peak_memory; see
common.run_step).'''
import argparse, sys

from common import (RESULTS, available_cores, check_memory_measurement, load, result_path,
                    run_step)
from einsum_cases import EINSUM_CASES, SKIP_BY_DEFAULT

STEPS = {'tcm': 'einsum_tcm.py', 'cpsat': 'einsum_cpsat.py'}


def mb(r):
    '''A result's peak memory in MB, or '' if not measured.'''
    return f"{r['peak_memory']['mb']:.0f}" if r and r.get('peak_memory') else ''


def summarize():
    '''Write results/einsum_summary.md (also printed) from whatever results exist.'''
    rows, machines, memory = [], {}, False
    for name in EINSUM_CASES:
        t, c = load(RESULTS / name / 'tcm.json'), load(RESULTS / name / 'cpsat.json')
        if not (t or c):
            continue
        for r in (t, c):
            if r:
                key = ', '.join(f'{k} {v}' for k, v in sorted(r['machine'].items()))
                machines[key] = machines.get(key, 0) + 1
        ratio = c and t and c.get('edp_Js') and f"{c['edp_Js'] / t['edp_Js']:.4f}"
        rows.append([name, f"{t['wall_s']:.1f}" if t else '', f"{t['edp_Js']:.6g}" if t else '',
                     f"{c['wall_s']:.2f} ({c['status']})" if c else '', ratio or '',
                     mb(t), mb(c)])
        memory = memory or bool(mb(t) or mb(c))
    head = ['einsum', 'TCM s', 'TCM EDP (J*s)', 'CP-SAT s (status)', 'CP-SAT EDP / TCM',
            'TCM MB', 'CP-SAT MB']
    if not memory:  # no result has peak memory: leave the columns out
        head, rows = head[:-2], [r[:-2] for r in rows]
    out = ['# cb_einsum_ml vs. TCM (O3) on single einsums, TPU-v4i', '',
           '- Both EDPs are evaluated by AccelForge on the same spec; `CP-SAT EDP / TCM` '
           'of 1 means CP-SAT found a mapping as good as TCM\'s optimum.',
           "- Times: TCM's mapping search; CP-SAT's whole call (model building, solve, "
           'cross-check), with its status at the time limit.',
           '- Mappings: results/<einsum>/tcm.txt and cpsat.txt.',
           *(['- `MB`: peak memory of the whole step (all processes, including imports '
              "and TCM's warm-up and detailed evaluation), from `--measure-memory`; it "
              'grows with --threads.'] if memory else []), '',
           '| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    out += ['| ' + ' | '.join(r) + ' |' for r in rows]
    out += ['', '## Machines', ''] + [f'- {m} ({n} runs)' for m, n in machines.items()]
    if len(machines) > 1:
        out += ['', 'Results come from different machines or settings; compare times only '
                'within one machine.']
    (RESULTS / 'einsum_summary.md').write_text('\n'.join(out) + '\n')
    print('\n'.join(out))


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog='\n\n'.join(__doc__.split('\n\n')[1:]))
    p.add_argument('einsums', nargs='*', metavar='EINSUM',
                   help='einsums to run (default: all but ' + ', '.join(SKIP_BY_DEFAULT) + ')')
    p.add_argument('--list', action='store_true', help='list the einsums and exit')
    p.add_argument('--summarize', action='store_true', help='only rewrite the summary')
    p.add_argument('--steps', default=','.join(STEPS),
                   help=f'comma-separated subset of {",".join(STEPS)} (default: all)')
    p.add_argument('--threads', type=int, default=available_cores(),
                   help='TCM processes and CP-SAT workers (default: all available cores)')
    p.add_argument('--time-limit', type=float, default=120,
                   help="seconds for CP-SAT's search (default 120)")
    p.add_argument('--force', action='store_true', help='rerun steps whose results exist')
    p.add_argument('--measure-memory', action='store_true',
                   help="record each step's peak memory (needs a systemd user session "
                        'with cgroup v2 memory accounting)')
    args = p.parse_args()
    if args.list:
        for name, c in EINSUM_CASES.items():
            print(f"{name:12s} {c['workload']:40s} " + ' x '.join(
                f'{d} {n}' for d, n in c['dims'].items()))
        return
    if args.summarize:
        return summarize()
    unknown = [e for e in args.einsums if e not in EINSUM_CASES]
    if unknown:
        p.error(f'unknown einsums {unknown}; see --list')
    steps = args.steps.split(',')
    if not set(steps) <= set(STEPS):
        p.error(f'--steps must be a subset of {list(STEPS)}')
    if args.measure_memory and (why := check_memory_measurement()):
        p.error(f'--measure-memory: {why}')

    common = ['--threads', str(args.threads)] + ['--force'] * args.force
    extra = {'tcm': [], 'cpsat': ['--time-limit', str(args.time_limit)]}
    failed = []
    for name in args.einsums or [e for e in EINSUM_CASES if e not in SKIP_BY_DEFAULT]:
        for step in steps:
            print(f'== {name}: {step}', flush=True)
            code, mem = run_step([STEPS[step], *common, *extra[step], name],
                                 result_path(name, step + '.json'), args.measure_memory)
            if code:
                peak = f", peak memory {mem['mb']:.0f} MB" if mem else ''
                oom = ', OOM-killed' if mem and mem['oom_kills'] else ''
                print(f'== {name}: {step} FAILED (exit {code}{oom}{peak})', flush=True)
                failed.append(f'{name} {step}{oom}{peak}')
    print()
    summarize()
    if failed:
        print('\nFailed steps: ' + ', '.join(failed))
        sys.exit(1)


if __name__ == '__main__':
    main()
