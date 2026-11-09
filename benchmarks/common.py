'''Shared paths, result files and run metadata for the benchmark tools.

Results go to results/<case>/ next to this file:
    einsums.json      the case's einsums as AccelForge parses them (export.py)
    ffm.json/.txt     FFM's result and mapping (ffm.py)
    dag.json/.txt     the DAG scheduler with a fixed time limit (dag.py)
    dag_capped.json   the DAG scheduler capped at FFM's time (dag.py --cap-at-ffm)
    tcm.json/.txt     single einsums: TCM's result and mapping (einsum_tcm.py)
    cpsat.json/.txt   single einsums: cb_einsum_ml's, evaluated by AccelForge
                      (einsum_cpsat.py)
Every result records the machine and package versions it ran with.'''
import importlib.metadata, json, os, platform, subprocess, sys
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


def machine_info(threads):
    '''What a result was produced with: worker threads/processes used, the
    machine, and the versions of the code compared.'''
    return {'threads': threads, 'cores_available': available_cores(),
            'memory_gb': total_memory_gb(), 'platform': platform.platform(),
            'python': platform.python_version(), 'ortools': _package('ortools'),
            'accelforge': _package('accelforge'), 'tensor_program_dse': _repo_commit()}
