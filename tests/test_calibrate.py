"""Integration test: the full calibration sweep produces sensible
coefficients for each default leaf evaluator."""
import math

import pytest

from bench import calibrate_default_evaluators, render_calibration_module


def test_default_calibration_runs_end_to_end():
    """A short calibration (small sizes, few repeats) produces a result
    with the four expected (tier, question) keys; every result has the
    standard shape (model, params, rms)."""
    # Use small sizes so the test runs in well under a minute.
    sizes = {
        "T0_count_solutions":  [4, 8, 12],
        "T2_matching_count":   [4, 6, 8],
        "T4_matching_count":   [2, 3, 4],
        "T2_matchgate_rank":   [2, 4, 6],
    }
    out = calibrate_default_evaluators(sizes=sizes, repeat=2)
    expected_keys = {
        ("T0", "count_solutions"),
        ("T2", "matching_count"),
        ("T4", "matching_count"),
        ("T2", "matchgate_rank"),
    }
    assert set(out.keys()) == expected_keys
    for key, result in out.items():
        assert result["model"] in ("power_law", "exponential")
        a, b = result["params"]
        assert isinstance(a, float) and isinstance(b, float)
        assert math.isfinite(a) and math.isfinite(b)
        assert "rms" in result
        assert "all_fits" in result


def test_calibration_includes_curves_when_requested():
    sizes = {"T0_count_solutions": [4, 8]}
    out = calibrate_default_evaluators(
        sizes=sizes, repeat=1, include_curves=True,
    )
    # T0 entry has the raw curve attached.
    curve = out[("T0", "count_solutions")]["curve"]
    assert [n for n, _ in curve] == [4, 8]


def test_render_calibration_module_is_valid_python():
    """The rendered module loads back as a Python source string with
    CALIBRATED_COSTS and METADATA top-level names."""
    sizes = {
        "T0_count_solutions":  [4, 8],
        "T2_matching_count":   [4, 6],
        "T4_matching_count":   [2, 3],
        "T2_matchgate_rank":   [2, 4],
    }
    out = calibrate_default_evaluators(sizes=sizes, repeat=1)
    source = render_calibration_module(out, bench_version="0.1.0a1")
    # The rendered text should exec cleanly.
    namespace = {}
    exec(source, namespace)
    assert "CALIBRATED_COSTS" in namespace
    assert "METADATA" in namespace
    # Every entry has the shape (tier, question) -> {model, params, rms}.
    for key, entry in namespace["CALIBRATED_COSTS"].items():
        assert isinstance(key, tuple) and len(key) == 2
        assert entry["model"] in ("power_law", "exponential")
        assert "params" in entry and len(entry["params"]) == 2
        assert "rms" in entry
