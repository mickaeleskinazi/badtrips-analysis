from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, median
from typing import Iterable


AGE_RE = re.compile(r"\bAge at time of experience:\s*(\d{1,3})", re.IGNORECASE)
EXP_YEAR_RE = re.compile(r"\bExp Year:\s*(\d{4})", re.IGNORECASE)
PUBLISHED_YEAR_RE = re.compile(
    r"\bPublished:\s*[A-Za-z]{3,9}\s+\d{1,2},\s+(\d{4})", re.IGNORECASE
)
GENDER_RE = re.compile(r"\bGender:\s*([A-Za-z][A-Za-z /-]{0,30})", re.IGNORECASE)


ROUTE_PATTERNS = {
    "route_oral": [r"\boral\b", r"\bdrank\b", r"\bate\b", r"\bswallow"],
    "route_smoked_vaporized": [r"\bsmok", r"\bvap(e|or)", r"\binhal"],
    "route_insufflated": [r"\binsufflat", r"\bsnort"],
    "route_sublingual": [r"\bsublingual\b", r"\bunder (my|the) tongue\b"],
    "route_rectal": [r"\brectal\b", r"\bplugged\b", r"\benema\b"],
    "route_injected": [r"\binject", r"\biv\b", r"\bintravenous\b", r"\bim\b", r"\bintramuscular\b"],
}

CONTEXT_PATTERNS = {
    "context_alone": [r"\balone\b", r"\bby myself\b", r"\bon my own\b"],
    "context_with_others": [
        r"\bwith (my )?friend",
        r"\bwith friends\b",
        r"\bwith my girlfriend\b",
        r"\bwith my boyfriend\b",
        r"\bwith my wife\b",
        r"\bwith my husband\b",
        r"\btrip sitter\b",
    ],
    "context_home": [r"\bat home\b", r"\bmy room\b", r"\bmy bedroom\b", r"\bmy house\b", r"\bmy apartment\b"],
    "context_party_festival": [r"\bparty\b", r"\bfestival\b", r"\brave\b", r"\bclub\b", r"\bconcert\b"],
    "context_outdoors": [r"\boutside\b", r"\bwoods\b", r"\bforest\b", r"\bpark\b", r"\bbeach\b", r"\bnature\b"],
}

STATE_PATTERNS = {
    "first_time": [r"\bfirst time\b", r"\bfirst experience\b", r"\bnever (done|tried|taken)\b"],
    "experienced_user": [r"\bexperienced\b", r"\bmany times\b", r"\bseveral times\b", r"\bregularly\b"],
    "negative_pre_state": [
        r"\bdepressed\b",
        r"\banxious before\b",
        r"\bstressed\b",
        r"\bbad mood\b",
        r"\bbad state of mind\b",
        r"\bnot in a good place\b",
    ],
    "intention_therapeutic": [r"\btherapeutic\b", r"\bhealing\b", r"\btherapy\b", r"\bwork on myself\b"],
}


def compile_patterns(patterns: dict[str, list[str]]) -> dict[str, list[re.Pattern[str]]]:
    return {
        name: [re.compile(pattern, re.IGNORECASE) for pattern in marker_patterns]
        for name, marker_patterns in patterns.items()
    }


ROUTE_REGEXES = compile_patterns(ROUTE_PATTERNS)
CONTEXT_REGEXES = compile_patterns(CONTEXT_PATTERNS)
STATE_REGEXES = compile_patterns(STATE_PATTERNS)


@dataclass(frozen=True)
class CovariateSummary:
    report_count: int
    availability: Counter[str]
    gender_counts: Counter[str]
    numeric_values: dict[str, list[int]]
    binary_counts: Counter[str]


def iter_rows(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        yield from csv.DictReader(handle)


def normalize_gender(value: str) -> str:
    cleaned = value.strip().lower()
    cleaned = re.sub(r"[^a-z /-].*$", "", cleaned).strip()
    if cleaned.startswith("male"):
        return "male"
    if cleaned.startswith("female"):
        return "female"
    if cleaned:
        return "other_or_unclear"
    return ""


def extract_int(pattern: re.Pattern[str], text: str) -> int | None:
    match = pattern.search(text)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def detect_any(regexes: dict[str, list[re.Pattern[str]]], text: str) -> dict[str, bool]:
    return {name: any(pattern.search(text) for pattern in patterns) for name, patterns in regexes.items()}


def read_report_codes(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    return {row["report_id"]: row for row in iter_rows(path)}


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def extract_covariate_rows(coding_corpus_path: Path, report_codes_path: Path) -> list[dict[str, str]]:
    code_rows = read_report_codes(report_codes_path)
    rows: list[dict[str, str]] = []

    for row in iter_rows(coding_corpus_path):
        report_id = row.get("report_id", "")
        text = row.get("text", "") or ""
        code_row = code_rows.get(report_id, {})

        age = extract_int(AGE_RE, text)
        exp_year = extract_int(EXP_YEAR_RE, text)
        published_year = extract_int(PUBLISHED_YEAR_RE, text)
        gender_match = GENDER_RE.search(text)
        gender = normalize_gender(gender_match.group(1)) if gender_match else ""

        substance_categories = [
            item for item in (row.get("substance_categories", "") or "").split(" | ") if item
        ]
        target_groups = [item for item in (code_row.get("target_groups", "") or "").split(" | ") if item]
        families = [item for item in (code_row.get("families", "") or "").split(" | ") if item]

        binary_features = {}
        binary_features.update(detect_any(ROUTE_REGEXES, text))
        binary_features.update(detect_any(CONTEXT_REGEXES, text))
        binary_features.update(detect_any(STATE_REGEXES, text))

        rows.append(
            {
                "report_id": report_id,
                "age": str(age or ""),
                "gender": gender,
                "exp_year": str(exp_year or ""),
                "published_year": str(published_year or ""),
                "dose_present": str(int("DOSE:" in text.upper())),
                "body_weight_present": str(int("BODY WEIGHT:" in text.upper())),
                "text_chars": str(len(text)),
                "word_count": str(count_words(text)),
                "source_row_count": row.get("source_row_count", ""),
                "substance_category_count": str(len(substance_categories)),
                "target_group_count": str(len(target_groups)),
                "family_count": str(len(families)),
                "multi_target_group": str(int(len(target_groups) > 1)),
                "target_groups": " | ".join(target_groups),
                "families": " | ".join(families),
                **{name: str(int(value)) for name, value in binary_features.items()},
            }
        )

    return rows


def write_covariate_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_covariates(rows: list[dict[str, str]]) -> CovariateSummary:
    availability: Counter[str] = Counter()
    gender_counts: Counter[str] = Counter()
    numeric_values: dict[str, list[int]] = defaultdict(list)
    binary_counts: Counter[str] = Counter()

    explicit_fields = ["age", "gender", "exp_year", "published_year", "dose_present", "body_weight_present"]
    numeric_fields = ["age", "exp_year", "published_year", "word_count", "substance_category_count", "target_group_count"]

    for row in rows:
        for field in explicit_fields:
            value = row.get(field, "")
            if value and value != "0":
                availability[field] += 1
        if row.get("gender"):
            gender_counts[row["gender"]] += 1
        for field in numeric_fields:
            value = row.get(field, "")
            if value:
                numeric_values[field].append(int(value))
        for field, value in row.items():
            if field.startswith(("route_", "context_", "first_time", "experienced_user", "negative_pre_state", "intention_")):
                if value == "1":
                    binary_counts[field] += 1

    return CovariateSummary(
        report_count=len(rows),
        availability=availability,
        gender_counts=gender_counts,
        numeric_values=dict(numeric_values),
        binary_counts=binary_counts,
    )


def write_availability(path: Path, summary: CovariateSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "age",
        "gender",
        "exp_year",
        "published_year",
        "dose_present",
        "body_weight_present",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["field", "n", "pct_reports"])
        for field in fields:
            count = summary.availability[field]
            pct = count / summary.report_count * 100 if summary.report_count else 0
            writer.writerow([field, count, f"{pct:.2f}"])


def write_counter(path: Path, key_name: str, counter: Counter[str], denominator: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([key_name, "n", "pct_reports"])
        for key, count in counter.most_common():
            pct = count / denominator * 100 if denominator else 0
            writer.writerow([key, count, f"{pct:.2f}"])


def write_numeric_summary(path: Path, summary: CovariateSummary) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["field", "n", "min", "median", "mean", "max"])
        for field, values in summary.numeric_values.items():
            if not values:
                continue
            writer.writerow(
                [
                    field,
                    len(values),
                    min(values),
                    f"{median(values):.1f}",
                    f"{mean(values):.1f}",
                    max(values),
                ]
            )


def write_covariate_outputs(
    coding_corpus_path: Path,
    report_codes_path: Path,
    covariate_rows_path: Path,
    output_dir: Path,
) -> CovariateSummary:
    rows = extract_covariate_rows(coding_corpus_path, report_codes_path)
    write_covariate_rows(covariate_rows_path, rows)
    summary = summarize_covariates(rows)
    write_availability(output_dir / "covariate_availability.csv", summary)
    write_counter(output_dir / "gender_counts.csv", "gender", summary.gender_counts, summary.report_count)
    write_counter(output_dir / "context_route_state_counts.csv", "feature", summary.binary_counts, summary.report_count)
    write_numeric_summary(output_dir / "covariate_numeric_summary.csv", summary)
    return summary

