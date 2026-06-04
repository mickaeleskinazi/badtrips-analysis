#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.covariates import write_covariate_outputs  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract report-level covariates from the local coding corpus."
    )
    parser.add_argument(
        "--coding-corpus",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "reports_for_coding.csv",
    )
    parser.add_argument(
        "--report-codes",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "report_codes.csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "report_covariates.csv",
    )
    parser.add_argument(
        "--tables",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "tables",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.coding_corpus.exists():
        raise SystemExit(
            f"Coding corpus not found: {args.coding_corpus}\n"
            "Run: python3 scripts/prepare_coding_corpus.py"
        )
    if not args.report_codes.exists():
        raise SystemExit(
            f"Report codes not found: {args.report_codes}\n"
            "Run: python3 scripts/analyze_phenomenology.py"
        )

    summary = write_covariate_outputs(args.coding_corpus, args.report_codes, args.out, args.tables)
    print(f"Reports processed: {summary.report_count}")
    print(f"Local covariate table written to: {args.out}")
    print(f"Aggregate tables written to: {args.tables}")


if __name__ == "__main__":
    main()

