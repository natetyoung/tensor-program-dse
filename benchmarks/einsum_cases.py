'''Single-einsum cases for comparing cb_einsum_ml_cpsat97 (einsum_cpsat.py)
with AccelForge's FFM mapper (TCM, einsum_tcm.py) on TPU-v4i: one einsum of
an AccelForge workload, mapped on its own.

name -> dict(
    workload  as in cases.py: a yaml in workloads/ or an attribute path under
              accelforge.examples.workloads
    jinja     jinja_parse_data for the workload yaml
    dims      dim sizes (AccelForge's rank variables)
    tensors   role -> (tensor, dims). Roles follow the workload's renames: the
              input, the weight (its absence makes the einsum elementwise: it
              runs on the ScalarUnit, not the PE array) and the output.
    bits      bits per value of every tensor)

The case name is the einsum's name in its workload. Approximate times on a
16-core machine: TCM takes 2-180 s per GPT-3 einsum and up to 13 minutes on
FFG and FFU; CP-SAT takes under 2 s on each. TCM has not mapped C (designed
to stress it) within 48 hours, so it is left out of runs unless named
(SKIP_BY_DEFAULT).'''

# GPT-3 6.7B prefill at batch 64 with 65,536 new tokens, from AccelForge's
# examples (the copy einsum I, which AccelForge models specially, is left out)
B, M, P, H, E, F, D, C, J, G = 64, 65536, 65536, 32, 128, 128, 4096, 16384, 4096, 4096
GPT = dict(workload='transformers.gpt.gpt3_6_7B',
           jinja={'BATCH_SIZE': B, 'DECODE': False, 'N_NEW_TOKENS': M,
                  'MAX_N_TOKENS': M},  # raised so the token-count assert allows them
           bits=16)
# One routed SwiGLU expert of DeepSeek-V4-Pro (workloads/deepseek_v4_pro_expert.yaml):
# tokens per expert per batch element (M * 6 experts per token / 384 routed
# experts), hidden dim, expert hidden dim
XT, DG, DC = M * 6 // 384, 7168, 3072
DEEPSEEK = dict(workload='workloads/deepseek_v4_pro_expert.yaml', jinja={}, bits=16)


def einsum(base, dims, input, output, weight=None):
    tensors = {'input': input, 'output': output}
    if weight:
        tensors['weight'] = weight
    return dict(base, dims=dims, tensors=tensors)


EINSUM_CASES = {
    **{n: einsum(GPT, {'b': B, 'm': M, 'h': H, 'e': E, 'd': D}, ('I', ('b', 'm', 'd')),
                 (n, ('b', 'm', 'h', 'e')), weight=('W' + n, ('h', 'e', 'd')))
       for n in ('V', 'K', 'Q')},
    'QK': einsum(GPT, {'b': B, 'm': M, 'p': P, 'h': H, 'e': E}, ('Q', ('b', 'm', 'h', 'e')),
                 ('QK', ('b', 'm', 'p', 'h')), weight=('K', ('b', 'p', 'h', 'e'))),
    'QK_softmax': einsum(GPT, {'b': B, 'm': M, 'p': P, 'h': H}, ('QK', ('b', 'm', 'p', 'h')),
                         ('QK_softmax', ('b', 'm', 'p', 'h'))),
    'AV': einsum(GPT, {'b': B, 'm': M, 'p': P, 'h': H, 'f': F},
                 ('QK_softmax', ('b', 'm', 'p', 'h')), ('AV', ('b', 'm', 'h', 'f')),
                 weight=('V', ('b', 'p', 'h', 'f'))),
    'Z': einsum(GPT, {'b': B, 'm': M, 'h': H, 'f': F, 'g': G}, ('AV', ('b', 'm', 'h', 'f')),
                ('Z', ('b', 'm', 'g')), weight=('WZ', ('h', 'f', 'g'))),
    'FFA': einsum(GPT, {'b': B, 'm': M, 'g': G, 'c': C}, ('Z', ('b', 'm', 'g')),
                  ('FFA', ('b', 'm', 'c')), weight=('WFFA', ('g', 'c'))),
    'FFB': einsum(GPT, {'b': B, 'm': M, 'c': C, 'j': J}, ('FFA', ('b', 'm', 'c')),
                  ('FFB', ('b', 'm', 'j')), weight=('WFFB', ('c', 'j'))),
    # FFH = silu(FFG) * FFU is elementwise but has three tensors, so it runs on
    # the PE array with FFU as the weight
    **{n: einsum(DEEPSEEK, {'b': B, 'xt': XT, 'g': DG, 'c': DC}, ('Z', ('b', 'xt', 'g')),
                 (n, ('b', 'xt', 'c')), weight=('W' + n, ('g', 'c')))
       for n in ('FFG', 'FFU')},
    'FFH': einsum(DEEPSEEK, {'b': B, 'xt': XT, 'c': DC}, ('FFG', ('b', 'xt', 'c')),
                  ('FFH', ('b', 'xt', 'c')), weight=('FFU', ('b', 'xt', 'c'))),
    'FFD': einsum(DEEPSEEK, {'b': B, 'xt': XT, 'c': DC, 'j': DG}, ('FFH', ('b', 'xt', 'c')),
                  ('FFD', ('b', 'xt', 'j')), weight=('WFFD', ('c', 'j'))),
    # C[m, l, n, p] = A[m, l, k] * B[k, n, p] (workloads/contraction.yaml)
    'C': einsum(dict(workload='workloads/contraction.yaml', jinja={}, bits=8),
                {'m': 210, 'l': 210, 'n': 210, 'p': 210, 'k': 2310}, ('B', ('k', 'n', 'p')),
                ('C', ('m', 'l', 'n', 'p')), weight=('A', ('m', 'l', 'k'))),
}

SKIP_BY_DEFAULT = {'C'}


def is_elementwise(case):
    return 'weight' not in case['tensors']
