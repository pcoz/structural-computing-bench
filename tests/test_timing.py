"""Tests for the timing primitives."""
import time

from bench import time_call, benchmark_curve


def test_time_call_returns_positive_float():
    """time_call on a sleep(0.01) call gives ~0.01 seconds."""
    t = time_call(lambda p: time.sleep(0.01), None, repeat=3, warmup=False)
    assert isinstance(t, float)
    assert 0.005 < t < 0.2          # generous bounds for CI jitter


def test_time_call_warmup_does_not_count():
    """The warmup run is not part of the timed median."""
    calls = []
    def fn(p):
        calls.append(time.perf_counter())
    time_call(fn, None, repeat=3, warmup=True)
    assert len(calls) == 4          # 1 warmup + 3 timed


def test_benchmark_curve_produces_one_entry_per_size():
    """benchmark_curve returns [(n, t), ...] in the supplied size order."""
    curve = benchmark_curve(
        lambda p: None,                 # zero-cost callable
        lambda n: n,                    # identity generator
        sizes=[2, 4, 8],
        repeat=2, warmup=False,
    )
    assert [n for n, _ in curve] == [2, 4, 8]
    assert all(t >= 0 for _, t in curve)
