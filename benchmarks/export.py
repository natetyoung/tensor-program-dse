'''Export each case's einsums, as AccelForge parses its workload, to
results/<case>/einsums.json: the input the DAG scheduler gets, so nothing
is transcribed by hand.

Usage: python export.py [CASE ...]   (default: all cases)

The scheduler's dims are AccelForge's rank variables: the scheduler links
loops across einsums by dim name, and FFM requires each rank variable to have
one size across einsums, as the scheduler does. Every projection must be a
bare rank variable. A tensor rank indexed by different rank variables in
different einsums (e.g. K[M: p] in QK vs K[M: m] in K) is a "reinterpreted"
dim for the scheduler, which then cannot loop over it around both uses when
they are fused or one produces the other (FFM can); these are listed under
"warnings".'''
import copy, sys

import accelforge as af
from accelforge.frontend._workload_isl._isl import get_rank_variable_bounds
from accelforge.util._basetypes import EvalableList

from common import HERE, result_path, save
from cases import CASES


def workload_yaml(case):
    '''A case's workload: a yaml in workloads/, or one of AccelForge's examples.'''
    if case['workload'].endswith('.yaml'):
        return str(HERE / case['workload'])
    workload = af.examples.workloads
    for part in case['workload'].split('.'):
        workload = getattr(workload, part)
    return workload


def load_spec(case):
    '''The AccelForge spec of a case: its workload on the snowcat arch.'''
    spec = af.Spec.from_yaml(af.examples.arches.snowcat, workload_yaml(case),
                             jinja_parse_data=case['jinja'])
    # FFM classifies tensors against the whole workload even when mapping a
    # subset (einsum_names), so an output of the subset read only by an einsum
    # outside it would count as an intermediate and never be written off-chip.
    # Make MainMemory keep those (the DAG scheduler writes them), and the
    # case's global outputs.
    keep = list(case.get('global_outputs', []))
    if case['einsums']:
        w = copy.deepcopy(spec)._spec_eval_expressions(eval_arch=False).workload
        subset = [e for e in w.einsums if e.name in case['einsums']]
        produced = {str(t) for e in subset for t in e.output_tensor_names}
        read = {str(t) for e in subset for t in e.input_tensor_names}
        read_outside = {str(t) for e in w.einsums if e.name not in case['einsums']
                        for t in e.input_tensor_names}
        keep += sorted((produced - read) & read_outside)
    if keep:
        spec.arch.nodes['MainMemory'].tensors.keep = '~Intermediates | ' + ' | '.join(keep)
    # FFM processes einsums in workload order (which must be topological).
    if case.get('order'):
        rank = lambda e: (case['order'].index(e.name) if e.name in case['order']
                          else len(case['order']))
        spec.workload.einsums = EvalableList(sorted(spec.workload.einsums, key=rank))
    return spec


def export(name):
    case = CASES[name]
    w = load_spec(case)._spec_eval_expressions(eval_arch=False).workload
    names = case['einsums'] or list(w.einsum_names)
    einsums, bits, warnings = [], set(), []
    tensor_rank_vars = {}  # tensor -> {rank: {rank variables indexing it}}
    for e in w.einsums:
        if e.name not in names:
            continue
        sizes = get_rank_variable_bounds(w, e.name)
        operand_dims, output = {}, None
        for ta in e.tensor_accesses:
            dims = []
            for rank, rv in dict(ta.projection).items():
                rv = str(rv)
                if rv not in sizes:
                    raise ValueError(f'{name}: {e.name}: {ta.name}[{rank}] = {rv} '
                                     'is not a bare rank variable')
                dims.append(rv)
                tensor_rank_vars.setdefault(ta.name, {}).setdefault(rank, set()).add(rv)
            operand_dims[ta.name] = dims
            bits.add(int(ta.bits_per_value))
            if ta.output:
                output = ta.name
        if e.is_copy_operation:
            warnings.append(f'{e.name} is a copy operation (FFM may elide it; '
                            'the DAG scheduler treats it as an einsum)')
        einsums.append({'name': e.name, 'operand_dims': operand_dims, 'output': output,
                        'dim_sizes': {d: int(s) for d, s in sizes.items()}})
    for t, ranks in tensor_rank_vars.items():
        for rank, rvs in ranks.items():
            if len(rvs) > 1:
                warnings.append(f'{t}[{rank}] is indexed by {sorted(rvs)} (reinterpreted dim)')
    if len(bits) != 1:
        raise ValueError(f'{name}: bits_per_value differs across tensors: {bits}')
    save(result_path(name, 'einsums.json'),
         {'case': name, **case, 'bits_per_value': bits.pop(), 'einsums': einsums,
          'warnings': warnings})
    print(f'{name}: {len(einsums)} einsums' + ''.join(f'\n  note: {x}' for x in warnings))


if __name__ == '__main__':
    for name in sys.argv[1:] or CASES:
        export(name)
