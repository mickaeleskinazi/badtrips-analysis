from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


FAMILY_RULES: list[tuple[str, list[str]]] = [
    (
        "classic_psychedelics",
        [
            "lsd",
            "mushroom",
            "psilocy",
            "dmt",
            "5meodmt",
            "5-meo",
            "ayahuasca",
            "huasca",
            "tryptamine",
            "dpt",
            "dipt",
            "mipt",
            "met",
            "det",
            "dalt",
            "4aco",
            "4-aco",
            "4ho",
            "4-ho",
            "allad",
            "ald52",
            "1p-lsd",
            "morning glory",
            "hb woodrose",
            "lsa",
            "mescaline",
            "peyote",
            "san pedro",
        ],
    ),
    (
        "phenethylamine_psychedelics",
        [
            "phenethylamine",
            "2c",
            "2ci",
            "2ce",
            "2cb",
            "2ct",
            "nbome",
            "25i",
            "25c",
            "25b",
            "dox",
            "dob",
            "doc",
            "doi",
            "amt",
            "dom",
        ],
    ),
    (
        "entactogens",
        ["mdma", "mda", "mdea", "bk-mdma", "methylone", "meph", "empathogen"],
    ),
    (
        "cannabis_cannabinoids",
        [
            "cannabis",
            "cannabinoid",
            "marijuana",
            "hash",
            "thc",
            "spice",
            "k2",
            "jwh",
            "smoking blends",
        ],
    ),
    (
        "stimulants",
        [
            "stimulant",
            "amphetamine",
            "methamphetamine",
            "cocaine",
            "caffeine",
            "methylphenidate",
            "ritalin",
            "adderall",
            "ephedra",
            "ephedrine",
            "cathinone",
            "bath salts",
            "mdpv",
            "modafinil",
            "piperazine",
        ],
    ),
    (
        "dissociatives",
        [
            "dissociative",
            "dxm",
            "ketamine",
            "pcp",
            "nitrous",
            "nmda",
            "arylcyclohexylamine",
            "methoxetamine",
            "mxe",
        ],
    ),
    (
        "deliriants",
        [
            "datura",
            "tropane",
            "diphenhydramine",
            "dimenhydrinate",
            "benadryl",
            "deliriant",
            "nutmeg",
            "belladonna",
            "brugmansia",
        ],
    ),
    (
        "depressants_sedatives",
        [
            "benzodiazepine",
            "alprazolam",
            "diazepam",
            "clonazepam",
            "zolpidem",
            "ambien",
            "ghb",
            "gbl",
            "butanediol",
            "phenibut",
            "barbiturate",
            "sedative",
        ],
    ),
    (
        "opioids",
        ["opioid", "opiate", "heroin", "morphine", "oxycodone", "hydrocodone", "fentanyl", "tramadol", "kratom"],
    ),
    (
        "alcohol",
        ["alcohol", "beer", "wine", "liquor"],
    ),
    (
        "pharmaceuticals",
        [
            "pharmaceutical",
            "pharms",
            "ssri",
            "snri",
            "maoi",
            "antidepressant",
            "antipsychotic",
            "lithium",
            "gabapentin",
            "pregabalin",
        ],
    ),
    (
        "salvia",
        ["salvia", "salvinorin"],
    ),
    (
        "inhalants",
        ["inhalant", "solvent", "butane", "gasoline", "ether"],
    ),
    (
        "tobacco_nicotine",
        ["tobacco", "nicotine", "cigarette"],
    ),
    (
        "plants_fungi_other",
        [
            "amanita",
            "muscaria",
            "kava",
            "yohimbe",
            "harmala",
            "syrian rue",
            "iboga",
            "anadenanthera",
            "sceletium",
            "voacanga",
            "heimia",
            "calamus",
        ],
    ),
    (
        "non_substance_context",
        ["dreams", "obe", "sleep deprivation", "endogenous", "unknown"],
    ),
]


TARGET_GROUP_RULES: list[tuple[str, list[str]]] = [
    (
        "psilocybin_mushrooms",
        ["mushroom", "psilocybin", "psilocin"],
    ),
    (
        "lsd_lysergamides",
        ["lsd", "1plsd", "1blsd", "allad", "ald52", "lysergamide"],
    ),
    (
        "dmt_ayahuasca_5meo",
        [
            "dmt",
            "5meodmt",
            "5-meo",
            "ayahuasca",
            "huasca",
            "pharmahuasca",
            "mimosa",
            "anadenanthera",
            "yopo",
        ],
    ),
    (
        "other_tryptamines",
        [
            "tryptamine",
            "dpt",
            "dipt",
            "mipt",
            "met",
            "det",
            "dalt",
            "4aco",
            "4-aco",
            "4ho",
            "4-ho",
        ],
    ),
    (
        "mescaline_cacti",
        ["mescaline", "peyote", "san pedro", "cacti", "pachanoi", "peruvianus"],
    ),
    (
        "phenethylamines_2c_nbome_dox",
        [
            "phenethylamine",
            "2c",
            "2ci",
            "2ce",
            "2cb",
            "2ct",
            "nbome",
            "25i",
            "25c",
            "25b",
            "dob",
            "doc",
            "doi",
            "dox",
        ],
    ),
    (
        "mdma_entactogens",
        ["mdma", "mda", "mdea", "mdai", "methylone", "6apb", "bk-mdma", "empathogen"],
    ),
    (
        "amphetamine_like_stimulants",
        [
            "amphetamine",
            "methamphetamine",
            "methylphenidate",
            "ritalin",
            "adderall",
            "cathinone",
            "mephedrone",
            "methylmethcathinone",
            "mdpv",
            "bath salts",
        ],
    ),
    (
        "cocaine_crack",
        ["cocaine", "crack"],
    ),
    (
        "cannabis_natural",
        ["cannabis", "marijuana", "hash", "high thc", "high cbd"],
    ),
    (
        "synthetic_cannabinoids",
        [
            "cannabinoid receptor agonist",
            "novel cannabinoid",
            "spice",
            "k2",
            "jwh",
            "am2201",
            "smoking blends",
        ],
    ),
    (
        "ketamine_pcp_arylcyclohexylamines",
        [
            "ketamine",
            "pcp",
            "arylcyclohexylamine",
            "methoxetamine",
            "mxe",
            "3meopcp",
            "deschloroketamine",
        ],
    ),
    (
        "dxm",
        ["dxm"],
    ),
    (
        "salvia",
        ["salvia", "salvinorin"],
    ),
    (
        "deliriants_anticholinergics",
        [
            "datura",
            "tropane",
            "diphenhydramine",
            "dimenhydrinate",
            "benadryl",
            "brugmansia",
            "belladonna",
            "nutmeg",
        ],
    ),
    (
        "benzodiazepines_zdrugs_sedatives",
        [
            "benzodiazepine",
            "alprazolam",
            "diazepam",
            "clonazepam",
            "lorazepam",
            "etizolam",
            "zolpidem",
            "ambien",
            "phenibut",
            "ghb",
            "gbl",
            "butanediol",
        ],
    ),
    (
        "opioids",
        ["opioid", "opiate", "heroin", "morphine", "oxycodone", "hydrocodone", "fentanyl", "tramadol", "kratom"],
    ),
    (
        "alcohol",
        ["alcohol", "beer", "wine", "liquor"],
    ),
]


MARKER_PATTERNS: dict[str, list[str]] = {
    "interoceptive_threat": [
        r"\bheart (attack|rate|beating|pounding|racing)\b",
        r"\bmy heart\b",
        r"\bpalpitation",
        r"\bchest pain\b",
        r"\bcould(n't| not) breathe\b",
        r"\bbreath(ing)?\b",
        r"\bvomit",
        r"\bnausea",
        r"\bshaking\b",
        r"\btrembl",
        r"\bsweat",
        r"\bhot and cold\b",
        r"\bseizure",
        r"\bconvulsion",
        r"\bbody was\b",
        r"\bpoison",
        r"\boverdose",
    ],
    "fear_of_death": [
        r"\bthought i (was|would be|might be)? ?dying\b",
        r"\bi (was|am|m) dying\b",
        r"\bgoing to die\b",
        r"\babout to die\b",
        r"\bafraid .* die\b",
        r"\bscared .* die\b",
        r"\bdeath\b",
        r"\bdead\b",
        r"\bnear[- ]death\b",
        r"\bthis is it\b",
        r"\bheart attack\b",
        r"\boverdose\b",
    ],
    "fear_of_madness": [
        r"\bgoing crazy\b",
        r"\bwent crazy\b",
        r"\bgo insane\b",
        r"\bwent insane\b",
        r"\blosing my mind\b",
        r"\blost my mind\b",
        r"\bpsychosis\b",
        r"\bpsychotic\b",
        r"\bschizophren",
        r"\bnever be sane\b",
    ],
    "loss_of_control": [
        r"\blost control\b",
        r"\blose control\b",
        r"\bout of control\b",
        r"\bcould(n't| not) control\b",
        r"\bno control\b",
        r"\btrapped\b",
        r"\bstuck\b",
        r"\bcould(n't| not) stop\b",
        r"\bloop\b",
        r"\bspiral",
    ],
    "derealization_depersonalization": [
        r"\breality\b",
        r"\bunreal\b",
        r"\bderealization\b",
        r"\bdepersonalization\b",
        r"\bnot real\b",
        r"\bdream\b",
        r"\bego death\b",
        r"\bego loss\b",
        r"\bdissolv",
        r"\bidentity\b",
        r"\bself\b",
    ],
    "paranoia_social_threat": [
        r"\bparanoi",
        r"\bpolice\b",
        r"\bcops\b",
        r"\beveryone was\b",
        r"\bpeople were\b",
        r"\bthey were watching\b",
        r"\bwatched\b",
        r"\bfollowing me\b",
        r"\bconspiracy\b",
        r"\bthreat",
    ],
    "time_distortion": [
        r"\btime stopped\b",
        r"\btime slowed\b",
        r"\btime was\b",
        r"\bforever\b",
        r"\beternity\b",
        r"\binfinite\b",
        r"\bnever end\b",
        r"\bnever-ending\b",
        r"\bstuck in time\b",
    ],
    "medical_intervention": [
        r"\bhospital\b",
        r"\bambulance\b",
        r"\bemergency room\b",
        r"\bparamedic",
        r"\bdoctor\b",
        r"\bnurse\b",
        r"\b911\b",
        r"\ber\b",
        r"\bpoison control\b",
    ],
    "social_support": [
        r"\bfriend helped\b",
        r"\bfriend(s)? calmed\b",
        r"\bmy friend\b",
        r"\bmy girlfriend\b",
        r"\bmy boyfriend\b",
        r"\bmy wife\b",
        r"\bmy husband\b",
        r"\bmy mother\b",
        r"\bmy father\b",
        r"\bcalled .* friend\b",
        r"\btalked me down\b",
        r"\btrip sitter\b",
        r"\bsitter\b",
    ],
    "acceptance_surrender": [
        r"\baccept",
        r"\bsurrender",
        r"\blet go\b",
        r"\bletting go\b",
        r"\bgive in\b",
        r"\bgave in\b",
        r"\bstop fighting\b",
        r"\bstopped fighting\b",
        r"\bembrace",
        r"\ballowed it\b",
    ],
    "integration_positive_afterwards": [
        r"\blearned\b",
        r"\blesson\b",
        r"\bmeaningful\b",
        r"\bpositive\b",
        r"\bgrateful\b",
        r"\bchanged my life\b",
        r"\btherapeutic\b",
        r"\bhealing\b",
        r"\bintegrat",
        r"\brespect for\b",
    ],
}


@dataclass(frozen=True)
class ReportCodes:
    report_id: str
    primary_family: str
    families: tuple[str, ...]
    target_groups: tuple[str, ...]
    markers: dict[str, bool]


def compile_patterns(patterns: dict[str, list[str]]) -> dict[str, list[re.Pattern[str]]]:
    return {
        name: [re.compile(pattern, re.IGNORECASE) for pattern in marker_patterns]
        for name, marker_patterns in patterns.items()
    }


COMPILED_MARKERS = compile_patterns(MARKER_PATTERNS)


def classify_families(substance_categories: str) -> tuple[str, ...]:
    text = substance_categories.lower()
    families: list[str] = []
    for family, needles in FAMILY_RULES:
        if any(needle in text for needle in needles):
            families.append(family)
    if not families:
        families.append("unclassified")
    return tuple(families)


def classify_target_groups(substance_categories: str) -> tuple[str, ...]:
    text = substance_categories.lower()
    groups: list[str] = []
    for group, needles in TARGET_GROUP_RULES:
        if any(needle in text for needle in needles):
            groups.append(group)
    if not groups:
        groups.append("other_or_unclassified")
    return tuple(groups)


def detect_markers(text: str) -> dict[str, bool]:
    return {
        name: any(pattern.search(text) for pattern in patterns)
        for name, patterns in COMPILED_MARKERS.items()
    }


def iter_coding_rows(path: Path) -> Iterable[dict[str, str]]:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        yield from csv.DictReader(handle)


def code_reports(path: Path) -> list[ReportCodes]:
    coded: list[ReportCodes] = []
    for row in iter_coding_rows(path):
        families = classify_families(row.get("substance_categories", ""))
        target_groups = classify_target_groups(row.get("substance_categories", ""))
        markers = detect_markers(row.get("text", "") or "")
        coded.append(
            ReportCodes(
                report_id=row.get("report_id", ""),
                primary_family=families[0],
                families=families,
                target_groups=target_groups,
                markers=markers,
            )
        )
    return coded


def write_report_codes(path: Path, coded: list[ReportCodes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    marker_names = list(MARKER_PATTERNS)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["report_id", "primary_family", "families", "target_groups", *marker_names])
        for report in coded:
            writer.writerow(
                [
                    report.report_id,
                    report.primary_family,
                    " | ".join(report.families),
                    " | ".join(report.target_groups),
                    *(int(report.markers[name]) for name in marker_names),
                ]
            )


def write_counter(path: Path, key_name: str, counter: Counter[str], denominator: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([key_name, "n", "pct_reports"])
        for key, count in counter.most_common():
            pct = count / denominator * 100 if denominator else 0
            writer.writerow([key, count, f"{pct:.2f}"])


def write_marker_prevalence(path: Path, coded: list[ReportCodes]) -> None:
    total = len(coded)
    counts = Counter()
    for report in coded:
        for marker, present in report.markers.items():
            if present:
                counts[marker] += 1
    write_counter(path, "marker", counts, total)


def write_family_counts(path: Path, coded: list[ReportCodes]) -> None:
    counts = Counter()
    for report in coded:
        for family in report.families:
            counts[family] += 1
    write_counter(path, "substance_family", counts, len(coded))


def write_target_group_counts(path: Path, coded: list[ReportCodes]) -> None:
    counts = Counter()
    for report in coded:
        for group in report.target_groups:
            counts[group] += 1
    write_counter(path, "target_group", counts, len(coded))


def write_marker_by_target_group(path: Path, coded: list[ReportCodes]) -> None:
    group_totals: Counter[str] = Counter()
    marker_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)

    for report in coded:
        for group in report.target_groups:
            group_totals[group] += 1
            for marker, present in report.markers.items():
                if present:
                    marker_counts[group][marker] += 1

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["target_group", "marker", "group_n", "marker_n", "pct_within_group"])
        for group, group_n in group_totals.most_common():
            for marker in MARKER_PATTERNS:
                marker_n = marker_counts[group][marker]
                pct = marker_n / group_n * 100 if group_n else 0
                writer.writerow([group, marker, group_n, marker_n, f"{pct:.2f}"])


def write_marker_by_family(path: Path, coded: list[ReportCodes]) -> None:
    family_totals: Counter[str] = Counter()
    marker_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)

    for report in coded:
        for family in report.families:
            family_totals[family] += 1
            for marker, present in report.markers.items():
                if present:
                    marker_counts[family][marker] += 1

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["substance_family", "marker", "family_n", "marker_n", "pct_within_family"])
        for family, family_n in family_totals.most_common():
            for marker in MARKER_PATTERNS:
                marker_n = marker_counts[family][marker]
                pct = marker_n / family_n * 100 if family_n else 0
                writer.writerow([family, marker, family_n, marker_n, f"{pct:.2f}"])


def write_marker_cooccurrence(path: Path, coded: list[ReportCodes]) -> None:
    marker_names = list(MARKER_PATTERNS)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["marker_a", "marker_b", "n", "pct_reports"])
        for index, marker_a in enumerate(marker_names):
            for marker_b in marker_names[index + 1 :]:
                count = sum(
                    1
                    for report in coded
                    if report.markers[marker_a] and report.markers[marker_b]
                )
                pct = count / len(coded) * 100 if coded else 0
                writer.writerow([marker_a, marker_b, count, f"{pct:.2f}"])


def write_analysis_outputs(coding_path: Path, report_codes_path: Path, output_dir: Path) -> list[ReportCodes]:
    coded = code_reports(coding_path)
    write_report_codes(report_codes_path, coded)
    write_family_counts(output_dir / "substance_family_counts.csv", coded)
    write_target_group_counts(output_dir / "target_group_counts.csv", coded)
    write_marker_prevalence(output_dir / "phenomenology_marker_prevalence.csv", coded)
    write_marker_by_family(output_dir / "phenomenology_marker_by_family.csv", coded)
    write_marker_by_target_group(output_dir / "phenomenology_marker_by_target_group.csv", coded)
    write_marker_cooccurrence(output_dir / "phenomenology_marker_cooccurrence.csv", coded)
    return coded
