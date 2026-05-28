"""Tests for per-phase orchestrator profiling."""
from structural_computing import Orchestrator

from bench import profile_evaluate, aggregate_phase_costs


def test_profile_evaluate_captures_phases():
    """Profiling a planar K_4 matching_count call captures the normalise
    / classify / direct-dispatch phases with positive durations."""
    orch = Orchestrator()
    graph = {
        "rotation": {0: [1, 2, 3], 1: [0, 3, 2], 2: [0, 1, 3], 3: [0, 2, 1]},
        "vertices": [0, 1, 2, 3],
        "edges": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
    }
    profile = profile_evaluate(orch, graph, "matching_count")
    assert profile["answer"] == 3
    assert profile["raised"] is None
    # At least three phases fired: normalise, classify, direct-dispatch.
    phase_names = [p["phase"] for p in profile["phases"]]
    assert "normalise" in phase_names
    assert "classify" in phase_names
    assert "direct-dispatch" in phase_names
    # Each phase has a non-negative duration.
    for p in profile["phases"]:
        assert p["duration_seconds"] >= 0
    # Total seconds is approximately the sum of phase durations.
    sum_durations = sum(p["duration_seconds"] for p in profile["phases"])
    assert sum_durations <= profile["total_seconds"] + 1e-3


def test_aggregate_phase_costs_summarises_runs():
    """Aggregating multiple profiles produces per-phase mean/median/total."""
    orch = Orchestrator()
    graph = {
        "rotation": {0: [1, 2, 3], 1: [0, 3, 2], 2: [0, 1, 3], 3: [0, 2, 1]},
        "vertices": [0, 1, 2, 3],
        "edges": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
    }
    profiles = [profile_evaluate(orch, graph, "matching_count") for _ in range(3)]
    summary = aggregate_phase_costs(profiles)
    assert "classify" in summary
    classify_stats = summary["classify"]
    assert classify_stats["count"] == 3
    assert classify_stats["mean_seconds"] >= 0
    assert classify_stats["median_seconds"] >= 0
    assert classify_stats["total_seconds"] >= 0
