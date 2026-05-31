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


# ---------------------------------------------------------------------------
# v1.1.0: problem generators for the tropical + CP-SAT leaves (v0.10-v0.13)
# ---------------------------------------------------------------------------


def make_weighted_bipartite_graph(n: int,
                                    *,
                                    rng_seed: int = 1) -> Dict[str, Any]:
    """Complete bipartite K_{n,n} with random edge weights in [1.0, 10.0].

    For ``_min_weight_matching_leaf``. The leaf dispatches to Hungarian
    (O(n^3)) for bipartite K_{n,n} inputs, so this exercises the
    bipartite path of the tropical Pfaffian dispatch.
    """
    rng = np.random.default_rng(rng_seed)
    L = list(range(n))
    R = list(range(n, 2 * n))
    edges = [(u, v) for u in L for v in R]
    weights = {(u, v): float(rng.uniform(1.0, 10.0)) for (u, v) in edges}
    return {
        "vertices": L + R,
        "edges": edges,
        "weights": weights,
    }


def make_scheduling_instance(n: int) -> Dict[str, Any]:
    """Square SchedulingInstance with ``n`` jobs and ``n`` machines.

    For ``_min_cost_schedule_leaf`` and
    ``_tropical_instance_coordinates_leaf``. Uniform-cost cost_fn so
    the structural diagnostic gets a clean rank-1 input.
    """
    import holant_tools
    jobs = [holant_tools.Job(name=f"J{i}") for i in range(n)]
    machines = [holant_tools.Machine(name=f"M{i}") for i in range(n)]
    instance = holant_tools.SchedulingInstance(jobs=jobs, machines=machines)

    def cost_fn(job, machine, slot):
        # Cheap when job index matches machine index; expensive otherwise.
        ji = int(job.name[1:])
        mi = int(machine.name[1:])
        return 1.0 if ji == mi else 5.0

    return {"instance": instance, "cost_fn": cost_fn}


def make_flow_instance(n: int) -> Dict[str, Any]:
    """1-source, 1-sink MinCostFlowInstance with ``n`` parallel
    edges of varying cost / capacity.

    For ``_min_cost_flow_leaf``.
    """
    import holant_tools
    src = holant_tools.FlowNode("S", supply=n)
    snk = holant_tools.FlowNode("T", supply=-n)
    edges = [
        holant_tools.FlowEdge(source="S", target="T",
                                cost=float(i + 1), capacity=1)
        for i in range(n)
    ]
    return {"instance": holant_tools.MinCostFlowInstance(
        sources=[src], sinks=[snk], edges=edges,
    )}


def make_rostering_instance(n: int) -> Dict[str, Any]:
    """Square RosteringInstance with ``n`` employees and ``n`` shifts.

    For ``_min_cost_roster_leaf``.
    """
    import holant_tools
    employees = [holant_tools.Employee(name=f"E{i}", max_shifts=1)
                  for i in range(n)]
    shifts = [holant_tools.Shift(name=f"S{i}", headcount=1)
              for i in range(n)]
    instance = holant_tools.RosteringInstance(employees=employees, shifts=shifts)

    def preference_fn(emp, shift):
        ei = int(emp.name[1:])
        si = int(shift.name[1:])
        return 1.0 if ei == si else 5.0

    return {"instance": instance, "preference_fn": preference_fn}


def make_dedup_instance(n: int) -> Dict[str, Any]:
    """Square MDMInstance with ``n`` records and ``n`` entity candidates.

    For ``_min_cost_dedup_leaf``.
    """
    import holant_tools
    records = [holant_tools.Record(name=f"R{i}") for i in range(n)]
    candidates = [holant_tools.EntityCandidate(id=f"E{i}", capacity=1)
                   for i in range(n)]
    instance = holant_tools.MDMInstance(records=records,
                                          entity_candidates=candidates)

    def similarity_fn(record, candidate):
        # Treated as a COST by the engine (lower = more similar).
        ri = int(record.name[1:])
        ci = int(candidate.id[1:])
        return 0.1 if ri == ci else 0.9

    return {"instance": instance, "similarity_fn": similarity_fn}


def make_cpsat_cardinality_model(n: int) -> Dict[str, Any]:
    """``cp_model.CpModel`` with ``n`` boolean variables and a single
    cardinality constraint ``sum(xs) == n // 2``.

    For ``_rewrite_cpsat_model_leaf``. The constraint is rank-explosive,
    which is exactly the shape the rewrite layer targets.
    """
    from ortools.sat.python import cp_model
    model = cp_model.CpModel()
    xs = [model.NewBoolVar(f"x{i}") for i in range(n)]
    model.Add(sum(xs) == n // 2)
    return {"model": model}
