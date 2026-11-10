'''Summarize the results of every case that has them into results/summary.md
(also printed).

Usage: python summarize.py

Traffic is off-chip elements read plus written; "/ FFM" below 1 means the
DAG scheduler moves less data than FFM.'''
from common import RESULTS, load
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


def mb(r):
    '''A result's peak memory in MB, or '' if not measured.'''
    return f"{r['peak_memory']['mb']:.0f}" if r and r.get('peak_memory') else ''


def seconds(v):
    return '' if v is None else f'{v:.1f}'


def main():
    rows, machines, notes, memory = [], {}, [], False
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
        rows.append([name, f"{(f or d or c)['capacity']}",
                     seconds(f and f['wall_s']), f'{ffm:.0f}' if ffm else '',
                     ratio(d, 'traffic_at_limit', ffm), status(d), seconds(d and d['wall_s']),
                     seconds(d and d.get('t_le_ffm_s')),
                     ratio(c, 'traffic_at_limit', ffm), status(c),
                     seconds(c and c.get('t_le_ffm_s')), mb(f), mb(d), mb(c)])
        memory = memory or any(map(mb, (f, d, c)))
        for tool, r in (('DAG', d), ('DAG capped', c)):
            for v in (r or {}).get('invalid_reduction_loops', []):
                notes.append(f'- **{name} {tool}: invalid schedule:** {v}')
        if f and not f['eval_in_detail']:
            notes.append(f"- {name}: FFM's detailed evaluation failed ({f['detail_error']}); "
                         "its traffic and time are the search's own.")
    head = ['case', 'capacity', 'FFM s', 'FFM traffic', 'DAG / FFM', 'DAG status', 'DAG s',
            'DAG s to <= FFM', 'capped DAG / FFM', 'capped status', 'capped s to <= FFM',
            'FFM MB', 'DAG MB', 'capped MB']
    if not memory:  # no result has peak memory: leave the columns out
        head, rows = head[:-3], [r[:-3] for r in rows]
    out = ['# DAG scheduler vs. FFM (O3) on snowcat', '',
           "- Traffic: off-chip elements read + written. `/ FFM` below 1: the DAG scheduler "
           "moves less data. `DAG`: fixed time limit; `capped`: limited to FFM's time on the "
           "case. Times include model building and hint tiling; `s to <= FFM`: when the DAG "
           "scheduler first matched FFM's traffic.",
           "- `bound`: CP-SAT's lower bound on traffic, over FFM's.",
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
