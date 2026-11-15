'''Ablation study of the DAG scheduler's optimality constraints
(general_dag_scheduler._build_optimality_constraints): how much each of its
five constraint families helps CP-SAT, on the FFM-comparison cases.

Usage:
    python ablation.py [options] [CASE ...]      (default: all cases)
    python ablation.py --list                     (cases and configurations)
    python ablation.py --dry-run [options] [CASE ...]
    python ablation.py --summarize                (only rewrite the summary)

The constraint families (general_dag_scheduler.OPTIMALITY_CONSTRAINTS):
    unused_temporal   temporal factor 1 for dims no operand at the node uses
    spatial_gran      spatial factor <= the max useful accelerator granularity
                      (1 here, as every case has compute_cost = 0)
    same_operand      no strict ancestry between copies of one tensor
    unfused_separate  with nothing fused, einsums share no ancestry
    no_empty_branch   a non-root anchor needs some factor > 1

Configurations (--configs, comma-separated):
    all          every family (the default scheduler, as in dag.py)
    none         no family (enforce_optimal_placement=False)
    no-<family>  every family but one (leave-one-out)
    only-<family> that family alone (add-one-in)
Default: all, none and the five leave-one-out configurations.

Each (case, seed, configuration) runs dag.py's run() in its own process, with
dag.py's settings (perfect factorization, partial sums, ...), so a crash or
memory blow-up stops only that run. For each case, the order is: every
configuration with seed 0, then every configuration with seed 1, and so on.
That way slow drift in the machine's state hits all configurations alike.
Multi-worker CP-SAT is nondeterministic even with a fixed seed, so use
several seeds (--seeds) and compare medians.

Writes results/<case>/ablation/<config>_s<seed>.{json,txt} (the same fields
as dag.json, plus model size and CP-SAT's conflicts, branches and
deterministic time), then results/ablation_summary.md. With --no-hint, the
runs go to results/<case>/ablation_nohint/ and the summary to
results/ablation_nohint_summary.md instead, so the two never mix. Existing runs are
skipped unless --force, so an interrupted study can be resumed. Needs
results/<case>/einsums.json, and runs export.py (which needs AccelForge)
for cases that lack it.'''
import argparse, statistics, sys
from math import exp, log

from common import (RESULTS, available_cores, check_memory_measurement, load, result_path,
                    run_step, save)
from cases import CASES
from general_dag_scheduler import OPTIMALITY_CONSTRAINTS

BASELINE = 'all'
DEFAULT_CONFIGS = [BASELINE, 'none'] + [f'no-{c}' for c in OPTIMALITY_CONSTRAINTS]
ALL_CONFIGS = DEFAULT_CONFIGS + [f'only-{c}' for c in OPTIMALITY_CONSTRAINTS]
SHIFT_S = 1.0  # shift of the shifted geometric mean of times


def enabled(config):
    '''The constraint families a configuration enables.'''
    if config == 'all':
        return list(OPTIMALITY_CONSTRAINTS)
    if config == 'none':
        return []
    kind, _, family = config.partition('-')
    if family not in OPTIMALITY_CONSTRAINTS or kind not in ('no', 'only'):
        raise ValueError(f'unknown configuration {config!r}; see --list')
    return ([c for c in OPTIMALITY_CONSTRAINTS if c != family] if kind == 'no' else [family])


def folder(hint):
    '''Where runs with or without hints go, under results/<case>/.'''
    return 'ablation' if hint else 'ablation_nohint'


def stem(config, seed, hint):
    return f'{folder(hint)}/{config}_s{seed}'


def path(case, config, seed, hint):
    return result_path(case, stem(config, seed, hint) + '.json')


def worker(case, config, seed, time_limit, threads, hint):
    '''One run, in this process (ablation.py runs itself with --worker).'''
    import dag
    result_path(case, folder(hint)).mkdir(exist_ok=True)
    fams = enabled(config)
    overrides = {'enforce_optimal_placement': bool(fams), 'optimality_constraints': fams}
    dag.run(case, time_limit, threads, hint, False, stem=stem(config, seed, hint),
            compare_ffm=False, seed=seed, overrides=overrides)
    r = load(path(case, config, seed, hint))
    r.update(ablation_config=config, constraints=fams)
    save(path(case, config, seed, hint), r)


# ── Summary ──────────────────────────────────────────────────────────────────

def solve_time(r):
    '''Seconds to prove optimality, or the time limit if not proved by then
    (so a timeout counts as the limit: a lower bound on its true time).'''
    if r.get('proved_optimal_by_limit'):
        return r['wall_s']
    return r['time_limit_s']


def traffic_at(r, t):
    '''Best traffic run r had found t seconds into the run (from its trace
    of improving solutions): inf if none yet, None if unknown (t is past the
    run's time limit and it did not prove optimality).'''
    if t > r['time_limit_s'] and not r.get('proved_optimal_by_limit'):
        return None
    found = [s[1] for s in r.get('trace') or [] if s[0] <= t]
    return found[-1] if found else float('inf')


def gap_at(r, t, ref):
    '''Percent by which r's best traffic at t exceeds ref (inf: no solution).'''
    x = traffic_at(r, t)
    if x is None or x == float('inf'):
        return x
    return 100 * (x - ref) / ref if ref else (0.0 if x == 0 else float('inf'))


def time_to_target(r, ref, target):
    '''Seconds until r first found traffic within target percent of ref, or
    None if it never did within its limit.'''
    return next((s[0] for s in r.get('trace') or []
                 if s[0] <= r['time_limit_s'] and s[1] <= ref * (1 + target / 100)), None)


def target_time(rs, ref, target):
    '''Median over runs rs of time_to_target, counting a run that never got
    there as its time limit; and whether the median rests on such a run (so
    the true median is at least the value shown).'''
    vals = sorted((r['time_limit_s'], True) if t is None else (t, False)
                  for r in rs for t in [time_to_target(r, ref, target)])
    n = len(vals)
    middle = vals[(n - 1) // 2:n // 2 + 1]
    return statistics.median(v for v, _ in vals), any(miss for _, miss in middle)


def med_gap(rs, t, ref):
    '''Median over runs rs of gap_at; None (unknown) if any run's is unknown,
    so runs with known values cannot stand in for the rest.'''
    gaps = [gap_at(r, t, ref) for r in rs]
    return None if None in gaps else statistics.median(gaps)


def fmt_gap(g):
    if g is None:
        return '-'
    return 'no sol.' if g == float('inf') else f'{g:.2f}'


def references(runs):
    '''Per case, the reference traffic for solution quality: the least
    traffic any ablation run of the case found, and whether some run proved
    it optimal.'''
    ref = {}
    for case, by in runs.items():
        rs = [r for v in by.values() for r in v if r.get('traffic') is not None]
        if rs:
            best = min(r['traffic'] for r in rs)
            ref[case] = (best, any(r['status'] == 'OPTIMAL' and r['traffic'] == best
                                   for r in rs))
    return ref


def sgm(xs, shift=SHIFT_S):
    '''Shifted geometric mean, the usual average of solver times.'''
    return exp(sum(log(x + shift) for x in xs) / len(xs)) - shift


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def fmt(x, digits=1):
    if x is None:
        return '-'
    if isinstance(x, float) and not x.is_integer():
        return f'{x:,.{digits}f}'
    return f'{int(x):,}'


def summarize(checkpoints=(10, 60, 300), target=1.0, hint=True):
    '''Write results/ablation_summary.md (ablation_nohint_summary.md for the
    runs without hints). checkpoints: seconds at which to
    report solution quality; target: percent above the reference traffic
    counted as a good solution for the time-to-target columns.'''
    runs = {}  # case -> config -> [result]
    for f in sorted(RESULTS.glob(f'*/{folder(hint)}/*.json')):
        r = load(f)
        if r and 'ablation_config' in r:
            runs.setdefault(r['case'], {}).setdefault(r['ablation_config'], []).append(r)
    if not runs:
        print('no ablation results yet')
        return
    configs = [c for c in ALL_CONFIGS if any(c in v for v in runs.values())]
    limits = sorted({r['time_limit_s'] for v in runs.values() for rs in v.values() for r in rs})
    hints = sorted({r['hint'] for v in runs.values() for rs in v.values() for r in rs})
    threads = sorted({r['machine']['threads'] for v in runs.values() for rs in v.values()
                      for r in rs})

    out = ['# Ablation of the optimality constraints', '',
           f'- Configurations: `all` is every constraint family (the default scheduler), '
           f'`none` none of them, `no-X` all but X, `only-X` X alone.',
           f"- `solve s`: median over seeds of the seconds to prove optimality (model build, "
           f"hint tiling and search), counting a run that did not prove it as the time limit. "
           f"`vs all`: that over `all`'s; above 1, the configuration is slower.",
           f'- `traffic`: median best traffic found within the limit; `bound`: best (highest) '
           f'proven lower bound on traffic over the seeds.',
           f'- `conflicts`, `det. s`: medians of CP-SAT\'s conflicts and deterministic time '
           f'(less noisy than wall time). `vars`, `cons`: model size.',
           f'- Solution quality is measured against each case\'s reference: the least '
           f'traffic any ablation run of the case found (so it can change as runs are added). '
           f'`gap @ t`: median over seeds of the percent by which the best traffic found '
           f'within t seconds (counting model build and hint tiling) exceeds the reference; '
           f'`no sol.`: no solution yet; `-`: t is past the time limit of some run that did not prove optimality. `t to {target:g}%`: '
           f'median seconds to first get within {target:g}% of the reference, counting a run '
           f'that never did as the time limit (shown as `>limit`).',
           f'- Time limits: {", ".join(fmt(l) for l in limits)} s; hints: {hints}; '
           f'CP-SAT workers: {threads}.', '']
    ref = references(runs)

    # Overview: one row per configuration, over cases every shown config has.
    common = [c for c in runs if all(cfg in runs[c] for cfg in configs)]
    out += ['## Overview', '',
            f'Over the {len(common)} cases with results for every configuration '
            f'({", ".join(common) or "none"}). `SGM solve s`: shifted geometric mean '
            f'(shift {SHIFT_S:g} s) over cases of the per-case median solve time; '
            '`SGM vs all`: shifted geometric mean of the ratio to `all`; '
            '`proved`: runs proving optimality within the limit; `worse traffic`: cases '
            "whose median traffic is above `all`'s; `slower` / `faster`: cases whose "
            "median solve time, plus the shift, is over 1.1x / under 0.9x `all`'s.", '']
    head = ['config', 'SGM solve s', 'SGM vs all', 'proved', 'worse traffic',
            'slower', 'faster']
    out += ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    for cfg in configs:
        if not common:
            break
        t = {c: med([solve_time(r) for r in runs[c][cfg]]) for c in common}
        tb = {c: med([solve_time(r) for r in runs[c][BASELINE]]) for c in common} \
            if all(BASELINE in runs[c] for c in common) else None
        rs = [r for c in common for r in runs[c][cfg]]
        proved = sum(bool(r.get('proved_optimal_by_limit')) for r in rs)
        row = [f'`{cfg}`', fmt(sgm(t.values()), 2)]
        if tb:
            ratio = exp(sum(log((t[c] + SHIFT_S) / (tb[c] + SHIFT_S)) for c in common)
                        / len(common))
            traffic = {c: med([r.get('traffic_at_limit') for r in runs[c][cfg]]) for c in common}
            base_tr = {c: med([r.get('traffic_at_limit') for r in runs[c][BASELINE]])
                       for c in common}
            worse = sum(1 for c in common if traffic[c] is None
                        or (base_tr[c] is not None and traffic[c] > base_tr[c]))
            row += [f'{ratio:.2f}', f'{proved}/{len(rs)}', str(worse),
                    str(sum(t[c] + SHIFT_S > 1.1 * (tb[c] + SHIFT_S) for c in common)),
                    str(sum(t[c] + SHIFT_S < 0.9 * (tb[c] + SHIFT_S) for c in common))]
        else:
            row += ['-', f'{proved}/{len(rs)}', '-', '-', '-']
        out.append('| ' + ' | '.join(row) + ' |')

    # Overview of solution quality over time.
    common_q = [c for c in common if c in ref]
    out += ['', f'### Solution quality over time', '',
            f'Over the {len(common_q)} cases above with a solution. `<= {target:g}% @ t`: '
            f'cases whose median gap at t is at most {target:g}%; `ratio @ t`: geometric mean '
            'over cases of the median traffic at t over the reference (1 is the reference; '
            'cases without a solution by t are left out and counted in brackets); '
            f'`SGM t to {target:g}%`: shifted geometric mean over cases of the median time to '
            f'within {target:g}%; `reached`: runs that got there within the limit.', '']
    head = ['config'] + [h for t in checkpoints for h in (f'<= {target:g}% @ {t:g} s',
                                                          f'ratio @ {t:g} s')] \
        + [f'SGM t to {target:g}%', 'reached']
    out += ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    for cfg in configs:
        if not common_q:
            break
        row = [f'`{cfg}`']
        for t in checkpoints:
            gaps = {c: med_gap(runs[c][cfg], t, ref[c][0]) for c in common_q}
            known = [c for c in common_q if gaps[c] is not None]
            sol = [c for c in known if gaps[c] != float('inf')]
            within = sum(gaps[c] <= target for c in sol)
            ratio = (exp(sum(log(1 + gaps[c] / 100) for c in sol) / len(sol))
                     if sol else None)
            row += [f'{within}/{len(known)}' if known else '-',
                    (f'{ratio:.3f}' if ratio is not None else '-')
                    + (f' ({len(known) - len(sol)})' if len(known) > len(sol) else '')]
        tt = [target_time(runs[c][cfg], ref[c][0], target)[0] for c in common_q]
        rs = [(c, r) for c in common_q for r in runs[c][cfg]]
        reached = sum(time_to_target(r, ref[c][0], target) is not None for c, r in rs)
        row += [fmt(sgm(tt), 2), f'{reached}/{len(rs)}']
        out.append('| ' + ' | '.join(row) + ' |')

    # Per case.
    notes = []
    out += ['', '## Per case', '']
    head = ['config', 'runs', 'proved', 'solve s', 'vs all', 'traffic', 'bound',
            'conflicts', 'det. s', 'vars', 'cons', 'MB']
    for case in runs:
        by = runs[case]
        base_t = med([solve_time(r) for r in by.get(BASELINE, [])]) if BASELINE in by else None
        rows = []
        for cfg in configs:
            rs = by.get(cfg)
            if not rs:
                continue
            t = med([solve_time(r) for r in rs])
            mb = med([(r.get('peak_memory') or {}).get('mb') for r in rs])
            rows.append([f'`{cfg}`', str(len(rs)),
                         f"{sum(bool(r.get('proved_optimal_by_limit')) for r in rs)}/{len(rs)}",
                         fmt(t, 2),
                         f'{(t + SHIFT_S) / (base_t + SHIFT_S):.2f}' if base_t is not None
                         else '-',
                         fmt(med([r.get('traffic_at_limit') for r in rs])),
                         fmt(max((r['bound'] for r in rs if r.get('bound') is not None),
                                 default=None)),
                         fmt(med([(r.get('search') or {}).get('conflicts') for r in rs])),
                         fmt(med([(r.get('search') or {}).get('deterministic_time')
                                  for r in rs]), 2),
                         fmt(med([(r.get('model_size') or {}).get('variables') for r in rs])),
                         fmt(med([(r.get('model_size') or {}).get('constraints') for r in rs])),
                         fmt(mb)])
            for r in rs:
                if r['status'] not in ('OPTIMAL', 'FEASIBLE'):
                    notes.append(f"- {case} `{cfg}` seed {r.get('seed')}: status {r['status']}"
                                 ' (no solution)')
                for v in r.get('invalid_reduction_loops', []):
                    notes.append(f"- **{case} `{cfg}` seed {r.get('seed')}: invalid "
                                 f'schedule:** {v}')
        # Soundness: the constraints should not change the optimum, so no
        # configuration's proven lower bound (a proved optimum's is its
        # traffic) may exceed the least traffic any run found. If one does,
        # that configuration's constraints cut off better schedules.
        flat = [(cfg, r) for cfg, rs in by.items() for r in rs]
        found = [(c, r) for c, r in flat if r.get('traffic') is not None]
        if found:
            c_best, best = min(found, key=lambda x: x[1]['traffic'])
            for cfg, rs in by.items():
                r = max((r for r in rs if r.get('bound') is not None),
                        key=lambda r: r['bound'], default=None)
                if r is None or r['bound'] <= best['traffic'] + 1e-6:
                    continue
                what = ('proved traffic ' + fmt(r['traffic']) + ' optimal'
                        if r['status'] == 'OPTIMAL' else 'proved a bound of ' + fmt(r['bound']))
                lacks = sorted(set(r['constraints']) - set(best['constraints']))
                notes.append(
                    f"- **{case}: `{cfg}` (seed {r.get('seed')}) {what}, but `{c_best}` "
                    f"(seed {best.get('seed')}) found traffic {fmt(best['traffic'])}**: "
                    f"`{cfg}`'s constraints cut off better schedules (`{c_best}` lacks "
                    f"{', '.join(lacks) or 'none of them'}).")
        out += [f'### {case}', '', '| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
        if not any(row[-1] != '-' for row in rows):
            out[-2:] = ['| ' + ' | '.join(head[:-1]) + ' |', '|' + '---|' * (len(head) - 1)]
            rows = [row[:-1] for row in rows]
        out += ['| ' + ' | '.join(row) + ' |' for row in rows] + ['']
        if case in ref:
            r0, proved = ref[case]
            out += [f"Reference traffic {fmt(r0)} ({'proved optimal' if proved else 'best found; not proved optimal'}).",
                    '']
            qhead = ['config'] + [f'gap @ {t:g} s' for t in checkpoints] \
                + [f't to {target:g}%']
            out += ['| ' + ' | '.join(qhead) + ' |', '|' + '---|' * len(qhead)]
            for cfg in configs:
                rs = by.get(cfg)
                if not rs:
                    continue
                m, censored = target_time(rs, r0, target)
                out.append('| ' + ' | '.join(
                    [f'`{cfg}`'] + [fmt_gap(med_gap(rs, t, r0))
                                    for t in checkpoints]
                    + [f'>{fmt(m)}' if censored else fmt(m, 2)]) + ' |')
            out.append('')
    if notes:
        out += ['## Notes', ''] + list(dict.fromkeys(notes))
    machines = {tuple(sorted((k, str(v)) for k, v in r['machine'].items()))
                for v in runs.values() for rs in v.values() for r in rs}
    out += ['', '## Machines', ''] + ['- ' + ', '.join(f'{k} {v}' for k, v in m)
                                      for m in machines]
    if len(machines) > 1:
        out += ['', 'Results come from different machines or settings; compare times only '
                'within one machine.']
    (RESULTS / f'{folder(hint)}_summary.md').write_text('\n'.join(out) + '\n')
    print('\n'.join(out))


# ── Driver ───────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog='\n\n'.join(__doc__.split('\n\n')[1:]))
    p.add_argument('cases', nargs='*', metavar='CASE', help='cases to run (default: all)')
    p.add_argument('--list', action='store_true', help='list cases and configurations, exit')
    p.add_argument('--configs', default=','.join(DEFAULT_CONFIGS),
                   help='comma-separated configurations (default: all, none, no-<each>); '
                        "'loo' = the default, 'every' = also only-<each>")
    p.add_argument('--seeds', type=int, default=3,
                   help='CP-SAT seeds 0..N-1 per configuration (default 3)')
    p.add_argument('--time-limit', type=float, default=600,
                   help='seconds per run, as dag.py (default 600)')
    p.add_argument('--threads', type=int, default=available_cores(),
                   help=f'CP-SAT workers (default: all available cores, {available_cores()} '
                        'here)')
    p.add_argument('--no-hint', action='store_true',
                   help='do not hint CP-SAT with single-einsum tilings')
    p.add_argument('--force', action='store_true', help='rerun runs whose results exist')
    p.add_argument('--measure-memory', action='store_true',
                   help="record each run's peak memory (see run.py)")
    p.add_argument('--dry-run', action='store_true',
                   help='print the runs that would be made, and a worst-case time, then exit')
    p.add_argument('--summarize', action='store_true',
                   help='only rewrite the summary (of the runs without hints, with --no-hint)')
    p.add_argument('--checkpoints', default='10,60,300',
                   help='comma-separated seconds at which the summary reports solution '
                        'quality (default 10,60,300); past a run\'s time limit it is unknown '
                        'unless the run proved optimality')
    p.add_argument('--target', type=float, default=1.0,
                   help='percent above the best traffic found that counts as a good '
                        'solution, for the summary\'s time-to-target columns (default 1)')
    p.add_argument('--worker', nargs=3, metavar=('CASE', 'CONFIG', 'SEED'),
                   help=argparse.SUPPRESS)
    args = p.parse_args()

    if args.worker:
        case, config, seed = args.worker
        worker(case, config, int(seed), args.time_limit, args.threads, not args.no_hint)
        return
    if args.list:
        for name, c in CASES.items():
            print(f"{name:24s} {c['workload']:40s} capacity {c['capacity']}")
        print('\nconfigurations: ' + ', '.join(ALL_CONFIGS))
        return
    try:
        checkpoints = [float(t) for t in args.checkpoints.split(',')]
    except ValueError:
        p.error('--checkpoints must be comma-separated numbers of seconds')
    if args.summarize:
        summarize(checkpoints, args.target, not args.no_hint)
        return

    configs = {'loo': DEFAULT_CONFIGS, 'every': ALL_CONFIGS}.get(args.configs,
                                                                 args.configs.split(','))
    for c in configs:
        try:
            enabled(c)
        except ValueError as e:
            p.error(str(e))
    unknown = [c for c in args.cases if c not in CASES]
    if unknown:
        p.error(f'unknown cases {unknown}; see --list')
    if args.seeds < 1:
        p.error('--seeds must be at least 1')
    if args.measure_memory and (why := check_memory_measurement()):
        p.error(f'--measure-memory: {why}')
    cases = args.cases or list(CASES)
    plan = [(case, cfg, seed) for case in cases for seed in range(args.seeds)
            for cfg in configs]
    todo = [x for x in plan if args.force or not path(*x, not args.no_hint).exists()]

    if args.dry_run:
        for case, cfg, seed in todo:
            print(f'{case} {cfg} seed {seed}')
        print(f'\n{len(todo)} of {len(plan)} runs to do ({len(cases)} cases x '
              f'{len(configs)} configurations x {args.seeds} seeds); at most about '
              f'{len(todo) * args.time_limit / 3600:.1f} h at {args.time_limit:g} s each, '
              f'with {args.threads} CP-SAT workers')
        return

    common = ['--time-limit', str(args.time_limit), '--threads', str(args.threads)] \
        + ['--no-hint'] * args.no_hint
    failed, skip = [], set()
    for i, (case, cfg, seed) in enumerate(plan):
        if case in skip:
            continue
        if not result_path(case, 'einsums.json').exists():
            print(f'== {case}: export', flush=True)
            if run_step(['export.py', case])[0]:
                print(f'== {case}: export FAILED; skipping the case', flush=True)
                failed.append(f'{case} export')
                skip.add(case)
                continue
        if (case, cfg, seed) not in todo:
            continue
        print(f'== [{todo.index((case, cfg, seed)) + 1}/{len(todo)}] {case} {cfg} seed {seed}',
              flush=True)
        code, mem = run_step(['ablation.py', *common, '--worker', case, cfg, str(seed)],
                             path(case, cfg, seed, not args.no_hint), args.measure_memory)
        if code:
            peak = f", peak memory {mem['mb']:.0f} MB" if mem else ''
            oom = ', OOM-killed' if mem and mem['oom_kills'] else ''
            print(f'== {case} {cfg} seed {seed} FAILED (exit {code}{oom}{peak})', flush=True)
            failed.append(f'{case} {cfg} s{seed}{oom}{peak}')
    print()
    summarize(checkpoints, args.target, not args.no_hint)
    if failed:
        print('\nFailed runs: ' + ', '.join(failed))
        sys.exit(1)


if __name__ == '__main__':
    main()
