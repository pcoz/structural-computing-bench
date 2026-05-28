"""Deterministic problem generators for each leaf evaluator.

Every generator takes a single integer `n` (the problem size) and
returns a problem dict in the shape the corresponding leaf evaluator
expects. The same `n` always produces the same problem (no global RNG
state), so calibration runs are reproducible.

  * :func:`make_gf2_affine_problem` -- random GF(2) affine constraint
    set with `n` variables and ~n/2 constraints. For `_count_solutions_leaf`.
  * :func:`make_cycle_graph` -- planar n-cycle. PerfMatch = 2 for even
    n, 0 for odd. For T2 `_matching_count_leaf`.
  * :func:`make_bipartite_graph` -- complete bipartite K_{n,n};
    non-planar for `n >= 3`. For T4 `_matching_count_leaf` (brute
    force, factorial-ish cost).
  * :func:`make_symmetric_signature` -- a matchgate-realisable
    symmetric arity-n signature with alternating zeros and constant
    non-zero entries. For `_matchgate_rank_leaf`.
"""
from __future__ import annotations

from typing import Any, Dict

import numpy as np


def make_gf2_affine_problem(n: int, *,
                             density: float = 0.5,
                             rng_seed: int = 1) -> Dict[str, Any]:
    """Random GF(2) affine constraint set with `n` variables and ~n/2
    constraints.

    Args:
      n: number of variables.
      density: fraction of non-zero entries in the constraint matrix.
      rng_seed: makes the problem deterministic across runs.

    Returns:
      ``{"A": A, "b": b}`` where A is m×n and b is length-m.
    """
    rng = np.random.default_rng(rng_seed)
    m = max(1, n // 2)
    A = (rng.random((m, n)) < density).astype(int)
    b = rng.integers(0, 2, size=m)
    return {"A": A, "b": b}


def make_cycle_graph(n: int) -> Dict[str, Any]:
    """An n-cycle (planar, tier T2). PerfMatch = 2 for even n, 0 for odd n.

    The smallest cycle this routine produces is the 3-cycle (triangle);
    any n < 3 is silently coerced to 3 to avoid degenerate graphs."""
    if n < 3:
        n = 3
    rotation = {i: [(i - 1) % n, (i + 1) % n] for i in range(n)}
    edges = [(i, (i + 1) % n) for i in range(n)]
    return {"rotation": rotation, "vertices": list(range(n)), "edges": edges}


def make_bipartite_graph(n: int) -> Dict[str, Any]:
    """The complete bipartite graph K_{n,n}. Non-planar for `n >= 3`.

    Useful for benchmarking T4 brute-force matching count: K_{n,n} has
    n! perfect matchings, so brute-force enumeration is factorial in n.
    """
    L = list(range(n))
    R = list(range(n, 2 * n))
    edges = [(u, v) for u in L for v in R]
    rotation = {u: list(R) for u in L}
    rotation.update({v: list(L) for v in R})
    return {"rotation": rotation, "vertices": L + R, "edges": edges}


def make_symmetric_signature(n: int) -> Dict[str, Any]:
    """A symmetric matchgate-realisable signature of arity `n`: the
    "all-even-indices-2" pattern ``[2, 0, 2, 0, ..., 2 or 0]``.

    Geometric progression with ratio 1 on the non-zero entries, so
    matchgate-realisable for any `n >= 2`."""
    vals = [2 if i % 2 == 0 else 0 for i in range(n + 1)]
    return {"values": vals}
