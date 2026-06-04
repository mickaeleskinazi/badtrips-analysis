#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.phenomenology import MARKER_PATTERNS, write_analysis_outputs  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate aggregate phenomenological marker tables from the local coding corpus."
    )
    parser.add_argument(
        "--coding-corpus",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "reports_for_coding.csv",
        help="Local deduplicated corpus with full report texts.",
    )
    parser.add_argument(
        "--report-codes",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "report_codes.csv",
        help="Local report-level marker table without report text.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "tables",
        help="Directory for aggregate analysis tables.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.coding_corpus.exists():
        raise SystemExit(
            f"Coding corpus not found: {args.coding_corpus}\n"
            "Run: python3 scripts/prepare_coding_corpus.py"
        )

    coded = write_analysis_outputs(args.coding_corpus, args.report_codes, args.out)
    print(f"Reports coded: {len(coded)}")
    print(f"Markers: {len(MARKER_PATTERNS)}")
    print(f"Local report codes written to: {args.report_codes}")
    print(f"Aggregate tables written to: {args.out}")


if __name__ == "__main__":
    main()

