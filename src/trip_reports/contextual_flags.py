from __future__ import annotations

import re

from trip_reports.serious_events import normalize_space


FEAR_OR_BELIEF_PATTERNS = [
    r"\bthought\b",
    r"\bthink\b",
    r"\bbeliev(ed|e)?\b",
    r"\bfelt like\b",
    r"\bseemed like\b",
    r"\bafraid\b",
    r"\bscared\b",
    r"\bfear(ed)?\b",
    r"\bparanoi",
    r"\bwas convinced\b",
    r"\bconvinced .* would\b",
    r"\bimagined\b",
    r"\bhallucinat",
    r"\bdelusion",
]

HYPOTHETICAL_PATTERNS = [
    r"\bwould\b",
    r"\bcould\b",
    r"\bmight\b",
    r"\bmay\b",
    r"\bif\b",
    r"\bwhat if\b",
    r"\balmost\b",
    r"\bnearly\b",
    r"\babout to\b",
    r"\bwanted to\b",
    r"\bwant(ed)? to\b",
    r"\btempted to\b",
    r"\bthought about\b",
    r"\bconsider(ed|ing)?\b",
]

NEGATION_PATTERNS = [
    r"\bno\b",
    r"\bnot\b",
    r"\bnever\b",
    r"\bnone\b",
    r"\bwithout\b",
    r"\bdidn'?t\b",
    r"\bdid not\b",
    r"\bwasn'?t\b",
    r"\bwas not\b",
    r"\bweren'?t\b",
    r"\bwere not\b",
    r"\bcouldn'?t\b",
    r"\bcould not\b",
    r"\binstead of\b",
]

ANALOGY_PATTERNS = [
    r"\b[- ]?like\b",
    r"\bsimilar to\b",
    r"\breminiscent of\b",
    r"\bas if\b",
    r"\bkind of like\b",
    r"\bsort of like\b",
    r"\breminded me of\b",
]

PAST_HISTORY_PATTERNS = [
    r"\bused to\b",
    r"\bin the past\b",
    r"\bpreviously\b",
    r"\bprior\b",
    r"\byears? ago\b",
    r"\bwhen i was\b",
    r"\bhistory of\b",
    r"\bbefore this\b",
]

ACTUAL_EVENT_PATTERNS = [
    r"\barriv(ed|al)\b",
    r"\bshow(ed)? up\b",
    r"\bcame\b",
    r"\bcalled\b",
    r"\btook me\b",
    r"\btaken\b",
    r"\bwas taken\b",
    r"\bhandcuff(ed|s)?\b",
    r"\barrest(ed)?\b",
    r"\badmitted\b",
    r"\bhospitali[sz]ed\b",
    r"\bwent to (the )?(er|hospital|emergency room)\b",
    r"\bdrove me\b",
    r"\bcrash(ed)?\b",
    r"\bfell\b",
    r"\bjumped\b",
    r"\bcut myself\b",
    r"\btried to\b",
]

MARKER_FALSE_POSITIVE_PATTERNS = {
    "arrest_detention_custody": [
        r"\bcardiac arrest\b",
        r"\brespiratory arrest\b",
        r"\barrested development\b",
    ],
    "law_enforcement_contact": [
        r"\bpolice (my|his|her|their) thoughts\b",
        r"\bpolice myself\b",
    ],
    "charges_court_probation": [
        r"\bcharged (my|the|his|her) (phone|battery)\b",
        r"\belectrical charge\b",
        r"\bin charge of\b",
    ],
    "assault_violence_weapon": [
        r"\beyes? (were )?assaulted\b",
        r"\bassaulted by (colors|colours|visuals|sounds|music|light|lights)\b",
        r"\bvisual assault\b",
        r"\bassault on (my )?(senses|eyes|ears)\b",
    ],
    "violence_aggression_assault": [
        r"\beyes? (were )?assaulted\b",
        r"\bassaulted by (colors|colours|visuals|sounds|music|light|lights)\b",
        r"\bvisual assault\b",
        r"\bassault on (my )?(senses|eyes|ears)\b",
    ],
    "death_fatality_reported": [
        r"\bego death\b",
        r"\bdeath of (my )?ego\b",
        r"\bfelt dead\b",
        r"\bdead tired\b",
    ],
    "homicide_death_investigation": [
        r"\bkill(ed)? (my )?ego\b",
        r"\bkill(ed)? time\b",
        r"\bthought .* killed\b",
        r"\bafraid .* killed\b",
    ],
    "suicide_self_harm_forensic": [
        r"\bthought about killing myself\b",
        r"\bwanted to die\b",
    ],
    "suicidality_self_harm": [
        r"\bthought about killing myself\b",
        r"\bwanted to die\b",
    ],
    "property_damage_vandalism_arson": [
        r"\bbrain (was )?fried\b",
        r"\bfelt fried\b",
    ],
}

SUBSTANCE_ANALOGY_PATTERNS = [
    r"\bmdma[- ]?like\b",
    r"\bdmt[- ]?like\b",
    r"\blsd[- ]?like\b",
    r"\bacid[- ]?like\b",
    r"\bmushroom[- ]?like\b",
    r"\bsalvia[- ]?like\b",
    r"\bkind of like (mdma|dmt|lsd|acid|mushrooms|salvia)\b",
    r"\bsimilar to (mdma|dmt|lsd|acid|mushrooms|salvia)\b",
]

ACTOR_PATTERNS = {
    "self_subject": [
        r"\bi\b",
        r"\bme\b",
        r"\bmyself\b",
        r"\bwe\b",
        r"\bus\b",
    ],
    "friend_or_peer": [
        r"\bfriend\b",
        r"\bbrother\b",
        r"\bsister\b",
        r"\bgirlfriend\b",
        r"\bboyfriend\b",
        r"\broommate\b",
    ],
    "authority_or_rescue": [
        r"\bpolice\b",
        r"\bcop\b",
        r"\bambulance\b",
        r"\bparamedic\b",
        r"\bdoctor\b",
        r"\bnurse\b",
        r"\bsecurity\b",
        r"\bfirefighter\b",
    ],
    "third_party_unclear": [
        r"\bsomeone\b",
        r"\bpeople\b",
        r"\bperson\b",
        r"\bhe\b",
        r"\bshe\b",
        r"\bthey\b",
    ],
}


def has_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def local_window(snippet: str, matched_text: str, radius: int = 95) -> str:
    if not matched_text:
        return normalize_space(snippet[: radius * 2])
    lower = snippet.lower()
    match_lower = matched_text.lower()
    index = lower.find(match_lower)
    if index < 0:
        return normalize_space(snippet[: radius * 2])
    left = max(0, index - radius)
    right = min(len(snippet), index + len(matched_text) + radius)
    return normalize_space(snippet[left:right])


def guess_actor(text: str) -> str:
    hits = []
    for actor, patterns in ACTOR_PATTERNS.items():
        if has_any(text, patterns):
            hits.append(actor)
    return " | ".join(hits) if hits else "unclear"


def classify_context(row: dict[str, str]) -> dict[str, str]:
    snippet = row.get("evidence_snippet", "") or ""
    matched_text = row.get("matched_text", "") or ""
    window = local_window(snippet, matched_text)
    whole = normalize_space(snippet)
    marker = row.get("forensic_marker") or row.get("serious_event_marker") or ""

    feared_or_belief = has_any(window, FEAR_OR_BELIEF_PATTERNS)
    hypothetical = has_any(window, HYPOTHETICAL_PATTERNS)
    negated = has_any(window, NEGATION_PATTERNS)
    analogy = has_any(window, ANALOGY_PATTERNS)
    substance_analogy = has_any(window, SUBSTANCE_ANALOGY_PATTERNS)
    past_history = has_any(window, PAST_HISTORY_PATTERNS)
    actual_event = has_any(window, ACTUAL_EVENT_PATTERNS)
    marker_false_positive = has_any(window, MARKER_FALSE_POSITIVE_PATTERNS.get(marker, []))

    ambiguity_score = sum([feared_or_belief, hypothetical, negated, analogy, substance_analogy, past_history])
    actual_score = int(actual_event) + int(bool(re.search(r"\b(arrived|handcuff|arrest|hospital|ambulance)\b", window, re.I)))

    if marker_false_positive:
        guess = "likely_marker_specific_false_positive"
    elif substance_analogy and marker.endswith("_keywords"):
        guess = "substance_analogy_not_exposure"
    elif negated:
        guess = "likely_not_event_or_negated"
    elif feared_or_belief and not actual_event:
        guess = "fear_belief_not_confirmed"
    elif hypothetical and not actual_event:
        guess = "hypothetical_or_ideation"
    elif past_history and not actual_event:
        guess = "past_history_or_background"
    elif actual_score >= 1 and ambiguity_score <= 1:
        guess = "actual_event_candidate"
    elif actual_score >= 1:
        guess = "actual_but_context_ambiguous"
    else:
        guess = "needs_human_review"

    if guess == "actual_event_candidate":
        priority = "high"
    elif guess in {"actual_but_context_ambiguous", "needs_human_review"}:
        priority = "medium"
    else:
        priority = "low"

    return {
        "auto_context_guess": guess,
        "auto_review_priority": priority,
        "auto_actor_guess": guess_actor(window),
        "auto_is_feared_or_belief": str(int(feared_or_belief)),
        "auto_is_hypothetical": str(int(hypothetical)),
        "auto_is_negated": str(int(negated)),
        "auto_is_analogy": str(int(analogy)),
        "auto_is_substance_analogy": str(int(substance_analogy)),
        "auto_is_past_history": str(int(past_history)),
        "auto_is_marker_specific_false_positive": str(int(marker_false_positive)),
        "auto_has_actual_event_cue": str(int(actual_event)),
        "auto_local_window": window,
        "auto_snippet_length": str(len(whole)),
    }
