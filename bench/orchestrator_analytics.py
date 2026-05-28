"""Per-phase timing analytics for ``Orchestrator.evaluate()``.

The orchestrator's leaf evaluators are already calibrated by
:mod:`bench.calibrate`. This module measures what HAPPENS AROUND the
leaf evaluator: classifier dispatch, hint-driven reductions, recursive
sub-evaluations, workflow-trace emission. Together with the leaf
calibration, this lets a user see exactly where time goes in a full
``orchestrator.evaluate()`` call.

The technique
-------------
The framework's ``Orchestrator.evaluate(..., verbose=True, log=fn)``
calls ``fn(line)`` once per workflow step. By passing a ``fn`` that
captures ``time.perf_counter()`` at each call, we get a timestamp at
the END of each phase. Subtracting consecutive timestamps gives the
duration of each phase.

This is non-invasive: nothing inside the orchestrator changes, we just
hook the log callable.

Output shape
------------
:func:`profile_evaluate` returns a list of ``(phase, action, outcome,
duration_seconds)`` tuples, one per phase that fired, in execution
order. The total wall-clock time of the call is the sum of the
durations PLUS a small unmeasured residual (orchestrator setup before
the first phase + return-path overhead after the last phase).
"""
from __future__ import annotations

import gc
import time
from typing import Any, Dict, List, Optional, Tuple


def profile_evaluate(orchestrator: Any,
                      problem: Any,
                      question: str,
                      *,
                      hints: Optional[Dict[str, Any]] = None,
                      ) -> Dict[str, Any]:
    """Profile a single ``Orchestrator.evaluate()`` call.

    Returns a dict with:

      * ``total_seconds``: total wall-clock time of the call.
      * ``phases``: list of ``{"phase": str, "action": str,
        "outcome": str, "duration_seconds": float}`` dicts, one per
        WorkflowStep that fired, in order.
      * ``answer``: the result's ``.answer`` (or None if it raised).
      * ``raised``: the exception instance, if any, else None.

    Args:
      orchestrator: a ``structural_computing.Orchestrator`` instance.
      problem: input passed to ``evaluate``.
      question: the question argument.
      hints: optional hints dict.
    """
    log_entries: List[Tuple[float, str]] = []

    def capture(line: str) -> None:
        log_entries.append((time.perf_counter(), line))

    gc.collect()
    gc.disable()
    answer = None
    raised = None
    try:
        t0 = time.perf_counter()
        try:
            result = orchestrator.evaluate(
                problem, question, hints=hints,
                verbose=True, log=capture,
            )
            answer = result.answer
        except Exception as exc:                   # pragma: no cover
            raised = exc
        total = time.perf_counter() - t0
    finally:
        gc.enable()

    # Pair up the captured log lines with the workflow_trace steps. Each
    # WorkflowStep produces a "[phase] action -> outcome" line followed
    # by an optional "    reason: ..." line. So phase boundaries are the
    # log entries whose line STARTS WITH "[".
    boundaries: List[Tuple[float, str]] = [
        (ts, ln) for (ts, ln) in log_entries if ln.startswith("[")
    ]
    phases: List[Dict[str, Any]] = []
    last_ts = t0
    for (ts, ln) in boundaries:
        # Parse "[phase] action -> outcome" out of the line.
        # We don't need to be perfectly robust; the format is fixed by
        # orchestrator.evaluate().
        phase_end = ln.find("]")
        phase = ln[1:phase_end] if phase_end > 0 else "?"
        rest  = ln[phase_end + 1:].strip() if phase_end > 0 else ln
        arrow = " -> "
        if arrow in rest:
            action, outcome = rest.split(arrow, 1)
            action = action.strip(); outcome = outcome.strip()
        else:
            action, outcome = rest, "?"
        phases.append({
            "phase":            phase,
            "action":           action,
            "outcome":          outcome,
            "duration_seconds": ts - last_ts,
        })
        last_ts = ts

    return {
        "total_seconds": total,
        "phases":        phases,
        "answer":        answer,
        "raised":        raised,
    }


def aggregate_phase_costs(profiles: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Summarise per-phase costs across many runs.

    Args:
      profiles: list of dicts returned by :func:`profile_evaluate`.

    Returns:
      A dict keyed by phase name with sub-dicts:
        * ``count``: number of times this phase appeared.
        * ``mean_seconds``: mean duration across runs.
        * ``median_seconds``: median duration across runs.
        * ``total_seconds``: total time spent in this phase across all
          runs (useful for finding hot phases).
    """
    import numpy as np
    by_phase: Dict[str, List[float]] = {}
    for prof in profiles:
        for ph in prof["phases"]:
            by_phase.setdefault(ph["phase"], []).append(ph["duration_seconds"])
    out: Dict[str, Dict[str, float]] = {}
    for phase, durations in by_phase.items():
        arr = np.array(durations, dtype=float)
        out[phase] = {
            "count":          int(len(arr)),
            "mean_seconds":   float(arr.mean()),
            "median_seconds": float(np.median(arr)),
            "total_seconds":  float(arr.sum()),
        }
    return out
