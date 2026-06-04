#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.audit import iter_rows  # noqa: E402
from trip_reports.prepare import write_coding_corpus, write_deduplication_summary  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a local deduplicated corpus for phenomenological coding."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=PROJECT_ROOT / "data" / "badtrip_reports_by_substance.csv",
        help="Path to the local non-versioned corpus CSV.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "reports_for_coding.csv",
        help="Local output CSV containing full texts for qualitative coding.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "tables" / "deduplication_summary.csv",
        help="Aggregate deduplication summary without report text.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.csv.exists():
        raise SystemExit(f"Corpus CSV not found: {args.csv}")

    source_count = sum(1 for _ in iter_rows(args.csv))
    rows = write_coding_corpus(args.csv, args.out)
    write_deduplication_summary(rows, args.summary, source_count)

    print(f"Source rows: {source_count}")
    print(f"Unique reports: {len(rows)}")
    print(f"Local coding corpus written to: {args.out}")
    print(f"Aggregate summary written to: {args.summary}")


if __name__ == "__main__":
    main()

