from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


SERIOUS_EVENT_PATTERNS: dict[str, list[str]] = {
    "defenestration_jump_fall_height": [
        r"\bjump(ed|ing)? (out of|from) (a|the|my)? ?window\b",
        r"\bjump(ed|ing)? (off|from) (a|the)? ?(balcony|roof|bridge|building)\b",
        r"\bfall(en|ing)? (out of|from) (a|the|my)? ?window\b",
        r"\bfell (out of|from) (a|the|my)? ?window\b",
        r"\bdefenestrat",
        r"\bjump(ed|ing)? .* balcony\b",
        r"\bfell .* balcony\b",
        r"\bjump(ed|ing)? .* rooftop\b",
        r"\bfell .* rooftop\b",
        r"\bjumped from a height\b",
    ],
    "traffic_driving_accident": [
        r"\bcar accident\b",
        r"\btraffic accident\b",
        r"\bcrash(ed)? (my|the|a)? ?(car|truck|bike|bicycle|motorcycle)\b",
        r"\bcar crash\b",
        r"\bdriving (while|whilst) (high|tripping|intoxicated|impaired)\b",
        r"\bdrove (while|whilst) (high|tripping|intoxicated|impaired)\b",
        r"\bdui\b",
        r"\bdwi\b",
        r"\bhit by (a|the)? ?car\b",
        r"\bran into traffic\b",
        r"\bwalked into traffic\b",
    ],
    "police_arrest_legal": [
        r"\bpolice\b",
        r"\bcops?\b",
        r"\bsheriff\b",
        r"\blaw enforcement\b",
        r"\barrest(ed)?\b",
        r"\bhandcuff",
        r"\bjail\b",
        r"\bprison\b",
        r"\bcourt\b",
        r"\bcharged with\b",
        r"\bcharges\b",
        r"\bprobation\b",
        r"\bcustoms\b",
        r"\bsecurity guard\b",
    ],
    "ambulance_paramedics_fire_rescue": [
        r"\bambulance\b",
        r"\bparamedic",
        r"\bemt\b",
        r"\bemts\b",
        r"\bfirst responder",
        r"\bfire ?fighters?\b",
        r"\bfire ?men\b",
        r"\bfire department\b",
        r"\brescue squad\b",
        r"\b911\b",
        r"\b999\b",
    ],
    "er_hospital_icu": [
        r"\bemergency room\b",
        r"\bER\b",
        r"\bhospital\b",
        r"\bICU\b",
        r"\bintubat",
        r"\bventilator\b",
        r"\bresuscitat",
        r"\bCPR\b",
        r"\bpoison control\b",
        r"\badmitted\b",
        r"\bpsychiatric ward\b",
        r"\bpsych ward\b",
    ],
    "suicidality_self_harm": [
        r"\bsuicid",
        r"\bkill myself\b",
        r"\bkill himself\b",
        r"\bkill herself\b",
        r"\bwanted to die\b",
        r"\bwant(ed)? to die\b",
        r"\btried to die\b",
        r"\bself[- ]harm\b",
        r"\bhurt myself\b",
        r"\bcut myself\b",
        r"\bslit (my|his|her)? ?wrists?\b",
        r"\boverdose(d)? on purpose\b",
    ],
    "psychosis_delirium_dangerous": [
        r"\bpsychosis\b",
        r"\bpsychotic\b",
        r"\bdeliri",
        r"\bdelusion",
        r"\bhallucinat(ed|ing)? people\b",
        r"\bvoices told\b",
        r"\bthought .* (police|cops|fbi|cia|government)",
        r"\bnot know (where|who) .* was\b",
        r"\bcompletely out of touch\b",
        r"\bnot in reality\b",
    ],
    "seizure_coma_unconscious": [
        r"\bseizure",
        r"\bconvulsion",
        r"\bcoma\b",
        r"\bcomatose\b",
        r"\bunconscious\b",
        r"\blost consciousness\b",
        r"\bpassed out\b",
        r"\bblack(ed)? out\b",
        r"\bstopped breathing\b",
    ],
    "serious_injury_trauma": [
        r"\bfracture",
        r"\bbroken (arm|leg|bone|nose|rib|wrist|ankle)\b",
        r"\bconcussion\b",
        r"\bstitches\b",
        r"\bsuture",
        r"\blaceration\b",
        r"\bsevere bleeding\b",
        r"\bblood everywhere\b",
        r"\bhead injury\b",
        r"\bburn(ed)?\b",
        r"\bsurgery\b",
    ],
    "violence_aggression_assault": [
        r"\bassault",
        r"\battack(ed|ing)? (someone|a person|my friend|my mother|my father|my girlfriend|my boyfriend)\b",
        r"\bwas attacked\b",
        r"\bfight(ing)? with\b",
        r"\bgot into a fight\b",
        r"\bpunched\b",
        r"\bkicked\b",
        r"\bstab(bed|bing)?\b",
        r"\bwith a knife\b",
        r"\bpulled a knife\b",
        r"\bwith a gun\b",
        r"\bpulled a gun\b",
        r"\bviolent\b",
        r"\brestrain(ed|t)?\b",
        r"\btackled\b",
    ],
    "dangerous_public_behavior": [
        r"\bnaked\b",
        r"\bnude\b",
        r"\brunning (around|through|down)\b",
        r"\brunning into (the )?street\b",
        r"\bwander(ed|ing)?\b",
        r"\blost in (the )?(woods|forest|city|street)\b",
        r"\bpublic place\b",
        r"\bclimb(ed|ing)? (a|the)? ?(tree|fence|building|roof)\b",
    ],
    "near_drowning_suffocation_exposure": [
        r"\bdrown",
        r"\bnear drowning\b",
        r"\bsuffocat",
        r"\bchok(ed|ing)\b",
        r"\bhypothermia\b",
        r"\bfrostbite\b",
        r"\bdehydrat",
        r"\bheat stroke\b",
    ],
    "death_fatality_reported": [
        r"\bdead on arrival\b",
        r"\bfatal\b",
        r"\bfatality\b",
        r"\bdeath certificate\b",
        r"\bpronounced dead\b",
        r"\b(friend|person|someone|he|she|they) died\b",
    ],
}


SEVERE_COMPOSITE_GROUPS = {
    "medical_rescue": ["ambulance_paramedics_fire_rescue", "er_hospital_icu"],
    "legal_police": ["police_arrest_legal"],
    "self_harm": ["suicidality_self_harm"],
    "accident_trauma": [
        "defenestration_jump_fall_height",
        "traffic_driving_accident",
        "serious_injury_trauma",
        "near_drowning_suffocation_exposure",
    ],
    "behavioral_danger": [
        "psychosis_delirium_dangerous",
        "violence_aggression_assault",
        "dangerous_public_behavior",
    ],
    "life_threatening_medical": ["seizure_coma_unconscious", "death_fatality_reported"],
}


HIGH_CONFIDENCE_SERIOUS_MARKERS = [
    "defenestration_jump_fall_height",
    "traffic_driving_accident",
    "police_arrest_legal",
    "ambulance_paramedics_fire_rescue",
    "er_hospital_icu",
    "suicidality_self_harm",
    "seizure_coma_unconscious",
    "serious_injury_trauma",
    "near_drowning_suffocation_exposure",
    "death_fatality_reported",
]


def compile_patterns(patterns: dict[str, list[str]]) -> dict[str, list[re.Pattern[str]]]:
    return {
        name: [re.compile(pattern, re.IGNORECASE) for pattern in marker_patterns]
        for name, marker_patterns in patterns.items()
    }


COMPILED_SERIOUS_EVENT_PATTERNS = compile_patterns(SERIOUS_EVENT_PATTERNS)


def iter_rows(path: Path):
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        yield from csv.DictReader(handle)


def narrative_portion(text: str) -> str:
    """Drop Erowid metadata/footer where category links create many false positives."""
    parts = re.split(r"\bExp Year:\s*\d{4}\b", text, maxsplit=1, flags=re.IGNORECASE)
    return parts[0]


def detect_serious_events(text: str) -> dict[str, bool]:
    text = narrative_portion(text)
    return {
        name: any(pattern.search(text) for pattern in patterns)
        for name, patterns in COMPILED_SERIOUS_EVENT_PATTERNS.items()
    }


def add_composites(markers: dict[str, bool]) -> dict[str, bool]:
    output = dict(markers)
    for composite, members in SEVERE_COMPOSITE_GROUPS.items():
        output[f"composite_{composite}"] = any(markers.get(member, False) for member in members)
    output["composite_any_serious_event"] = any(markers.values())
    output["composite_high_confidence_serious_event"] = any(
        markers.get(marker, False) for marker in HIGH_CONFIDENCE_SERIOUS_MARKERS
    )
    return output


def extract_serious_event_rows(coding_corpus_path: Path, report_codes_path: Path) -> list[dict[str, str]]:
    code_rows = {row["report_id"]: row for row in iter_rows(report_codes_path)}
    rows: list[dict[str, str]] = []
    for row in iter_rows(coding_corpus_path):
        report_id = row.get("report_id", "")
        code_row = code_rows.get(report_id, {})
        markers = add_composites(detect_serious_events(row.get("text", "") or ""))
        rows.append(
            {
                "report_id": report_id,
                "url": row.get("url", ""),
                "target_groups": code_row.get("target_groups", ""),
                **{name: str(int(value)) for name, value in markers.items()},
            }
        )
    return rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def marker_names(include_composites: bool = True) -> list[str]:
    names = list(SERIOUS_EVENT_PATTERNS)
    if include_composites:
        names.extend([f"composite_{name}" for name in SEVERE_COMPOSITE_GROUPS])
        names.append("composite_any_serious_event")
        names.append("composite_high_confidence_serious_event")
    return names


def write_prevalence(path: Path, rows: list[dict[str, str]]) -> None:
    counts: Counter[str] = Counter()
    for row in rows:
        for marker in marker_names():
            if row.get(marker) == "1":
                counts[marker] += 1

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["serious_event_marker", "n", "pct_reports"])
        for marker, count in counts.most_common():
            pct = count / len(rows) * 100 if rows else 0
            writer.writerow([marker, count, f"{pct:.2f}"])


def write_by_target_group(path: Path, rows: list[dict[str, str]], min_group_n: int = 100) -> None:
    group_totals: Counter[str] = Counter()
    marker_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        groups = [group for group in row.get("target_groups", "").split(" | ") if group]
        for group in groups:
            group_totals[group] += 1
            for marker in marker_names():
                if row.get(marker) == "1":
                    marker_counts[group][marker] += 1

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["target_group", "serious_event_marker", "group_n", "event_n", "pct_within_group"])
        for group, group_n in group_totals.most_common():
            if group_n < min_group_n:
                continue
            for marker in marker_names():
                count = marker_counts[group][marker]
                pct = count / group_n * 100 if group_n else 0
                writer.writerow([group, marker, group_n, count, f"{pct:.2f}"])


def write_keyword_inventory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["serious_event_marker", "pattern"])
        for marker, patterns in SERIOUS_EVENT_PATTERNS.items():
            for pattern in patterns:
                writer.writerow([marker, pattern])


def write_validation_index(path: Path, rows: list[dict[str, str]], max_per_marker: int = 50) -> None:
    """Write local report IDs/URLs for manual audit without copying report text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    emitted: Counter[str] = Counter()
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["serious_event_marker", "report_id", "url", "target_groups"])
        for marker in marker_names(include_composites=False):
            for row in rows:
                if emitted[marker] >= max_per_marker:
                    break
                if row.get(marker) == "1":
                    writer.writerow([marker, row.get("report_id", ""), row.get("url", ""), row.get("target_groups", "")])
                    emitted[marker] += 1


def write_serious_event_outputs(
    coding_corpus_path: Path,
    report_codes_path: Path,
    serious_rows_path: Path,
    validation_index_path: Path,
    output_dir: Path,
) -> list[dict[str, str]]:
    rows = extract_serious_event_rows(coding_corpus_path, report_codes_path)
    write_rows(serious_rows_path, rows)
    write_validation_index(validation_index_path, rows)
    write_prevalence(output_dir / "serious_event_prevalence.csv", rows)
    write_by_target_group(output_dir / "serious_event_by_target_group.csv", rows)
    write_keyword_inventory(output_dir / "serious_event_keyword_inventory.csv")
    return rows
