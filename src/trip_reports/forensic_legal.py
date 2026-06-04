from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

from trip_reports.serious_events import (
    compile_patterns,
    iter_rows,
    narrative_portion,
    normalize_space,
    snippet_around,
)


PSYCHEDELIC_TARGET_GROUPS = {
    "psilocybin_mushrooms",
    "lsd_lysergamides",
    "dmt_ayahuasca_5meo",
    "other_tryptamines",
    "mescaline_cacti",
    "phenethylamines_2c_nbome_dox",
    "mdma_entactogens",
    "salvia",
}


PSYCHEDELIC_SUBSTANCE_PATTERNS: dict[str, list[str]] = {
    "lsd_lysergamides_keywords": [
        r"\blsd\b",
        r"\bacid\b",
        r"\bblotter(s)?\b",
        r"\btab(s)? of acid\b",
        r"\bgel tab(s)?\b",
        r"\b1p[- ]?lsd\b",
        r"\b1b[- ]?lsd\b",
        r"\bald[- ]?52\b",
        r"\bal[- ]?lad\b",
        r"\beth[- ]?lad\b",
        r"\blysergamide",
    ],
    "psilocybin_mushrooms_keywords": [
        r"\bpsilocybin\b",
        r"\bpsilocin\b",
        r"\bmagic mushroom(s)?\b",
        r"\bmushroom(s)?\b",
        r"\bshroom(s)?\b",
        r"\bliberty cap(s)?\b",
        r"\bcubensis\b",
        r"\bp\.? cubensis\b",
    ],
    "dmt_ayahuasca_5meo_keywords": [
        r"\bdmt\b",
        r"\b5[- ]?meo[- ]?dmt\b",
        r"\bbufotenin\b",
        r"\bbufo\b",
        r"\bayahuasca\b",
        r"\byage\b",
        r"\bpharmahuasca\b",
        r"\bchanga\b",
        r"\bmimosa hostilis\b",
        r"\bsyrian rue\b",
    ],
    "other_tryptamines_keywords": [
        r"\btryptamine(s)?\b",
        r"\b4[- ]?aco[- ]?dmt\b",
        r"\b4[- ]?ho[- ]?met\b",
        r"\b4[- ]?ho[- ]?mipt\b",
        r"\b4[- ]?aco[- ]?det\b",
        r"\b5[- ]?meo[- ]?mipt\b",
        r"\b5[- ]?meo[- ]?dipt\b",
        r"\bdpt\b",
        r"\bdipt\b",
        r"\bmipt\b",
    ],
    "mescaline_cacti_keywords": [
        r"\bmescaline\b",
        r"\bpeyote\b",
        r"\bsan pedro\b",
        r"\bperuvian torch\b",
        r"\btrichocereus\b",
        r"\bechinopsis\b",
    ],
    "phenethylamines_2c_nbome_dox_keywords": [
        r"\b2c[- ]?[a-z]{1,3}\b",
        r"\b2cb\b",
        r"\b2c-b\b",
        r"\b2ce\b",
        r"\b2c-e\b",
        r"\b2ci\b",
        r"\b2c-i\b",
        r"\b2ct7\b",
        r"\b2c-t-7\b",
        r"\bnbome\b",
        r"\b25[i,c,b][- ]?nbome\b",
        r"\b25i\b",
        r"\b25c\b",
        r"\b25b\b",
        r"\bdob\b",
        r"\bdoc\b",
        r"\bdoi\b",
        r"\bdom\b",
        r"\bdox\b",
    ],
    "mdma_entactogens_keywords": [
        r"\bmdma\b",
        r"\bmda\b",
        r"\bmdea\b",
        r"\becstasy\b",
        r"\bmolly\b",
        r"\bxtc\b",
        r"\bmethylone\b",
        r"\bbk[- ]?mdma\b",
        r"\b6[- ]?apb\b",
    ],
    "salvia_keywords": [
        r"\bsalvia\b",
        r"\bsalvinorin\b",
    ],
}


FORENSIC_LEGAL_PATTERNS: dict[str, list[str]] = {
    "law_enforcement_contact": [
        r"\bpolice\b",
        r"\bcops?\b",
        r"\bsheriff\b",
        r"\btrooper(s)?\b",
        r"\blaw enforcement\b",
        r"\bsecurity guard(s)?\b",
        r"\bcampus security\b",
        r"\bcalled 911\b",
        r"\b911 was called\b",
    ],
    "arrest_detention_custody": [
        r"\barrested\b",
        r"\barrested by\b",
        r"\barrested for\b",
        r"\bunder arrest\b",
        r"\barresting officer\b",
        r"\barrest warrant\b",
        r"\bresist(ed|ing)? arrest\b",
        r"\bhandcuff(ed|s|ing)?\b",
        r"\bcuffed\b",
        r"\bdetain(ed|ing)?\b",
        r"\bheld in custody\b",
        r"\btaken into custody\b",
        r"\bbooked\b",
        r"\bjail(ed)?\b",
        r"\bprison\b",
        r"\block(ed)? up\b",
        r"\b(jail|prison|holding|police) cell\b",
        r"\bcell block\b",
        r"\bspent .* night .* jail\b",
    ],
    "charges_court_probation": [
        r"\bcharged with\b",
        r"\bcharged for (possession|assault|dui|dwi|theft|burglary|robbery|trespass|vandalism|arson)\b",
        r"\bcharges? (filed|dropped|pending|against)\b",
        r"\bfacing charges?\b",
        r"\bpressed charges?\b",
        r"\bcriminal charge(s)?\b",
        r"\bconvict(ed|ion)?\b",
        r"\bcourt\b",
        r"\btrial\b",
        r"\bprobation\b",
        r"\bparole\b",
        r"\blawyer\b",
        r"\battorney\b",
        r"\bfelony\b",
        r"\bmisdemeanor\b",
        r"\bcriminal record\b",
    ],
    "drug_crime_possession_supply": [
        r"\bpossession\b",
        r"\bdrug possession\b",
        r"\bpossession of\b",
        r"\bintent to distribute\b",
        r"\btraffick(ing)?\b",
        r"\bdealing\b",
        r"\bdealer\b",
        r"\bsell(ing)? drugs\b",
        r"\bsold .* drugs\b",
        r"\bbuy(ing)? drugs\b",
        r"\bcontrolled substance\b",
        r"\bparaphernalia\b",
        r"\bcustoms\b",
    ],
    "assault_violence_weapon": [
        r"\bassault(ed|ing)?\b",
        r"\bdomestic violence\b",
        r"\battack(ed|ing)? (someone|him|her|them|my friend|a person)\b",
        r"\bwas attacked\b",
        r"\bfight(ing)? with\b",
        r"\bgot into a fight\b",
        r"\bpunched\b",
        r"\bkicked (me|him|her|them|someone|a person|my friend|my mother|my father|my girlfriend|my boyfriend)\b",
        r"\bwas kicked\b",
        r"\bkicked in the\b",
        r"\bstrangled\b",
        r"\bchoked (him|her|them|someone)\b",
        r"\bstabbed\b",
        r"\bstabbed (me|him|her|them|someone|a person|my friend)\b",
        r"\bstabbing (him|her|them|someone|a person|my friend)\b",
        r"\bknife\b",
        r"\bgun\b",
        r"\bweapon\b",
        r"\bthreaten(ed|ing)? to kill\b",
        r"\bviolent\b",
    ],
    "homicide_death_investigation": [
        r"\bhomicide\b",
        r"\bmurder(ed|ing)?\b",
        r"\bmanslaughter\b",
        r"\bkilled (someone|him|her|them|a person|my friend)\b",
        r"\bsomeone was killed\b",
        r"\bdead body\b",
        r"\bcoroner\b",
        r"\bautopsy\b",
        r"\bdeath investigation\b",
        r"\bvehicular homicide\b",
    ],
    "suicide_self_harm_forensic": [
        r"\bsuicid",
        r"\bkill myself\b",
        r"\bwanted to die\b",
        r"\bwant(ed)? to die\b",
        r"\btried to die\b",
        r"\bsuicide attempt\b",
        r"\bself[- ]harm\b",
        r"\bhurt myself\b",
        r"\bcut myself\b",
        r"\bslit (my|his|her)? ?wrists?\b",
        r"\boverdose(d)? on purpose\b",
    ],
    "sexual_assault_exploitation": [
        r"\bsexual assault\b",
        r"\brape(d)?\b",
        r"\bmolest(ed|ation)?\b",
        r"\bnon[- ]consensual\b",
        r"\bwithout consent\b",
        r"\bforced sex\b",
    ],
    "theft_burglary_robbery": [
        r"\btheft\b",
        r"\bstole\b",
        r"\bstolen\b",
        r"\bsteal(ing)?\b",
        r"\bshoplift(ed|ing)?\b",
        r"\brob(bed|bery|bing)?\b",
        r"\bburglary\b",
        r"\bbroke into\b",
        r"\bbreaking into\b",
        r"\bbreak[- ]in\b",
    ],
    "trespass_intrusion": [
        r"\btrespass(ed|ing)?\b",
        r"\bprivate property\b",
        r"\bentered .* house\b",
        r"\bentered .* apartment\b",
        r"\bwalked into .* house\b",
        r"\bbroke into .* house\b",
        r"\bbreaking and entering\b",
        r"\bhome invasion\b",
    ],
    "property_damage_vandalism_arson": [
        r"\bvandali[sz](ed|m|ing)?\b",
        r"\bproperty damage\b",
        r"\bdamaged .* property\b",
        r"\bbroke .* window\b",
        r"\bsmashed\b",
        r"\bset .* on fire\b",
        r"\barson\b",
        r"\bstarted .* fire\b",
        r"\bburned .* down\b",
    ],
    "public_order_disorderly_exposure": [
        r"\bdisorderly conduct\b",
        r"\bdisturbing the peace\b",
        r"\bpublic intoxication\b",
        r"\bpublic nudity\b",
        r"\bnaked in public\b",
        r"\bnude in public\b",
        r"\brunning naked\b",
        r"\bscreaming in (the )?street\b",
        r"\byelling in (the )?street\b",
        r"\bcaused a scene\b",
    ],
    "impaired_driving_traffic_endangerment": [
        r"\bdui\b",
        r"\bdwi\b",
        r"\bdriving (while|whilst) (high|tripping|intoxicated|impaired)\b",
        r"\bdrove (while|whilst) (high|tripping|intoxicated|impaired)\b",
        r"\bcar accident\b",
        r"\bcar crash\b",
        r"\bcrashed .* car\b",
        r"\bran into traffic\b",
        r"\bwalked into traffic\b",
        r"\balmost hit\b",
        r"\bnearly hit\b",
    ],
    "fleeing_resisting_pursuit": [
        r"\bran from (the )?police\b",
        r"\bfled (from )?(the )?police\b",
        r"\bpolice chase\b",
        r"\bchased by (the )?police\b",
        r"\bresist(ed|ing)? arrest\b",
        r"\bevading\b",
        r"\bescaped (from )?(the )?police\b",
    ],
    "endangerment_of_others": [
        r"\bput .* in danger\b",
        r"\bendanger(ed|ing)? (someone|others|my friend|people)\b",
        r"\balmost killed\b",
        r"\bnearly killed\b",
        r"\bcould have killed\b",
        r"\bhurt someone\b",
        r"\binjured someone\b",
        r"\bthrew (?!up\b).{0,80}\bat\b",
        r"\bpushed .* into\b",
    ],
    "involuntary_psychiatric_legal_hold": [
        r"\b5150\b",
        r"\binvoluntary commitment\b",
        r"\binvoluntarily committed\b",
        r"\bpsych hold\b",
        r"\bpsychiatric hold\b",
        r"\bsectioned\b",
        r"\bmental hospital\b",
        r"\bpsych ward\b",
    ],
    "search_rescue_missing_person": [
        r"\bsearch party\b",
        r"\bsearch and rescue\b",
        r"\bmissing person\b",
        r"\breported missing\b",
        r"\brescue(d)? by\b",
        r"\bfire department\b",
        r"\bfirefighter(s)?\b",
    ],
}


FORENSIC_COMPOSITE_GROUPS = {
    "justice_system": [
        "law_enforcement_contact",
        "arrest_detention_custody",
        "charges_court_probation",
        "drug_crime_possession_supply",
    ],
    "criminalized_behavior": [
        "drug_crime_possession_supply",
        "theft_burglary_robbery",
        "trespass_intrusion",
        "property_damage_vandalism_arson",
        "public_order_disorderly_exposure",
        "impaired_driving_traffic_endangerment",
        "fleeing_resisting_pursuit",
    ],
    "interpersonal_violence": [
        "assault_violence_weapon",
        "homicide_death_investigation",
        "sexual_assault_exploitation",
        "endangerment_of_others",
    ],
    "public_safety_endangerment": [
        "impaired_driving_traffic_endangerment",
        "endangerment_of_others",
        "search_rescue_missing_person",
        "public_order_disorderly_exposure",
    ],
    "forensic_psychiatry_interface": [
        "suicide_self_harm_forensic",
        "involuntary_psychiatric_legal_hold",
        "law_enforcement_contact",
        "arrest_detention_custody",
    ],
}


COMPILED_PSYCHEDELIC_SUBSTANCE_PATTERNS = compile_patterns(PSYCHEDELIC_SUBSTANCE_PATTERNS)
COMPILED_FORENSIC_LEGAL_PATTERNS = compile_patterns(FORENSIC_LEGAL_PATTERNS)


def split_groups(value: str) -> list[str]:
    return [group for group in value.split(" | ") if group]


def detect_pattern_groups(text: str, compiled_patterns: dict[str, list[re.Pattern[str]]]) -> dict[str, bool]:
    text = narrative_portion(text)
    return {
        name: any(pattern.search(text) for pattern in patterns)
        for name, patterns in compiled_patterns.items()
    }


def add_composites(markers: dict[str, bool]) -> dict[str, bool]:
    output = dict(markers)
    for composite, members in FORENSIC_COMPOSITE_GROUPS.items():
        output[f"composite_{composite}"] = any(markers.get(member, False) for member in members)
    output["composite_any_forensic_legal"] = any(markers.values())
    return output


def marker_names(include_composites: bool = True) -> list[str]:
    names = list(FORENSIC_LEGAL_PATTERNS)
    if include_composites:
        names.extend([f"composite_{name}" for name in FORENSIC_COMPOSITE_GROUPS])
        names.append("composite_any_forensic_legal")
    return names


def substance_marker_names() -> list[str]:
    return list(PSYCHEDELIC_SUBSTANCE_PATTERNS)


def find_evidence(
    text: str,
    marker: str,
    compiled_patterns: dict[str, list[re.Pattern[str]]],
    max_hits: int = 2,
) -> list[dict[str, str]]:
    text = narrative_portion(text)
    evidence: list[dict[str, str]] = []
    for pattern in compiled_patterns[marker]:
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


def extract_forensic_rows(coding_corpus_path: Path, report_codes_path: Path) -> list[dict[str, str]]:
    code_rows = {row["report_id"]: row for row in iter_rows(report_codes_path)}
    rows: list[dict[str, str]] = []
    for row in iter_rows(coding_corpus_path):
        report_id = row.get("report_id", "")
        code_row = code_rows.get(report_id, {})
        target_groups = split_groups(code_row.get("target_groups", ""))
        target_psychedelic_groups = sorted(set(target_groups) & PSYCHEDELIC_TARGET_GROUPS)
        substance_markers = detect_pattern_groups(row.get("text", "") or "", COMPILED_PSYCHEDELIC_SUBSTANCE_PATTERNS)
        forensic_markers = add_composites(
            detect_pattern_groups(row.get("text", "") or "", COMPILED_FORENSIC_LEGAL_PATTERNS)
        )
        psychedelic_keyword_markers = [name for name, value in substance_markers.items() if value]
        psychedelic_related = bool(target_psychedelic_groups or psychedelic_keyword_markers)
        rows.append(
            {
                "report_id": report_id,
                "url": row.get("url", ""),
                "primary_family": code_row.get("primary_family", ""),
                "target_groups": code_row.get("target_groups", ""),
                "psychedelic_target_groups": " | ".join(target_psychedelic_groups),
                "psychedelic_substance_markers": " | ".join(psychedelic_keyword_markers),
                "psychedelic_target_group_flag": str(int(bool(target_psychedelic_groups))),
                "psychedelic_keyword_flag": str(int(bool(psychedelic_keyword_markers))),
                "psychedelic_related": str(int(psychedelic_related)),
                **{name: str(int(value)) for name, value in substance_markers.items()},
                **{name: str(int(value)) for name, value in forensic_markers.items()},
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


def write_prevalence(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["population", "marker", "n", "denominator", "pct"])
        populations = {
            "all_reports": rows,
            "psychedelic_related": [row for row in rows if row.get("psychedelic_related") == "1"],
            "psychedelic_target_group_only": [
                row for row in rows if row.get("psychedelic_target_group_flag") == "1"
            ],
        }
        for population, population_rows in populations.items():
            denominator = len(population_rows)
            for marker in marker_names():
                count = sum(row.get(marker) == "1" for row in population_rows)
                pct = count / denominator * 100 if denominator else 0
                writer.writerow([population, marker, count, denominator, f"{pct:.2f}"])


def write_by_psychedelic_group(path: Path, rows: list[dict[str, str]], min_group_n: int = 20) -> None:
    totals: Counter[str] = Counter()
    marker_counts: defaultdict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        for group in split_groups(row.get("psychedelic_target_groups", "")):
            totals[group] += 1
            for marker in marker_names():
                if row.get(marker) == "1":
                    marker_counts[group][marker] += 1

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["psychedelic_target_group", "marker", "group_n", "event_n", "pct_within_group"])
        for group, group_n in totals.most_common():
            if group_n < min_group_n:
                continue
            for marker in marker_names():
                count = marker_counts[group][marker]
                pct = count / group_n * 100 if group_n else 0
                writer.writerow([group, marker, group_n, count, f"{pct:.2f}"])


def write_substance_marker_prevalence(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["substance_marker", "n", "pct_reports"])
        denominator = len(rows)
        for marker in substance_marker_names():
            count = sum(row.get(marker) == "1" for row in rows)
            pct = count / denominator * 100 if denominator else 0
            writer.writerow([marker, count, f"{pct:.2f}"])


def write_keyword_inventory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dictionary", "marker", "pattern"])
        for marker, patterns in PSYCHEDELIC_SUBSTANCE_PATTERNS.items():
            for pattern in patterns:
                writer.writerow(["psychedelic_substance", marker, pattern])
        for marker, patterns in FORENSIC_LEGAL_PATTERNS.items():
            for pattern in patterns:
                writer.writerow(["forensic_legal", marker, pattern])


def write_validation_queue(
    path: Path,
    rows: list[dict[str, str]],
    coding_corpus_path: Path,
    max_per_marker: int = 75,
) -> None:
    text_rows = {row["report_id"]: row for row in iter_rows(coding_corpus_path)}
    path.parent.mkdir(parents=True, exist_ok=True)
    emitted: Counter[str] = Counter()
    with path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "forensic_marker",
            "report_id",
            "url",
            "target_groups",
            "psychedelic_target_groups",
            "psychedelic_substance_markers",
            "matched_text",
            "matched_pattern",
            "evidence_snippet",
            "validation_status",
            "legal_event_confirmed",
            "event_type",
            "actor_role",
            "third_party_harm_or_risk",
            "legal_outcome",
            "substance_contribution",
            "notes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for marker in marker_names(include_composites=False):
            for row in rows:
                if emitted[marker] >= max_per_marker:
                    break
                if row.get("psychedelic_related") != "1" or row.get(marker) != "1":
                    continue
                report_id = row.get("report_id", "")
                evidence = find_evidence(
                    text_rows.get(report_id, {}).get("text", ""),
                    marker,
                    COMPILED_FORENSIC_LEGAL_PATTERNS,
                    max_hits=1,
                )
                if not evidence:
                    continue
                hit = evidence[0]
                writer.writerow(
                    {
                        "forensic_marker": marker,
                        "report_id": report_id,
                        "url": row.get("url", ""),
                        "target_groups": row.get("target_groups", ""),
                        "psychedelic_target_groups": row.get("psychedelic_target_groups", ""),
                        "psychedelic_substance_markers": row.get("psychedelic_substance_markers", ""),
                        "matched_text": hit["matched_text"],
                        "matched_pattern": hit["pattern"],
                        "evidence_snippet": hit["snippet"],
                        "validation_status": "",
                        "legal_event_confirmed": "",
                        "event_type": "",
                        "actor_role": "",
                        "third_party_harm_or_risk": "",
                        "legal_outcome": "",
                        "substance_contribution": "",
                        "notes": "",
                    }
                )
                emitted[marker] += 1


def write_forensic_outputs(
    coding_corpus_path: Path,
    report_codes_path: Path,
    forensic_rows_path: Path,
    validation_queue_path: Path,
    output_dir: Path,
    max_validation_per_marker: int = 75,
) -> list[dict[str, str]]:
    rows = extract_forensic_rows(coding_corpus_path, report_codes_path)
    write_rows(forensic_rows_path, rows)
    write_validation_queue(
        validation_queue_path,
        rows,
        coding_corpus_path,
        max_per_marker=max_validation_per_marker,
    )
    write_prevalence(output_dir / "forensic_legal_prevalence.csv", rows)
    write_by_psychedelic_group(output_dir / "forensic_legal_by_psychedelic_group.csv", rows)
    write_substance_marker_prevalence(output_dir / "forensic_psychedelic_keyword_prevalence.csv", rows)
    write_keyword_inventory(output_dir / "forensic_legal_keyword_inventory.csv")
    return rows
