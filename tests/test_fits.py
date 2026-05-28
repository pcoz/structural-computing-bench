"""Tests for the curve fitters."""
import math

import pytest

from bench import fit_power_law, fit_exponential, best_fit


def test_fit_power_law_recovers_known_exponent():
    """Synthetic data with time = 3 * n^2 fits to exponent ~2.0 and
    prefactor ~3.0."""
    curve = [(n, 3.0 * n ** 2) for n in range(2, 12)]
    a, b, rms = fit_power_law(curve)
    assert abs(b - 2.0) < 1e-6
    assert abs(a - 3.0) < 1e-6
    assert rms < 1e-6


def test_fit_exponential_recovers_known_rate():
    """time = 0.1 * 2^n fits to a=0.1 and b=ln(2)."""
    curve = [(n, 0.1 * (2.0 ** n)) for n in range(2, 12)]
    a, b, rms = fit_exponential(curve)
    assert abs(a - 0.1) < 1e-6
    assert abs(b - math.log(2.0)) < 1e-6
    assert rms < 1e-6


def test_best_fit_picks_power_law_for_polynomial_data():
    curve = [(n, 0.5 * n ** 3) for n in range(2, 10)]
    result = best_fit(curve)
    assert result["model"] == "power_law"
    assert abs(result["params"][1] - 3.0) < 1e-6


def test_best_fit_picks_exponential_for_exponential_data():
    curve = [(n, 0.01 * (3.0 ** n)) for n in range(2, 10)]
    result = best_fit(curve)
    assert result["model"] == "exponential"
    assert abs(result["params"][1] - math.log(3.0)) < 1e-6


def test_fit_power_law_rejects_too_few_points():
    with pytest.raises(ValueError):
        fit_power_law([(2, 0.001)])


def test_fit_power_law_drops_zero_times():
    """Zero-time data points are unmeasurable; they're discarded."""
    curve = [(n, 0.0 if n == 4 else 2.0 * n ** 2) for n in range(2, 10)]
    a, b, rms = fit_power_law(curve)
    # Should still recover the n^2 shape from the other points.
    assert abs(b - 2.0) < 1e-3
