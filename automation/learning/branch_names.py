"""Deterministic, bounded Git branch names for autonomous learning output."""

from __future__ import annotations

import hashlib
import re

from automation.learning.contracts import ALLOWED_DOMAINS, SUPPORTED_SKILLS

_MAX_BRANCH_LEN = 180


def _slug(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    if not normalized:
        raise ValueError("topic must contain at least one alphanumeric character")
    return normalized


def _bounded(prefix: str, topic: str) -> str:
    topic_slug = _slug(topic)
    candidate = prefix + topic_slug
    if len(candidate) <= _MAX_BRANCH_LEN:
        return candidate
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()[:10]
    room = _MAX_BRANCH_LEN - len(prefix) - len(digest) - 1
    trimmed = topic_slug[:room].rstrip("-")
    return f"{prefix}{trimmed}-{digest}"


def learning_branch(domain: str, date: str, topic: str) -> str:
    if domain not in ALLOWED_DOMAINS:
        raise ValueError("unsupported learning domain")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError("date must use YYYY-MM-DD")
    return _bounded(f"learning/{domain}/{date}-", topic)


def skill_branch(skill_name: str, date: str, topic: str) -> str:
    if skill_name not in SUPPORTED_SKILLS:
        raise ValueError("unsupported Skill name")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError("date must use YYYY-MM-DD")
    return _bounded(f"evolution/{skill_name}/{date}-", topic)
