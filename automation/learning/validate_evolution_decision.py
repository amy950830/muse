"""Validate the governed L0-L3 evolution decision emitted by Muse."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from automation.learning.contracts import EVOLUTION_LEVELS, SUPPORTED_SKILLS

_UNVALIDATED_MARKERS = ("not yet", "unvalidated", "not validated", "not run", "pending")


def _nonempty_text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _behavior_was_validated(value: str) -> bool:
    lowered = value.strip().lower()
    return bool(lowered) and not any(marker in lowered for marker in _UNVALIDATED_MARKERS)


def validate_evolution_decision(data: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["decision must be a JSON object"]

    level = data.get("level")
    if level not in EVOLUTION_LEVELS:
        errors.append("level must be one of L0, L1, L2, L3")

    score = data.get("confidence_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 100:
        errors.append("confidence_score must be numeric from 0 to 100")

    if not _nonempty_text(data.get("reason")):
        errors.append("reason must be a non-empty string")

    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must contain provenance for at least one source")

    behavior_validation = data.get("behavior_validation")
    if not isinstance(behavior_validation, str):
        errors.append("behavior_validation must be a string")

    protected = data.get("protected_core_impact")
    if not isinstance(protected, bool):
        errors.append("protected_core_impact must be boolean")
    elif protected and level != "L3":
        errors.append("protected_core_impact requires L3 escalation")

    candidate = data.get("skill_candidate")

    if level == "L2":
        if not isinstance(score, bool) and isinstance(score, (int, float)) and score < 75:
            errors.append("L2 requires confidence_score >= 75")
        if not isinstance(behavior_validation, str) or not _behavior_was_validated(behavior_validation):
            errors.append("L2 requires completed behavior validation, not an unvalidated placeholder")
        if protected is not False:
            errors.append("L2 may not have protected-core impact")
        if not isinstance(candidate, dict):
            errors.append("L2 requires exactly one skill_candidate object")
        else:
            target = candidate.get("target_skill")
            if target not in SUPPORTED_SKILLS:
                errors.append("L2 skill_candidate target_skill must name one existing supported Skill")
            if not _nonempty_text(candidate.get("proposal_path")):
                errors.append("L2 skill_candidate requires proposal_path")

    if level == "L3":
        if data.get("status") != "HUMAN_REVIEW_REQUIRED":
            errors.append("L3 requires status HUMAN_REVIEW_REQUIRED")
        if candidate not in (None, False):
            errors.append("L3 may not include an auto-applicable skill_candidate")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("decision", type=Path)
    args = parser.parse_args()
    data = json.loads(args.decision.read_text(encoding="utf-8"))
    errors = validate_evolution_decision(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("evolution decision valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
