"""Validate Muse's machine-readable research plan."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from automation.learning.contracts import ALLOWED_DOMAINS, CANDIDATE_TRACKS, SIGNAL_LEVELS

_TOPIC_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_research_plan(data: dict, expected_domain: str) -> list[str]:
    errors: list[str] = []
    domain = data.get("domain")
    if domain not in ALLOWED_DOMAINS:
        errors.append("domain must be an allowed domain")
    if domain != expected_domain:
        errors.append(f"domain must match expected domain {expected_domain!r}")

    topic = data.get("topic")
    if not isinstance(topic, str) or not _TOPIC_RE.fullmatch(topic):
        errors.append("topic must be a non-empty lowercase slug")

    score = data.get("priority_score")
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        errors.append("priority_score must be an integer from 0 to 100")

    reason = data.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        errors.append("reason must be a non-empty string")

    for field in ("knowledge_gap", "freshness_risk", "trend_signal"):
        if data.get(field) not in SIGNAL_LEVELS:
            errors.append(f"{field} must be one of {', '.join(SIGNAL_LEVELS)}")

    questions = data.get("research_questions")
    if (
        not isinstance(questions, list)
        or not 1 <= len(questions) <= 8
        or any(not isinstance(q, str) or not q.strip() for q in questions)
    ):
        errors.append("research_questions must contain 1 to 8 non-empty strings")

    tracks = data.get("candidate_tracks")
    if not isinstance(tracks, list) or any(track not in CANDIDATE_TRACKS for track in tracks):
        errors.append("candidate_tracks contains an unsupported value")
    else:
        required = set(CANDIDATE_TRACKS)
        if set(tracks) != required:
            niche_reason = data.get("niche_topic_exception")
            if not isinstance(niche_reason, str) or not niche_reason.strip():
                errors.append("candidate_tracks must include stable and emerging unless niche_topic_exception is documented")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--expected-domain", required=True)
    args = parser.parse_args()
    data = json.loads(args.plan.read_text(encoding="utf-8"))
    errors = validate_research_plan(data, args.expected_domain)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("research plan valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
