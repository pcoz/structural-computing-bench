# structural-computing-bench

[![PyPI](https://img.shields.io/pypi/v/structural-computing-bench.svg)](https://pypi.org/project/structural-computing-bench/)

Calibrate the cost models used by
[`structural-computing`](https://github.com/pcoz/structural-computing)'s
router by measuring actual wall-clock performance of its leaf
evaluators on your machine and fitting a power-law / exponential model
to the measurements.

The router decides which evaluator to dispatch to based on a *predicted*
runtime. The shipped predictions are hand-picked defaults; this repo
produces machine-specific replacements so the predictions match what
your hardware actually does.

## Why a separate repo

The benchmark machinery is heavier than the core library — timing
primitives, GC handling, curve fitting, problem generators, plus
optional plotting / reporting. Keeping it out of the
`structural-computing` PyPI package means:

  * Users installing the framework don't pull in unused benchmarking code.
  * The bench repo can grow heavier deps later (matplotlib, scipy,
    hypothesis) without bloating the core.
  * Calibration runs can have their own CI and don't interleave with
    framework PRs.

The output is a small `calibration_data.py` (or `.json`) file that the
framework's `structural_computing.calibration.apply_calibration()` loads
to update the router's coefficients at runtime.

## Quick start

```
pip install structural-computing-bench
python scripts/run_calibration.py --out calibration_data/my_machine.py
```

then in your application:

```python
import importlib.util, importlib
spec = importlib.util.spec_from_file_location(
    "my_calibration", "calibration_data/my_machine.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

from structural_computing.calibration import apply_calibration
apply_calibration(mod.CALIBRATED_COSTS)

# Now the router uses your machine's measured constants.
```

## What gets measured

| Leaf evaluator              | Problem generator       | Default sizes        |
|-----------------------------|-------------------------|----------------------|
| `_count_solutions_leaf`     | random GF(2) affine     | n ∈ [4, 8, 12, 16, 20, 24] |
| `_matching_count_leaf` (T2) | n-cycle (planar)        | n ∈ [4, 6, 8, 10, 12, 14, 16] |
| `_matching_count_leaf` (T4) | K_{n,n} bipartite       | n ∈ [2, 3, 4, 5]     |
| `_matchgate_rank_leaf`      | symmetric arity-n sig   | n ∈ [2, 4, 6, 8, 10, 12] |

For each, the harness:

1. Generates a deterministic problem of size `n`.
2. Runs the leaf evaluator `repeat=5` times.
3. Records the median elapsed seconds (median is robust to GC pauses).
4. Fits both `time ≈ a * n^b` (power law) and `time ≈ a * exp(b * n)`
   (exponential); reports whichever has lower log-residual as the
   preferred model.

## License

MIT-with-attribution to Edward Chalk / sapientronic.ai.
