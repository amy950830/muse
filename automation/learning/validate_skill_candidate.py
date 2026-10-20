"""Validate a temporary, review-only Skill replacement candidate."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import PurePosixPath, Path

from automation.learning.contracts import SUPPORTED_SKILLS

_FORBIDDEN_GOVERNANCE_PATTERNS = (
    re.compile(r"ignore\s+(?:the\s+)?(?:root\s+)?AGENTS\.md", re.I),
    re.compile(r"override\s+(?:the\s+)?IDENTITY\.md", re.I),
    re.compile(r"disable\s+approval", re.I),
    re.compile(r"(?:skip|bypass)\s+authorization", re.I),
    re.compile(r"(?:expose|print|log)\s+(?:all\s+)?secrets", re.I),
    re.compile(r"auto[- ]?merge", re.I),
    re.compile(r"no\s+human\s+review", re.I),
)


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return result
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return {}


def _valid_proposal_path(value) -> bool:
    if not isinstance(value, str) or not value:
        return False
    normalized = value.replace("\\", "/")
    if normalized.startswith("/"):
        return False
    parts = PurePosixPath(normalized).parts
    if ".." in parts or "." in parts:
        return False
    return bool(re.fullmatch(r"evolution/proposals/[a-z0-9][a-z0-9._-]*\.md", normalized))


def validate_skill_candidate(metadata: dict, candidate_text: str, current_text: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(metadata, dict):
        return ["candidate metadata must be a JSON object"]

    target_skill = metadata.get("target_skill")
    target_path = metadata.get("target_path")
    if target_skill not in SUPPORTED_SKILLS:
        errors.append("target_skill must name one existing supported Skill")
    expected_path = f".agents/skills/{target_skill}/SKILL.md" if target_skill in SUPPORTED_SKILLS else None
    if not isinstance(target_path, str) or target_path != expected_path:
        errors.append("target_path must be exactly one existing .agents/skills/<skill>/SKILL.md path")

    if metadata.get("review_only") is not True:
        errors.append("Skill candidates must be explicitly review_only")

    if target_skill == "continuous-learning" and metadata.get("governance_sensitive") is not True:
        errors.append("continuous-learning changes require explicit governance-sensitive review")

    if not _valid_proposal_path(metadata.get("proposal_path")):
        errors.append("proposal_path must point to evolution/proposals/*.md")

    evidence = metadata.get("evidence")
    if not isinstance(evidence, list) or not evidence or any(not isinstance(item, str) or not item.strip() for item in evidence):
        errors.append("evidence must contain at least one non-empty provenance reference")

    current = _frontmatter(current_text)
    candidate = _frontmatter(candidate_text)
    if not current:
        errors.append("current Skill text must contain valid frontmatter")
    if not candidate:
        errors.append("candidate Skill text must contain valid frontmatter")
    else:
        if candidate.get("name") != current.get("name") or candidate.get("name") != target_skill:
            errors.append("candidate frontmatter name must match the current and target Skill name")
        description = candidate.get("description", "")
        if not description.startswith("Use when"):
            errors.append("candidate description must begin with 'Use when'")

    if not isinstance(candidate_text, str) or not candidate_text.strip():
        errors.append("candidate Skill text must be non-empty")
    else:
        if any(pattern.search(candidate_text) for pattern in _FORBIDDEN_GOVERNANCE_PATTERNS):
            errors.append("candidate contains language that may weaken protected governance")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("current", type=Path)
    args = parser.parse_args()
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    errors = validate_skill_candidate(
        metadata,
        args.candidate.read_text(encoding="utf-8"),
        args.current.read_text(encoding="utf-8"),
    )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("skill candidate valid for review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
