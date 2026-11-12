'''Run the general DAG scheduler (general_dag_scheduler.py) on a case at the
case's capacity, configured to match FFM on snowcat.

Usage:
    python dag.py [--time-limit S] [--threads N] [--no-hint] [--hint-bound] [--force] CASE ...
    python dag.py --cap-at-ffm [--threads N] [--no-hint] [--hint-bound] [--force] CASE ...
The first writes results/<case>/dag.{json,txt} with a fixed time limit
(default 600 s); the second writes results/<case>/dag_capped.{json,txt} with
the time limit set to FFM's time on the case (needs results/<case>/ffm.json,
so run on the same machine with the same --threads as ffm.py). Existing
results are kept unless --force. Needs results/<case>/einsums.json
(export.py) but not AccelForge.

The time limit covers the whole run: building the model, the single-einsum
tilings used as a hint, and CP-SAT's search. CP-SAT may overrun it slightly;
traffic_at_limit is the best traffic found within the limit.

Settings matching snowcat: one on-chip memory of `capacity` elements, one
core, compute_cost = 0 (so the objective is 6 x traffic: minimum off-chip
elements read plus written), spilling of intermediates allowed (FFM's
MainMemory may keep them), partial-sum spilling allowed (FFM
read-modify-writes unfused outputs in MainMemory, skipping the first read; the
scheduler charges each write after an element's first as one read), and
perfect factorization (FFM's default mapspace). With hints (the default),
each einsum is first tiled on its own and the unfused schedule built from
those tilings is given to CP-SAT as a solution hint (scheduler(hint=True)).'''
import argparse, contextlib, io, sys, time, warnings

from common import available_cores, load, machine_info, result_path, save
from cases import CASES
import general_dag_scheduler as gds
from general_dag_scheduler import Einsum, scheduler
from ortools.sat.python import cp_model

SETTINGS = dict(num_cores=1, allow_spilling=True, perfect_factorization=True,
                partial_sums=True, sparse_domains=True, tight_bounds=True, debug=False)


class Trace(cp_model.CpSolverSolutionCallback):
    '''(seconds since the run started, traffic, compute cost, objective) of
    each improving solution. With compute_cost = 0 everywhere the objective is
    6 x traffic.'''
    def __init__(self, t0):
        super().__init__()
        self.t0, self.solutions, self.costs = t0, [], None

    def watch(self, model):
        '''Read the scheduler's traffic and compute cost variables of model.'''
        index = {v.name: i for i, v in enumerate(model.proto.variables)}
        self.costs = [model.get_int_var_from_proto_index(index[n])
                      for n in ('final_communication_cost', 'final_compute_cost')]

    def on_solution_callback(self):
        self.solutions.append((time.perf_counter() - self.t0, *map(self.Value, self.costs),
                               self.ObjectiveValue()))


def reduction_violations(sm, solver):
    '''Sanity check on a solved schedule: loops over a reduction dim of an
    einsum that also enclose a consumer of its output (which would read a
    partial sum). Should always be empty.'''
    V = solver.Value
    bad = []
    for ei, e in enumerate(sm.einsums):
        o = e.output_operand
        reduction = [d for d in e.dim_sizes if d not in sm.all_operand_dims[o]]
        for ki, k in enumerate(sm.einsums):
            if not any(sm.original_names[y] == sm.original_names[o] for y in k.operand_dims
                       if y != k.output_operand):
                continue
            for r in (r for r in reduction if r in k.dim_sizes):
                for a in sm.all_operands:
                    if r not in sm.temporal_dim[a]:
                        continue
                    if V(sm.temporal_dim[a][r]) * V(sm.parallel_dim[a][r]) == 1:
                        continue
                    if (any(V(sm.ancestor[a][x]) for x in e.operand_dims)
                            and any(V(sm.ancestor[a][y]) for y in k.operand_dims)):
                        bad.append(f'loop over {r} at {a} encloses einsum {ei} (reducing {r}) '
                                   f'and its consumer einsum {ki}')
    return bad


def extract(sm, solver):
    '''Traffic, per-tensor reads/writes, fusion and peak on-chip usage of a
    solved model, keyed by original tensor names.'''
    V = solver.Value
    per_tensor = {}
    for op in sm.all_operands:
        d = per_tensor.setdefault(sm.original_names[op], {'read': 0, 'write': 0})
        total = V(sm.total_cost_vars[op])
        if op in sm.must_write:
            fills = V(sm.partial_sum_fills[op]) if op in sm.partial_sum_fills else 0
            d['write'] += total - fills
            d['read'] += fills
        else:
            d['read'] += total
    fused = sorted(t for t, g in sm.operand_groups.items()
                   if g['producer'] is not None and g['consumers']
                   and not V(sm.must_write[g['producer']]))
    peak = 0  # the capacity constraint's live set at each einsum step
    for k in range(len(sm.einsums)):
        p = V(sm.pos[k])
        peak = max(peak, sum(V(sm.spatial_cost[j]) for j in sm.all_operands
                             if V(sm.time_start[j]) <= p <= V(sm.time_end[j])
                             and (j not in sm.must_read or V(sm.must_read[j]))))
    return {'traffic': V(sm.final_communication_cost), 'per_tensor': per_tensor,
            'fused': fused, 'glb_usage': peak,
            'einsum_order': [sm.einsums[k].operation for k in
                             sorted(range(len(sm.einsums)), key=lambda k: V(sm.pos[k]))],
            'invalid_reduction_loops': reduction_violations(sm, solver)}


@contextlib.contextmanager
def deadline_solve(deadline, trace, timing):
    '''Make the scheduler's CP-SAT solve stop at the deadline (counting the
    model build) and record improving solutions. The CP-SAT solves that
    build the hint (each einsum's tiling, and with hint_bound the hint's
    completion) have their own limits and are left alone.'''
    helpers = ('_tile_einsum', '_solve_einsum_alone', '_complete_hint')
    orig_solve = cp_model.CpSolver.Solve
    orig = {h: getattr(gds, h) for h in helpers}
    tiling = []

    def inner(f):
        def wrapped(*args, **kwargs):
            tiling.append(True)
            try:
                return f(*args, **kwargs)
            finally:
                tiling.pop()
        return wrapped

    def solve(solver, model, cb=None):
        if tiling:
            return orig_solve(solver, model, cb)
        timing['build_s'] = time.perf_counter() - trace.t0
        trace.watch(model)
        solver.parameters.max_time_in_seconds = max(deadline - time.perf_counter(), 1e-3)
        return orig_solve(solver, model, trace)

    cp_model.CpSolver.Solve = solve
    for h, f in orig.items():
        setattr(gds, h, inner(f))
    try:
        yield
    finally:
        cp_model.CpSolver.Solve = orig_solve
        for h, f in orig.items():
            setattr(gds, h, f)


def run(name, time_limit, threads, hint, capped, num_cores=1, stem=None, compare_ffm=True,
        workload=None, hint_bound=False):
    '''One run; writes results/<name>/<stem>.{json,txt} (stem: dag or
    dag_capped by default). num_cores: the scheduler's cores (parallel
    hardware units), not CP-SAT's threads. workload: optional dict(einsums
    (Einsum objects), capacity, global_outputs) to schedule instead of
    results/<name>/einsums.json with compute_cost = 0.'''
    settings = dict(SETTINGS, num_cores=num_cores)
    stem = stem or ('dag_capped' if capped else 'dag')
    ffm = load(result_path(name, 'ffm.json')) if compare_ffm else None
    if workload is None:
        ex = load(result_path(name, 'einsums.json'))
        if ex is None:
            sys.exit(f'{name}: results/{name}/einsums.json missing; run export.py first')
        workload = dict(
            einsums=[Einsum({t: tuple(d) for t, d in e['operand_dims'].items()}, e['output'],
                            e['dim_sizes'], compute_cost=0, operation=e['name'])
                     for e in ex['einsums']],
            capacity=ex['capacity'], global_outputs=ex.get('global_outputs', ()),
            bits_per_value=ex['bits_per_value'], export_warnings=ex['warnings'])
    einsums = workload['einsums']
    t0 = time.perf_counter()
    trace, timing, log = Trace(t0), {}, io.StringIO()
    with deadline_solve(t0 + time_limit, trace, timing), contextlib.redirect_stdout(log), \
            warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        sm, solver = scheduler(einsums, workload['capacity'], time_limit=time_limit, hint=hint,
                               hint_bound=hint_bound, num_workers=threads,
                               global_outputs=workload.get('global_outputs', ()), **settings)
    wall = time.perf_counter() - t0
    status = solver.StatusName(solver.response_proto.status)
    r = {'case': name, 'tool': 'dag', 'capped_at_ffm': capped, 'status': status,
         'wall_s': wall, 'build_s': timing.get('build_s'), 'time_limit_s': time_limit,
         'hint': hint, 'hint_bound': hint_bound, 'hint_given': len(sm.model.proto.solution_hint.vars) > 0,
         'capacity': workload['capacity'], 'bits_per_value': workload.get('bits_per_value'),
         'ffm_traffic': ffm and ffm['traffic'],
         'export_warnings': workload.get('export_warnings', []),
         'compute_costs': [e.compute_cost for e in einsums],
         'warnings': [str(w.message) for w in caught], 'settings': settings,
         'machine': machine_info(threads)}
    if status in ('OPTIMAL', 'FEASIBLE'):
        r.update(extract(sm, solver))
        r['compute'] = solver.Value(sm.final_compute_cost)
        r['objective'] = solver.ObjectiveValue()
        r['objective_bound'] = solver.BestObjectiveBound()
        # With no compute cost the objective is 6 x traffic, so this bounds traffic.
        r['bound'] = (r['objective_bound'] / 6 if not any(r['compute_costs']) else None)
        within = [s for s in trace.solutions if s[0] <= time_limit]
        at = within[-1] if within else (None,) * 4
        r['traffic_at_limit'], r['compute_at_limit'], r['objective_at_limit'] = at[1:]
        r['proved_optimal_by_limit'] = status == 'OPTIMAL' and wall <= time_limit
        r['t_best_s'] = trace.solutions[-1][0]
        if ffm:
            r['t_le_ffm_s'] = next((s[0] for s in trace.solutions if s[1] <= ffm['traffic']),
                                   None)
        r['trace'] = trace.solutions
    save(result_path(name, stem + '.json'), r)
    result_path(name, stem + '.txt').write_text(
        f'# {name} ({stem}): wall {wall:.2f} s of {time_limit:.2f}, status {status}\n'
        + log.getvalue() + ''.join(f'WARNING {w}\n' for w in r['warnings']))
    print(f"{name} ({stem}): {wall:.1f} s of {time_limit:.1f}, {status}, traffic "
          f"{r.get('traffic_at_limit')} elements" + (f" (FFM {ffm['traffic']:.0f})" if ffm else '')
          + ''.join(f'\n  INVALID: {v}' for v in r.get('invalid_reduction_loops', [])),
          flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--time-limit', type=float, default=600,
                   help='seconds for the whole run (default 600); ignored with --cap-at-ffm')
    p.add_argument('--cap-at-ffm', action='store_true',
                   help="limit the run to FFM's time on the case (results/<case>/ffm.json)")
    p.add_argument('--threads', type=int, default=available_cores(),
                   help='CP-SAT workers (default: all available cores)')
    p.add_argument('--no-hint', action='store_true',
                   help='do not hint CP-SAT with single-einsum tilings')
    p.add_argument('--hint-bound', action='store_true',
                   help='never return a schedule worse than the hint (scheduler(hint_bound=True))')
    p.add_argument('--force', action='store_true', help='rerun even if the result exists')
    p.add_argument('cases', nargs='+', choices=CASES, metavar='CASE')
    args = p.parse_args()
    for name in args.cases:
        stem = 'dag_capped' if args.cap_at_ffm else 'dag'
        if not args.force and result_path(name, stem + '.json').exists():
            print(f'{name} ({stem}): already done, skipping (--force to rerun)')
            continue
        limit = args.time_limit
        if args.cap_at_ffm:
            ffm = load(result_path(name, 'ffm.json'))
            if ffm is None:
                print(f'{name} ({stem}): no FFM result (results/{name}/ffm.json); skipping')
                continue
            if ffm['machine']['threads'] != args.threads:
                print(f"{name} ({stem}): warning: FFM ran with {ffm['machine']['threads']} "
                      f'processes, CP-SAT gets {args.threads} workers')
            limit = ffm['wall_s']
        run(name, limit, args.threads, not args.no_hint, args.cap_at_ffm,
            hint_bound=args.hint_bound)
