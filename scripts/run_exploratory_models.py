#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.models import run_all_models  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run exploratory regression models on report-level codes and covariates."
    )
    parser.add_argument(
        "--report-codes",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "report_codes.csv",
    )
    parser.add_argument(
        "--covariates",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "report_covariates.csv",
    )
    parser.add_argument(
        "--doses",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "report_doses.csv",
    )
    parser.add_argument(
        "--analysis-table",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "analysis_table.csv",
    )
    parser.add_argument(
        "--tables",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "tables",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    missing = [path for path in [args.report_codes, args.covariates] if not path.exists()]
    if missing:
        raise SystemExit(
            "Missing required local tables:\n"
            + "\n".join(str(path) for path in missing)
            + "\nRun scripts/analyze_phenomenology.py and scripts/extract_covariates.py first."
        )
    if not args.doses.exists():
        print(f"Dose table not found, dose-response screen will be skipped unless generated: {args.doses}")

    tables = run_all_models(args.report_codes, args.covariates, args.doses, args.analysis_table, args.tables)
    print(f"Model groups written: {', '.join(tables)}")
    print(f"Local analysis table written to: {args.analysis_table}")
    print(f"Aggregate model tables written to: {args.tables}")


if __name__ == "__main__":
    main()

