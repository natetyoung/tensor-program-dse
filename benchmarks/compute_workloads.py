'''The workloads cores.py runs, as described in this repository's Python
(with their compute_cost, accel_gran and operation), rather than the
AccelForge exports the FFM comparison uses (which have compute_cost = 0).

name -> function returning dict(einsums, capacity, global_outputs), with the
sizes and capacity of the same-named case in cases.py.'''
from common import REPO  # puts the repository on sys.path
from siso_workload import siso_ssd_intra_chunk_einsums
from test_cases import kda_full_batched_decode_einsums, llama_ffn_einsums


WORKLOADS = {
    # test_cases.py's Test Case 6 (its uncommented __main__ arguments). The
    # FFM comparison's swiglu_merged (up and gate merged into one einsum over
    # an extra dim u) is not used: with its compute costs, the scheduler's
    # bound on that einsum's compute (70710 x prod(2 x size) over 5 dims)
    # overflows CP-SAT's 64-bit objective, and CP-SAT rejects the model.
    'swiglu': lambda: dict(
        einsums=llama_ffn_einsums(64 * 1024, 1024, 2048, num_exp=1), capacity=3 * 1024 * 1024),
    # test_cases.py's Test Case 10 (its __main__ arguments).
    'kda_batched': lambda: dict(
        einsums=kda_full_batched_decode_einsums(batch=128, hidden=7168, d_k=128, d_v=128,
                                                heads=96, a_rank=128),
        capacity=3 * 1024 * 1024,
        global_outputs=('S_t', 'k_lin_out', 'q_lin_out', 'v_lin_out', 'out')),
    'siso_k128': lambda: dict(
        einsums=siso_ssd_intra_chunk_einsums(Q=64, N=128, P=64, K=128),
        capacity=3 * 1024 * 1024),
}
