from typing import List

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

def attention_block_einsums_breakq(b=1, s=256, s1=256, h=512, d=64):
    return [
        Einsum(
            operand_dims={
                'X': ('b', 's', 'h'),
                'WQ': ('h', 'd'),
                'Q': ('b', 's', 'd'),
            },
            output_operand='Q',
            dim_sizes={'b': b, 's': s, 'h': h, 'd': d},
            accel_gran={'s': 512, 'h': 128, 'd': 128},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'X': ('b', 's', 'h'),
                'WK': ('h', 'd'),
                'K': ('b', 's', 'd'),
            },
            output_operand='K',
            dim_sizes={'b': b, 's': s, 'h': h, 'd': d},
            accel_gran={'s': 512, 'h': 128, 'd': 128},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'X': ('b', 's', 'h'),
                'WV': ('h', 'd'),
                'V': ('b', 's', 'd'),
            },
            output_operand='V',
            dim_sizes={'b': b, 's': s, 'h': h, 'd': d},
            accel_gran={'s': 128, 'h': 128, 'd': 512},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'Q': ('b', 's1', 'd'),
                'K': ('b', 's', 'd'),
                'S': ('b', 's1', 's'),
            },
            output_operand='S',
            dim_sizes={'b': b, 's1': s1, 's': s, 'd': d},
            accel_gran={'s': 128, 's1': 512, 'd': 128},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'S': ('b', 's1', 's'),
                'V': ('b', 's', 'd'),
                'O': ('b', 's1', 'd'),
            },
            output_operand='O',
            dim_sizes={'b': b, 's1': s1, 's': s, 'd': d},
            accel_gran={'s1': 512, 's': 128, 'd': 128},
            compute_cost=70710,
            operation='matmul'
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
def llama_ffn_einsums(bs=128, h=2880, d_ff=2880, num_exp=1):
    return [
        Einsum(
            operand_dims={
                'X': ('bs', 'h'),
                'W_up': ('h', 'd_ff', 'e'),
                'Y_up': ('bs', 'd_ff', 'e'),
            },
            output_operand='Y_up',
            dim_sizes={'bs': bs, 'h': h, 'd_ff': d_ff, 'e': num_exp},
            accel_gran={'bs': 128, 'h': 128, 'd_ff': 512, 'e': 1},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'X': ('bs', 'h'),
                'W_gate': ('h', 'd_ff', 'e'),
                'Y_gate': ('bs', 'd_ff', 'e'),
            },
            output_operand='Y_gate',
            dim_sizes={'bs': bs, 'h': h, 'd_ff': d_ff, 'e': num_exp},
            accel_gran={'bs': 128, 'h': 128, 'd_ff': 512, 'e': 1},
            compute_cost=70710,
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
                'Y_up': ('bs', 'd_ff', 'e'),
                'Y_gate': ('bs', 'd_ff', 'e'),
                'Y_mid': ('bs', 'd_ff', 'e'),
            },
            output_operand='Y_mid',
            dim_sizes={'bs': bs, 'd_ff': d_ff, 'e': num_exp},
            accel_gran={'PRODUCT': 128},
            compute_cost=44,
            operation='elemwise_mul(linear_gate(Y_up),sigmoid(alpha*clamp(Y_gate)))'
        ),
        Einsum(
            operand_dims={
                'Y_mid': ('bs', 'd_ff', 'e'),
                'W_down': ('d_ff', 'h1', 'e'),
                'Z': ('bs', 'h1'),
            },
            output_operand='Z',
            dim_sizes={'bs': bs, 'h1': h, 'd_ff': d_ff, 'e': num_exp},
            accel_gran={'bs': 128, 'h1': 512, 'd_ff': 128, 'e': 1},
            compute_cost=70710,
            operation='matmul'
        )
    ]

# Test Case 7: Attention decode
def attention_decode_einsums(b=1, s=256, s1=1, h=128, d=512):
    return [
        Einsum(
            operand_dims={
                'X': ('b', 's1', 'h'),
                'WQ': ('h', 'd'),
                'Q': ('b', 's1', 'd'),
            },
            output_operand='Q',
            dim_sizes={'b': b, 's1': s1, 'h': h, 'd': d},
            accel_gran={'b': 512, 's1': 1, 'h': 128, 'd': 128},
            compute_cost=100,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'Q': ('b', 's1', 'd'),
                'K': ('b', 's', 'd'),
                'S': ('b', 's1', 's'),
            },
            output_operand='S',
            dim_sizes={'b': b, 's1': s1, 's': s, 'd': d},
            accel_gran={'b': 512, 's1': 1, 's': 128, 'd': 128},
            compute_cost=100,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'S': ('b', 's1', 's'),
                'V': ('b', 's', 'd'),
                'O': ('b', 's1', 'd'),
            },
            output_operand='O',
            dim_sizes={'b': b, 's1': s1, 's': s, 'd': d},
            accel_gran={'b': 512, 's1': 1, 's': 128, 'd': 128},
            compute_cost=100,
            operation='matmul'
        )
    ]

# Test Case 8: KDA core decode
def kda_core_decode_einsums(d_k=128, d_v=128, heads=96):
    # S_t = (I - β_t k_t k_t^T) Diag(α_t) S_{t-1} + β_t k_t v_t^T
    # = 
    # K3 numbers are as given: d_k=128, d_v=128, heads=96
    return [
        Einsum(
            operand_dims={
                'k': ('d_k0', 'h'),
                'b': ('h',),
                'bk': ('d_k0', 'h')
            },
            output_operand='bk',
            dim_sizes={'h': heads, 'd_k0': d_k},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='elew_mul'
        ),
        Einsum(
            operand_dims={
                'bk': ('d_k0', 'h'),
                'k': ('d_k1', 'h'),
                'a': ('d_k1', 'h'),
                '1bkka': ('d_k0', 'd_k1', 'h')
            },
            output_operand='1bkka',
            dim_sizes={'h': heads, 'd_k0': d_k, 'd_k1': d_k},
            accel_gran={'PRODUCT': 128},
            compute_cost=4 * 22,
            operation='(I - b k k^T) Diag(a)'
        ),
        Einsum(
            operand_dims={
                '1bkka': ('d_k0', 'd_k1', 'h'),
                'S_{t-1}': ('d_k1', 'd_v', 'h'),
                '1bkkas': ('d_k0', 'd_v', 'h')
            },
            output_operand='1bkkas',
            dim_sizes={'h': heads, 'd_k0': d_k, 'd_k1': d_k, 'd_v': d_v},
            accel_gran={'d_k0': 128, 'd_k1': 128, 'd_v': 512, 'h': 1},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'bk': ('d_k0', 'h'),
                'v': ('d_v', 'h'),
                'bkv': ('d_k0', 'd_v', 'h')
            },
            output_operand='bkv',
            dim_sizes={'h': heads, 'd_k0': d_k, 'd_v': d_v},
            accel_gran={'PRODUCT': 128},
            compute_cost=2 * 22,
            operation='elew_mul'
        ),
        Einsum(
            operand_dims={
                '1bkkas': ('d_k0', 'd_v', 'h'),
                'bkv': ('d_k0', 'd_v', 'h'),
                'S_t': ('d_k0', 'd_v', 'h')
            },
            output_operand='S_t',
            dim_sizes={'h': heads, 'd_k0': d_k, 'd_v': d_v},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='elew_add'
        )
    ]

def lcan_einsums(name, hidden=7168, d_out=128, d_out_name='d_k', heads=96, norm=True):
    ret = [
        Einsum(
            operand_dims={
                'hidden': ('hidden',),
                name+'_lin_w': ('hidden', d_out_name, 'h'),
                name+'_lin_out': (d_out_name, 'h')
            },
            output_operand=name+'_lin_out',
            dim_sizes={'hidden': hidden, d_out_name: d_out, 'h': heads},
            accel_gran={'hidden': 128, (d_out_name, 'h'): 128},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                name+'_history': (d_out_name, 'h', 'hist'),
                name+'_conv_w': (d_out_name, 'h', 'hist'),
                name+'_partial_conv': (d_out_name, 'h')
            },
            output_operand=name+'_partial_conv',
            dim_sizes={'hist': 3, d_out_name: d_out, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=44,
            operation='batched_dotproduct'
        ),
        Einsum(
            operand_dims={
                name+'_lin_out': (d_out_name, 'h'),
                name+'_conv_w_0': (d_out_name, 'h'),
                name+'_lin_out_scaled': (d_out_name, 'h')
            },
            output_operand=name+'_lin_out_scaled',
            dim_sizes={d_out_name: d_out, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='elew_mul'
        ),
        Einsum(
            operand_dims={
                name+'_lin_out_scaled': (d_out_name, 'h'),
                name+'_partial_conv': (d_out_name, 'h'),
                name+'_act_out' if norm else name: (d_out_name, 'h')
            },
            output_operand=name+'_act_out' if norm else name,
            dim_sizes={d_out_name: d_out, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=44,
            operation='silu(elew_add)'
        )
    ]
    if norm:
        ret.append(
            Einsum(
                operand_dims={
                    name+'_act_out': (d_out_name, 'h'),
                    name+'_computed_norm': ('h',)
                },
                output_operand=name+'_computed_norm',
                dim_sizes={d_out_name: d_out, 'h': heads},
                accel_gran={'PRODUCT': 128},
                compute_cost=22,
                operation='l2_norm_compute'
            )
        )
        ret.append(
            Einsum(
                operand_dims={
                    name+'_act_out': (d_out_name, 'h'),
                    name+'_computed_norm': ('h',),
                    name: (d_out_name, 'h')
                },
                output_operand=name,
                dim_sizes={d_out_name: d_out, 'h': heads},
                accel_gran={'PRODUCT': 128},
                compute_cost=22,
                operation='l2_norm_divide'
            )
        )
    return ret

# Test Case 9: KDA Full Decode
def kda_full_decode_einsums(hidden=7168, d_k=128, d_v=128, heads=96, a_rank=128):
    # (mostly from diagram, not actual code)
    # qk: linear->shortconv->act->norm
    # v: linear->shortconv->act
    # a: linear_dn->linear_up->sigmoid
    # b: linear_dn->sigmoid
    # bypass: linear_dn->linear_up->sigmoid
    # output=linear(norm(KDA_core(qk, v, a, b)) * bypass)
    einsums = []
    einsums += lcan_einsums('q', hidden=hidden, d_out=d_k, d_out_name='d_k1', heads=heads, norm=True)
    einsums += lcan_einsums('k', hidden=hidden, d_out=d_k, d_out_name='d_k0', heads=heads, norm=True)
    einsums += lcan_einsums('v', hidden=hidden, d_out=d_v, d_out_name='d_v', heads=heads, norm=False)
    einsums += [ # a and b
        Einsum(
            operand_dims={
                'hidden': ('hidden',),
                'W_a_down': ('hidden', 'a_rank'),
                'a_down': ('a_rank',)
            },
            output_operand='a_down',
            dim_sizes={'hidden': hidden, 'a_rank': a_rank},
            accel_gran={'hidden': 128, 'a_rank': 128},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                'a_down': ('a_rank',),
                'W_a_up': ('a_rank', 'd_k1', 'h'),
                'a_inter': ('d_k1', 'h')
            },
            output_operand='a_inter',
            dim_sizes={'a_rank': a_rank, 'h': heads, 'd_k1': d_k},
            accel_gran={'a_rank': 128, ('d_k1', 'h'): 128},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                'a_inter': ('d_k1', 'h'),
                'exp_alog': ('h',),
                'dt_bias': ('d_k1', 'h'),
                'a': ('d_k1', 'h')
            },
            output_operand='a',
            dim_sizes={'d_k1': d_k, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=110,
            operation='exp(-5*sigmoid(exp_alog*(a_inter+dt_bias)))'
        ),
        Einsum(
            operand_dims={
                'hidden': ('hidden',),
                'W_b_down': ('hidden', 'h'),
                'b_inter': ('h',)
            },
            output_operand='b_inter',
            dim_sizes={'hidden': hidden, 'h': heads},
            accel_gran={'hidden': 128, 'h': 128},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                'b_inter': ('h',),
                'b': ('h',)
            },
            output_operand='b',
            dim_sizes={'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='sigmoid'
        )
    ]
    einsums += kda_core_decode_einsums(d_k=d_k, d_v=d_v, heads=heads)
    einsums += [ # S_{t-1}q -> RMSNorm
        Einsum(
            operand_dims={
                'S_t': ('d_k1', 'd_v', 'h'),
                'q': ('d_k1', 'h'),
                'o': ('d_v', 'h')
            },
            output_operand='o',
            dim_sizes={'d_k1': d_k, 'd_v': d_v, 'h': heads},
            accel_gran={'d_k1': 128, 'd_v': 128, 'h': 1},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                'o': ('d_v', 'h'),
                'computed_o_rmsnorm': ('h',)
            },
            output_operand='computed_o_rmsnorm',
            dim_sizes={'d_v': d_v, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='rmsnorm'
        )
    ]
    einsums += [ # bypass
        Einsum(
            operand_dims={
                'hidden': ('hidden',),
                'W_g': ('hidden', 'd_v', 'h'),
                'g_inter': ('d_v', 'h')
            },
            output_operand='g_inter',
            dim_sizes={'hidden': hidden, 'h': heads, 'd_v': d_v},
            accel_gran={'hidden': 128, ('d_v', 'h'): 128},
            compute_cost=4481,
            operation='matvec'
        )
    ]
    einsums += [ # final output
        Einsum(
            operand_dims={
                'o': ('d_v', 'h'),
                'computed_o_rmsnorm': ('h',),
                'norm_weight': ('d_v',),
                'g_inter': ('d_v', 'h'),
                'o_bypassed': ('d_v', 'h')
            },
            output_operand='o_bypassed',
            dim_sizes={'d_v': d_v, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='o / computed_o_rmsnorm * norm_weight * sigmoid(g_inter)'
        ),
        Einsum(
            operand_dims={
                'o_bypassed': ('d_v', 'h'),
                'W_out': ('d_v', 'h', 'out_hidden'),
                'out': ('out_hidden',)
            },
            output_operand='out',
            dim_sizes={'d_v': d_v, 'h': heads, 'out_hidden': hidden},
            accel_gran={('d_v', 'h'): 128, 'out_hidden': 128},
            compute_cost=4481,
            operation='matvec'
        )
    ]
    return einsums

def head_dims(heads, rep=1):
    # Head dims of an operand.  When several value heads share one key head
    # (GQA-style, as in larger Qwen3.5 GDN layers), the value-head axis is split
    # into ('h', 'r'): 'h' indexes the key head and 'r' the value head within it.
    if rep > 1:
        return ('h', 'r'), {'h': heads, 'r': rep}
    return ('h',), {'h': heads}

# lcan_einsums with GDN's head layout and configurable short-conv history.
def gdn_lcan_einsums(name, hidden=1024, d_out=128, d_out_name='d_k', heads=16, norm=True, rep=1, hist=3):
    hd, hs = head_dims(heads, rep)
    ret = [
        Einsum(
            operand_dims={
                'hidden': ('hidden',),
                name+'_lin_w': ('hidden', d_out_name) + hd,
                name+'_lin_out': (d_out_name,) + hd
            },
            output_operand=name+'_lin_out',
            dim_sizes={'hidden': hidden, d_out_name: d_out, **hs},
            accel_gran={'hidden': 128, (d_out_name,) + hd: 128},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                name+'_history': (d_out_name,) + hd + ('hist',),
                name+'_conv_w': (d_out_name,) + hd + ('hist',),
                name+'_partial_conv': (d_out_name,) + hd
            },
            output_operand=name+'_partial_conv',
            dim_sizes={'hist': hist, d_out_name: d_out, **hs},
            accel_gran={'PRODUCT': 128},
            compute_cost=44,
            operation='batched_dotproduct'
        ),
        Einsum(
            operand_dims={
                name+'_lin_out': (d_out_name,) + hd,
                name+'_conv_w_0': (d_out_name,) + hd,
                name+'_lin_out_scaled': (d_out_name,) + hd
            },
            output_operand=name+'_lin_out_scaled',
            dim_sizes={d_out_name: d_out, **hs},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='elew_mul'
        ),
        Einsum(
            operand_dims={
                name+'_lin_out_scaled': (d_out_name,) + hd,
                name+'_partial_conv': (d_out_name,) + hd,
                name+'_act_out' if norm else name: (d_out_name,) + hd
            },
            output_operand=name+'_act_out' if norm else name,
            dim_sizes={d_out_name: d_out, **hs},
            accel_gran={'PRODUCT': 128},
            compute_cost=44,
            operation='silu(elew_add)'
        )
    ]
    if norm:
        ret.append(
            Einsum(
                operand_dims={
                    name+'_act_out': (d_out_name,) + hd,
                    name+'_computed_norm': hd
                },
                output_operand=name+'_computed_norm',
                dim_sizes={d_out_name: d_out, **hs},
                accel_gran={'PRODUCT': 128},
                compute_cost=22,
                operation='l2_norm_compute'
            )
        )
        ret.append(
            Einsum(
                operand_dims={
                    name+'_act_out': (d_out_name,) + hd,
                    name+'_computed_norm': hd,
                    name: (d_out_name,) + hd
                },
                output_operand=name,
                dim_sizes={d_out_name: d_out, **hs},
                accel_gran={'PRODUCT': 128},
                compute_cost=22,
                operation='l2_norm_divide'
            )
        )
    return ret

# Test Case 11: GDN core decode
def gdn_core_decode_einsums(d_k=128, d_v=128, k_heads=16, v_heads=16):
    # S_t = g_t S_{t-1} + k_t (β_t (v_t - g_t S_{t-1}^T k_t))^T
    # Unlike KDA, the decay g_t is a scalar per head, so it is folded into the
    # state read and update rather than forming (I - β k k^T) Diag(α) explicitly.
    # Defaults are Qwen3.5-0.8B (qwen3.5-pytorch/config.py).
    rep = v_heads // k_heads
    hd, hs = head_dims(k_heads, rep)
    return [
        Einsum(
            operand_dims={
                'S_{t-1}': ('d_k0', 'd_v') + hd,
                'k': ('d_k0', 'h'),
                'kv_mem': ('d_v',) + hd
            },
            output_operand='kv_mem',
            dim_sizes={'d_k0': d_k, 'd_v': d_v, **hs},
            accel_gran={'d_k0': 128, 'd_v': 128, **{d: 1 for d in hd}},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                'v': ('d_v',) + hd,
                'kv_mem': ('d_v',) + hd,
                'g': hd,
                'b': hd,
                'delta': ('d_v',) + hd
            },
            output_operand='delta',
            dim_sizes={'d_v': d_v, **hs},
            accel_gran={'PRODUCT': 128},
            compute_cost=3 * 22,
            operation='b * (v - g * kv_mem)'
        ),
        Einsum(
            operand_dims={
                'S_{t-1}': ('d_k0', 'd_v') + hd,
                'g': hd,
                'k': ('d_k0', 'h'),
                'delta': ('d_v',) + hd,
                'S_t': ('d_k0', 'd_v') + hd
            },
            output_operand='S_t',
            dim_sizes={'d_k0': d_k, 'd_v': d_v, **hs},
            accel_gran={'PRODUCT': 128},
            compute_cost=3 * 22,
            operation='g * S_{t-1} + k delta^T'
        )
    ]

# Test Case 12: GDN Full Decode
def gdn_full_decode_einsums(hidden=1024, d_k=128, d_v=128, k_heads=16, v_heads=16, conv_kernel=4):
    # From qwen3.5-pytorch/model.py GatedDeltaNet:
    # qk: linear->shortconv->silu->l2norm (q also scaled by 1/sqrt(d_k))
    # v: linear->shortconv->silu
    # g: linear->exp(-exp(A_log) * softplus(. + dt_bias))
    # b: linear->sigmoid
    # z: linear
    # output=linear(rmsnorm(GDN_core(qk, v, g, b)) * silu(z))
    # The fused in_proj_qkv is split into q, k and v projections; the depthwise
    # short conv acts per channel, so this is equivalent.
    rep = v_heads // k_heads
    hd, hs = head_dims(k_heads, rep)
    einsums = []
    einsums += gdn_lcan_einsums('q', hidden=hidden, d_out=d_k, d_out_name='d_k1', heads=k_heads, norm=True, hist=conv_kernel - 1)
    einsums += gdn_lcan_einsums('k', hidden=hidden, d_out=d_k, d_out_name='d_k0', heads=k_heads, norm=True, hist=conv_kernel - 1)
    einsums += gdn_lcan_einsums('v', hidden=hidden, d_out=d_v, d_out_name='d_v', heads=k_heads, norm=False, rep=rep, hist=conv_kernel - 1)
    einsums += [ # g and b
        Einsum(
            operand_dims={
                'hidden': ('hidden',),
                'W_a': ('hidden',) + hd,
                'a_inter': hd
            },
            output_operand='a_inter',
            dim_sizes={'hidden': hidden, **hs},
            accel_gran={'hidden': 128, hd: 128},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                'a_inter': hd,
                'exp_alog': hd,
                'dt_bias': hd,
                'g': hd
            },
            output_operand='g',
            dim_sizes=dict(hs),
            accel_gran={'PRODUCT': 128},
            compute_cost=110,
            operation='exp(-exp_alog*softplus(a_inter+dt_bias))'
        ),
        Einsum(
            operand_dims={
                'hidden': ('hidden',),
                'W_b': ('hidden',) + hd,
                'b_inter': hd
            },
            output_operand='b_inter',
            dim_sizes={'hidden': hidden, **hs},
            accel_gran={'hidden': 128, hd: 128},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                'b_inter': hd,
                'b': hd
            },
            output_operand='b',
            dim_sizes=dict(hs),
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='sigmoid'
        )
    ]
    einsums += gdn_core_decode_einsums(d_k=d_k, d_v=d_v, k_heads=k_heads, v_heads=v_heads)
    einsums += [ # S_t q -> RMSNorm
        Einsum(
            operand_dims={
                'S_t': ('d_k1', 'd_v') + hd,
                'q': ('d_k1', 'h'),
                'o': ('d_v',) + hd
            },
            output_operand='o',
            dim_sizes={'d_k1': d_k, 'd_v': d_v, **hs},
            accel_gran={'d_k1': 128, 'd_v': 128, **{d: 1 for d in hd}},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                'o': ('d_v',) + hd,
                'computed_o_rmsnorm': hd
            },
            output_operand='computed_o_rmsnorm',
            dim_sizes={'d_v': d_v, **hs},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='rmsnorm'
        )
    ]
    einsums += [ # output gate
        Einsum(
            operand_dims={
                'hidden': ('hidden',),
                'W_z': ('hidden', 'd_v') + hd,
                'z': ('d_v',) + hd
            },
            output_operand='z',
            dim_sizes={'hidden': hidden, 'd_v': d_v, **hs},
            accel_gran={'hidden': 128, ('d_v',) + hd: 128},
            compute_cost=4481,
            operation='matvec'
        )
    ]
    einsums += [ # final output
        Einsum(
            operand_dims={
                'o': ('d_v',) + hd,
                'computed_o_rmsnorm': hd,
                'norm_weight': ('d_v',),
                'z': ('d_v',) + hd,
                'o_gated': ('d_v',) + hd
            },
            output_operand='o_gated',
            dim_sizes={'d_v': d_v, **hs},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='o / computed_o_rmsnorm * norm_weight * silu(z)'
        ),
        Einsum(
            operand_dims={
                'o_gated': ('d_v',) + hd,
                'W_out': ('d_v',) + hd + ('out_hidden',),
                'out': ('out_hidden',)
            },
            output_operand='out',
            dim_sizes={'d_v': d_v, **hs, 'out_hidden': hidden},
            accel_gran={('d_v',) + hd: 128, 'out_hidden': 128},
            compute_cost=4481,
            operation='matvec'
        )
    ]
    return einsums

# Batched variants of Test Cases 8 and 9.  Activations, short-conv history and
# recurrent state gain a 'batch' dim; weights are shared across the batch.
# Weight projections (matvecs at batch 1) become matmuls with the batch on the
# 128-wide accelerator axis, as in llama_ffn_einsums.  Per-sequence state
# contractions have no reuse across the batch, so 'batch' has granularity 1.
def kda_core_batched_decode_einsums(batch=32, d_k=128, d_v=128, heads=96):
    return [
        Einsum(
            operand_dims={
                'k': ('batch', 'd_k0', 'h'),
                'b': ('batch', 'h'),
                'bk': ('batch', 'd_k0', 'h')
            },
            output_operand='bk',
            dim_sizes={'batch': batch, 'h': heads, 'd_k0': d_k},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='elew_mul'
        ),
        Einsum(
            operand_dims={
                'bk': ('batch', 'd_k0', 'h'),
                'k': ('batch', 'd_k1', 'h'),
                'a': ('batch', 'd_k1', 'h'),
                '1bkka': ('batch', 'd_k0', 'd_k1', 'h')
            },
            output_operand='1bkka',
            dim_sizes={'batch': batch, 'h': heads, 'd_k0': d_k, 'd_k1': d_k},
            accel_gran={'PRODUCT': 128},
            compute_cost=4 * 22,
            operation='(I - b k k^T) Diag(a)'
        ),
        Einsum(
            operand_dims={
                '1bkka': ('batch', 'd_k0', 'd_k1', 'h'),
                'S_{t-1}': ('batch', 'd_k1', 'd_v', 'h'),
                '1bkkas': ('batch', 'd_k0', 'd_v', 'h')
            },
            output_operand='1bkkas',
            dim_sizes={'batch': batch, 'h': heads, 'd_k0': d_k, 'd_k1': d_k, 'd_v': d_v},
            accel_gran={'d_k0': 128, 'd_k1': 128, 'd_v': 512, 'h': 1, 'batch': 1},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'bk': ('batch', 'd_k0', 'h'),
                'v': ('batch', 'd_v', 'h'),
                'bkv': ('batch', 'd_k0', 'd_v', 'h')
            },
            output_operand='bkv',
            dim_sizes={'batch': batch, 'h': heads, 'd_k0': d_k, 'd_v': d_v},
            accel_gran={'PRODUCT': 128},
            compute_cost=2 * 22,
            operation='elew_mul'
        ),
        Einsum(
            operand_dims={
                '1bkkas': ('batch', 'd_k0', 'd_v', 'h'),
                'bkv': ('batch', 'd_k0', 'd_v', 'h'),
                'S_t': ('batch', 'd_k0', 'd_v', 'h')
            },
            output_operand='S_t',
            dim_sizes={'batch': batch, 'h': heads, 'd_k0': d_k, 'd_v': d_v},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='elew_add'
        )
    ]

def lcan_batched_einsums(name, batch=32, hidden=7168, d_out=128, d_out_name='d_k', heads=96, norm=True):
    ret = [
        Einsum(
            operand_dims={
                'hidden': ('batch', 'hidden'),
                name+'_lin_w': ('hidden', d_out_name, 'h'),
                name+'_lin_out': ('batch', d_out_name, 'h')
            },
            output_operand=name+'_lin_out',
            dim_sizes={'batch': batch, 'hidden': hidden, d_out_name: d_out, 'h': heads},
            accel_gran={'batch': 128, 'hidden': 128, (d_out_name, 'h'): 512},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                name+'_history': ('batch', d_out_name, 'h', 'hist'),
                name+'_conv_w': (d_out_name, 'h', 'hist'),
                name+'_partial_conv': ('batch', d_out_name, 'h')
            },
            output_operand=name+'_partial_conv',
            dim_sizes={'batch': batch, 'hist': 3, d_out_name: d_out, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=44,
            operation='batched_dotproduct'
        ),
        Einsum(
            operand_dims={
                name+'_lin_out': ('batch', d_out_name, 'h'),
                name+'_conv_w_0': (d_out_name, 'h'),
                name+'_lin_out_scaled': ('batch', d_out_name, 'h')
            },
            output_operand=name+'_lin_out_scaled',
            dim_sizes={'batch': batch, d_out_name: d_out, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='elew_mul'
        ),
        Einsum(
            operand_dims={
                name+'_lin_out_scaled': ('batch', d_out_name, 'h'),
                name+'_partial_conv': ('batch', d_out_name, 'h'),
                name+'_act_out' if norm else name: ('batch', d_out_name, 'h')
            },
            output_operand=name+'_act_out' if norm else name,
            dim_sizes={'batch': batch, d_out_name: d_out, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=44,
            operation='silu(elew_add)'
        )
    ]
    if norm:
        ret.append(
            Einsum(
                operand_dims={
                    name+'_act_out': ('batch', d_out_name, 'h'),
                    name+'_computed_norm': ('batch', 'h')
                },
                output_operand=name+'_computed_norm',
                dim_sizes={'batch': batch, d_out_name: d_out, 'h': heads},
                accel_gran={'PRODUCT': 128},
                compute_cost=22,
                operation='l2_norm_compute'
            )
        )
        ret.append(
            Einsum(
                operand_dims={
                    name+'_act_out': ('batch', d_out_name, 'h'),
                    name+'_computed_norm': ('batch', 'h'),
                    name: ('batch', d_out_name, 'h')
                },
                output_operand=name,
                dim_sizes={'batch': batch, d_out_name: d_out, 'h': heads},
                accel_gran={'PRODUCT': 128},
                compute_cost=22,
                operation='l2_norm_divide'
            )
        )
    return ret

# Test Case 10: KDA Full Decode, batched
def kda_full_batched_decode_einsums(batch=32, hidden=7168, d_k=128, d_v=128, heads=96, a_rank=128):
    einsums = []
    einsums += lcan_batched_einsums('q', batch=batch, hidden=hidden, d_out=d_k, d_out_name='d_k1', heads=heads, norm=True)
    einsums += lcan_batched_einsums('k', batch=batch, hidden=hidden, d_out=d_k, d_out_name='d_k0', heads=heads, norm=True)
    einsums += lcan_batched_einsums('v', batch=batch, hidden=hidden, d_out=d_v, d_out_name='d_v', heads=heads, norm=False)
    einsums += [ # a and b
        Einsum(
            operand_dims={
                'hidden': ('batch', 'hidden'),
                'W_a_down': ('hidden', 'a_rank'),
                'a_down': ('batch', 'a_rank')
            },
            output_operand='a_down',
            dim_sizes={'batch': batch, 'hidden': hidden, 'a_rank': a_rank},
            accel_gran={'batch': 128, 'hidden': 128, 'a_rank': 512},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'a_down': ('batch', 'a_rank'),
                'W_a_up': ('a_rank', 'd_k1', 'h'),
                'a_inter': ('batch', 'd_k1', 'h')
            },
            output_operand='a_inter',
            dim_sizes={'batch': batch, 'a_rank': a_rank, 'h': heads, 'd_k1': d_k},
            accel_gran={'batch': 128, 'a_rank': 128, ('d_k1', 'h'): 512},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'a_inter': ('batch', 'd_k1', 'h'),
                'exp_alog': ('h',),
                'dt_bias': ('d_k1', 'h'),
                'a': ('batch', 'd_k1', 'h')
            },
            output_operand='a',
            dim_sizes={'batch': batch, 'd_k1': d_k, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=110,
            operation='exp(-5*sigmoid(exp_alog*(a_inter+dt_bias)))'
        ),
        Einsum(
            operand_dims={
                'hidden': ('batch', 'hidden'),
                'W_b_down': ('hidden', 'h'),
                'b_inter': ('batch', 'h')
            },
            output_operand='b_inter',
            dim_sizes={'batch': batch, 'hidden': hidden, 'h': heads},
            accel_gran={'batch': 128, 'hidden': 128, 'h': 512},
            compute_cost=70710,
            operation='matmul'
        ),
        Einsum(
            operand_dims={
                'b_inter': ('batch', 'h'),
                'b': ('batch', 'h')
            },
            output_operand='b',
            dim_sizes={'batch': batch, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='sigmoid'
        )
    ]
    einsums += kda_core_batched_decode_einsums(batch=batch, d_k=d_k, d_v=d_v, heads=heads)
    einsums += [ # S_{t-1}q -> RMSNorm
        Einsum(
            operand_dims={
                'S_t': ('batch', 'd_k1', 'd_v', 'h'),
                'q': ('batch', 'd_k1', 'h'),
                'o': ('batch', 'd_v', 'h')
            },
            output_operand='o',
            dim_sizes={'batch': batch, 'd_k1': d_k, 'd_v': d_v, 'h': heads},
            accel_gran={'d_k1': 128, 'd_v': 128, 'h': 1, 'batch': 1},
            compute_cost=4481,
            operation='matvec'
        ),
        Einsum(
            operand_dims={
                'o': ('batch', 'd_v', 'h'),
                'computed_o_rmsnorm': ('batch', 'h')
            },
            output_operand='computed_o_rmsnorm',
            dim_sizes={'batch': batch, 'd_v': d_v, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='rmsnorm'
        )
    ]
    einsums += [ # bypass
        Einsum(
            operand_dims={
                'hidden': ('batch', 'hidden'),
                'W_g': ('hidden', 'd_v', 'h'),
                'g_inter': ('batch', 'd_v', 'h')
            },
            output_operand='g_inter',
            dim_sizes={'batch': batch, 'hidden': hidden, 'h': heads, 'd_v': d_v},
            accel_gran={'batch': 128, 'hidden': 128, ('d_v', 'h'): 512},
            compute_cost=70710,
            operation='matmul'
        )
    ]
    einsums += [ # final output
        Einsum(
            operand_dims={
                'o': ('batch', 'd_v', 'h'),
                'computed_o_rmsnorm': ('batch', 'h'),
                'norm_weight': ('d_v',),
                'g_inter': ('batch', 'd_v', 'h'),
                'o_bypassed': ('batch', 'd_v', 'h')
            },
            output_operand='o_bypassed',
            dim_sizes={'batch': batch, 'd_v': d_v, 'h': heads},
            accel_gran={'PRODUCT': 128},
            compute_cost=22,
            operation='o / computed_o_rmsnorm * norm_weight * sigmoid(g_inter)'
        ),
        Einsum(
            operand_dims={
                'o_bypassed': ('batch', 'd_v', 'h'),
                'W_out': ('d_v', 'h', 'out_hidden'),
                'out': ('batch', 'out_hidden')
            },
            output_operand='out',
            dim_sizes={'batch': batch, 'd_v': d_v, 'h': heads, 'out_hidden': hidden},
            accel_gran={'batch': 128, ('d_v', 'h'): 128, 'out_hidden': 512},
            compute_cost=70710,
            operation='matmul'
        )
    ]
    return einsums


def einsum_by_einsum_scheduler(
    einsums: List[Einsum],
    capacity: int,
    num_cores: int = 1,
    enforce_optimal_placement: bool = True,
    allow_spilling: bool = False
):
    total_compute = 0
    total_comm = 0
    for e in einsums:
        sm, solver = scheduler([e], capacity, num_cores, enforce_optimal_placement, allow_spilling, debug=False)
        total_compute += solver.Value(sm.final_compute_cost)
        total_comm += solver.Value(sm.final_communication_cost)
    print("FINAL COMPUTE AND COMMUNICATION", total_compute, total_comm)

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
    scheduler(attention_block_einsums_breakq(b=32, s=1*1024, s1=1*1024, h=4096, d=512), num_cores=1, capacity=3 * 1024 * 1024, allow_spilling=True)
    einsum_by_einsum_scheduler(attention_block_einsums_breakq(b=32, s=1*1024, s1=1*1024, h=4096, d=512), num_cores=1, capacity=3 * 1024 * 1024, allow_spilling=True)

    print("=========================================")
    print("Running Test Case 5: Transformer Feed-Forward Network")
    print("=========================================")
    scheduler(feed_forward_einsums, capacity=512 * 1024, allow_spilling=True)

    print("=========================================")
    print("Running Test Case 6: Llama-style Feed-Forward Network (SwiGLU)")
    print("=========================================")
    scheduler(llama_ffn_einsums(1024, 7168, 3072, num_exp=6), capacity=6 * 1024 * 1024, num_cores=1, allow_spilling=True)
    einsum_by_einsum_scheduler(llama_ffn_einsums(1024, 7168, 3072, num_exp=6), capacity=6 * 1024 * 1024, num_cores=1, allow_spilling=True)
    scheduler(llama_ffn_einsums(64 * 1024, 1024, 2048, num_exp=1), capacity=3 * 1024 * 1024, num_cores=8, allow_spilling=True)
    einsum_by_einsum_scheduler(llama_ffn_einsums(16 * 1024, 1024, 2048, num_exp=1), capacity=3 * 1024 * 1024, num_cores=8, allow_spilling=True)
    # scheduler(
    #     llama_ffn_einsums(64 * 1024, 1024, 2048, num_exp=1),
    #     capacity=1024 * 1024 * 1024,
    #     num_cores=1,
    #     allow_spilling=True,
    #     perfect_factorization=True,
    #     sparse_domains=True,
    #     tight_bounds=True,
    #     codesign_costs=((149 * 1024 * 1024 * 1024) // (700 * 1000 * 1000), int(332.25 * 4), int(2.59 * 400), int(432.2 * 1000 * 1000 * 4) // 100)
    # )


    print("=========================================")
    print("Running Test Case 7: Attention Decode")
    print("=========================================")
    scheduler(attention_decode_einsums(b=512, s=128 + 1024, s1=1, h=128, d=512), capacity=3 * 1024 * 1024, allow_spilling=True)

    print("=========================================")
    print("Running Test Case 8: KDA Core Decode")
    print("=========================================")
    scheduler(kda_core_decode_einsums(d_k=128, d_v=128, heads=96), capacity=3 * 1024 * 1024, allow_spilling=True)

    # print("=========================================")
    # print("Running Test Case 9: KDA Full Decode")
    # print("=========================================")
    # scheduler(
    #     kda_full_decode_einsums(hidden=7168, d_k=128, d_v=128, heads=96, a_rank=128),
    #     capacity=3 * 1024 * 1024,
    #     num_cores=1,
    #     allow_spilling=True,
    #     perfect_factorization=True,
    #     sparse_domains=True,
    #     tight_bounds=True,
    #     global_outputs=('S_t', 'k_lin_out', 'q_lin_out', 'v_lin_out', 'out')
    # )
    # print("=========================================")
    # print("Running Test Case 12: GDN Full Decode")
    # print("=========================================")
    # scheduler(
    #     gdn_full_decode_einsums(hidden=1024, d_k=128, d_v=128, k_heads=16, v_heads=16, conv_kernel=4),
    #     capacity=3 * 1024 * 1024,
    #     num_cores=1,
    #     allow_spilling=True,
    #     perfect_factorization=True,
    #     sparse_domains=True,
    #     tight_bounds=True,
    #     global_outputs=('S_t', 'k_lin_out', 'q_lin_out', 'v_lin_out', 'out')
    # )
    # print("=========================================")
    # print("Running Test Case 10: KDA Full Decode (batched)")
    # print("=========================================")
    # import time
    # start_time = time.process_time()
    # scheduler(
    #     kda_full_batched_decode_einsums(batch=128, hidden=7168, d_k=128, d_v=128, heads=96, a_rank=128),
    #     capacity=3 * 1024 * 1024,
    #     num_cores=1,
    #     allow_spilling=True,
    #     perfect_factorization=True,
    #     sparse_domains=True,
    #     tight_bounds=True,
    #     global_outputs=('S_t', 'k_lin_out', 'q_lin_out', 'v_lin_out', 'out'),
    #     codesign_costs=((149 * 1024 * 1024 * 1024) // (700 * 1000 * 1000), int(332.25 * 4), int(2.59 * 4), int(432.2 * 1000 * 1000 * 4) // 100)
    # )
    # end_time = time.process_time()
    # print("Execution time:", end_time - start_time, "seconds")
