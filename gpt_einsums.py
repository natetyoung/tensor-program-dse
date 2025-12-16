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

    # ---------- Q projection ----------
    einsums.append(
        Einsum(
            operand_dims={
                f"{prefix}_X": ("m", "d"),
                f"{prefix}_WQ": ("d", "k"),
                f"{prefix}_Q": ("m", "k"),
            },
            output_operand=f"{prefix}_Q",
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
    tiny_layer = gpt_layer_einsums(
        batch=1,
        seq_len=32,
        model_dim=128,
        prefix="L0"
    )
    small_layer = gpt_layer_einsums(
        batch=1,
        seq_len=64,
        model_dim=256,
        prefix="L0"
    )
    med_layer = gpt_layer_einsums(
        batch=1,
        seq_len=128,
        model_dim=512,
        prefix="L0"
    )
    large_layer = gpt_layer_einsums(
        batch=1,
        seq_len=256,
        model_dim=1024,
        prefix="L0"
    )
    huge_layer = gpt_layer_einsums(
        batch=1,
        seq_len=2048,
        model_dim=4096,
        prefix="L0"
    )

    for e in tiny_layer:
        print(e.operand_dims, "->", e.output_operand)

    c_code = emit_c_program(tiny_layer)
    with open("../../tinygpt.c", "w") as f:
        f.write(c_code)
    caps = [8*1024, 16*1024, 32*1024]
    for cap in caps:
        c_code = emit_c_program(tiny_layer, optimized=True, capacity=cap)
        with open(f"../../tinygpt_opt_{cap}.c", "w") as f:
            f.write(c_code)
    
    c_code = emit_c_program(small_layer)
    with open("../../smallgpt.c", "w") as f:
        f.write(c_code)

    caps = [32*1024, 64*1024, 128*1024]
    for cap in caps:
        c_code = emit_c_program(small_layer, optimized=True, capacity=cap)
        with open(f"../../smallgpt_opt_{cap}.c", "w") as f:
            f.write(c_code)

    c_code = emit_c_program(med_layer)
    with open("../../medgpt.c", "w") as f:
        f.write(c_code)

    caps = [64*1024, 128*1024, 256*1024]
    for cap in caps:
        c_code = emit_c_program(med_layer, optimized=True, capacity=cap)
        with open(f"../../medgpt_opt_{cap}.c", "w") as f:
            f.write(c_code)

    c_code = emit_c_program(large_layer)
    with open("../../largegpt.c", "w") as f:
        f.write(c_code)

    caps = [256*1024, 512*1024, 1024*1024]
    for cap in caps:
        c_code = emit_c_program(large_layer, optimized=True, capacity=cap)
        with open(f"../../largegpt_opt_{cap}.c", "w") as f:
            f.write(c_code)
    
    #c_code = emit_c_program(huge_layer)
    #with open("../../hugegpt.c", "w") as f:
    #    f.write(c_code)
#
    #c_code = emit_c_program(huge_layer, optimized=True)
    #with open("../../hugegpt_opt.c", "w") as f:
    #    f.write(c_code)