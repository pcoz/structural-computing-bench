"""structural-computing-bench -- calibrate the router's cost models.

Top-level exports:

  * `time_call`, `benchmark_curve` -- timing primitives.
  * `fit_power_law`, `fit_exponential`, `best_fit` -- curve fitters.
  * `make_*_problem` -- deterministic problem generators per leaf evaluator.
  * `calibrate_default_evaluators` -- run the full default benchmark sweep.
  * `render_calibration_module` -- write the output as a Python module.

Run `python scripts/run_calibration.py --help` for the CLI entry point.
"""
__version__ = "0.1.0a1"

from .timing import time_call, benchmark_curve
from .fits import fit_power_law, fit_exponential, best_fit
from .problems import (
    make_gf2_affine_problem,
    make_cycle_graph,
    make_bipartite_graph,
    make_symmetric_signature,
)
from .calibrate import calibrate_default_evaluators
from .render import render_calibration_module
from .orchestrator_analytics import profile_evaluate, aggregate_phase_costs

__all__ = [
    "time_call",
    "benchmark_curve",
    "fit_power_law",
    "fit_exponential",
    "best_fit",
    "make_gf2_affine_problem",
    "make_cycle_graph",
    "make_bipartite_graph",
    "make_symmetric_signature",
    "calibrate_default_evaluators",
    "render_calibration_module",
    "profile_evaluate",
    "aggregate_phase_costs",
    "__version__",
]
