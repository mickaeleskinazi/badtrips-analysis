#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".cache" / "matplotlib"))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.models import plot_dose_response_panels  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot exploratory binned dose-response curves for selected group/outcome pairs."
    )
    parser.add_argument(
        "--analysis-table",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "analysis_table.csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "figures" / "dose_response_panels.png",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.analysis_table.exists():
        raise SystemExit(
            f"Analysis table not found: {args.analysis_table}\n"
            "Run: python3 scripts/run_exploratory_models.py"
        )
    plotted = plot_dose_response_panels(args.analysis_table, args.out)
    print(f"Panels plotted: {plotted}")
    print(f"Dose-response figure written to: {args.out}")


if __name__ == "__main__":
    main()

