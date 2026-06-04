from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


DOSE_BLOCK_RE = re.compile(r"\bDOSE:\s*(.*?)(?:\bBODY WEIGHT:|\bExp Year:|\bExpID:|$)", re.IGNORECASE | re.DOTALL)
DOSE_RE = re.compile(
    r"(?P<amount>\d+(?:\.\d+)?)(?:\s*(?:-|to)\s*\d+(?:\.\d+)?)?\s*"
    r"(?P<unit>micrograms?|mcg|ug|µg|milligrams?|mg|grams?|g|ml|mL|"
    r"tabs?|hits?|blotters?|buvards?|squares?|papers?|stamps?|"
    r"drops?|gouttes?|pills?|tablets?|capsules?|caps?)\b",
    re.IGNORECASE,
)


UNIT_MAP = {
    "microgram": "ug",
    "micrograms": "ug",
    "mcg": "ug",
    "ug": "ug",
    "µg": "ug",
    "milligram": "mg",
    "milligrams": "mg",
    "mg": "mg",
    "gram": "g",
    "grams": "g",
    "g": "g",
    "ml": "ml",
    "mL": "ml",
    "tab": "blotter",
    "tabs": "blotter",
    "hit": "blotter",
    "hits": "blotter",
    "blotter": "blotter",
    "blotters": "blotter",
    "buvard": "blotter",
    "buvards": "blotter",
    "square": "blotter",
    "squares": "blotter",
    "paper": "blotter",
    "papers": "blotter",
    "stamp": "blotter",
    "stamps": "blotter",
    "drop": "drop",
    "drops": "drop",
    "goutte": "drop",
    "gouttes": "drop",
    "pill": "pill",
    "pills": "pill",
    "tablet": "pill",
    "tablets": "pill",
    "capsule": "capsule",
    "capsules": "capsule",
    "cap": "capsule",
    "caps": "capsule",
}


def iter_rows(path: Path):
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        yield from csv.DictReader(handle)


def dose_block(text: str) -> str:
    match = DOSE_BLOCK_RE.search(text)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()[:800]


def extract_amounts(text: str) -> list[tuple[float, str]]:
    block = dose_block(text)
    amounts: list[tuple[float, str]] = []
    for match in DOSE_RE.finditer(block):
        amount = float(match.group("amount"))
        unit = UNIT_MAP.get(match.group("unit"), match.group("unit").lower())
        amounts.append((amount, unit))
    return amounts


def extract_dose_rows(coding_corpus_path: Path, report_codes_path: Path) -> list[dict[str, str]]:
    code_rows = {row["report_id"]: row for row in iter_rows(report_codes_path)}
    rows: list[dict[str, str]] = []
    for row in iter_rows(coding_corpus_path):
        report_id = row.get("report_id", "")
        amounts = extract_amounts(row.get("text", "") or "")
        by_unit: defaultdict[str, list[float]] = defaultdict(list)
        for amount, unit in amounts:
            by_unit[unit].append(amount)

        code_row = code_rows.get(report_id, {})
        rows.append(
            {
                "report_id": report_id,
                "target_groups": code_row.get("target_groups", ""),
                "dose_numeric_count": str(len(amounts)),
                "dose_units": " | ".join(sorted(by_unit)),
                "dose_max_mg": str(max(by_unit["mg"]) if by_unit["mg"] else ""),
                "dose_max_ug": str(max(by_unit["ug"]) if by_unit["ug"] else ""),
                "dose_max_g": str(max(by_unit["g"]) if by_unit["g"] else ""),
                "dose_max_ml": str(max(by_unit["ml"]) if by_unit["ml"] else ""),
                "dose_max_blotter": str(max(by_unit["blotter"]) if by_unit["blotter"] else ""),
                "dose_max_drop": str(max(by_unit["drop"]) if by_unit["drop"] else ""),
                "dose_max_pill": str(max(by_unit["pill"]) if by_unit["pill"] else ""),
                "dose_max_capsule": str(max(by_unit["capsule"]) if by_unit["capsule"] else ""),
                "dose_max_count": str(max(by_unit["count"]) if by_unit["count"] else ""),
            }
        )
    return rows


def write_dose_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_dose_unit_summary(path: Path, rows: list[dict[str, str]]) -> None:
    unit_counts: Counter[str] = Counter()
    any_dose = 0
    for row in rows:
        units = [unit for unit in row.get("dose_units", "").split(" | ") if unit]
        if units:
            any_dose += 1
        for unit in units:
            unit_counts[unit] += 1

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["unit", "reports", "pct_reports"])
        denominator = len(rows)
        writer.writerow(["any_numeric_dose", any_dose, f"{any_dose / denominator * 100:.2f}" if denominator else "0.00"])
        for unit, count in unit_counts.most_common():
            pct = count / denominator * 100 if denominator else 0
            writer.writerow([unit, count, f"{pct:.2f}"])


def write_dose_outputs(
    coding_corpus_path: Path,
    report_codes_path: Path,
    dose_rows_path: Path,
    output_dir: Path,
) -> list[dict[str, str]]:
    rows = extract_dose_rows(coding_corpus_path, report_codes_path)
    write_dose_rows(dose_rows_path, rows)
    write_dose_unit_summary(output_dir / "dose_unit_summary.csv", rows)
    return rows
