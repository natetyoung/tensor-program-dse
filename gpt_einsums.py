from typing import Dict, Tuple, List
from full_tree_cpsat97 import Einsum
from utils import emit_c_program

def gpt_layer_einsums(
    *,
    batch: int,
    seq_len: int,
    model_dim: int,
    ffn_mult: int = 4,
    prefix: str = "L0",
) -> List[Einsum]:
    """
    Generate Einsum objects for one GPT inference layer.
    """

    B, S, D = batch, seq_len, model_dim
    F = ffn_mult * D
    m = B * S

    einsums: List[Einsum] = []

    # ---------- QKV projections ----------
    for proj in ["Q", "K", "V"]:
        einsums.append(
            Einsum(
                operand_dims={
                    f"{prefix}_X": ("m", "d"),
                    f"{prefix}_W{proj}": ("d", "k"),
                    f"{prefix}_{proj}": ("m", "k"),
                },
                output_operand=f"{prefix}_{proj}",
                dim_sizes={
                    "m": m,
                    "d": D,
                    "k": D,
                },
            )
        )

    # ---------- Attention scores: Q x K^T ----------
    einsums.append(
        Einsum(
            operand_dims={
                f"{prefix}_Q": ("m", "k"),
                f"{prefix}_K": ("n", "k"),
                f"{prefix}_S": ("m", "n"),
            },
            output_operand=f"{prefix}_S",
            dim_sizes={
                "m": m,
                "n": S,
                "k": D,
            },
        )
    )

    # ---------- Attention output: S x V ----------
    einsums.append(
        Einsum(
            operand_dims={
                f"{prefix}_S": ("m", "n"),
                f"{prefix}_V": ("n", "k"),
                f"{prefix}_O": ("m", "k"),
            },
            output_operand=f"{prefix}_O",
            dim_sizes={
                "m": m,
                "n": S,
                "k": D,
            },
        )
    )

    # ---------- Output projection ----------
    einsums.append(
        Einsum(
            operand_dims={
                f"{prefix}_O": ("m", "k"),
                f"{prefix}_Wo": ("k", "d"),
                f"{prefix}_Y": ("m", "d"),
            },
            output_operand=f"{prefix}_Y",
            dim_sizes={
                "m": m,
                "k": D,
                "d": D,
            },
        )
    )

    # ---------- FFN layer 1 ----------
    einsums.append(
        Einsum(
            operand_dims={
                f"{prefix}_Y": ("m", "d"),
                f"{prefix}_W1": ("d", "f"),
                f"{prefix}_H": ("m", "f"),
            },
            output_operand=f"{prefix}_H",
            dim_sizes={
                "m": m,
                "d": D,
                "f": F,
            },
        )
    )

    # ---------- FFN layer 2 ----------
    einsums.append(
        Einsum(
            operand_dims={
                f"{prefix}_H": ("m", "f"),
                f"{prefix}_W2": ("f", "d"),
                f"{prefix}_Z": ("m", "d"),
            },
            output_operand=f"{prefix}_Z",
            dim_sizes={
                "m": m,
                "f": F,
                "d": D,
            },
        )
    )

    return einsums

if __name__ == "__main__":
    layer = gpt_layer_einsums(
        batch=1,
        seq_len=2048,
        model_dim=4096,
        prefix="L0"
    )

    for e in layer:
        print(e.operand_dims, "->", e.output_operand)

    c_code = emit_c_program(layer)
    with open("gpt_naive.c", "w") as f:
        f.write(c_code)