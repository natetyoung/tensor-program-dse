'''Benchmark cases for comparing the general DAG scheduler with AccelForge's
FFM mapper: an AccelForge workload on the single-level snowcat arch at one
on-chip capacity, shared by both tools.

name -> dict(
    workload  a yaml in workloads/ ('workloads/x.yaml'), or an attribute path
              under accelforge.examples.workloads (e.g. 'basic.matmuls')
    jinja     jinja_parse_data for the workload yaml
    einsums   einsum names to map (None = all)
    capacity  on-chip capacity in elements (FFM gets capacity * bits_per_value
              bits)
    global_outputs  optional: einsum outputs consumed by later einsums that
              must also be written off-chip
    order     optional: einsums FFM should process first (FFM keeps workload
              order; the DAG scheduler chooses its own))

Approximate times on a 16-core machine: FFM takes under 30 s per case
except kda_batched (about 13 minutes). The DAG scheduler proves optimality
within about 20 s except on attn512 and attn512_qfirst (about 6 minutes),
and chain8 and kda_batched, which use the whole time limit. A full run
(python run.py) takes about 1.5 hours, plus the two attention cases below:
on an 8-core machine with 4 threads, gqa_llama3_8b took 74 s in FFM and
2 s to optimality in the DAG scheduler, and kimi_k3_mla 445 s in FFM (over
6 GB of memory) and 186 s to optimality.'''

CASES = {
    # Smoke tests: both tools finish in seconds.
    'chain2_tiny': dict(workload='basic.matmuls', jinja={'N_EINSUMS': 2, 'M': 64, 'KN': 64},
                        einsums=None, capacity=1024),
    'matvecs': dict(workload='basic.matvecs', jinja={}, einsums=None, capacity=8),
    # Matmul chains I -> A -> B -> ...: activations M x KN (4 Mi elements),
    # weights KN x KN (1 Mi). Capacity is a quarter of a weight, so fusing an
    # intermediate requires tiling it.
    **{f'chain{n}': dict(workload='basic.matmuls',
                         jinja={'N_EINSUMS': n, 'M': 4096, 'KN': 1024},
                         einsums=None, capacity=256 * 1024)
       for n in (2, 4, 8)},
    # SwiGLU FFN (workloads/swiglu_ffn.yaml), the two setups of
    # test_cases.py: X feeds the up and gate projections, which meet in
    # Y_mid, then the down projection reduces over f and e. swiglu (and
    # swiglu_merged) is one DeepSeek-V4-Pro routed expert (hidden 7168,
    # moe_intermediate_size 3072) at a batch of 2048 tokens.
    'swiglu_e6': dict(workload='workloads/swiglu_ffn.yaml',
                      jinja={'BS': 1024, 'H': 7168, 'D_FF': 3072, 'N_EXP': 6},
                      einsums=None, capacity=6 * 1024 * 1024),
    'swiglu': dict(workload='workloads/swiglu_ffn.yaml',
                   jinja={'BS': 2048, 'H': 7168, 'D_FF': 3072, 'N_EXP': 1},
                   einsums=None, capacity=3 * 1024 * 1024),
    # The same with up and gate merged into one einsum over u.
    'swiglu_e6_merged': dict(workload='workloads/swiglu_ffn_merged.yaml',
                             jinja={'BS': 1024, 'H': 7168, 'D_FF': 3072, 'N_EXP': 6},
                             einsums=None, capacity=6 * 1024 * 1024),
    'swiglu_merged': dict(workload='workloads/swiglu_ffn_merged.yaml',
                          jinja={'BS': 2048, 'H': 7168, 'D_FF': 3072, 'N_EXP': 1},
                          einsums=None, capacity=3 * 1024 * 1024),
    # Test Cases 1-3 of test_cases.py, at the capacities its __main__ uses.
    'shared_input': dict(workload='workloads/shared_input.yaml', jinja={}, einsums=None,
                         capacity=512 * 1024),
    'skip_connection': dict(workload='workloads/skip_connection.yaml', jinja={},
                            einsums=None, capacity=1024 * 1024),
    'multi_stage_reduction': dict(workload='workloads/multi_stage_reduction.yaml', jinja={},
                                  einsums=None, capacity=256 * 1024),
    # Test Case 10 of test_cases.py: KDA full decode, batched (batch 128,
    # capacity 3 Mi). The largest case: FFM needs much more time and memory
    # than the others.
    'kda_batched': dict(workload='workloads/kda_batched_decode.yaml',
                        jinja={'BATCH': 128, 'HIDDEN': 7168, 'D_K': 128, 'D_V': 128,
                               'HEADS': 96, 'A_RANK': 128},
                        einsums=None, capacity=3 * 1024 * 1024,
                        global_outputs=['S_t', 'k_lin_out', 'q_lin_out', 'v_lin_out', 'out']),
    # Test Case 15 of test_cases.py: Gated DeltaNet core decode with its gate
    # and gated RMSNorm output (what gdn_nki_kernel.py computes), at
    # Qwen3.5-35B-A3B's linear-attention layers (16 key heads and 32 value
    # heads of 128, so 2 value heads per key head), batch 128, capacity 3 Mi.
    # S_prev and S_t are 64 Mi elements each, so the state must be tiled.
    # The new state S_t, also read by o, is a global output.
    'gdn_decode': dict(workload='workloads/gdn_decode.yaml',
                       jinja={'BATCH': 128, 'D_K': 128, 'D_V': 128, 'K_HEADS': 16,
                              'V_HEADS': 32},
                       einsums=None, capacity=3 * 1024 * 1024, global_outputs=['S_t']),
    # Mamba3 SISO SSD intra-chunk contribution (siso_workload.py, its
    # default Q 64, N 128, P 64, K 1). All its tensors total 65,920 elements
    # (compulsory traffic 28,928), so the capacity is swept from 4 Ki (tight)
    # to 64 Ki (just under everything).
    **{f'siso_c{c}k': dict(workload='workloads/siso_ssd_intra_chunk.yaml',
                           jinja={'K': 1, 'Q': 64, 'N': 128, 'P': 64},
                           einsums=None, capacity=c * 1024)
       for c in (4, 8, 16, 64)},
    # The same with 128 chunks (all tensors 7,917,568 elements, compulsory
    # traffic 3,182,592) and 3 Mi capacity.
    'siso_k128': dict(workload='workloads/siso_ssd_intra_chunk.yaml',
                      jinja={'K': 128, 'Q': 64, 'N': 128, 'P': 64},
                      einsums=None, capacity=3 * 1024 * 1024),
    # GPT-3 6.7B attention (copy einsum I left out), prefill of 512 tokens at
    # batch 1. I feeds V, K and Q; K and V are reinterpreted in QK and AV
    # (K[M: p], V[M: p, E: f]). Capacity: half a 512 x 4096 activation.
    'attn512': dict(workload='transformers.gpt.gpt3_6_7B',
                    jinja={'BATCH_SIZE': 1, 'DECODE': False, 'N_NEW_TOKENS': 512},
                    einsums=['V', 'K', 'Q', 'QK', 'QK_softmax', 'AV', 'Z'],
                    capacity=1024 * 1024),
    # The same with Q computed before K, so K's producer and consumer (QK) are
    # adjacent in FFM's einsum order, as in the DAG scheduler's schedule.
    'attn512_qfirst': dict(workload='transformers.gpt.gpt3_6_7B',
                           jinja={'BATCH_SIZE': 1, 'DECODE': False, 'N_NEW_TOKENS': 512},
                           einsums=['V', 'K', 'Q', 'QK', 'QK_softmax', 'AV', 'Z'],
                           order=['I', 'V', 'Q', 'K'], capacity=1024 * 1024),
    # Grouped-query attention prefill with softmax (workloads/
    # gqa_attention_prefill.yaml, Test Case 13 of test_cases.py) at
    # Llama-3-8B's shapes: 32 query heads in 8 KV groups of 4, head dim 128,
    # 1024 tokens. S and P (32 Mi elements each) dwarf Q, K, V and O.
    'gqa_llama3_8b': dict(workload='workloads/gqa_attention_prefill.yaml',
                          jinja={'KV': 8, 'G': 4, 'S': 1024, 'D': 128},
                          einsums=None, capacity=3 * 1024 * 1024),
    # Kimi K3's gated multi-latent attention block (workloads/kimi_k3_mla.yaml,
    # Test Case 14 of test_cases.py), prefill of 1024 tokens: 18 einsums,
    # about 232 Mi elements of weights. X is reinterpreted: read over m by the
    # query path and gate, and over n by the key/value path.
    'kimi_k3_mla': dict(workload='workloads/kimi_k3_mla.yaml',
                        jinja={'S': 1024, 'HEADS': 96, 'HIDDEN': 7168, 'Q_LORA': 1536,
                               'KV_LORA': 512, 'QK_NOPE': 128, 'QK_ROPE': 64,
                               'V_DIM': 128},
                        einsums=None, capacity=3 * 1024 * 1024),
}
