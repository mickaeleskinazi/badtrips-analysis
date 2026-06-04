#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.audit import write_audit_outputs  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate aggregate audit tables for the local Erowid bad trips corpus."
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
        default=PROJECT_ROOT / "outputs" / "tables",
        help="Directory for aggregate CSV outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.csv.exists():
        raise SystemExit(f"Corpus CSV not found: {args.csv}")

    audit = write_audit_outputs(args.csv, args.out)
    print(f"Reports: {audit.report_count}")
    print(f"Unique URLs: {audit.unique_url_count}")
    print(f"Duplicate URLs: {audit.duplicate_url_count}")
    print(f"Substance categories: {len(audit.substance_counts)}")
    print(f"Outputs written to: {args.out}")


if __name__ == "__main__":
    main()

