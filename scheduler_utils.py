"""
Shared types and utilities used by DAG scheduler implementations.

This module is intentionally minimal: it holds the Einsum description dataclass
and the add_mul_chain CP-SAT helper so that multiple scheduler files can share
a single definition.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from ortools.sat.python import cp_model


def add_mul_chain(model: cp_model.CpModel, components, lb, ub, pfx):
    """
    Build a chain of pairwise multiplication constraints in the CP-SAT model,
    returning a variable equal to the product of all elements in `components`.

    If `components` has only one element, that element is returned directly
    without creating any new variables.
    """
    old_var = components[0]
    new_var = components[0]
    for i in range(len(components) - 1):
        old_var = new_var
        new_var = model.NewIntVar(lb, ub, pfx + '_mul_chain' + str(i))
        constr = model.AddMultiplicationEquality(new_var, (old_var, components[i + 1]))
    return new_var


# Einsum description:
#   operand_dims  — dict mapping operand names to tuples of coordinate names
#   output_operand — name of the single output operand
#   dim_sizes     — dict mapping coordinate names to their sizes
#   accel_gran    — optional dict mapping dim names, tuples of dim names, or
#                   'PRODUCT' to accelerator granularities; used to compute
#                   compute cost in the scheduler.  A tuple key such as
#                   ('b', 'c') means the product of those dims' spatial factors
#                   maps onto one accelerator axis of the given size.
#   compute_cost  — scalar weight for this einsum's compute cost in the objective
#   operation     — optional human-readable operation label (e.g. 'matmul')

@dataclass
class Einsum:
    operand_dims: Dict[str, Tuple[str, ...]]
    output_operand: str
    dim_sizes: Dict[str, int]
    accel_gran: Dict[Union[str, Tuple[str, ...]], int] = None
    compute_cost: int = 0
    operation: str = None


def normalize_accel_gran(e: Einsum) -> List[Tuple[Tuple[str, ...], int]]:
    """
    Return the einsum's accelerator granularities as a list of
    (dims_tuple, size) groups.  A string key is a group of one dim.  The
    special 'PRODUCT' key must be the only key and is returned as-is
    (('PRODUCT',), size).  Raises ValueError on malformed specifications.
    """
    groups: List[Tuple[Tuple[str, ...], int]] = []
    seen = set()
    for key, size in (e.accel_gran or {}).items():
        dims = (key,) if isinstance(key, str) else tuple(key)
        if size <= 0:
            raise ValueError(f'accel_gran size for {key!r} must be positive')
        if dims == ('PRODUCT',):
            if len(e.accel_gran) != 1:
                raise ValueError("'PRODUCT' cannot be combined with other accel_gran keys")
        else:
            if not dims:
                raise ValueError('accel_gran key must not be an empty tuple')
            for d in dims:
                if d not in e.dim_sizes:
                    raise ValueError(f'accel_gran dim {d!r} is not a dim of the einsum')
                if d in seen:
                    raise ValueError(f'accel_gran dim {d!r} appears in more than one key')
                seen.add(d)
        groups.append((dims, size))
    return groups
