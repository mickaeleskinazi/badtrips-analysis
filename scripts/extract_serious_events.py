#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.serious_events import write_serious_event_outputs  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract serious adverse-event-like markers from all reports."
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
        default=PROJECT_ROOT / "data" / "processed" / "report_serious_events.csv",
    )
    parser.add_argument(
        "--validation-index",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "serious_event_validation_index.csv",
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
        raise SystemExit("Run scripts/prepare_coding_corpus.py first.")
    if not args.report_codes.exists():
        raise SystemExit("Run scripts/analyze_phenomenology.py first.")
    rows = write_serious_event_outputs(
        args.coding_corpus,
        args.report_codes,
        args.out,
        args.validation_index,
        args.tables,
    )
    print(f"Reports processed: {len(rows)}")
    print(f"Local serious event table written to: {args.out}")
    print(f"Local validation index written to: {args.validation_index}")
    print(f"Aggregate serious event tables written to: {args.tables}")


if __name__ == "__main__":
    main()

