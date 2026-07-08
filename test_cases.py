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
            'Q': ('b', 's1', 'd'),
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

# Test Case 5: Transformer Feed-Forward Network
# Projects input X to a larger hidden dimension, applies an elementwise activation, then projects back.
# X(b, s, h) * W1(h, d_ff) -> Y(b, s, d_ff)
# Y(b, s, d_ff) -> Y_act(b, s, d_ff) (elementwise activation)
# Y_act(b, s, d_ff) * W2(d_ff, h) -> Z(b, s, h)
feed_forward_einsums = [
    Einsum(
        operand_dims={
            'X': ('b', 's', 'h'),
            'W1': ('h', 'd_ff'),
            'Y': ('b', 's', 'd_ff'),
        },
        output_operand='Y',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd_ff': 2048}
    ),
    Einsum(
        operand_dims={
            'Y': ('b', 's', 'd_ff'),
            'Y_act': ('b', 's', 'd_ff'),
        },
        output_operand='Y_act',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd_ff': 2048}
    ),
    Einsum(
        operand_dims={
            'Y_act': ('b', 's', 'd_ff'),
            'W2': ('d_ff', 'h'),
            'Z': ('b', 's', 'h'),
        },
        output_operand='Z',
        dim_sizes={'b': 4, 's': 256, 'h': 512, 'd_ff': 2048}
    )
]

# Test Case 6: Llama-style Feed-Forward Network (SwiGLU)
# Uses a gate projection and an up projection, multiplies them, then projects down.
# X(bs, h) * W_up(h, d_ff) -> Y_up(bs, d_ff)
# X(bs, h) * W_gate(h, d_ff) -> Y_gate(bs, d_ff)
# Y_gate(bs, d_ff) -> Y_act(bs, d_ff) (elementwise activation)
# Y_up(bs, d_ff) * Y_act(bs, d_ff) -> Y_mid(bs, d_ff) (elementwise multiplication)
# Y_mid(bs, d_ff) * W_down(d_ff, h) -> Z(bs, h)
def llama_ffn_einsums(bs=128, h=2880, d_ff=2880):
    return [
        Einsum(
            operand_dims={
                'X': ('bs', 'h'),
                'W_up': ('h', 'd_ff'),
                'Y_up': ('bs', 'd_ff'),
            },
            output_operand='Y_up',
            dim_sizes={'bs': bs, 'h': h, 'd_ff': d_ff},
            accel_gran={'bs': 1, 'h': 128, 'd_ff': 128},
            compute_cost=100,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'X': ('bs', 'h'),
                'W_gate': ('h', 'd_ff'),
                'Y_gate': ('bs', 'd_ff'),
            },
            output_operand='Y_gate',
            dim_sizes={'bs': bs, 'h': h, 'd_ff': d_ff},
            accel_gran={'bs': 1, 'h': 128, 'd_ff': 128},
            compute_cost=100,
            operation='matmul'
        ),
        # Einsum(
        #     operand_dims={
        #         'Y_gate': ('bs', 'd_ff'),
        #         'Y_act': ('bs', 'd_ff'),
        #     },
        #     output_operand='Y_act',
        #     dim_sizes={'bs': 128, 'd_ff': 2880},
        #     accel_gran={'PRODUCT': 128},
        #     compute_cost=100,
        #     operation='sigmoid(alpha*clamp(Y_gate))'
        # ),
        Einsum(
            operand_dims={
                'Y_up': ('bs', 'd_ff'),
                'Y_gate': ('bs', 'd_ff'),
                'Y_mid': ('bs', 'd_ff'),
            },
            output_operand='Y_mid',
            dim_sizes={'bs': bs, 'd_ff': d_ff},
            accel_gran={'PRODUCT': 128},
            compute_cost=100,
            operation='elemwise_mul(linear_gate(Y_up),sigmoid(alpha*clamp(Y_gate)))'
        ),
        Einsum(
            operand_dims={
                'Y_mid': ('bs', 'd_ff'),
                'W_down': ('d_ff', 'h'),
                'Z': ('bs', 'h'),
            },
            output_operand='Z',
            dim_sizes={'bs': bs, 'h': h, 'd_ff': d_ff},
            accel_gran={'bs': 1, 'h': 128, 'd_ff': 128},
            compute_cost=100,
            operation='matmul'
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
    scheduler(attention_block_einsums_breakq, capacity=16 * 1024, allow_spilling=True)

    print("=========================================")
    print("Running Test Case 5: Transformer Feed-Forward Network")
    print("=========================================")
    scheduler(feed_forward_einsums, capacity=512 * 1024, allow_spilling=True)

    print("=========================================")
    print("Running Test Case 6: Llama-style Feed-Forward Network (SwiGLU)")
    print("=========================================")
    scheduler(llama_ffn_einsums(128, 2880, 2880), capacity=512 * 1024, allow_spilling=True)
