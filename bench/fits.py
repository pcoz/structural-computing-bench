"""Curve fitters for benchmark data.

Three public functions:

  * :func:`fit_power_law` -- fit ``time = a * n^b`` (linear in log-log).
    Right for evaluators with polynomial cost (T0 GF(2) solver,
    T2 planar matching count via Kasteleyn, etc).
  * :func:`fit_exponential` -- fit ``time = a * exp(b * n)``
    (linear in log-vs-n). Right for brute-force evaluators (T1
    quadratic enumeration, T4 brute matching on bipartite K_{n,n}).
  * :func:`best_fit` -- run BOTH fits, return whichever has the lower
    log-residual. Use this when you don't know a priori which model
    applies to a given evaluator.

All fitters return ``(a, b, rms_residual)``. The residual is computed
on the same scale the fit was done in (log-space), so a value < 0.1
means the fit explains the data to within ~10% on each point; > 1.0
means the wrong model is being used.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

import numpy as np


def fit_power_law(curve: List[Tuple[int, float]]) -> Tuple[float, float, float]:
    """Fit ``time ≈ a * n^b`` on log-log axes.

    ``log(time) = log(a) + b * log(n)`` is a straight line in log-log
    space. Returns ``(a, b, rms_residual)`` where:

      * `a` is the constant prefactor (units: seconds).
      * `b` is the exponent (positive for growing-cost evaluators).
      * `rms_residual` is the root-mean-square residual on log-log axes;
        a value ``<< 1`` means the power law fits well, ``>> 1`` means a
        different model (e.g., exponential) is needed.

    Discards any ``(n, t)`` points with ``t <= 0`` (unmeasurable).
    """
    finite = [(n, t) for n, t in curve if t > 0 and n > 0]
    if len(finite) < 2:
        raise ValueError(
            f"fit_power_law: need >= 2 positive-time data points; got {len(finite)}"
        )
    xs = np.log([n for n, _ in finite])
    ys = np.log([t for _, t in finite])
    slope, intercept = np.polyfit(xs, ys, 1)
    a = float(math.exp(intercept))
    b = float(slope)
    predicted = intercept + slope * xs
    rms = float(np.sqrt(np.mean((ys - predicted) ** 2)))
    return a, b, rms


def fit_exponential(curve: List[Tuple[int, float]]) -> Tuple[float, float, float]:
    """Fit ``time ≈ a * exp(b * n)`` (equivalently ``a * c^n`` with
    ``c = exp(b)``).

    ``log(time) = log(a) + b * n`` is a straight line in log-linear
    space. Returns ``(a, b, rms_residual)``. The base ``c = exp(b)``;
    a measured exponent ``b ≈ ln(2)`` corresponds to ``2^n`` cost.
    """
    finite = [(n, t) for n, t in curve if t > 0]
    if len(finite) < 2:
        raise ValueError(
            f"fit_exponential: need >= 2 positive-time data points; got {len(finite)}"
        )
    xs = np.array([n for n, _ in finite], dtype=float)
    ys = np.log([t for _, t in finite])
    slope, intercept = np.polyfit(xs, ys, 1)
    a = float(math.exp(intercept))
    b = float(slope)
    predicted = intercept + slope * xs
    rms = float(np.sqrt(np.mean((ys - predicted) ** 2)))
    return a, b, rms


def best_fit(curve: List[Tuple[int, float]]) -> Dict[str, Any]:
    """Fit BOTH a power law and an exponential to `curve`; return the
    one with smaller log-residual plus the comparison details.

    Returns a dict with:
      * ``model``: ``"power_law"`` or ``"exponential"``.
      * ``params``: the fitted ``(a, b)``.
      * ``rms``: the residual of the chosen model.
      * ``all_fits``: a dict carrying both fits with their residuals,
        for inspection / reporting.
    """
    pl_a, pl_b, pl_rms = fit_power_law(curve)
    try:
        ex_a, ex_b, ex_rms = fit_exponential(curve)
    except ValueError:
        ex_a, ex_b, ex_rms = float("nan"), float("nan"), float("inf")
    all_fits = {
        "power_law":   {"params": (pl_a, pl_b), "rms": pl_rms},
        "exponential": {"params": (ex_a, ex_b), "rms": ex_rms},
    }
    if pl_rms <= ex_rms:
        return {"model": "power_law", "params": (pl_a, pl_b),
                "rms": pl_rms, "all_fits": all_fits}
    return {"model": "exponential", "params": (ex_a, ex_b),
            "rms": ex_rms, "all_fits": all_fits}
