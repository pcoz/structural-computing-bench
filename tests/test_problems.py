"""Tests for the problem generators."""
import numpy as np

from bench import (
    make_gf2_affine_problem,
    make_cycle_graph,
    make_bipartite_graph,
    make_symmetric_signature,
)


def test_gf2_affine_shape():
    p = make_gf2_affine_problem(8)
    A, b = p["A"], p["b"]
    assert A.shape == (4, 8)        # m = n // 2 = 4
    assert b.shape == (4,)
    assert ((A == 0) | (A == 1)).all()


def test_gf2_affine_deterministic():
    """Same seed -> same matrix."""
    p1 = make_gf2_affine_problem(8, rng_seed=42)
    p2 = make_gf2_affine_problem(8, rng_seed=42)
    np.testing.assert_array_equal(p1["A"], p2["A"])
    np.testing.assert_array_equal(p1["b"], p2["b"])


def test_cycle_graph_basic_invariants():
    g = make_cycle_graph(8)
    assert len(g["vertices"]) == 8
    assert len(g["edges"]) == 8
    # Each vertex has exactly two neighbours in the rotation.
    for v in g["vertices"]:
        assert len(g["rotation"][v]) == 2


def test_cycle_graph_coerces_small_n():
    """Cycle of length < 3 is silently coerced to a triangle."""
    g = make_cycle_graph(1)
    assert len(g["vertices"]) == 3


def test_bipartite_graph_edge_count():
    """K_{n,n} has n^2 edges."""
    g = make_bipartite_graph(4)
    assert len(g["vertices"]) == 8
    assert len(g["edges"]) == 16


def test_symmetric_signature_pattern():
    """[2, 0, 2, 0, ...] of arity n."""
    sig = make_symmetric_signature(4)["values"]
    assert sig == [2, 0, 2, 0, 2]
    sig5 = make_symmetric_signature(5)["values"]
    assert sig5 == [2, 0, 2, 0, 2, 0]
