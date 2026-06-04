#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from trip_reports.contextual_flags import (  # noqa: E402
    ACTOR_PATTERNS,
    ACTUAL_EVENT_PATTERNS,
    ANALOGY_PATTERNS,
    FEAR_OR_BELIEF_PATTERNS,
    HYPOTHETICAL_PATTERNS,
    MARKER_FALSE_POSITIVE_PATTERNS,
    NEGATION_PATTERNS,
    PAST_HISTORY_PATTERNS,
    SUBSTANCE_ANALOGY_PATTERNS,
)
from trip_reports.forensic_legal import (  # noqa: E402
    FORENSIC_LEGAL_PATTERNS,
    PSYCHEDELIC_SUBSTANCE_PATTERNS,
)
from trip_reports.phenomenological_taxonomy import PHENOMENOLOGICAL_DOMAINS  # noqa: E402
from trip_reports.phenomenology import FAMILY_RULES, MARKER_PATTERNS, TARGET_GROUP_RULES  # noqa: E402
from trip_reports.serious_events import SERIOUS_EVENT_PATTERNS  # noqa: E402


def iter_inventory_rows():
    for marker, patterns in MARKER_PATTERNS.items():
        for pattern in patterns:
            yield ["phenomenology_current", marker, "", "", pattern]

    for marker, spec in PHENOMENOLOGICAL_DOMAINS.items():
        label = str(spec.get("label_fr", ""))
        definition = str(spec.get("definition", ""))
        for pattern in spec.get("patterns", []):
            yield ["phenomenology_extended", marker, label, definition, str(pattern)]

    for family, needles in FAMILY_RULES:
        for needle in needles:
            yield ["substance_family_rule", family, "", "", needle]

    for group, needles in TARGET_GROUP_RULES:
        for needle in needles:
            yield ["substance_target_group_rule", group, "", "", needle]

    for marker, patterns in SERIOUS_EVENT_PATTERNS.items():
        for pattern in patterns:
            yield ["serious_adverse_event", marker, "", "", pattern]

    for marker, patterns in FORENSIC_LEGAL_PATTERNS.items():
        for pattern in patterns:
            yield ["forensic_legal", marker, "", "", pattern]

    for marker, patterns in PSYCHEDELIC_SUBSTANCE_PATTERNS.items():
        for pattern in patterns:
            yield ["psychedelic_substance_mentions", marker, "", "", pattern]

    contextual_groups = {
        "fear_or_belief": FEAR_OR_BELIEF_PATTERNS,
        "hypothetical": HYPOTHETICAL_PATTERNS,
        "negation": NEGATION_PATTERNS,
        "analogy": ANALOGY_PATTERNS,
        "substance_analogy": SUBSTANCE_ANALOGY_PATTERNS,
        "past_history": PAST_HISTORY_PATTERNS,
        "actual_event_cue": ACTUAL_EVENT_PATTERNS,
    }
    for group, patterns in contextual_groups.items():
        for pattern in patterns:
            yield ["contextual_flag", group, "", "", pattern]

    for marker, patterns in MARKER_FALSE_POSITIVE_PATTERNS.items():
        for pattern in patterns:
            yield ["marker_specific_false_positive", marker, "", "", pattern]

    for actor, patterns in ACTOR_PATTERNS.items():
        for pattern in patterns:
            yield ["actor_guess", actor, "", "", pattern]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export all transparent keyword/rule inventories.")
    parser.add_argument(
        "--out",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "tables" / "keyword_inventory_all.csv",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    rows = list(iter_inventory_rows())
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["dictionary", "marker", "label_fr", "definition", "pattern_or_keyword"])
        writer.writerows(rows)
    print(f"Keyword/rule inventory rows: {len(rows)}")
    print(f"Inventory written to: {args.out}")


if __name__ == "__main__":
    main()
