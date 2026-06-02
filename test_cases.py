from general_dag_scheduler import scheduler, Einsum

# Test Case 1: Branching DAG (Shared Input)
# Computes two independent paths starting from a shared input A.
# A(i, j) * W1(j, k) -> B(i, k)
# A(i, j) * W2(j, l) -> C(i, l)
shared_input_einsums = [
    Einsum(
        operand_dims={
            'A': ('i', 'j'),
            'W1': ('j', 'k'),
            'B': ('i', 'k'),
        },
        output_operand='B',
        dim_sizes={'i': 1024, 'j': 512, 'k': 256, 'l': 128}
    ),
    Einsum(
        operand_dims={
            'A': ('i', 'j'),
            'W2': ('j', 'l'),
            'C': ('i', 'l'),
        },
        output_operand='C',
        dim_sizes={'i': 1024, 'j': 512, 'k': 256, 'l': 128}
    )
]

# Test Case 2: Skip-Connection / ResNet Block
# An input X is projected to a different channel size, projected again, and then added back to X.
# X(h, w, c) * W1(c, d) -> Y(h, w, d)
# Y(h, w, d) * W2(d, c) -> Z(h, w, c)
# Z(h, w, c) + X(h, w, c) -> Out(h, w, c) (elementwise skip-addition)
skip_connection_einsums = [
    Einsum(
        operand_dims={
            'X': ('h', 'w', 'c'),
            'W1': ('c', 'd'),
            'Y': ('h', 'w', 'd'),
        },
        output_operand='Y',
        dim_sizes={'h': 64, 'w': 64, 'c': 128, 'd': 256}
    ),
    Einsum(
        operand_dims={
            'Y': ('h', 'w', 'd'),
            'W2': ('d', 'c'),
            'Z': ('h', 'w', 'c'),
        },
        output_operand='Z',
        dim_sizes={'h': 64, 'w': 64, 'c': 128, 'd': 256}
    ),
    Einsum(
        operand_dims={
            'Z': ('h', 'w', 'c'),
            'X': ('h', 'w', 'c'),
            'Out': ('h', 'w', 'c'),
        },
        output_operand='Out',
        dim_sizes={'h': 64, 'w': 64, 'c': 128, 'd': 256}
    )
]

# Test Case 3: Multi-Stage Reduction
# Compresses channel dimensions and then sequentially reduces spatial, then channel dimensions.
# X(n, c, h, w) * W(d, c) -> Y(n, d, h, w)
# Y(n, d, h, w) -> Z(n, d)  (spatial sum reduction over h, w)
# Z(n, d) -> Out(n)         (channel sum reduction over d)
multi_stage_reduction_einsums = [
    Einsum(
        operand_dims={
            'X': ('n', 'c', 'h', 'w'),
            'W': ('d', 'c'),
            'Y': ('n', 'd', 'h', 'w'),
        },
        output_operand='Y',
        dim_sizes={'n': 32, 'c': 64, 'h': 16, 'w': 16, 'd': 128}
    ),
    Einsum(
        operand_dims={
            'Y': ('n', 'd', 'h', 'w'),
            'Z': ('n', 'd'),
        },
        output_operand='Z',
        dim_sizes={'n': 32, 'c': 64, 'h': 16, 'w': 16, 'd': 128}
    ),
    Einsum(
        operand_dims={
            'Z': ('n', 'd'),
            'Out': ('n',),
        },
        output_operand='Out',
        dim_sizes={'n': 32, 'c': 64, 'h': 16, 'w': 16, 'd': 128}
    )
]

# Test Case 4: Attention Projection Block (5 Einsums)
# Computes Q, K, V projections from X. Then contracts Q and K to get S (attention score).
# Finally contracts S and V to compute attention output O.
# X(b, s, h) * WQ(h, d) -> Q(b, s, d)
# X(b, s, h) * WK(h, d) -> K(b, s, d)
# X(b, s, h) * WV(h, d) -> V(b, s, d)
# Q(b, s, d) * K(b, s, d) -> S(b, s, s)  (contracts d)
# S(b, s, s) * V(b, s, d) -> O(b, s, d)  (contracts s)
attention_block_einsums = [
    Einsum(
        operand_dims={
            'X': ('b', 's', 'h'),
            'WQ': ('h', 'd'),
            'Q': ('b', 's', 'd'),
        },
        output_operand='Q',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd': 64}
    ),
    Einsum(
        operand_dims={
            'X': ('b', 's', 'h'),
            'WK': ('h', 'd'),
            'K': ('b', 's', 'd'),
        },
        output_operand='K',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd': 64}
    ),
    Einsum(
        operand_dims={
            'X': ('b', 's', 'h'),
            'WV': ('h', 'd'),
            'V': ('b', 's', 'd'),
        },
        output_operand='V',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd': 64}
    ),
    Einsum(
        operand_dims={
            'Q': ('b', 's', 'd'),
            'K': ('b', 's', 'd'),
            'S': ('b', 's', 's'),
        },
        output_operand='S',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd': 64}
    ),
    Einsum(
        operand_dims={
            'S': ('b', 's', 's'),
            'V': ('b', 's', 'd'),
            'O': ('b', 's', 'd'),
        },
        output_operand='O',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd': 64}
    )
]

attention_block_einsums_breakq = [
    Einsum(
        operand_dims={
            'X': ('b', 's', 'h'),
            'WQ': ('h', 'd'),
            'Q0': ('b', 's', 'd'),
        },
        output_operand='Q0',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd': 64}
    ),
    Einsum(
        operand_dims={
            'X': ('b', 's', 'h'),
            'WK': ('h', 'd'),
            'K': ('b', 's', 'd'),
        },
        output_operand='K',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd': 64}
    ),
    Einsum(
        operand_dims={
            'X': ('b', 's', 'h'),
            'WV': ('h', 'd'),
            'V': ('b', 's', 'd'),
        },
        output_operand='V',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd': 64}
    ),
    Einsum(
        operand_dims={
            'Q1': ('b', 's1', 'd'),
            'K': ('b', 's', 'd'),
            'S': ('b', 's1', 's'),
        },
        output_operand='S',
        dim_sizes={'b': 4, 's1': 256, 's': 256, 'd': 64}
    ),
    Einsum(
        operand_dims={
            'S': ('b', 's1', 's'),
            'V': ('b', 's', 'd'),
            'O': ('b', 's1', 'd'),
        },
        output_operand='O',
        dim_sizes={'b': 4, 's1': 256, 's': 256, 'd': 64}
    )
]

if __name__ == '__main__':
    print("=========================================")
    print("Running Test Case 1: Shared Input (Branching DAG)")
    print("=========================================")
    # Using small capacity to force tile decisions
    scheduler(shared_input_einsums, capacity=512 * 1024, allow_spilling=True)
    
    print("=========================================")
    print("Running Test Case 2: Skip-Connection / ResNet Block")
    print("=========================================")
    scheduler(skip_connection_einsums, capacity=1024 * 1024, allow_spilling=True)
    
    print("=========================================")
    print("Running Test Case 3: Multi-Stage Reduction")
    print("=========================================")
    scheduler(multi_stage_reduction_einsums, capacity=256 * 1024, allow_spilling=True)

    print("=========================================")
    print("Running Test Case 4: Attention Projection Block (break q)")
    print("=========================================")
    scheduler(attention_block_einsums_breakq, capacity=16 * 1024, allow_spilling=True, force_order_A_B=('Q0', 'Q1'))
