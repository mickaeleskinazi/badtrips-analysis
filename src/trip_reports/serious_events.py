from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


SERIOUS_EVENT_PATTERNS: dict[str, list[str]] = {
    "defenestration_jump_fall_height": [
        r"\bjump(ed|ing)? (out of|from) (a|the|my)? ?window\b",
        r"\bjump(ed|ing)? (off|from|out of|over) (a|the|my)? ?(balcony|roof|bridge|building)\b",
        r"\bfall(en|ing)? (out of|from) (a|the|my)? ?window\b",
        r"\bfell (out of|from) (a|the|my)? ?window\b",
        r"\bfell (off|from|out of|over) (a|the|my)? ?(balcony|roof|bridge|building)\b",
        r"\bdefenestrat",
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
        r"\barrested\b",
        r"\barrested by\b",
        r"\barrested for\b",
        r"\bunder arrest\b",
        r"\bresist(ed|ing)? arrest\b",
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
        r"\bkicked (me|him|her|them|someone|a person|my friend|my mother|my father|my girlfriend|my boyfriend)\b",
        r"\bwas kicked\b",
        r"\bkicked in the\b",
        r"\bstabbed\b",
        r"\bstabbed (me|him|her|them|someone|a person|my friend)\b",
        r"\bstabbing (him|her|them|someone|a person|my friend)\b",
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
        r"\bfatal (overdose|reaction|accident|dose|intoxication|poisoning)\b",
        r"\bfatalit(y|ies)\b",
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
    text = re.sub(
        r"\[\s*erowid note:.*?\]",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(
        r"Hand-Crafted Glass Molecules!.*?\bCitation:\s*",
        "Citation: ",
        text,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    parts = re.split(r"\bExp Year:\s*\d{4}\b", text, maxsplit=1, flags=re.IGNORECASE)
    return parts[0]


def detect_serious_events(text: str) -> dict[str, bool]:
    text = narrative_portion(text)
    return {
        name: any(pattern.search(text) for pattern in patterns)
        for name, patterns in COMPILED_SERIOUS_EVENT_PATTERNS.items()
    }


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def snippet_around(text: str, start: int, end: int, radius: int = 180) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    prefix = "..." if left else ""
    suffix = "..." if right < len(text) else ""
    return prefix + normalize_space(text[left:right]) + suffix


def find_marker_evidence(text: str, marker: str, max_hits: int = 2) -> list[dict[str, str]]:
    text = narrative_portion(text)
    evidence: list[dict[str, str]] = []
    for pattern in COMPILED_SERIOUS_EVENT_PATTERNS[marker]:
        for match in pattern.finditer(text):
            evidence.append(
                {
                    "matched_text": normalize_space(match.group(0)),
                    "pattern": pattern.pattern,
                    "snippet": snippet_around(text, match.start(), match.end()),
                }
            )
            if len(evidence) >= max_hits:
                return evidence
    return evidence


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


def write_validation_queue(
    path: Path,
    rows: list[dict[str, str]],
    coding_corpus_path: Path,
    report_codes_path: Path,
    max_per_marker: int = 75,
    max_negative_controls: int = 200,
) -> None:
    """Write a local coder-facing validation queue with snippets, never versioned."""
    text_rows = {row["report_id"]: row for row in iter_rows(coding_corpus_path)}
    code_rows = {row["report_id"]: row for row in iter_rows(report_codes_path)}
    row_by_report = {row["report_id"]: row for row in rows}
    emitted: Counter[str] = Counter()

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "review_set",
            "serious_event_marker",
            "report_id",
            "url",
            "target_groups",
            "matched_text",
            "matched_pattern",
            "evidence_snippet",
            "validation_status",
            "event_role",
            "intentionality",
            "severity",
            "substance_contribution",
            "notes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for marker in marker_names(include_composites=False):
            for row in rows:
                if emitted[marker] >= max_per_marker:
                    break
                if row.get(marker) != "1":
                    continue
                report_id = row.get("report_id", "")
                text = text_rows.get(report_id, {}).get("text", "")
                evidence = find_marker_evidence(text, marker, max_hits=1)
                if not evidence:
                    continue
                hit = evidence[0]
                writer.writerow(
                    {
                        "review_set": "positive_screen",
                        "serious_event_marker": marker,
                        "report_id": report_id,
                        "url": row.get("url", ""),
                        "target_groups": row.get("target_groups", ""),
                        "matched_text": hit["matched_text"],
                        "matched_pattern": hit["pattern"],
                        "evidence_snippet": hit["snippet"],
                        "validation_status": "",
                        "event_role": "",
                        "intentionality": "",
                        "severity": "",
                        "substance_contribution": "",
                        "notes": "",
                    }
                )
                emitted[marker] += 1

        negative_candidates = []
        for report_id, text_row in text_rows.items():
            event_row = row_by_report.get(report_id, {})
            code_row = code_rows.get(report_id, {})
            if event_row.get("composite_high_confidence_serious_event") == "1":
                continue
            marker_score = sum(
                code_row.get(marker) == "1"
                for marker in [
                    "medical_intervention",
                    "fear_of_death",
                    "interoceptive_threat",
                    "loss_of_control",
                    "paranoia_social_threat",
                ]
            )
            if marker_score == 0:
                continue
            negative_candidates.append((marker_score, len(text_row.get("text", "")), report_id))

        negative_candidates.sort(reverse=True)
        for _, __, report_id in negative_candidates[:max_negative_controls]:
            text_row = text_rows[report_id]
            code_row = code_rows.get(report_id, {})
            writer.writerow(
                {
                    "review_set": "negative_control_high_risk",
                    "serious_event_marker": "none_screened",
                    "report_id": report_id,
                    "url": text_row.get("url", ""),
                    "target_groups": code_row.get("target_groups", ""),
                    "matched_text": "",
                    "matched_pattern": "",
                    "evidence_snippet": snippet_around(narrative_portion(text_row.get("text", "")), 0, 0, radius=260),
                    "validation_status": "",
                    "event_role": "",
                    "intentionality": "",
                    "severity": "",
                    "substance_contribution": "",
                    "notes": "",
                }
            )


def write_serious_event_outputs(
    coding_corpus_path: Path,
    report_codes_path: Path,
    serious_rows_path: Path,
    validation_index_path: Path,
    output_dir: Path,
    validation_queue_path: Path | None = None,
    max_validation_per_marker: int = 75,
) -> list[dict[str, str]]:
    rows = extract_serious_event_rows(coding_corpus_path, report_codes_path)
    write_rows(serious_rows_path, rows)
    write_validation_index(validation_index_path, rows)
    if validation_queue_path is not None:
        write_validation_queue(
            validation_queue_path,
            rows,
            coding_corpus_path,
            report_codes_path,
            max_per_marker=max_validation_per_marker,
        )
    write_prevalence(output_dir / "serious_event_prevalence.csv", rows)
    write_by_target_group(output_dir / "serious_event_by_target_group.csv", rows)
    write_keyword_inventory(output_dir / "serious_event_keyword_inventory.csv")
    return rows
