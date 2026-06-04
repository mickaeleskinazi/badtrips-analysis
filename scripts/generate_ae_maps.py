#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".cache" / "matplotlib"))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.adverse_events import write_ae_outputs  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate adverse-event-like marker maps by targeted substance group."
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
        default=PROJECT_ROOT / "data" / "processed" / "report_ae_codes.csv",
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
    rows = write_ae_outputs(args.coding_corpus, args.report_codes, args.out, args.tables)
    print(f"Reports processed: {len(rows)}")
    print(f"Local AE code table written to: {args.out}")
    print(f"Aggregate AE map tables written to: {args.tables}")


if __name__ == "__main__":
    main()
