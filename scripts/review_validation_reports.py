#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.serious_events import narrative_portion, normalize_space  # noqa: E402


DEFAULT_CORPUS = PROJECT_ROOT / "data" / "processed" / "reports_for_coding.csv"
DEFAULT_QUEUE = PROJECT_ROOT / "data" / "processed" / "forensic_legal_validation_queue.csv"
DEFAULT_OUT = PROJECT_ROOT / "data" / "processed" / "review_batches" / "validation_batch.md"


def iter_rows(path: Path):
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        yield from csv.DictReader(handle)


def load_reports(path: Path) -> dict[str, dict[str, str]]:
    return {row["report_id"]: row for row in iter_rows(path)}


def load_queue(path: Path) -> list[dict[str, str]]:
    return list(iter_rows(path))


def matches_filters(row: dict[str, str], report_id: str | None, marker: str | None) -> bool:
    if report_id and row.get("report_id") != report_id:
        return False
    marker_value = row.get("forensic_marker") or row.get("serious_event_marker") or ""
    if marker and marker_value != marker:
        return False
    return True


def format_queue_fields(row: dict[str, str]) -> str:
    relevant = [
        "forensic_marker",
        "serious_event_marker",
        "review_set",
        "report_id",
        "url",
        "target_groups",
        "psychedelic_target_groups",
        "psychedelic_substance_markers",
        "matched_text",
        "matched_pattern",
        "evidence_snippet",
        "validation_status",
        "legal_event_confirmed",
        "event_type",
        "event_role",
        "actor_role",
        "intentionality",
        "third_party_harm_or_risk",
        "severity",
        "legal_outcome",
        "substance_contribution",
        "notes",
    ]
    lines = []
    for key in relevant:
        value = row.get(key, "")
        if value:
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def format_report(report: dict[str, str], queue_row: dict[str, str] | None, full_text: bool) -> str:
    title = report.get("title", "")
    report_id = report.get("report_id", "")
    url = report.get("url", "")
    header = [
        f"# {report_id}",
        "",
        f"- title: {title}",
        f"- url: {url}",
        f"- substance_categories: {report.get('substance_categories', '')}",
        f"- erowid_categories: {report.get('erowid_categories', '')}",
    ]
    if queue_row:
        header.extend(["", "## Queue row", "", format_queue_fields(queue_row)])
    if full_text:
        text = narrative_portion(report.get("text", ""))
        header.extend(["", "## Full local narrative", "", normalize_space(text)])
    return "\n".join(header).strip() + "\n"


def select_queue_rows(rows: list[dict[str, str]], report_id: str | None, marker: str | None, limit: int) -> list[dict[str, str]]:
    selected = [row for row in rows if matches_filters(row, report_id, marker)]
    return selected[:limit]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review full local reports from a validation queue without versioning report text."
    )
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--report-id", help="Show/export one report_id, e.g. exp100200.")
    parser.add_argument("--marker", help="Filter a forensic_marker or serious_event_marker.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--out", type=Path, help="Write a local markdown batch instead of printing.")
    parser.add_argument(
        "--snippet-only",
        action="store_true",
        help="Do not include full narrative text; useful for quick triage.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.corpus.exists():
        raise SystemExit(f"Corpus not found: {args.corpus}\nRun scripts/prepare_coding_corpus.py first.")
    if not args.queue.exists():
        raise SystemExit(f"Queue not found: {args.queue}")

    reports = load_reports(args.corpus)
    queue_rows = select_queue_rows(load_queue(args.queue), args.report_id, args.marker, args.limit)
    if args.report_id and not queue_rows and args.report_id in reports:
        queue_rows = [{"report_id": args.report_id}]
    if not queue_rows:
        raise SystemExit("No matching validation rows found.")

    sections = []
    for queue_row in queue_rows:
        report_id = queue_row.get("report_id", "")
        report = reports.get(report_id)
        if not report:
            continue
        sections.append(format_report(report, queue_row, full_text=not args.snippet_only))

    output = "\n\n---\n\n".join(sections)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
        print(f"Wrote local review batch: {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
