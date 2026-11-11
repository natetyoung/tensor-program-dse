from typing import List

from general_dag_scheduler import scheduler, Einsum


def siso_ssd_intra_chunk_einsums(Q=64, N=128, P=64, K=1) -> List[Einsum]:
    """Logical SISO SSD local contribution, with precomputed FP32 inputs.

    k: independent chunk, t/s: destination/source token, n: state, p: value.
    Physical inputs are X[K,Q,P], B[K,Q,N], C_T[K,N,Q], four [K,Q]
    scaling vectors, and upper-triangular triu[Q,Q] (including diagonal).
    B and X use s in the main branch and t in the token-aligned correction;
    these are index reinterpretations of the same buffers, not new inputs.

    Transposes are expressed by indices, not physical copy operations. The
    separate multiply/reduce stages retain baseline.py's arithmetic order.
    Costs/granularities follow the existing examples: they are uncalibrated
    scheduling weights, not measured Trainium2 times or hardware constraints.
    The extracted NKI baseline supports only Q=64, N=128, P=64; other sizes
    here describe logical scheduling experiments.
    """
    sizes = {"k": K, "t": Q, "s": Q, "n": N, "p": P}
    for name, value in {"Q": Q, "N": N, "P": P, "K": K}.items():
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer, got {value!r}")

    def stage(operands, output, operation, granularity=None):
        used_dims = {dim for dims in operands.values() for dim in dims}
        return Einsum(
            operand_dims=operands,
            output_operand=output,
            dim_sizes={dim: size for dim, size in sizes.items() if dim in used_dims},
            accel_gran=granularity if granularity is not None else {"PRODUCT": 128},
            compute_cost=70710 if operation == "matmul" else 22,
            operation=operation,
        )

    return [
        stage(
            {"X": ("k", "s", "p"), "scale": ("k", "s"), "X_scale": ("k", "s", "p")},
            "X_scale",
            "multiply",
        ),
        stage(
            {"C_T": ("k", "n", "t"), "B": ("k", "s", "n"), "G": ("k", "t", "s")},
            "G",
            "matmul",
            {"k": 1, "t": 512, "s": 128, "n": 128},
        ),
        stage(
            {"G": ("k", "t", "s"), "triu": ("s", "t"), "M": ("k", "t", "s")},
            "M",
            "multiply",
        ),
        stage(
            {"X_scale": ("k", "s", "p"), "e_minus": ("k", "s"), "V": ("k", "s", "p")},
            "V",
            "multiply",
        ),
        stage(
            {"M": ("k", "t", "s"), "V": ("k", "s", "p"), "U": ("k", "t", "p")},
            "U",
            "matmul",
            {"k": 1, "t": 128, "s": 128, "p": 512},
        ),
        stage(
            {"U": ("k", "t", "p"), "e_plus": ("k", "t"), "Y_scaled": ("k", "t", "p")},
            "Y_scaled",
            "multiply",
        ),
        stage(
            {"C_T": ("k", "n", "t"), "B": ("k", "t", "n"), "CB_elem": ("k", "t", "n")},
            "CB_elem",
            "multiply",
        ),
        stage({"CB_elem": ("k", "t", "n"), "cb_diag": ("k", "t")}, "cb_diag", "sum"),
        stage(
            {"cb_diag": ("k", "t"), "shifted_gamma": ("k", "t"), "cb_sg": ("k", "t")},
            "cb_sg",
            "multiply",
        ),
        stage(
            {"X": ("k", "t", "p"), "cb_sg": ("k", "t"), "correction": ("k", "t", "p")},
            "correction",
            "multiply",
        ),
        stage(
            {
                "Y_scaled": ("k", "t", "p"),
                "correction": ("k", "t", "p"),
                "Y_local": ("k", "t", "p"),
            },
            "Y_local",
            "subtract",
        ),
    ]
