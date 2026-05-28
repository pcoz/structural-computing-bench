"""Timing primitives for the calibration harness.

The two public functions:

  * :func:`time_call` -- measure a single callable on a fixed input,
    reporting the MEDIAN elapsed wall-clock seconds over multiple runs.
    Median (not min, not mean) is chosen because:

      - min underestimates typical cost (best-case-only),
      - mean is sensitive to outlier GC pauses or context switches,
      - median tracks the "typical run" cleanly.

  * :func:`benchmark_curve` -- measure a callable across a range of
    problem sizes, producing ``[(n, seconds), ...]``.

Both functions disable Python's GC during each timed run (so a GC pause
mid-measurement doesn't pollute the result) and re-enable it
afterwards. The `warmup` flag is recommended: it runs the callable once
un-timed before timing begins, so caches, JIT'd code, and lazy imports
are paid up-front.
"""
from __future__ import annotations

import gc
import time
from typing import Any, Callable, List, Tuple

import numpy as np

TimingFn = Callable[[Any], Any]
ProblemGenerator = Callable[[int], Any]


def time_call(fn: TimingFn, problem: Any, *,
              repeat: int = 5,
              warmup: bool = True) -> float:
    """Time ``fn(problem)`` and return the median elapsed seconds over
    `repeat` runs.

    Args:
      fn: the callable to time.
      problem: the input passed to fn. Same object reused across runs.
      repeat: number of timed runs. Recommended >= 5 for stable medians.
      warmup: if True, do one un-timed pre-run.

    Returns:
      Median elapsed seconds. Always non-negative.
    """
    if warmup:
        fn(problem)
    times: List[float] = []
    for _ in range(repeat):
        gc.collect()
        gc.disable()
        try:
            t0 = time.perf_counter()
            fn(problem)
            elapsed = time.perf_counter() - t0
        finally:
            gc.enable()
        times.append(max(elapsed, 0.0))
    return float(np.median(times))


def benchmark_curve(fn: TimingFn,
                    generator: ProblemGenerator,
                    sizes: List[int],
                    *,
                    repeat: int = 5,
                    warmup: bool = True) -> List[Tuple[int, float]]:
    """Time `fn` on problems of size `n` for each `n` in `sizes`.

    Each measurement uses :func:`time_call`. Returns a list
    ``[(n, seconds), ...]`` suitable for the curve fitters in
    :mod:`bench.fits`."""
    out: List[Tuple[int, float]] = []
    for n in sizes:
        problem = generator(n)
        t = time_call(fn, problem, repeat=repeat, warmup=warmup)
        out.append((n, t))
    return out
