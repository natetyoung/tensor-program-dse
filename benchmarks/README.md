# Benchmarks: the CP-SAT schedulers vs. AccelForge FFM

Two comparisons with AccelForge's FFM mapper:
- **Multi-einsum** (most of this README): `general_dag_scheduler.py` (in the parent directory) vs. FFM.
- **Single einsums** ([below](#single-einsums-cb_einsum_ml-vs-tcm)): `cb_einsum_ml_cpsat97.py` vs. FFM (TCM) on TPU-v4i.

The multi-einsum comparison:
- **Workloads:** multi-einsum workloads.
- **Hardware:** a single-level memory hierarchy with one fixed on-chip capacity per case.
- **Goal of both tools:** minimize off-chip traffic.

Each case is run three ways:
1. **FFM** at its default optimization level (O3).
2. **DAG, fixed limit:** the DAG scheduler with a fixed time limit (default 600 s), which shows the traffic it can reach.
3. **DAG, capped:** the DAG scheduler limited to the time FFM took on the case, which shows the traffic each tool reaches in the same time on the same machine.

## Setup
You need Python 3.10 or newer and a checkout of `tensor-program-dse`; this folder is part of it.

```
python -m venv venv
venv/bin/pip install -r benchmarks/requirements.txt
```

`requirements.txt` installs:
- `ortools`;
- AccelForge, pinned to the git commit the comparison was developed against. Installing it this way takes about 30 s.

Neither Docker nor Graphviz is needed.

## Running
Run these from this folder:

```
python run.py --list                       # the cases
python run.py chain2_tiny siso_c4k         # some cases (about a minute)
python run.py                              # every case (about 1.75 h on 16 cores)
```

`run.py` writes `results/summary.md` at the end and prints it. For each case it runs four steps, each in its own process, so a failure in one step doesn't stop the rest:

| Step | Command it runs | Writes |
|---|---|---|
| export | `export.py CASE` | `results/<case>/einsums.json`: the einsums as AccelForge parses the workload; the DAG scheduler's input |
| ffm | `ffm.py CASE` | `results/<case>/ffm.json`, `ffm.txt` (mapping) |
| dag | `dag.py --time-limit S CASE` | `results/<case>/dag.json`, `dag.txt` (schedule) |
| capped | `dag.py --cap-at-ffm CASE` | `results/<case>/dag_capped.json`, `dag_capped.txt` |

Each tool can also be run on its own. `summarize.py` rebuilds the summary from whatever results exist.

### Options

| Option | Effect |
|---|---|
| `--threads N` | FFM worker processes and CP-SAT workers. Default: every core this process may use. Both tools get the same number, so the capped comparison is like-for-like. |
| `--dag-time-limit S` | Seconds for the fixed-limit DAG run (default 600). |
| `--steps ffm,dag` | Run only some steps. |
| `--force` | Rerun steps whose results already exist. By default they are skipped, so an interrupted run can be resumed. |
| `--no-hint` | Don't hint CP-SAT with single-einsum tilings (see below). |
| `--measure-memory` | Record each step's peak memory (see [Measuring memory](#measuring-memory)). |

### Different machines
- **Times depend on the machine.** The capped run takes its limit from the `ffm.json` produced on the same machine. Always run `ffm` and `capped` together, with the same `--threads`. `dag.py` warns if the thread counts differ.
- **Every result records its machine:** threads, cores, memory, and the versions of Python, ortools, AccelForge and this repository. `summary.md` lists them.
- **Mixed results:** if a results folder mixes machines or settings, `summary.md` says so; compare times only within one machine.
- **Memory:** FFM's memory use grows with its number of worker processes. `kda_batched` is by far the largest case. If FFM is killed there, for example by the out-of-memory killer, rerun that case with fewer `--threads`, and use the same number for its DAG runs.

### Measuring memory
With `--measure-memory`, `run.py` and `einsum_run.py` run each tool step in its own transient systemd scope, which is its own cgroup. Export steps are not measured.
- **What is recorded:** the cgroup's `memory.peak`, added to the step's result as `peak_memory` (`mb`, and `oom_kills`), and shown as `MB` columns in the summaries.
- **What it covers:** every process of the step, so all of FFM's worker processes, with each page counted once.
  - It covers the whole step, not only the timed part: imports, FFM's warm-up and its untimed detailed evaluation are included.
  - It includes page cache the step reads in. Files already cached by other processes, such as shared libraries, are charged to those processes instead.
- **Comparisons:** like times, peaks are only comparable at the same `--threads` on one machine.
- **Skipped and failed steps:** a step skipped because its result exists keeps its old `peak_memory`, if any. A step rerun without the flag loses it. A failed step's peak, and whether the out-of-memory killer fired, is printed and listed under the failed steps.
- **Requirements**, checked at start-up:
  - cgroup v2: `stat -fc %T /sys/fs/cgroup` prints `cgroup2fs`;
  - Linux 5.19 or newer, for `memory.peak`;
  - a systemd user session: `systemctl --user status` works;
  - the memory controller delegated to it: `cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/user@$(id -u).service/cgroup.controllers` includes `memory`.
- **Quick test:** this should print about 315,000,000:
  ```
  systemd-run --user --scope -q sh -c 'python3 -c "x=b\"x\"*(300*2**20)"; cat /sys/fs/cgroup$(cut -d: -f3 /proc/self/cgroup)/memory.peak'
  ```
- **The core-count runs:** `cores.py` runs in one process, so it doesn't support `--measure-memory`.

## What is compared
- **Architecture:** AccelForge's `snowcat` example arch.
  - MainMemory charges 1 per bit read or written, so FFM's energy is the off-chip bits moved.
  - One GlobalBuffer, whose size is set to the case's capacity, may keep every tensor.
  - The MAC is free.
  - MainMemory keeps everything except intermediates, so an intermediate is fused if and only if it never touches MainMemory.
- **FFM settings:** `metrics = ENERGY` alone, so it returns one minimum-traffic mapping.
  - **FFM's time** is its mapping search alone, measured after an untimed warm-up search on a tiny workload. The warm-up absorbs the roughly 3 s start-up cost of each new process.
  - **Detailed evaluation:** FFM's chosen mapping is then evaluated in detail, untimed, for per-tensor traffic and buffer usage. That evaluation fails on some workloads (`kda_batched`, `siso_c8k`). The search's own total is then reported and `summary.md` notes it; the two totals agree where both are available.
- **DAG scheduler settings** (`dag.py`'s `SETTINGS`): `num_cores=1`, `compute_cost=0`, `allow_spilling`, `partial_sums`, `perfect_factorization` (FFM's default mapspace), `sparse_domains` and `tight_bounds`.
  - With `compute_cost=0`, the objective is 6 × traffic.
- **Partial sums:** FFM read-modify-writes unfused outputs in MainMemory, skipping the first read. The scheduler likewise charges each write after an element's first as one read.
- **Recomputation:** neither tool recomputes.
- **Shared tiles:** both can share one on-chip tile of an input between consumers.
- **Hints:** by default, `scheduler(hint=True)` first tiles each einsum on its own with `cb_einsum_ml_cpsat97` and gives CP-SAT the resulting unfused schedule as a starting solution.
  - That tiling counts against the DAG scheduler's time.
- **DAG time limits** cover everything: building the model, the hint tilings and the search.
  - CP-SAT may overrun the limit slightly. `traffic_at_limit` is the best traffic found within it, and the summary reports that.
- **Units:** traffic is in elements read plus written off-chip (FFM's bits ÷ `bits_per_value`).
- **Sanity check:** `invalid_reduction_loops` in the DAG results must be empty. It lists any loop that would make a consumer read a partial sum; the summary flags any it finds.

## Core counts, with compute costs
`python cores.py` runs the DAG scheduler alone, with no FFM, on `swiglu`, `kda_batched`, `gdn_decode`, `siso_k128`, `gqa_llama3_8b` and `kimi_k3_mla`.
- **Core counts:** each case runs with `num_cores` = 1 and 8, the hardware cores a schedule may split loops across.
- **Time limit:** every run gets the same limit, 30 minutes by default, so all twelve runs take up to 6 hours.
- **Compute costs:** unlike the FFM comparison, these workloads use this repository's Python descriptions with their `compute_cost`, `accel_gran` and `operation` (`compute_workloads.py`):
  - `kda_batched` is `test_cases.kda_full_batched_decode_einsums`;
  - `gdn_decode` is `test_cases.gdn_full_decode_einsums`;
  - `siso_k128` is `siso_workload.siso_ssd_intra_chunk_einsums`;
  - `gqa_llama3_8b` is `test_cases.gqa_attention_prefill_einsums`;
  - `kimi_k3_mla` is `test_cases.kimi_k3_mla_einsums`;
  - `swiglu` is `test_cases.llama_ffn_einsums`. The merged variant isn't used: with compute costs, its model overflows CP-SAT's 64-bit objective, as `compute_workloads.py` explains.
- **Objective:** with compute costs, it is 5 × max(compute, traffic) + compute + traffic. Both traffic and compute are per core.
- **Output:** `results/<case>/compute_cores<N>.{json,txt}`, separate from the comparison's `dag*.json`, and `results/compute_cores_report.md`, which has a table of all runs followed by each schedule's loop nest.
- **Options:** `--time-limit`, `--cores`, `--threads`, `--no-hint`, `--force`, and case names.

## Single einsums: cb_einsum_ml vs. TCM
`python einsum_run.py` maps single einsums on AccelForge's `tpu_v4i` arch with TCM (FFM at O3) and with `cb_einsum_ml_cpsat97`, and writes `results/einsum_summary.md`.
- **Einsums** (`einsum_cases.py`): GPT-3 6.7B's prefill einsums at batch 64 and 65,536 tokens (16 bits), the four einsums of one routed SwiGLU expert of DeepSeek-V4-Pro (`workloads/deepseek_v4_pro_expert.yaml`, 16 bits), and a tensor contraction `C` (`workloads/contraction.yaml`, 8 bits). `C` runs only when named, since TCM has not mapped it within 48 hours.
- **Spec** (`einsum_tcm.spec_for`): the TCM paper artifact's constraints. Both tools' mappings are evaluated by AccelForge on this spec, so their EDPs compare directly.
- **CP-SAT settings** (`einsum_cpsat.SETTINGS`): `redundant_bounds`, `sparse_domains`, `merge_dims` and `partial_sums`, with perfect division (FFM's default mapspace). The architecture is translated into the solver's integer costs by `einsum_cpsat.tpu_v4i`; its docstring explains how.
- **Times:** TCM's is its mapping search, after a warm-up, as in `ffm.py`. CP-SAT's is the whole `cb_einsum_ml` call, with a 120 s limit (`--time-limit`).

| Step | Command it runs | Writes |
|---|---|---|
| tcm | `einsum_tcm.py EINSUM` | `results/<einsum>/tcm.json`, `tcm.txt` (mapping) |
| cpsat | `einsum_cpsat.py EINSUM` | `results/<einsum>/cpsat.json`, `cpsat.txt` (mapping as evaluated by AccelForge, then the solver's output) |

Options: `--list`, `--steps tcm,cpsat`, `--threads N` (both tools), `--time-limit S`, `--force`, `--measure-memory` (see [Measuring memory](#measuring-memory)), `--summarize` (only rewrite the summary), and einsum names.

## Files

| File | Contents |
|---|---|
| `cases.py` | The cases: workload, jinja parameters, einsum subset and capacity. Approximate run times are in its docstring. |
| `workloads/` | Workload yamls not in AccelForge's examples. |
| `common.py` | Paths, result files and machine/version metadata. |
| `export.py` | Exports einsums from AccelForge. Rank variables become the scheduler's dims. A tensor rank indexed by different rank variables in different einsums is a "reinterpreted dim", and is noted. |
| `ffm.py`, `dag.py` | The two tools. |
| `summarize.py` | Writes `results/summary.md`. |
| `run.py` | Runs everything. |
| `cores.py`, `compute_workloads.py` | The core-count runs with compute costs; see above. |
| `einsum_cases.py`, `einsum_tcm.py`, `einsum_cpsat.py`, `einsum_run.py` | The single-einsum comparison: cases, the two tools, and the runner and summary. |

## Adding cases and tests
- **A new multi-einsum case:** add an entry to `CASES` in `cases.py`, with a yaml in `workloads/` if AccelForge's examples don't have the workload.
- **A new single-einsum case:** add an entry to `EINSUM_CASES` in `einsum_cases.py`. Its name is the einsum's name in its workload; its results go to `results/<einsum>/tcm.json` and `cpsat.json`.
