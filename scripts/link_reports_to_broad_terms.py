#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from extract_corpus_derived_terms import ngrams, tokenize  # noqa: E402


DEFAULT_REPORTS = PROJECT_ROOT / "data" / "processed" / "reports_for_coding.csv"
DEFAULT_KEEP_TERMS = PROJECT_ROOT / "outputs" / "human_review" / "broad_category_keep_terms.csv"
DEFAULT_FLAGS = PROJECT_ROOT / "data" / "processed" / "broad_category_report_flags.csv"
DEFAULT_LONG = PROJECT_ROOT / "data" / "processed" / "broad_category_report_terms_long.csv"
DEFAULT_CATEGORY_SUMMARY = PROJECT_ROOT / "outputs" / "tables" / "broad_category_report_summary.csv"
DEFAULT_TERM_SUMMARY = PROJECT_ROOT / "outputs" / "tables" / "broad_category_term_match_summary.csv"


@dataclass(frozen=True)
class TermDecision:
    analysis_domain: str
    broad_cohort: str
    original_cohort: str
    term: str
    term_key: str
    broad_slug: str


def iter_rows(path: Path):
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        yield from csv.DictReader(handle)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "unknown"


def normalize_term(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def load_keep_terms(path: Path) -> list[TermDecision]:
    decisions: list[TermDecision] = []
    seen: set[tuple[str, str, str]] = set()
    for row in iter_rows(path):
        if row.get("review_decision", "").strip().lower() != "keep":
            continue
        term_key = normalize_term(row.get("term", ""))
        if not term_key:
            continue
        decision = TermDecision(
            analysis_domain=row.get("analysis_domain", "").strip(),
            broad_cohort=row.get("broad_cohort", "").strip(),
            original_cohort=row.get("original_cohort", "").strip(),
            term=row.get("term", "").strip(),
            term_key=term_key,
            broad_slug=slugify(row.get("broad_cohort", "")),
        )
        key = (decision.analysis_domain, decision.broad_cohort, decision.term_key)
        if key in seen:
            continue
        seen.add(key)
        decisions.append(decision)
    return decisions


def term_ngram_bounds(decisions: list[TermDecision]) -> tuple[int, int]:
    sizes = [decision.term_key.count(" ") + 1 for decision in decisions]
    if not sizes:
        return 1, 1
    return min(sizes), max(sizes)


def build_term_index(decisions: list[TermDecision]) -> dict[str, list[TermDecision]]:
    index: dict[str, list[TermDecision]] = defaultdict(list)
    for decision in decisions:
        index[decision.term_key].append(decision)
    return index


def report_metadata(row: dict[str, str]) -> dict[str, str]:
    return {
        "report_id": row.get("report_id", ""),
        "url": row.get("url", ""),
        "title": row.get("title", ""),
        "substance_categories": row.get("substance_categories", ""),
        "erowid_categories": row.get("erowid_categories", ""),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Link every deduplicated trip report to reviewed broad-category terms."
    )
    parser.add_argument("--reports", type=Path, default=DEFAULT_REPORTS)
    parser.add_argument("--keep-terms", type=Path, default=DEFAULT_KEEP_TERMS)
    parser.add_argument("--flags-out", type=Path, default=DEFAULT_FLAGS)
    parser.add_argument("--long-out", type=Path, default=DEFAULT_LONG)
    parser.add_argument("--category-summary-out", type=Path, default=DEFAULT_CATEGORY_SUMMARY)
    parser.add_argument("--term-summary-out", type=Path, default=DEFAULT_TERM_SUMMARY)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    decisions = load_keep_terms(args.keep_terms)
    term_index = build_term_index(decisions)
    min_n, max_n = term_ngram_bounds(decisions)
    broad_categories = sorted({decision.broad_cohort for decision in decisions})
    broad_slug_by_name = {name: slugify(name) for name in broad_categories}

    long_rows: list[dict[str, object]] = []
    flag_rows: list[dict[str, object]] = []
    category_report_ids: dict[str, set[str]] = defaultdict(set)
    term_report_ids: dict[tuple[str, str, str, str], set[str]] = defaultdict(set)
    report_count = 0

    for row in iter_rows(args.reports):
        report_count += 1
        metadata = report_metadata(row)
        report_id = metadata["report_id"]
        report_terms = set(ngrams(tokenize(row.get("text", "")), min_n=min_n, max_n=max_n))
        matched_decisions: list[TermDecision] = []
        for term_key in report_terms.intersection(term_index):
            matched_decisions.extend(term_index[term_key])

        matched_by_category: dict[str, list[TermDecision]] = defaultdict(list)
        for decision in matched_decisions:
            matched_by_category[decision.broad_cohort].append(decision)
            category_report_ids[decision.broad_cohort].add(report_id)
            term_report_ids[
                (
                    decision.analysis_domain,
                    decision.broad_cohort,
                    decision.original_cohort,
                    decision.term,
                )
            ].add(report_id)
            long_rows.append(
                {
                    **metadata,
                    "analysis_domain": decision.analysis_domain,
                    "broad_cohort": decision.broad_cohort,
                    "original_cohort": decision.original_cohort,
                    "term": decision.term,
                }
            )

        flag_row: dict[str, object] = {
            **metadata,
            "n_broad_categories_matched": len(matched_by_category),
            "n_kept_terms_matched": len({decision.term_key for decision in matched_decisions}),
            "matched_broad_categories": " | ".join(sorted(matched_by_category)),
            "matched_analysis_domains": " | ".join(
                sorted({decision.analysis_domain for decision in matched_decisions})
            ),
        }
        for broad_name in broad_categories:
            slug = broad_slug_by_name[broad_name]
            terms = sorted({decision.term for decision in matched_by_category.get(broad_name, [])})
            flag_row[f"flag__{slug}"] = int(bool(terms))
            flag_row[f"n_terms__{slug}"] = len(terms)
            flag_row[f"terms__{slug}"] = " | ".join(terms)
        flag_rows.append(flag_row)

    category_summary_rows = []
    for broad_name in broad_categories:
        n_reports = len(category_report_ids[broad_name])
        category_summary_rows.append(
            {
                "analysis_domain": sorted(
                    {decision.analysis_domain for decision in decisions if decision.broad_cohort == broad_name}
                )[0],
                "broad_cohort": broad_name,
                "broad_slug": broad_slug_by_name[broad_name],
                "n_reviewed_keep_terms": sum(1 for decision in decisions if decision.broad_cohort == broad_name),
                "n_matched_reports": n_reports,
                "pct_reports": f"{(n_reports / report_count * 100):.2f}" if report_count else "0.00",
            }
        )
    category_summary_rows.sort(key=lambda row: (-int(row["n_matched_reports"]), row["broad_cohort"]))

    term_summary_rows = []
    for (analysis_domain, broad_cohort, original_cohort, term), report_ids in term_report_ids.items():
        term_summary_rows.append(
            {
                "analysis_domain": analysis_domain,
                "broad_cohort": broad_cohort,
                "original_cohort": original_cohort,
                "term": term,
                "n_matched_reports": len(report_ids),
                "pct_reports": f"{(len(report_ids) / report_count * 100):.2f}" if report_count else "0.00",
            }
        )
    term_summary_rows.sort(key=lambda row: (-int(row["n_matched_reports"]), row["broad_cohort"], row["term"]))

    base_flag_fields = [
        "report_id",
        "url",
        "title",
        "substance_categories",
        "erowid_categories",
        "n_broad_categories_matched",
        "n_kept_terms_matched",
        "matched_broad_categories",
        "matched_analysis_domains",
    ]
    category_flag_fields: list[str] = []
    for broad_name in broad_categories:
        slug = broad_slug_by_name[broad_name]
        category_flag_fields.extend([f"flag__{slug}", f"n_terms__{slug}", f"terms__{slug}"])

    write_csv(args.flags_out, base_flag_fields + category_flag_fields, flag_rows)
    write_csv(
        args.long_out,
        [
            "report_id",
            "url",
            "title",
            "substance_categories",
            "erowid_categories",
            "analysis_domain",
            "broad_cohort",
            "original_cohort",
            "term",
        ],
        long_rows,
    )
    write_csv(
        args.category_summary_out,
        [
            "analysis_domain",
            "broad_cohort",
            "broad_slug",
            "n_reviewed_keep_terms",
            "n_matched_reports",
            "pct_reports",
        ],
        category_summary_rows,
    )
    write_csv(
        args.term_summary_out,
        [
            "analysis_domain",
            "broad_cohort",
            "original_cohort",
            "term",
            "n_matched_reports",
            "pct_reports",
        ],
        term_summary_rows,
    )

    matched_report_count = sum(1 for row in flag_rows if int(row["n_broad_categories_matched"]) > 0)
    category_counter = Counter()
    for row in flag_rows:
        for broad_name in broad_categories:
            if row[f"flag__{broad_slug_by_name[broad_name]}"]:
                category_counter[broad_name] += 1

    print(f"Reports processed: {report_count}")
    print(f"Reviewed keep terms loaded: {len(decisions)}")
    print(f"Reports with >=1 broad-category term: {matched_report_count}")
    print(f"Long report-term rows: {len(long_rows)}")
    print(f"Report flags written to: {args.flags_out}")
    print(f"Report-term long table written to: {args.long_out}")
    print(f"Category summary written to: {args.category_summary_out}")
    print(f"Term summary written to: {args.term_summary_out}")
    print("Top categories:")
    for broad_name, count in category_counter.most_common(10):
        print(f"  {broad_name}: {count}")


if __name__ == "__main__":
    main()
