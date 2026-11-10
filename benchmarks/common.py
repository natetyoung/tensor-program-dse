'''Shared paths, result files and run metadata for the benchmark tools.

Results go to results/<case>/ next to this file:
    einsums.json      the case's einsums as AccelForge parses them (export.py)
    ffm.json/.txt     FFM's result and mapping (ffm.py)
    dag.json/.txt     the DAG scheduler with a fixed time limit (dag.py)
    dag_capped.json   the DAG scheduler capped at FFM's time (dag.py --cap-at-ffm)
    tcm.json/.txt     single einsums: TCM's result and mapping (einsum_tcm.py)
    cpsat.json/.txt   single einsums: cb_einsum_ml's, evaluated by AccelForge
                      (einsum_cpsat.py)
Every result records the machine and package versions it ran with, and,
when run.py or einsum_run.py ran it with --measure-memory, its step's peak
memory (peak_memory).'''
import importlib.metadata, json, os, platform, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent  # the tensor-program-dse checkout holding general_dag_scheduler.py
RESULTS = HERE / 'results'
sys.path.insert(0, str(REPO))


def result_path(case, name):
    '''results/<case>/<name>, creating the directory.'''
    d = RESULTS / case
    d.mkdir(parents=True, exist_ok=True)
    return d / name


def load(path):
    '''A JSON result, or None if it does not exist.'''
    path = Path(path)
    return json.loads(path.read_text()) if path.exists() else None


def save(path, data):
    Path(path).write_text(json.dumps(data, indent=1))


def available_cores():
    '''Cores this process may run on (respects CPU affinity and containers).'''
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:  # not Linux
        return os.cpu_count() or 1


def total_memory_gb():
    try:
        return round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 2 ** 30, 1)
    except (AttributeError, ValueError, OSError):
        return None


def _package(name):
    '''Version of an installed package, with the git commit for git installs.'''
    try:
        dist = importlib.metadata.distribution(name)
    except importlib.metadata.PackageNotFoundError:
        return None
    version = dist.version
    try:
        commit = json.loads(dist.read_text('direct_url.json') or '{}').get(
            'vcs_info', {}).get('commit_id')
        if commit:
            version += f' (git {commit[:12]})'
    except (json.JSONDecodeError, TypeError):
        pass
    return version


def _repo_commit():
    try:
        commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True,
                                text=True, check=True).stdout.strip()
        dirty = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no'],
                               cwd=REPO, capture_output=True, text=True).stdout.strip()
        return commit[:12] + (' (modified)' if dirty else '')
    except (OSError, subprocess.CalledProcessError):
        return None


# Runs "$@" in the shell's cgroup, then copies that cgroup's memory.peak and
# memory.events to $1. The cgroup disappears when its last process exits, so
# they must be read from inside it.
_IN_SCOPE = ('out=$1; shift; cg=/sys/fs/cgroup$(cut -d: -f3 /proc/self/cgroup); "$@"; rc=$?; '
             'cat "$cg/memory.peak" "$cg/memory.events" > "$out"; exit $rc')


def _in_scope(argv, out):
    '''argv run in a new transient systemd scope (its own cgroup), with the
    scope's memory stats written to out.'''
    return ['systemd-run', '--user', '--scope', '--quiet', 'sh', '-c', _IN_SCOPE, 'sh',
            str(out), *argv]


def check_memory_measurement():
    '''None if run_step(measure_memory=True) works here, else why not.'''
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'mem'
        try:
            r = subprocess.run(_in_scope(['true'], out), capture_output=True, text=True)
        except OSError as e:
            return f'cannot run systemd-run ({e})'
        if r.returncode or not out.exists() or not out.read_text().split()[0].isdigit():
            return ('a systemd user scope with cgroup v2 memory accounting is not available '
                    f"here ({(r.stderr or 'no memory.peak').strip()}); needs cgroup v2, "
                    'Linux >= 5.19, a systemd user session and the memory controller '
                    'delegated to it (see README)')
    return None


def run_step(argv, result=None, measure_memory=False):
    '''Run `python argv...` in this folder; its exit code.

    With measure_memory, the step runs in its own systemd scope, and the peak
    memory of its whole process tree (cgroup v2 memory.peak: every process,
    each page counted once, including page cache) is added to the JSON file
    `result` as `peak_memory` -- if the step (re)wrote it, i.e. was not
    skipped. The peak covers the whole step, including untimed parts (imports,
    FFM's warm-up and detailed evaluation). It is also printed, and returned
    as the second value when the step fails (e.g. killed by the OOM killer).'''
    argv = [sys.executable, *argv]
    if not measure_memory:
        return subprocess.run(argv, cwd=HERE).returncode, None
    before = result.stat().st_mtime_ns if result.exists() else None
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'mem'
        code = subprocess.run(_in_scope(argv, out), cwd=HERE).returncode
        if not out.exists():
            return code, None
        peak, *events = out.read_text().split('\n')
    events = dict(l.split() for l in events if l.strip())
    mem = {'mb': round(int(peak) / 2 ** 20, 1), 'oom_kills': int(events.get('oom_kill', 0)),
           'measured': 'whole step, all processes (cgroup v2 memory.peak)'}
    if result is not None and result.exists() and result.stat().st_mtime_ns != before:
        r = load(result)
        r['peak_memory'] = mem
        save(result, r)
    elif not code:  # skipped: the peak is just the skip check's
        return code, None
    print(f"   peak memory {mem['mb']:.0f} MB"
          + (f", {mem['oom_kills']} OOM kills" if mem['oom_kills'] else ''), flush=True)
    return code, mem


def machine_info(threads):
    '''What a result was produced with: worker threads/processes used, the
    machine, and the versions of the code compared.'''
    return {'threads': threads, 'cores_available': available_cores(),
            'memory_gb': total_memory_gb(), 'platform': platform.platform(),
            'python': platform.python_version(), 'ortools': _package('ortools'),
            'accelforge': _package('accelforge'), 'tensor_program_dse': _repo_commit()}
