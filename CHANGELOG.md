# Changelog

All notable changes to `structural-computing-bench`.

## 2026-05-31 — v0.7 arc (PyPI publication unblock; no version bump)

**Shipped 2026-05-31.** No version bump. This arc landed
`structural-computing-bench 0.1.0a1` on PyPI for the first time.
Live at https://pypi.org/project/structural-computing-bench/0.1.0a1/.

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

### Upload ordering (verified)

- Uploaded AFTER `structural-computing 0.6.0a1` landed on PyPI.
- End-to-end clean-venv smoke check: `pip install
  structural-computing-bench` pulls in structural-computing
  0.6.0a1 + holant-tools 0.6.1 transparently.

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
