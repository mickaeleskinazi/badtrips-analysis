from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


AE_PATTERNS: dict[str, list[str]] = {
    "cardiovascular": [
        r"\bheart (attack|rate|racing|pounding|beating|palpitation)",
        r"\bpalpitation",
        r"\btachycard",
        r"\bchest pain\b",
        r"\bblood pressure\b",
        r"\bfaint",
    ],
    "respiratory": [
        r"\bcould(n't| not) breathe\b",
        r"\bcan't breathe\b",
        r"\bshort(ness)? of breath\b",
        r"\bbreathing\b",
        r"\bhyperventilat",
        r"\bchoking\b",
    ],
    "gastrointestinal": [
        r"\bnausea",
        r"\bvomit",
        r"\bpuk",
        r"\bthrowing up\b",
        r"\bdiarrhea\b",
        r"\bstomach pain\b",
        r"\babdominal\b",
    ],
    "neurological_motor": [
        r"\bseizure",
        r"\bconvulsion",
        r"\btrembl",
        r"\bshaking\b",
        r"\btwitch",
        r"\bnumb",
        r"\bparaly",
        r"\bataxia\b",
    ],
    "panic_anxiety": [
        r"\bpanic",
        r"\banxiety\b",
        r"\banxious\b",
        r"\bterror\b",
        r"\bterrified\b",
        r"\bscared\b",
        r"\bfear\b",
    ],
    "psychosis_paranoia": [
        r"\bparanoi",
        r"\bpsychosis\b",
        r"\bpsychotic\b",
        r"\bdelusion",
        r"\bvoices\b",
        r"\bthey were watching\b",
        r"\bfollowing me\b",
    ],
    "confusion_delirium": [
        r"\bconfus",
        r"\bdeliri",
        r"\bdisorient",
        r"\bdid(n't| not) know where\b",
        r"\bdid(n't| not) know who\b",
        r"\bmemory gap\b",
        r"\bblackout\b",
    ],
    "derealization_depersonalization": [
        r"\bderealization\b",
        r"\bdepersonalization\b",
        r"\bunreal\b",
        r"\bnot real\b",
        r"\breality\b",
        r"\bego death\b",
        r"\bego loss\b",
        r"\bdissolv",
    ],
    "loss_of_consciousness_blackout": [
        r"\bblack(ed)? out\b",
        r"\bpassed out\b",
        r"\bunconscious\b",
        r"\blost consciousness\b",
        r"\bcame to\b",
    ],
    "injury_accident": [
        r"\binjur",
        r"\bbruise",
        r"\bcut\b",
        r"\bbleed",
        r"\bblood\b",
        r"\bfell\b",
        r"\bfall\b",
        r"\bcrash",
        r"\baccident\b",
    ],
    "medical_emergency": [
        r"\bhospital\b",
        r"\bambulance\b",
        r"\bemergency room\b",
        r"\bparamedic",
        r"\bdoctor\b",
        r"\bnurse\b",
        r"\b911\b",
        r"\bpoison control\b",
    ],
    "self_harm_suicidality": [
        r"\bsuicid",
        r"\bkill myself\b",
        r"\bhurt myself\b",
        r"\bself[- ]harm\b",
    ],
}


def compile_patterns(patterns: dict[str, list[str]]) -> dict[str, list[re.Pattern[str]]]:
    return {
        name: [re.compile(pattern, re.IGNORECASE) for pattern in marker_patterns]
        for name, marker_patterns in patterns.items()
    }


COMPILED_AE_PATTERNS = compile_patterns(AE_PATTERNS)


def iter_rows(path: Path):
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        yield from csv.DictReader(handle)


def detect_ae_markers(text: str) -> dict[str, bool]:
    return {
        name: any(pattern.search(text) for pattern in patterns)
        for name, patterns in COMPILED_AE_PATTERNS.items()
    }


def extract_ae_rows(coding_corpus_path: Path, report_codes_path: Path) -> list[dict[str, str]]:
    code_rows = {row["report_id"]: row for row in iter_rows(report_codes_path)}
    rows: list[dict[str, str]] = []
    for row in iter_rows(coding_corpus_path):
        report_id = row.get("report_id", "")
        code_row = code_rows.get(report_id, {})
        markers = detect_ae_markers(row.get("text", "") or "")
        rows.append(
            {
                "report_id": report_id,
                "target_groups": code_row.get("target_groups", ""),
                **{name: str(int(value)) for name, value in markers.items()},
            }
        )
    return rows


def write_ae_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_ae_prevalence(path: Path, rows: list[dict[str, str]]) -> None:
    counts: Counter[str] = Counter()
    for row in rows:
        for marker in AE_PATTERNS:
            if row.get(marker) == "1":
                counts[marker] += 1
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["ae_marker", "n", "pct_reports"])
        for marker, count in counts.most_common():
            pct = count / len(rows) * 100 if rows else 0
            writer.writerow([marker, count, f"{pct:.2f}"])


def write_ae_by_target_group(path: Path, rows: list[dict[str, str]], min_group_n: int = 100) -> None:
    group_totals: Counter[str] = Counter()
    marker_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        groups = [group for group in row.get("target_groups", "").split(" | ") if group]
        for group in groups:
            group_totals[group] += 1
            for marker in AE_PATTERNS:
                if row.get(marker) == "1":
                    marker_counts[group][marker] += 1

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["target_group", "ae_marker", "group_n", "ae_n", "pct_within_group"])
        for group, group_n in group_totals.most_common():
            if group_n < min_group_n:
                continue
            for marker in AE_PATTERNS:
                count = marker_counts[group][marker]
                pct = count / group_n * 100 if group_n else 0
                writer.writerow([group, marker, group_n, count, f"{pct:.2f}"])


def write_ae_heatmap_matrix(path: Path, rows: list[dict[str, str]], min_group_n: int = 100) -> None:
    group_totals: Counter[str] = Counter()
    marker_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        groups = [group for group in row.get("target_groups", "").split(" | ") if group]
        for group in groups:
            group_totals[group] += 1
            for marker in AE_PATTERNS:
                if row.get(marker) == "1":
                    marker_counts[group][marker] += 1

    groups = [group for group, count in group_totals.most_common() if count >= min_group_n]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["target_group", *AE_PATTERNS])
        for group in groups:
            row = [group]
            for marker in AE_PATTERNS:
                pct = marker_counts[group][marker] / group_totals[group] * 100
                row.append(f"{pct:.2f}")
            writer.writerow(row)


def write_ae_heatmap_png(matrix_path: Path, image_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
        import seaborn as sns
    except ImportError:
        return

    matrix = pd.read_csv(matrix_path).set_index("target_group")
    if matrix.empty:
        return

    image_path.parent.mkdir(parents=True, exist_ok=True)
    height = max(6, 0.45 * len(matrix))
    width = max(9, 0.7 * len(matrix.columns))
    plt.figure(figsize=(width, height))
    sns.heatmap(matrix, cmap="viridis", vmin=0, vmax=100, linewidths=0.3, linecolor="white", cbar_kws={"label": "% reports"})
    plt.title("AE-like marker prevalence by targeted substance group")
    plt.xlabel("AE-like marker")
    plt.ylabel("Targeted substance group")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(image_path, dpi=200)
    plt.close()


def write_ae_outputs(
    coding_corpus_path: Path,
    report_codes_path: Path,
    ae_rows_path: Path,
    output_dir: Path,
) -> list[dict[str, str]]:
    rows = extract_ae_rows(coding_corpus_path, report_codes_path)
    write_ae_rows(ae_rows_path, rows)
    write_ae_prevalence(output_dir / "ae_marker_prevalence.csv", rows)
    write_ae_by_target_group(output_dir / "ae_marker_by_target_group.csv", rows)
    matrix_path = output_dir / "ae_marker_heatmap_matrix.csv"
    write_ae_heatmap_matrix(matrix_path, rows)
    write_ae_heatmap_png(matrix_path, output_dir.parent / "figures" / "ae_marker_heatmap.png")
    return rows
