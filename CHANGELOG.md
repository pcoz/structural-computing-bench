# Changelog

All notable changes to `structural-computing-bench`.

## [Unreleased] — v0.7 arc (PyPI publication unblock)

**No version bump.** This arc lands `structural-computing-bench
0.1.0a1` on PyPI for the first time.

### Added

- `.github/workflows/publish.yml` — Trusted Publisher workflow,
  same shape as the structural-computing + holant-tools equivalents.
  Triggers on GitHub Release publication OR via workflow_dispatch
  (target=pypi / testpypi). Requires a PyPI Trusted Publisher entry
  for `structural-computing-bench` to be configured (user-action).

### Changed

- `pyproject.toml`: dep floor bumped `structural-computing>=0.2.0a1`
  → `structural-computing>=0.6.0a1`. Reflects the version that the
  structural-computing PyPI publication will carry.

### Verified

- Dist artefacts built at `dist/structural_computing_bench-0.1.0a1*`;
  `twine check` PASSED.
- Wheel METADATA correctly carries `Requires-Dist:
  structural-computing>=0.6.0a1`.

### Required ordering

- `structural-computing-bench 0.1.0a1` MUST be uploaded AFTER
  `structural-computing 0.6.0a1` lands on PyPI, otherwise a clean
  `pip install structural-computing-bench` will fail.

---

## [0.1.0a1] — 2026-05-28 (initial GitHub release)

Per-machine cost-model calibration runner. Produces the data file
consumed by `structural_computing.calibration.apply_calibration(...)`.

### Includes

- Timing primitives (clock + warmup harness).
- Curve fitters (power-law / exponential) for fitting wall-clock
  cost models per leaf evaluator.
- Problem generators per leaf evaluator (planar Pfaffian, dart
  chain, Bodlaender DP, etc.).
- Calibration runner CLI (`python -m structural_computing_bench`).
- Orchestrator-trace analytics for post-hoc cost-model validation.

PyPI release blocked on `structural-computing>=0.2.0a1` being live —
which is itself blocked on the structural-computing PyPI publication.
v0.7 arc resolves this.
