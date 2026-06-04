from __future__ import annotations

import csv
import hashlib
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from trip_reports.audit import iter_rows


EXP_ID_RE = re.compile(r"[?&]ID=(\d+)")


def canonical_report_key(url: str) -> str:
    parsed = urlparse(url.strip())
    query = parse_qs(parsed.query)
    exp_id = query.get("ID") or query.get("id")
    if exp_id and exp_id[0]:
        return f"exp:{exp_id[0]}"

    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = parsed.path.rstrip("/")
    return f"url:{host}{path}?{parsed.query}"


def stable_report_id(url: str) -> str:
    key = canonical_report_key(url)
    if key.startswith("exp:"):
        return f"exp{key.split(':', 1)[1]}"
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
    return f"url{digest}"


def collapse_values(values: set[str]) -> str:
    cleaned = sorted(value.strip() for value in values if value and value.strip())
    return " | ".join(cleaned)


def prepare_coding_rows(csv_path: Path) -> list[dict[str, str]]:
    by_key: dict[str, dict[str, object]] = {}
    source_row_counts: defaultdict[str, int] = defaultdict(int)

    for row in iter_rows(csv_path):
        url = row.get("url", "").strip()
        if not url:
            continue

        key = canonical_report_key(url)
        source_row_counts[key] += 1
        if key not in by_key:
            by_key[key] = {
                "report_id": stable_report_id(url),
                "url": url,
                "title": row.get("title", "").strip(),
                "substance_categories": set(),
                "erowid_categories": set(),
                "source_category_urls": set(),
                "text": row.get("text", "") or "",
            }

        by_key[key]["substance_categories"].add(row.get("substance_category", ""))
        by_key[key]["erowid_categories"].add(row.get("erowid_category", ""))
        by_key[key]["source_category_urls"].add(row.get("source_category_url", ""))

        current_text = by_key[key]["text"]
        new_text = row.get("text", "") or ""
        if isinstance(current_text, str) and len(new_text) > len(current_text):
            by_key[key]["text"] = new_text

    coding_rows: list[dict[str, str]] = []
    for key, item in sorted(by_key.items(), key=lambda pair: pair[0]):
        coding_rows.append(
            {
                "report_id": str(item["report_id"]),
                "url": str(item["url"]),
                "title": str(item["title"]),
                "substance_categories": collapse_values(item["substance_categories"]),
                "erowid_categories": collapse_values(item["erowid_categories"]),
                "source_category_urls": collapse_values(item["source_category_urls"]),
                "source_row_count": str(source_row_counts[key]),
                "text": str(item["text"]),
            }
        )

    return coding_rows


def write_coding_corpus(csv_path: Path, output_path: Path) -> list[dict[str, str]]:
    rows = prepare_coding_rows(csv_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "report_id",
        "url",
        "title",
        "substance_categories",
        "erowid_categories",
        "source_category_urls",
        "source_row_count",
        "text",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_deduplication_summary(rows: list[dict[str, str]], output_path: Path, source_count: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    duplicate_rows = source_count - len(rows)
    max_source_count = max((int(row["source_row_count"]) for row in rows), default=0)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["source_rows", source_count])
        writer.writerow(["unique_reports", len(rows)])
        writer.writerow(["duplicate_rows_removed", duplicate_rows])
        writer.writerow(["max_rows_for_one_report", max_source_count])
