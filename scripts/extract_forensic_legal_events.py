#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.forensic_legal import write_forensic_outputs  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract forensic/legal markers, with psychedelic-related stratification."
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
        default=PROJECT_ROOT / "data" / "processed" / "forensic_legal_rows.csv",
    )
    parser.add_argument(
        "--validation-queue",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "forensic_legal_validation_queue.csv",
    )
    parser.add_argument(
        "--tables",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "tables",
    )
    parser.add_argument(
        "--max-validation-per-marker",
        type=int,
        default=75,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.coding_corpus.exists():
        raise SystemExit("Run scripts/prepare_coding_corpus.py first.")
    if not args.report_codes.exists():
        raise SystemExit("Run scripts/analyze_phenomenology.py first.")
    rows = write_forensic_outputs(
        args.coding_corpus,
        args.report_codes,
        args.out,
        args.validation_queue,
        args.tables,
        max_validation_per_marker=args.max_validation_per_marker,
    )
    psychedelic_related = sum(row.get("psychedelic_related") == "1" for row in rows)
    forensic_legal = sum(row.get("composite_any_forensic_legal") == "1" for row in rows)
    psychedelic_forensic_legal = sum(
        row.get("psychedelic_related") == "1" and row.get("composite_any_forensic_legal") == "1"
        for row in rows
    )
    print(f"Reports processed: {len(rows)}")
    print(f"Psychedelic-related reports: {psychedelic_related}")
    print(f"Forensic/legal screen-positive reports: {forensic_legal}")
    print(f"Psychedelic-related + forensic/legal screen-positive reports: {psychedelic_forensic_legal}")
    print(f"Local forensic/legal table written to: {args.out}")
    print(f"Local validation queue written to: {args.validation_queue}")
    print(f"Aggregate forensic/legal tables written to: {args.tables}")


if __name__ == "__main__":
    main()
