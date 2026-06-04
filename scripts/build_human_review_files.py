#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.contextual_flags import classify_context  # noqa: E402


DEFAULT_FORENSIC_QUEUE = PROJECT_ROOT / "data" / "processed" / "forensic_legal_validation_queue.csv"
DEFAULT_SERIOUS_QUEUE = PROJECT_ROOT / "data" / "processed" / "serious_event_validation_queue.csv"
DEFAULT_OUT_DIR = PROJECT_ROOT / "data" / "processed" / "human_review"
DEFAULT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"
DEFAULT_XLSX = PROJECT_ROOT / "outputs" / "human_review" / "human_review_workbook.xlsx"


HUMAN_REVIEW_PREFIX_FIELDS = [
    "pipeline",
    "review_id",
    "auto_review_priority",
    "auto_context_guess",
    "auto_actor_guess",
    "validation_status",
    "legal_event_confirmed",
    "event_confirmed",
    "substance_contribution",
    "notes",
]

AUTO_CONTEXT_FIELDS = [
    "auto_is_feared_or_belief",
    "auto_is_hypothetical",
    "auto_is_negated",
    "auto_is_analogy",
    "auto_is_substance_analogy",
    "auto_is_past_history",
    "auto_is_marker_specific_false_positive",
    "auto_has_actual_event_cue",
    "auto_local_window",
    "auto_snippet_length",
]

TAIL_FIELDS = [
    "report_id",
    "url",
    "forensic_marker",
    "serious_event_marker",
    "review_set",
    "target_groups",
    "psychedelic_target_groups",
    "psychedelic_substance_markers",
    "matched_text",
    "matched_pattern",
    "evidence_snippet",
    "event_type",
    "event_role",
    "actor_role",
    "intentionality",
    "third_party_harm_or_risk",
    "severity",
    "legal_outcome",
]


def iter_rows(path: Path):
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        yield from csv.DictReader(handle)


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def marker_for(row: dict[str, str]) -> str:
    return row.get("forensic_marker") or row.get("serious_event_marker") or "unknown_marker"


def enrich_queue(queue_path: Path, pipeline: str, limit: int | None = None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, row in enumerate(iter_rows(queue_path), start=1):
        if limit is not None and len(rows) >= limit:
            break
        context = classify_context(row)
        marker = marker_for(row)
        enriched = {
            **row,
            **context,
            "pipeline": pipeline,
            "review_id": f"{pipeline}_{index:05d}",
            "event_confirmed": row.get("legal_event_confirmed", ""),
            "validation_status": row.get("validation_status", ""),
            "substance_contribution": row.get("substance_contribution", ""),
            "notes": row.get("notes", ""),
            "forensic_marker": row.get("forensic_marker", ""),
            "serious_event_marker": row.get("serious_event_marker", ""),
            "marker": marker,
        }
        rows.append(enriched)
    rows.sort(
        key=lambda row: (
            {"high": 0, "medium": 1, "low": 2}.get(row.get("auto_review_priority", ""), 3),
            row.get("marker", ""),
            row.get("report_id", ""),
        )
    )
    return rows


def fieldnames_for(rows: list[dict[str, str]]) -> list[str]:
    preferred = HUMAN_REVIEW_PREFIX_FIELDS + AUTO_CONTEXT_FIELDS + TAIL_FIELDS
    seen = set()
    fieldnames = []
    for field in preferred:
        if field not in seen:
            seen.add(field)
            fieldnames.append(field)
    for row in rows:
        for field in row:
            if field not in seen:
                seen.add(field)
                fieldnames.append(field)
    return fieldnames


def write_summary(path: Path, rows_by_pipeline: dict[str, list[dict[str, str]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["pipeline", "summary_type", "value", "n"])
        for pipeline, rows in rows_by_pipeline.items():
            writer.writerow([pipeline, "total_rows", "all", len(rows)])
            for field in ["auto_review_priority", "auto_context_guess", "auto_actor_guess"]:
                counts = Counter(row.get(field, "") for row in rows)
                for value, count in counts.most_common():
                    writer.writerow([pipeline, field, value, count])
            marker_counts = Counter(marker_for(row) for row in rows)
            for marker, count in marker_counts.most_common():
                writer.writerow([pipeline, "marker", marker, count])


def excel_column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def inline_string_cell(ref: str, value: str) -> str:
    value = value or ""
    return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{escape(value)}</t></is></c>'


def write_simple_xlsx(path: Path, rows: list[dict[str, str]], fieldnames: list[str], sheet_name: str = "Human review") -> None:
    """Write a lightweight one-sheet XLSX with filters using only the standard library."""
    path.parent.mkdir(parents=True, exist_ok=True)
    max_col = excel_column_name(len(fieldnames))
    max_row = len(rows) + 1
    table_ref = f"A1:{max_col}{max_row}"

    sheet_rows = []
    header_cells = [
        inline_string_cell(f"{excel_column_name(col_index)}1", field)
        for col_index, field in enumerate(fieldnames, start=1)
    ]
    sheet_rows.append(f'<row r="1">{"".join(header_cells)}</row>')
    for row_index, row in enumerate(rows, start=2):
        cells = []
        for col_index, field in enumerate(fieldnames, start=1):
            ref = f"{excel_column_name(col_index)}{row_index}"
            cells.append(inline_string_cell(ref, row.get(field, "")))
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    cols = "".join(
        f'<col min="{idx}" max="{idx}" width="{width}" customWidth="1"/>'
        for idx, width in enumerate([18, 20, 16, 28, 28, 18, 18, 18, 22, 34], start=1)
    )
    sheet_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheetViews>
    <sheetView workbookViewId="0">
      <pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>
    </sheetView>
  </sheetViews>
  <cols>{cols}</cols>
  <sheetData>{"".join(sheet_rows)}</sheetData>
  <autoFilter ref="{table_ref}"/>
</worksheet>'''

    workbook_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
  xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="{escape(sheet_name)}" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>'''

    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>''',
        )
        archive.writestr(
            "_rels/.rels",
            '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>''',
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>''',
        )
        archive.writestr("xl/workbook.xml", workbook_xml)
        archive.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build local human-review CSV files with contextual flags for validation."
    )
    parser.add_argument("--forensic-queue", type=Path, default=DEFAULT_FORENSIC_QUEUE)
    parser.add_argument("--serious-queue", type=Path, default=DEFAULT_SERIOUS_QUEUE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--tables", type=Path, default=DEFAULT_TABLE_DIR)
    parser.add_argument("--xlsx-out", type=Path, default=DEFAULT_XLSX)
    parser.add_argument("--limit", type=int, help="Optional row limit per pipeline for testing.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.forensic_queue.exists():
        raise SystemExit(f"Missing forensic queue: {args.forensic_queue}")
    if not args.serious_queue.exists():
        raise SystemExit(f"Missing serious event queue: {args.serious_queue}")

    forensic_rows = enrich_queue(args.forensic_queue, "forensic_legal", limit=args.limit)
    serious_rows = enrich_queue(args.serious_queue, "serious_adverse_event", limit=args.limit)
    all_rows = forensic_rows + serious_rows

    write_rows(args.out_dir / "forensic_legal_human_review.csv", forensic_rows, fieldnames_for(forensic_rows))
    write_rows(args.out_dir / "serious_event_human_review.csv", serious_rows, fieldnames_for(serious_rows))
    combined_fieldnames = fieldnames_for(all_rows)
    write_rows(args.out_dir / "combined_human_review.csv", all_rows, combined_fieldnames)
    write_simple_xlsx(args.xlsx_out, all_rows, combined_fieldnames)
    write_summary(
        args.tables / "human_review_context_summary.csv",
        {"forensic_legal": forensic_rows, "serious_adverse_event": serious_rows},
    )

    print(f"Forensic/legal review rows: {len(forensic_rows)}")
    print(f"Serious adverse event review rows: {len(serious_rows)}")
    print(f"Human review CSVs written to: {args.out_dir}")
    print(f"Human review XLSX written to: {args.xlsx_out}")
    print(f"Context summary table written to: {args.tables / 'human_review_context_summary.csv'}")


if __name__ == "__main__":
    main()
