'''Summarize the results of every case that has them into results/summary.md
(also printed).

Usage: python summarize.py

Traffic is off-chip elements read plus written; "/ FFM" below 1 means the
DAG scheduler moves less data than FFM.

The capped columns are derived from the fixed-limit DAG run (dag.json): what
its traces show it had reached by FFM's time (common.at_time). Cases with a
measured capped run (dag_capped.json, from dag.py --cap-at-ffm) also get
"measured" columns.'''
from common import RESULTS, at_time, load
from cases import CASES


def ratio(d, key, ffm):
    v = d.get(key) if d else None
    return f'{v / ffm:.3f}' if v is not None and ffm else ''


def status(d):
    if d is None:
        return ''
    if d.get('traffic_at_limit') is None:
        return 'no solution by limit' if d['status'] in ('OPTIMAL', 'FEASIBLE') else d['status']
    if d['proved_optimal_by_limit']:
        return 'optimal'
    if d['status'] == 'OPTIMAL':
        return 'optimal (proved after limit)'
    return f"feasible (bound {d['bound'] / d['ffm_traffic']:.3f})" if d.get('ffm_traffic') \
        else 'feasible'


def derived_status(d, a, ffm):
    '''Status of DAG run d as of FFM's time, from a = at_time(d, FFM's time).'''
    if d is None:
        return ''
    if a is None:
        return 'unknown (DAG limit < FFM time)' if d.get('trace') else d['status']
    if a['traffic'] is None:
        return 'no solution by limit'
    if a['proved']:
        return 'optimal'
    if a['proved_later']:
        return 'optimal (proved after limit)'
    return f"feasible (bound {a['bound'] / ffm:.3f})" if a['bound'] is not None and ffm \
        else 'feasible'


def mb(r):
    '''A result's peak memory in MB, or '' if not measured.'''
    return f"{r['peak_memory']['mb']:.0f}" if r and r.get('peak_memory') else ''


def seconds(v):
    return '' if v is None else f'{v:.1f}'


def main():
    rows, machines, notes, measured, memory = [], {}, [], False, False
    for name in CASES:
        f = load(RESULTS / name / 'ffm.json')
        d = load(RESULTS / name / 'dag.json')
        c = load(RESULTS / name / 'dag_capped.json')
        if not (f or d or c):
            continue
        for tool, r in (('FFM', f), ('DAG', d), ('DAG capped', c)):
            if r:
                m = r['machine']
                machines.setdefault(tuple(sorted((k, str(v)) for k, v in m.items())), []).append(
                    f'{name} {tool}')
        ffm = f and f['traffic']
        T = f and f['wall_s']
        a = at_time(d, T) if d and T else None
        t_le = d and d.get('t_le_ffm_s')
        rows.append([name, f"{(f or d or c)['capacity']}",
                     seconds(T), f'{ffm:.0f}' if ffm else '',
                     ratio(d, 'traffic_at_limit', ffm), status(d), seconds(d and d['wall_s']),
                     seconds(t_le),
                     ratio(a, 'traffic', ffm), derived_status(d, a, ffm) if f else '',
                     seconds(t_le if a and t_le is not None and t_le <= T else None),
                     ratio(c, 'traffic_at_limit', ffm), status(c),
                     mb(f), mb(d), mb(c)])
        measured = measured or c is not None
        memory = memory or any(map(mb, (f, d, c)))
        # A capped run gives the hint tilings a tenth of its limit (results
        # from before hint_s was recorded cannot be checked).
        if a and d.get('hint') and (d.get('hint_s') or 0) > 0.1 * T:
            notes.append(f"- {name}: the DAG run's hint tilings took {d['hint_s']:.2f} s, "
                         f"more than the {0.1 * T:.2f} s (a tenth of FFM's time) a capped run "
                         "gives them, so its derived capped numbers may be optimistic; "
                         "`dag.py --cap-at-ffm` measures them.")
        if a and d.get('hint_bound'):
            notes.append(f"- {name}: the DAG run used --hint-bound, whose hint completion a "
                         "capped run would get less time for; its derived capped numbers may "
                         "be optimistic.")
        if f and d and f['machine'].get('threads') != d['machine'].get('threads'):
            notes.append(f"- {name}: FFM ran with {f['machine'].get('threads')} processes, the "
                         f"DAG run with {d['machine'].get('threads')} workers, so the capped "
                         "columns do not compare like for like.")
        for tool, r in (('DAG', d), ('DAG capped', c)):
            for v in (r or {}).get('invalid_reduction_loops', []):
                notes.append(f'- **{name} {tool}: invalid schedule:** {v}')
        if f and not f['eval_in_detail']:
            notes.append(f"- {name}: FFM's detailed evaluation failed ({f['detail_error']}); "
                         "its traffic and time are the search's own.")
    head = ['case', 'capacity', 'FFM s', 'FFM traffic', 'DAG / FFM', 'DAG status', 'DAG s',
            'DAG s to <= FFM', 'capped DAG / FFM', 'capped status', 'capped s to <= FFM',
            'measured capped / FFM', 'measured capped status', 'FFM MB', 'DAG MB',
            'capped MB']
    keep = [h for h in head  # leave out the columns no result has
            if (measured or not h.startswith('measured'))
            and (memory or not h.endswith(' MB'))
            and (measured or h != 'capped MB')]
    rows = [[v for h, v in zip(head, r) if h in keep] for r in rows]
    head = keep
    out = ['# DAG scheduler vs. FFM (O3) on snowcat', '',
           "- Traffic: off-chip elements read + written. `/ FFM` below 1: the DAG scheduler "
           "moves less data. `DAG`: fixed time limit; `capped`: the fixed-limit run as of "
           "FFM's time on the case, from its traces (the same as a run capped at FFM's time, "
           "up to CP-SAT's run-to-run variation)"
           + ("; `measured capped`: a run actually capped at FFM's time (`dag.py "
              "--cap-at-ffm`)" if measured else '')
           + ". Times include model building and hint tiling; `s to <= FFM`: when the DAG "
           "scheduler first matched FFM's traffic.",
           "- `bound`: CP-SAT's lower bound on traffic, over FFM's. Derived capped bounds "
           "need a DAG run recorded with `bound_trace`; older runs show `feasible` alone.",
           *(['- `MB`: peak memory of the whole step (all processes, including imports, '
              "FFM's warm-up and detailed evaluation, and the DAG scheduler's hint tilings), "
              'from `run.py --measure-memory`; it grows with --threads.'] if memory else []),
           '',
           '| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    out += ['| ' + ' | '.join(r) + ' |' for r in rows]
    if notes:
        out += ['', '## Notes', ''] + notes
    out += ['', '## Machines', '']
    for m, runs in machines.items():
        out += ['- ' + ', '.join(f'{k} {v}' for k, v in m) + f' ({len(runs)} runs)']
    if len(machines) > 1:
        out += ['', 'Results come from different machines or settings; compare times only '
                'within one machine.']
    (RESULTS / 'summary.md').write_text('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
