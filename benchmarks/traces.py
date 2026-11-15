'''Collect the DAG scheduler's solution traces, normalized to FFM, so every
case can be plotted on one graph.

Usage:
    python traces.py [options] [CASE ...]      (default: every case with results)

For each case with results/<case>/ffm.json, reads the trace of each DAG run
(dag.json, and dag_capped.json for the run capped at FFM's time). A trace
has one entry per improving solution CP-SAT found: (seconds since the run
started, traffic, compute, objective). Each entry becomes one row with
    t_rel       = seconds / FFM's wall_s
    traffic_rel = traffic / FFM's traffic
so (1, 1) is where FFM finishes; a point left of x = 1 is found sooner than
FFM finishes, and below y = 1 is less traffic than FFM's.

Times start when dag.py starts the run, so they include building the model,
as FFM's wall_s includes its whole search. Each run also gets a final row
(point = "end") at its wall_s with its last traffic, so a step plot of a
run's rows extends to where the run stopped.

Writes results/traces.csv (--out). With --plot PATH, also draws every trace
(needs matplotlib).'''
import argparse, csv, sys

from common import RESULTS, load

RUNS = {'dag': 'dag.json', 'capped': 'dag_capped.json'}
COLUMNS = ['case', 'run', 'point', 't_s', 'traffic', 'ffm_wall_s', 'ffm_traffic',
           't_rel', 'traffic_rel', 'status']


def case_rows(case, runs):
    '''The normalized trace rows of case's runs, and a list of warnings.'''
    ffm = load(RESULTS / case / 'ffm.json')
    if ffm is None:
        return [], [f'{case}: no ffm.json; skipped']
    if not ffm.get('traffic') or not ffm.get('wall_s'):
        return [], [f"{case}: FFM's traffic or wall_s is 0 or missing; skipped"]
    rows, notes = [], []
    for run in runs:
        r = load(RESULTS / case / RUNS[run])
        if r is None:
            continue
        if not r.get('trace'):
            notes.append(f"{case} {run}: no trace (status {r.get('status')}); skipped")
            continue
        if any(r.get('compute_costs') or ()):
            notes.append(f'{case} {run}: has compute costs; traffic is only part of '
                         'what it minimized')
        points = [('solution', t, traffic) for t, traffic, *_ in r['trace']]
        points.append(('end', max(r['wall_s'], points[-1][1]), points[-1][2]))
        for point, t, traffic in points:
            rows.append({'case': case, 'run': run, 'point': point, 't_s': t,
                         'traffic': traffic, 'ffm_wall_s': ffm['wall_s'],
                         'ffm_traffic': ffm['traffic'], 't_rel': t / ffm['wall_s'],
                         'traffic_rel': traffic / ffm['traffic'],
                         'status': r.get('status')})
    return rows, notes


def plot(rows, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    runs = [run for run in RUNS if any(r['run'] == run for r in rows)]
    fig, axes = plt.subplots(1, len(runs), figsize=(6.5 * len(runs), 5), squeeze=False,
                             sharey=True)
    cases = sorted({r['case'] for r in rows})
    colors = {c: plt.cm.tab20(i % 20) for i, c in enumerate(cases)}
    for ax, run in zip(axes[0], runs):
        for case in cases:
            pts = [r for r in rows if r['case'] == case and r['run'] == run]
            if not pts:
                continue
            x = [p['t_rel'] for p in pts]
            y = [p['traffic_rel'] for p in pts]
            ax.step(x, y, where='post', color=colors[case], lw=1.2, label=case)
            sol = [p for p in pts if p['point'] == 'solution']
            ax.plot([p['t_rel'] for p in sol], [p['traffic_rel'] for p in sol], '.',
                    color=colors[case], ms=4)
        ax.axhline(1, color='gray', ls='--', lw=0.8)
        ax.axvline(1, color='gray', ls='--', lw=0.8)
        ax.plot([1], [1], 'k*', ms=10, label='FFM')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel("time / FFM's time")
        ax.set_title({'dag': 'DAG, fixed limit', 'capped': "DAG, capped at FFM's time"}[run])
    axes[0][0].set_ylabel("off-chip traffic / FFM's traffic")
    axes[0][-1].legend(fontsize=7, loc='center left', bbox_to_anchor=(1.01, 0.5))
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches='tight')


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog='\n\n'.join(__doc__.split('\n\n')[1:]))
    p.add_argument('cases', nargs='*', metavar='CASE',
                   help='cases to collect (default: every case with an ffm.json)')
    p.add_argument('--runs', default=','.join(RUNS),
                   help=f'comma-separated subset of {",".join(RUNS)} (default: all)')
    p.add_argument('--out', default=str(RESULTS / 'traces.csv'),
                   help='CSV to write (default: results/traces.csv)')
    p.add_argument('--plot', metavar='PATH', help='also plot the traces to PATH (e.g. .png)')
    args = p.parse_args()
    runs = args.runs.split(',')
    if not set(runs) <= set(RUNS):
        p.error(f'--runs must be a subset of {list(RUNS)}')
    cases = args.cases or sorted(d.name for d in RESULTS.iterdir()
                                 if (d / 'ffm.json').exists())

    rows = []
    for case in cases:
        case_r, notes = case_rows(case, runs)
        rows += case_r
        for n in notes:
            print(n, file=sys.stderr)
    with open(args.out, 'w', newline='') as f:
        w = csv.DictWriter(f, COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows from {len({(r['case'], r['run']) for r in rows})} runs "
          f'-> {args.out}')
    if args.plot:
        plot(rows, args.plot)
        print(f'plot -> {args.plot}')


if __name__ == '__main__':
    main()
