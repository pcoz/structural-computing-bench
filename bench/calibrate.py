"""End-to-end calibration runner.

:func:`calibrate_default_evaluators` measures each of the framework's
default leaf evaluators on a sensible range of problem sizes, fits
both a power-law and an exponential model, and returns the best fit
per ``(tier, question)``.

The output is a dict shaped for :func:`bench.render.render_calibration_module`
or for direct use via
:func:`structural_computing.calibration.apply_calibration`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .timing import benchmark_curve
from .fits import best_fit
from .problems import (
    make_gf2_affine_problem,
    make_cycle_graph,
    make_bipartite_graph,
    make_symmetric_signature,
)


DEFAULT_SIZES: Dict[str, List[int]] = {
    "T0_count_solutions":    [4, 8, 12, 16, 20],
    "T2_matching_count":     [4, 6, 8, 10, 12, 14],
    "T4_matching_count":     [2, 3, 4, 5],
    "T2_matchgate_rank":     [2, 4, 6, 8, 10],
}


def calibrate_default_evaluators(*,
                                  sizes: Optional[Dict[str, List[int]]] = None,
                                  repeat: int = 5,
                                  warmup: bool = True,
                                  include_curves: bool = False,
                                  ) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Run :func:`benchmark_curve` on each default leaf evaluator and
    fit a model to the timings.

    Args:
      sizes: per-evaluator size lists. Keys are
        ``"T0_count_solutions"``, ``"T2_matching_count"``,
        ``"T4_matching_count"``, ``"T2_matchgate_rank"``. Missing keys
        fall back to :data:`DEFAULT_SIZES`.
      repeat: timed runs per measurement (median is taken).
      warmup: do one un-timed pre-run per measurement.
      include_curves: if True, include the raw ``[(n, seconds), ...]``
        curve in each result dict under key ``"curve"``. Useful for
        debugging / plotting.

    Returns:
      Dict keyed by ``(tier, question)`` with the same shape as
      :func:`best_fit` plus (optionally) the curve. Example::

          {
              ("T0", "count_solutions"): {
                  "model": "power_law",
                  "params": (1.2e-6, 2.97),
                  "rms": 0.08,
                  "all_fits": {...},
                  "curve": [(4, 0.00001), (8, 0.00004), ...],   # if include_curves
              },
              ...
          }
    """
    from structural_computing.orchestrator import (
        _count_solutions_leaf,
        _matching_count_leaf,
        _matchgate_rank_leaf,
    )
    effective_sizes = dict(DEFAULT_SIZES)
    if sizes is not None:
        effective_sizes.update(sizes)
    out: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def _add(key: Tuple[str, str], leaf, generator, sizes_key: str, question: str):
        sizes_list = effective_sizes[sizes_key]
        curve = benchmark_curve(
            lambda p: leaf(p, question),
            generator,
            sizes_list,
            repeat=repeat,
            warmup=warmup,
        )
        result = best_fit(curve)
        if include_curves:
            result["curve"] = curve
        out[key] = result

    _add(("T0", "count_solutions"), _count_solutions_leaf,
         make_gf2_affine_problem,  "T0_count_solutions", "count_solutions")
    _add(("T2", "matching_count"),  _matching_count_leaf,
         make_cycle_graph,         "T2_matching_count",  "matching_count")
    _add(("T4", "matching_count"),  _matching_count_leaf,
         make_bipartite_graph,     "T4_matching_count",  "matching_count")
    _add(("T2", "matchgate_rank"),  _matchgate_rank_leaf,
         make_symmetric_signature, "T2_matchgate_rank",  "matchgate_rank")

    return out
