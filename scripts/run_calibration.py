"""CLI: run the default calibration sweep and write the result as a
Python module the framework can load.

Usage:
    python scripts/run_calibration.py --out calibration_data/my_machine.py
    python scripts/run_calibration.py --out - | tee my_calibration.py

Optional flags:
    --repeat N     timed runs per measurement (default 5)
    --no-warmup    skip the warmup run
    --no-curves    omit raw curves from the output
"""
from __future__ import annotations

import argparse
import os
import sys

# Allow running this script without installing the package: prepend the
# repo root (parent of this `scripts/` directory) to sys.path.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from bench import (
    __version__ as bench_version,
    calibrate_default_evaluators,
    render_calibration_module,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", "-o", required=True,
        help="output path for the rendered Python module, or '-' for stdout",
    )
    parser.add_argument("--repeat", type=int, default=5,
                          help="timed runs per measurement (default 5)")
    parser.add_argument("--no-warmup", action="store_true",
                          help="skip the un-timed warmup run")
    args = parser.parse_args(argv)

    print("Running calibration (this can take a minute or two)...", file=sys.stderr)
    calibration = calibrate_default_evaluators(
        repeat=args.repeat,
        warmup=not args.no_warmup,
    )

    # Brief report on stderr so the user sees progress.
    for key, result in sorted(calibration.items()):
        a, b = result["params"]
        print(f"  {key}  model={result['model']:11s}  "
              f"a={a:.3e}  b={b:+.3f}  rms={result['rms']:.3f}",
              file=sys.stderr)

    source = render_calibration_module(calibration, bench_version=bench_version)
    if args.out == "-":
        sys.stdout.write(source)
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(source)
        print(f"Wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
