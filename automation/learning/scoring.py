"""Deterministic repository scoring and untrusted-content risk flagging."""

from __future__ import annotations

import re
from typing import Mapping

STABLE_WEIGHTS = {
    "technical_quality": 20,
    "maintenance_health": 15,
    "tests_ci": 15,
    "documentation_quality": 10,
    "security_practices": 10,
    "community_health": 10,
    "production_adoption": 10,
    "transferability": 5,
    "license_clarity": 5,
}

EMERGING_WEIGHTS = {
    "recent_growth_signal": 20,
    "recent_development_activity": 20,
    "technical_innovation_value": 15,
    "code_architecture_quality": 15,
    "tests_ci": 10,
    "maintainer_responsiveness": 10,
    "transferability": 5,
    "license_clarity": 5,
}

_PROMPT_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.I),
    re.compile(r"disregard\s+(?:all\s+)?(?:prior|previous)\s+instructions", re.I),
    re.compile(r"system\s+prompt", re.I),
)
_SHELL_PIPE_PATTERN = re.compile(r"(?:curl|wget)\b[^\n|]{0,500}\|\s*(?:sh|bash|zsh)\b", re.I)


def _normalized_score(signals: Mapping[str, float | int | None], weights: Mapping[str, int]) -> dict:
    missing: list[str] = []
    factors: dict[str, float | None] = {}
    weighted_sum = 0.0
    available_weight = 0

    for name, weight in weights.items():
        raw = signals.get(name)
        if raw is None:
            factors[name] = None
            missing.append(name)
            continue
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError(f"{name} must be numeric, None, or absent")
        value = float(raw)
        if not 0 <= value <= 100:
            raise ValueError(f"{name} must be between 0 and 100")
        factors[name] = value
        weighted_sum += value * weight
        available_weight += weight

    score = 0.0 if available_weight == 0 else round(weighted_sum / available_weight, 2)
    return {
        "score": score,
        "band": value_band(score),
        "factors": factors,
        "missing_signals": missing,
        "available_weight": available_weight,
    }


def score_stable(signals: Mapping[str, float | int | None]) -> dict:
    """Score a mature reference candidate; popularity metadata is intentionally ignored."""
    return _normalized_score(signals, STABLE_WEIGHTS)


def score_emerging(signals: Mapping[str, float | int | None]) -> dict:
    """Score an emerging candidate, transparently re-normalizing unavailable signals."""
    return _normalized_score(signals, EMERGING_WEIGHTS)


def value_band(score: float) -> str:
    if score >= 90:
        return "HIGH-VALUE"
    if score >= 80:
        return "STRONG"
    if score >= 70:
        return "USEFUL"
    if score >= 60:
        return "EXPLORATORY"
    return "SKIP"


def detect_risk_flags(repository_text: str, metadata: Mapping | None = None) -> list[str]:
    """Flag suspicious repository content without interpreting it as instructions."""
    text = repository_text or ""
    flags: list[str] = []
    if any(pattern.search(text) for pattern in _PROMPT_INJECTION_PATTERNS):
        flags.append("PROMPT_INJECTION_LANGUAGE")
    if _SHELL_PIPE_PATTERN.search(text):
        flags.append("SHELL_PIPE_INSTALL")
    metadata = metadata or {}
    if metadata.get("archived"):
        flags.append("ARCHIVED_REPOSITORY")
    if metadata.get("fork") and metadata.get("mirror_only"):
        flags.append("MIRROR_ONLY")
    if flags:
        flags.append("UNTRUSTED_REPOSITORY_CONTENT")
    return flags
