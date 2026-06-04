from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Iterable


METADATA_PATTERNS = {
    "exp_id": re.compile(r"\bExpID:\s*\d+", re.IGNORECASE),
    "exp_year": re.compile(r"\bExp Year:\s*\d{4}", re.IGNORECASE),
    "gender": re.compile(r"\bGender:\s*[^.|\n\r]+", re.IGNORECASE),
    "age": re.compile(r"\bAge at time of experience:\s*\d+", re.IGNORECASE),
    "published": re.compile(r"\bPublished:\s*[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}", re.IGNORECASE),
    "dose": re.compile(r"\bDOSE:", re.IGNORECASE),
    "body_weight": re.compile(r"\bBODY WEIGHT:", re.IGNORECASE),
}


@dataclass
class CorpusAudit:
    report_count: int
    unique_url_count: int
    duplicate_url_count: int
    text_length_min: int
    text_length_median: float
    text_length_mean: float
    text_length_max: int
    substance_counts: Counter[str]
    erowid_category_counts: Counter[str]
    metadata_counts: Counter[str]


def iter_rows(csv_path: Path) -> Iterable[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        yield from reader


def audit_corpus(csv_path: Path) -> CorpusAudit:
    substance_counts: Counter[str] = Counter()
    erowid_category_counts: Counter[str] = Counter()
    metadata_counts: Counter[str] = Counter()
    url_counts: Counter[str] = Counter()
    text_lengths: list[int] = []
    report_count = 0

    for row in iter_rows(csv_path):
        report_count += 1
        url = row.get("url", "").strip()
        text = row.get("text", "") or ""
        substance = row.get("substance_category", "").strip() or "Unknown"
        erowid_category = row.get("erowid_category", "").strip() or "Unknown"

        url_counts[url] += 1
        substance_counts[substance] += 1
        erowid_category_counts[erowid_category] += 1
        text_lengths.append(len(text))

        for name, pattern in METADATA_PATTERNS.items():
            if pattern.search(text):
                metadata_counts[name] += 1

    if not text_lengths:
        text_lengths = [0]

    duplicate_url_count = sum(count - 1 for count in url_counts.values() if count > 1)

    return CorpusAudit(
        report_count=report_count,
        unique_url_count=len(url_counts),
        duplicate_url_count=duplicate_url_count,
        text_length_min=min(text_lengths),
        text_length_median=median(text_lengths),
        text_length_mean=mean(text_lengths),
        text_length_max=max(text_lengths),
        substance_counts=substance_counts,
        erowid_category_counts=erowid_category_counts,
        metadata_counts=metadata_counts,
    )


def write_counter(path: Path, key_name: str, counter: Counter[str], total: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([key_name, "n", "pct"])
        for key, count in counter.most_common():
            pct = (count / total * 100) if total else 0
            writer.writerow([key, count, f"{pct:.2f}"])


def write_summary(path: Path, audit: CorpusAudit) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("report_count", audit.report_count),
        ("unique_url_count", audit.unique_url_count),
        ("duplicate_url_count", audit.duplicate_url_count),
        ("text_length_min_chars", audit.text_length_min),
        ("text_length_median_chars", f"{audit.text_length_median:.1f}"),
        ("text_length_mean_chars", f"{audit.text_length_mean:.1f}"),
        ("text_length_max_chars", audit.text_length_max),
        ("substance_category_count", len(audit.substance_counts)),
        ("erowid_category_count", len(audit.erowid_category_counts)),
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerows(rows)


def write_metadata_presence(path: Path, audit: CorpusAudit) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metadata_field", "n", "pct"])
        for key in METADATA_PATTERNS:
            count = audit.metadata_counts[key]
            pct = (count / audit.report_count * 100) if audit.report_count else 0
            writer.writerow([key, count, f"{pct:.2f}"])


def write_audit_outputs(csv_path: Path, output_dir: Path) -> CorpusAudit:
    audit = audit_corpus(csv_path)
    write_summary(output_dir / "corpus_audit_summary.csv", audit)
    write_counter(
        output_dir / "substance_category_counts.csv",
        "substance_category",
        audit.substance_counts,
        audit.report_count,
    )
    write_counter(
        output_dir / "erowid_category_counts.csv",
        "erowid_category",
        audit.erowid_category_counts,
        audit.report_count,
    )
    write_metadata_presence(output_dir / "metadata_presence.csv", audit)
    return audit

