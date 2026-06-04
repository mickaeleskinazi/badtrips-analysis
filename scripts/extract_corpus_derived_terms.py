#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.serious_events import narrative_portion, normalize_space  # noqa: E402


DEFAULT_CORPUS = PROJECT_ROOT / "data" / "processed" / "reports_for_coding.csv"
DEFAULT_REPORT_CODES = PROJECT_ROOT / "data" / "processed" / "report_codes.csv"
DEFAULT_SERIOUS = PROJECT_ROOT / "data" / "processed" / "report_serious_events.csv"
DEFAULT_FORENSIC = PROJECT_ROOT / "data" / "processed" / "forensic_legal_rows.csv"
DEFAULT_OUT = PROJECT_ROOT / "outputs" / "tables" / "corpus_derived_terms.csv"
DEFAULT_SUMMARY = PROJECT_ROOT / "outputs" / "tables" / "corpus_derived_terms_summary.csv"


STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "almost",
    "alone",
    "along",
    "already",
    "also",
    "although",
    "always",
    "am",
    "an",
    "and",
    "another",
    "any",
    "are",
    "around",
    "as",
    "at",
    "away",
    "back",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "came",
    "can",
    "could",
    "day",
    "did",
    "didn",
    "do",
    "does",
    "doing",
    "don",
    "down",
    "during",
    "each",
    "even",
    "ever",
    "every",
    "everything",
    "felt",
    "few",
    "first",
    "for",
    "from",
    "get",
    "go",
    "going",
    "got",
    "had",
    "has",
    "have",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "him",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "just",
    "know",
    "last",
    "later",
    "like",
    "little",
    "long",
    "looked",
    "made",
    "make",
    "many",
    "me",
    "more",
    "most",
    "much",
    "my",
    "myself",
    "never",
    "no",
    "not",
    "now",
    "of",
    "off",
    "on",
    "once",
    "one",
    "only",
    "or",
    "other",
    "our",
    "out",
    "over",
    "own",
    "really",
    "said",
    "same",
    "saw",
    "say",
    "see",
    "she",
    "should",
    "so",
    "some",
    "something",
    "started",
    "still",
    "such",
    "than",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "thing",
    "things",
    "think",
    "this",
    "those",
    "thought",
    "through",
    "time",
    "to",
    "told",
    "too",
    "took",
    "trip",
    "under",
    "up",
    "us",
    "very",
    "want",
    "wanted",
    "was",
    "wasn",
    "way",
    "we",
    "well",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "will",
    "with",
    "within",
    "without",
    "would",
    "you",
}

BOILERPLATE = {
    "erowid",
    "experience",
    "experiences",
    "exp",
    "citation",
    "published",
    "views",
    "copyright",
    "copyrights",
    "terms",
    "use",
    "dose",
    "body",
    "weight",
    "oral",
    "smoked",
    "not",
    "given",
    "report",
    "reports",
    "vault",
    "art",
    "artist",
    "canvas",
    "donate",
    "donation",
    "details",
    "elucido",
    "front",
    "gift",
    "giclee",
    "glass",
    "hand-crafted",
    "hoodie",
    "logo",
    "ltd",
    "molecules",
    "pockets",
    "print",
    "receive",
    "signed",
    "solve",
    "stretched",
    "support",
    "reverberating",
    "shopping",
    "bag",
    "tote",
    "yours",
}

TOKEN_RE = re.compile(r"[a-z][a-z0-9\-']{2,}")


def iter_rows(path: Path):
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        yield from csv.DictReader(handle)


def split_groups(value: str) -> list[str]:
    return [item.strip() for item in value.split(" | ") if item.strip()]


def clean_text(text: str) -> str:
    text = narrative_portion(text)
    text = re.sub(r"\[\s*erowid note:.*?\]", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"\bCitation:.*?\bDOSE:\s*", " ", text, count=1, flags=re.IGNORECASE | re.DOTALL)
    return normalize_space(text.lower())


def tokenize(text: str) -> list[str]:
    tokens = []
    for token in TOKEN_RE.findall(clean_text(text)):
        token = token.strip("-'")
        if token in STOPWORDS or token in BOILERPLATE:
            continue
        if len(token) < 3:
            continue
        tokens.append(token)
    return tokens


def ngrams(tokens: list[str], min_n: int = 1, max_n: int = 3) -> list[str]:
    terms: list[str] = []
    for size in range(min_n, max_n + 1):
        for index in range(0, len(tokens) - size + 1):
            gram = tokens[index : index + size]
            if any(token in STOPWORDS or token in BOILERPLATE for token in gram):
                continue
            terms.append(" ".join(gram))
    return terms


def load_report_terms(corpus_path: Path, min_n: int, max_n: int) -> dict[str, Counter[str]]:
    report_terms: dict[str, Counter[str]] = {}
    for row in iter_rows(corpus_path):
        report_id = row.get("report_id", "")
        terms = ngrams(tokenize(row.get("text", "")), min_n=min_n, max_n=max_n)
        report_terms[report_id] = Counter(terms)
    return report_terms


def load_code_rows(path: Path) -> dict[str, dict[str, str]]:
    return {row["report_id"]: row for row in iter_rows(path)}


def document_frequency(report_terms: dict[str, Counter[str]], report_ids: set[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for report_id in report_ids:
        counts.update(report_terms.get(report_id, {}).keys())
    return counts


def total_frequency(report_terms: dict[str, Counter[str]], report_ids: set[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for report_id in report_ids:
        counts.update(report_terms.get(report_id, {}))
    return counts


def filter_counters(
    df: Counter[str],
    tf: Counter[str],
    min_df: int,
    max_vocab: int,
) -> tuple[Counter[str], Counter[str], set[str]]:
    vocab = {
        term
        for term, doc_n in df.most_common(max_vocab)
        if doc_n >= min_df and not is_low_value_term(term)
    }
    return (
        Counter({term: count for term, count in df.items() if term in vocab}),
        Counter({term: count for term, count in tf.items() if term in vocab}),
        vocab,
    )


def is_low_value_term(term: str) -> bool:
    tokens = term.split()
    if not tokens:
        return True
    if all(token in STOPWORDS or token in BOILERPLATE for token in tokens):
        return True
    if len(tokens) > 1 and (tokens[0] in STOPWORDS or tokens[-1] in STOPWORDS):
        return True
    if any(token.isdigit() for token in tokens):
        return True
    return False


def term_size(term: str) -> int:
    return term.count(" ") + 1


def log_odds(cohort_term_df: int, cohort_n: int, background_term_df: int, background_n: int) -> float:
    return math.log((cohort_term_df + 0.5) / (cohort_n - cohort_term_df + 0.5)) - math.log(
        (background_term_df + 0.5) / (background_n - background_term_df + 0.5)
    )


def add_overall_rows(
    output_rows: list[list[object]],
    all_df: Counter[str],
    all_tf: Counter[str],
    report_ids: set[str],
    top_n: int,
    min_df: int,
) -> None:
    for term, doc_n in all_df.most_common():
        if doc_n < min_df:
            continue
        output_rows.append(
            [
                "overall",
                "all_reports",
                len(report_ids),
                term_size(term),
                term,
                doc_n,
                f"{doc_n / len(report_ids) * 100:.2f}",
                all_tf[term],
                "",
                "",
                "",
            ]
        )
        if sum(row[0] == "overall" for row in output_rows) >= top_n:
            break


def add_specific_rows(
    output_rows: list[list[object]],
    comparison_type: str,
    cohort: str,
    cohort_ids: set[str],
    all_ids: set[str],
    report_terms: dict[str, Counter[str]],
    all_df: Counter[str],
    all_tf: Counter[str],
    vocab: set[str],
    top_n: int,
    min_df: int,
) -> None:
    if len(cohort_ids) < 10:
        return
    background_n = len(all_ids) - len(cohort_ids)
    if background_n < 10:
        return
    cohort_df: Counter[str] = Counter()
    cohort_tf: Counter[str] = Counter()
    for report_id in cohort_ids:
        terms = report_terms.get(report_id, {})
        cohort_df.update(term for term in terms if term in vocab)
        cohort_tf.update({term: count for term, count in terms.items() if term in vocab})
    scored = []
    for term, doc_n in cohort_df.items():
        if doc_n < min_df:
            continue
        background_term_df = all_df.get(term, 0) - doc_n
        score = log_odds(doc_n, len(cohort_ids), background_term_df, background_n)
        scored.append((score, doc_n, term))
    scored.sort(reverse=True)
    for score, doc_n, term in scored[:top_n]:
        output_rows.append(
            [
                comparison_type,
                cohort,
                len(cohort_ids),
                term_size(term),
                term,
                doc_n,
                f"{doc_n / len(cohort_ids) * 100:.2f}",
                cohort_tf[term],
                all_df.get(term, 0) - doc_n,
                f"{(all_df.get(term, 0) - doc_n) / background_n * 100:.2f}",
                f"{score:.4f}",
            ]
        )


def collect_cohorts(
    report_codes: dict[str, dict[str, str]],
    serious_rows: dict[str, dict[str, str]],
    forensic_rows: dict[str, dict[str, str]],
) -> dict[tuple[str, str], set[str]]:
    cohorts: defaultdict[tuple[str, str], set[str]] = defaultdict(set)
    for report_id, row in report_codes.items():
        for group in split_groups(row.get("target_groups", "")):
            cohorts[("target_group", group)].add(report_id)
        for marker, value in row.items():
            if marker in {"report_id", "primary_family", "families", "target_groups"}:
                continue
            if value == "1":
                cohorts[("phenomenology_marker", marker)].add(report_id)

    for report_id, row in serious_rows.items():
        for marker, value in row.items():
            if marker in {"report_id", "url", "target_groups"}:
                continue
            if not marker.startswith("composite_") and marker not in {
                "defenestration_jump_fall_height",
                "traffic_driving_accident",
                "ambulance_paramedics_fire_rescue",
                "er_hospital_icu",
                "suicidality_self_harm",
                "psychosis_delirium_dangerous",
                "death_fatality_reported",
            }:
                continue
            if value == "1":
                cohorts[("serious_event_marker", marker)].add(report_id)

    for report_id, row in forensic_rows.items():
        for marker, value in row.items():
            if marker in {
                "report_id",
                "url",
                "primary_family",
                "target_groups",
                "psychedelic_target_groups",
                "psychedelic_substance_markers",
            }:
                continue
            if not marker.startswith("composite_") and marker not in {
                "law_enforcement_contact",
                "arrest_detention_custody",
                "charges_court_probation",
                "assault_violence_weapon",
                "homicide_death_investigation",
                "suicide_self_harm_forensic",
                "sexual_assault_exploitation",
                "impaired_driving_traffic_endangerment",
                "endangerment_of_others",
            }:
                continue
            if value == "1":
                cohorts[("forensic_legal_marker", marker)].add(report_id)
    return dict(cohorts)


def write_summary(path: Path, rows: list[list[object]]) -> None:
    counts: Counter[str] = Counter(row[0] for row in rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["comparison_type", "n_terms"])
        writer.writerows(counts.most_common())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract corpus-derived n-grams and specificity scores.")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--report-codes", type=Path, default=PROJECT_ROOT / "data" / "processed" / "report_codes.csv")
    parser.add_argument("--serious", type=Path, default=DEFAULT_SERIOUS)
    parser.add_argument("--forensic", type=Path, default=DEFAULT_FORENSIC)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--top-n", type=int, default=75)
    parser.add_argument("--overall-top-n", type=int, default=300)
    parser.add_argument("--min-df", type=int, default=10)
    parser.add_argument("--max-vocab", type=int, default=25000)
    parser.add_argument("--min-ngram", type=int, default=1)
    parser.add_argument("--max-ngram", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for path in [args.corpus, args.report_codes, args.serious, args.forensic]:
        if not path.exists():
            raise SystemExit(f"Missing required input: {path}")

    report_terms = load_report_terms(args.corpus, min_n=args.min_ngram, max_n=args.max_ngram)
    all_ids = set(report_terms)
    all_df_raw = document_frequency(report_terms, all_ids)
    all_tf_raw = total_frequency(report_terms, all_ids)
    all_df, all_tf, vocab = filter_counters(
        all_df_raw,
        all_tf_raw,
        min_df=args.min_df,
        max_vocab=args.max_vocab,
    )
    report_codes = load_code_rows(args.report_codes)
    serious_rows = load_code_rows(args.serious)
    forensic_rows = load_code_rows(args.forensic)
    cohorts = collect_cohorts(report_codes, serious_rows, forensic_rows)

    rows: list[list[object]] = []
    add_overall_rows(rows, all_df, all_tf, all_ids, top_n=args.overall_top_n, min_df=args.min_df)
    for (comparison_type, cohort), cohort_ids in sorted(cohorts.items()):
        add_specific_rows(
            rows,
            comparison_type,
            cohort,
            cohort_ids & all_ids,
            all_ids,
            report_terms,
            all_df,
            all_tf,
            vocab,
            top_n=args.top_n,
            min_df=args.min_df,
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "comparison_type",
                "cohort",
                "cohort_n_reports",
                "ngram_n",
                "term",
                "cohort_doc_n",
                "cohort_doc_pct",
                "cohort_term_count",
                "background_doc_n",
                "background_doc_pct",
                "specificity_log_odds",
            ]
        )
        writer.writerows(rows)
    write_summary(args.summary, rows)
    print(f"Reports processed: {len(all_ids)}")
    print(f"Vocabulary terms retained: {len(vocab)}")
    print(f"Cohorts compared: {len(cohorts)}")
    print(f"Corpus-derived term rows: {len(rows)}")
    print(f"Terms written to: {args.out}")
    print(f"Summary written to: {args.summary}")


if __name__ == "__main__":
    main()
