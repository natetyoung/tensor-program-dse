'''Run cb_einsum_ml_cpsat97 on single-einsum cases (einsum_cases.py) with
the TPU-v4i parameters, then evaluate its schedule with AccelForge's model on
TCM's spec (einsum_tcm.spec_for), so its energy, latency and EDP compare
directly with TCM's.

Usage: python einsum_cpsat.py [--time-limit S] [--threads N] [--force] EINSUM ...
Writes results/<einsum>/cpsat.{json,txt} (an existing cpsat.json is kept
unless --force).

Solver settings (SETTINGS): redundant_bounds, sparse_domains, merge_dims and
partial_sums (temporal reduction outside the output's tiles allowed, as FFM
allows), with perfect division (FFM's default mapspace). The reported time
is the whole cb_einsum_ml call (model building, solve, cross-check); the
evaluation is untimed.

TPU-v4i in the solver (tpu_v4i): costs are integers from the arch yaml's
per-bit energies and throughputs at the einsum's bits per value (energy unit
one MAC, 0.084 pJ; time unit a third of an 8-bit GlobalBuffer read), and
capacities are in elements. Einsums with a weight run on the 128 x 128 PE
array: L0 = Register (one weight), L1 = LocalBuffer (input and output, Z
fanout 4), L2 = GlobalBuffer (the weight optional). Einsums without one run on
the ScalarUnit, which sits under the LocalBuffer: L0 = LocalBuffer, L1 =
GlobalBuffer. DRAM is MainMemory, whose reads and writes share one port.

Conversion to an AccelForge mapping: MainMemory holds every tensor; then,
bucket by bucket (outermost first), the bucket's temporal loops, its parallel
loops (FANOUTS) and the next slot's tensor as a storage node; tile shapes are
the remaining tile after each loop.'''
import argparse, contextlib, io, logging, time

from accelforge.frontend.mapping.mapping import Compute, Mapping, Spatial, Storage, Temporal

from common import available_cores, machine_info, result_path, save
from einsum_cases import EINSUM_CASES, is_elementwise
from einsum_tcm import breakdown, spec_for
from ffm import tree_lines
from cb_einsum_ml_cpsat97 import MemCosts, cb_einsum_ml

SETTINGS = dict(redundant_bounds=True, sparse_domains=True, merge_dims=True,
                partial_sums=True, perfect_division=True)

E_UNIT = 0.084e-12         # energy unit (J): one MAC
T_UNIT = 1 / (3 * 2048e9)  # time unit (s): a third of an 8-bit GlobalBuffer read

# solver level -> AccelForge component, and (level, array dim) -> spatial fanout
LEVELS = {0: 'Register', 1: 'LocalBuffer', 2: 'GlobalBuffer'}
FANOUTS = {(1, 0): ('LocalBuffer', 'Z'), (0, 0): ('ProcessingElement', 'reuse_input'),
           (0, 1): ('ProcessingElement', 'reuse_output')}
SCALAR_LEVELS = {0: 'LocalBuffer', 1: 'GlobalBuffer'}
SCALAR_FANOUTS = {(0, 0): ('LocalBuffer', 'Z')}


def tpu_v4i(bits):
    '''TPU-v4i (accelforge/examples/arches/tpu_v4i.yaml) in the solver's
    integer units for elements of the given width. E.g. at 16 bits a DRAM
    access is 16 * 7.03 / 0.084 = 1339.05 -> 1339 energy units and
    16 / (8 * 614e9) s = 20.01 -> 20 time units, and a MAC 5851.4 -> 5851.'''
    def mem(e_rd, e_wr, tp_rd=None, tp_wr=None, **kw):
        time = lambda tp: round(bits / tp / T_UNIT) if tp else 0  # None: infinite
        return MemCosts(round(bits * e_rd / E_UNIT), round(bits * e_wr / E_UNIT),
                        time(tp_rd), time(tp_wr), **kw)
    return dict(
        local=mem(0.249e-12, 0.293e-12),
        glob=mem(1.88e-12, 2.36e-12, 8 * 2048e9, 8 * 1024e9),
        dram=mem(7.03e-12, 7.03e-12, 8 * 614e9, 8 * 614e9, shared_port=True),
        local_cap=4 * 1024 * 1024 * 8 // bits,
        glob_cap=128 * 1024 * 1024 * 8 // bits,
        mac_time=round(1 / 1.05e9 / T_UNIT),
        mac_energy=round(0.084e-12 / E_UNIT),
        scalar_time=round(1 / (1.05e9 * 128) / T_UNIT),  # 45.71 -> 46; no energy
    )


def solver_args(case):
    '''cb_einsum_ml's arguments for a case (without SETTINGS).'''
    arch = tpu_v4i(case['bits'])
    t = {role: tensor for role, (tensor, _) in case['tensors'].items()}
    i, o = t['input'], t['output']
    args = dict(operand_dims={tensor: dims for tensor, dims in case['tensors'].values()},
                output_operand=o, dim_sizes=case['dims'], dram_costs=arch['dram'],
                objective='edp')
    if is_elementwise(case):
        return dict(args, capacities=[[(arch['local_cap'], (i, o))], arch['glob_cap']],
                    level_costs=[arch['local'], arch['glob']], fanouts=[4, 1],
                    multicast=[(i, o), False], compute_time=arch['scalar_time'],
                    compute_energy=0)
    w = t['weight']
    return dict(args,
                capacities=[[(1, (w,))], [(arch['local_cap'], (i, o))], arch['glob_cap']],
                level_costs=[MemCosts(0, 0, 0, 0), arch['local'], arch['glob']],
                fanouts=[(128, 128), 4, 1],
                multicast=[((i,), (o,)), (i, w), False],
                # the PE array's spatial reuse is a hard constraint in AccelForge
                reuse=[((i,), (o,)), False, False],
                optional=[(), (), (w,)],  # GlobalBuffer: may_keep All
                compute_time=arch['mac_time'], compute_energy=arch['mac_energy'])


def to_mapping(name, case, sched):
    '''The solver's schedule as an AccelForge mapping.'''
    elementwise = is_elementwise(case)
    levels = SCALAR_LEVELS if elementwise else LEVELS
    fanouts = SCALAR_FANOUTS if elementwise else FANOUTS
    # level l's parallel loops sit in the bucket after the slots of the levels above it
    par_bucket = {l: sum(1 for u in sched.order if u.lvl > l) for l in sched.par_rows}
    tile = dict(case['dims'])

    def loop(cls, d, n, **kw):
        assert tile[d] % n == 0, (name, d, tile[d], n)
        tile[d] //= n
        return cls(rank_variable=d, tile_shape=tile[d], **kw)

    nodes = [Storage(tensors=[t for t, _ in case['tensors'].values()], component='MainMemory')]
    for b in range(len(sched.order) + 1):
        nodes += [loop(Temporal, d, fs[b]) for d, fs in sched.factors.items() if fs[b] > 1]
        for l, rows in sorted(sched.par_rows.items()):
            if par_bucket[l] == b:
                for s, row in enumerate(rows):
                    component, fanout = fanouts[(l, s)]
                    nodes += [loop(Spatial, d, f, name=fanout, component=component)
                              for d, f in row.items() if f > 1]
        if b < len(sched.order):
            u = sched.order[b]
            nodes.append(Storage(tensors=[u.op], component=levels[u.lvl]))
    assert all(t == 1 for t in tile.values()), (name, tile)
    nodes.append(Compute(einsum=name, component='ScalarUnit' if elementwise else 'MAC'))
    return Mapping(nodes=nodes)


def run(name, threads, time_limit):
    case = EINSUM_CASES[name]
    log = io.StringIO()
    t0 = time.perf_counter()
    with contextlib.redirect_stdout(log):
        sched = cb_einsum_ml(**solver_args(case), **SETTINGS, num_workers=threads,
                             time_limit=time_limit)
    wall = time.perf_counter() - t0
    status = next(l.split(':', 1)[1].strip() for l in log.getvalue().splitlines()
                  if l.startswith('status:'))
    r = {'case': name, 'tool': 'cpsat', 'settings': SETTINGS, 'status': status,
         'wall_s': wall, 'time_limit_s': time_limit, 'machine': machine_info(threads)}
    lines = []
    if sched is not None:
        spec = spec_for(case)
        spec.mapping = to_mapping(name, case, sched)
        result = spec.evaluate_mapping()
        energy, latency = float(result.energy()), float(result.latency())
        energy_parts, latency_parts = breakdown(result)
        r.update(solver_energy=sched.energy, solver_delay=sched.delay, energy_J=energy,
                 latency_s=latency, edp_Js=energy * latency, energy_parts_J=energy_parts,
                 latency_parts_s=latency_parts,
                 order=[(u.op, u.lvl) for u in sched.order], factors=sched.factors,
                 parallel={str(l): rows for l, rows in sched.par_rows.items()})
        lines = [*tree_lines(result.mapping()),
                 f'Energy by component/tensor/action (J): {energy_parts}',
                 f'Latency by component (s): {latency_parts}',
                 f'Energy {energy} J, latency {latency} s, EDP {energy * latency} J*s']
    save(result_path(name, 'cpsat.json'), r)
    result_path(name, 'cpsat.txt').write_text('\n'.join(
        [f'# {name} (CP-SAT): wall {wall:.2f} s of {time_limit:.0f}, status {status}, '
         f'{threads} workers', '# Evaluated by AccelForge:', *lines,
         '# Solver output:', log.getvalue()]))
    print(f"{name} (CP-SAT): {wall:.2f} s, {status}, EDP {r.get('edp_Js', float('nan')):.6g} J*s",
          flush=True)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARNING)
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--time-limit', type=float, default=120,
                   help="seconds for CP-SAT's search (default 120)")
    p.add_argument('--threads', type=int, default=available_cores(),
                   help='CP-SAT workers (default: all available cores)')
    p.add_argument('--force', action='store_true', help='rerun even if cpsat.json exists')
    p.add_argument('einsums', nargs='+', choices=EINSUM_CASES, metavar='EINSUM')
    args = p.parse_args()
    for name in args.einsums:
        if not args.force and result_path(name, 'cpsat.json').exists():
            print(f'{name} (CP-SAT): already done, skipping (--force to rerun)')
            continue
        run(name, args.threads, args.time_limit)
