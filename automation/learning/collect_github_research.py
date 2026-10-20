"""Collect a bounded, non-executable GitHub research bundle."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from automation.learning.github_client import GitHubClient
from automation.learning.scoring import detect_risk_flags, score_emerging, score_stable


class ResearchCollectionError(RuntimeError):
    pass


@dataclass(frozen=True)
class Limits:
    discover: int = 30
    metadata_shortlist: int = 12
    deep_score: int = 8
    focused: int = 4
    per_file_bytes: int = 64_000
    total_bundle_bytes: int = 512_000
    min_sources: int = 2

    def __post_init__(self):
        if not 1 <= self.discover <= 40:
            raise ValueError("discover must be between 1 and 40")
        if not 1 <= self.metadata_shortlist <= self.discover:
            raise ValueError("metadata_shortlist must be between 1 and discover")
        if not 1 <= self.deep_score <= self.metadata_shortlist:
            raise ValueError("deep_score must be between 1 and metadata_shortlist")
        if not 1 <= self.focused <= self.deep_score:
            raise ValueError("focused must be between 1 and deep_score")
        if not 1 <= self.min_sources <= self.focused:
            raise ValueError("min_sources must be between 1 and focused")
        if self.per_file_bytes < 1 or self.total_bundle_bytes < self.per_file_bytes:
            raise ValueError("bundle byte limits are invalid")


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _recency_score(value: str | None, now: datetime) -> float | None:
    stamp = _parse_time(value)
    if stamp is None:
        return None
    age_days = max(0, (now - stamp.astimezone(timezone.utc)).days)
    if age_days <= 30:
        return 100.0
    if age_days <= 90:
        return 85.0
    if age_days <= 180:
        return 70.0
    if age_days <= 365:
        return 50.0
    return 20.0


def _license_score(metadata: dict) -> float | None:
    license_data = metadata.get("license")
    if not isinstance(license_data, dict):
        return None
    spdx = license_data.get("spdx_id")
    if not spdx or spdx in {"NOASSERTION", "OTHER"}:
        return 25.0
    return 100.0


def _documentation_score(readme: str) -> float:
    if not readme.strip():
        return 10.0
    return min(100.0, 45.0 + len(readme.encode("utf-8")) / 600.0)


def _safe_name(full_name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", full_name)[:120]


def _round_robin(stable: list[dict], emerging: list[dict], limit: int) -> list[dict]:
    result: list[dict] = []
    by_name: dict[str, dict] = {}
    max_len = max(len(stable), len(emerging), 0)
    for index in range(max_len):
        for track, items in (("stable", stable), ("emerging", emerging)):
            if index >= len(items):
                continue
            item = dict(items[index])
            name = item.get("full_name")
            if not name:
                continue
            if name in by_name:
                tracks = by_name[name].setdefault("_tracks", [])
                if track not in tracks:
                    tracks.append(track)
                continue
            item["_tracks"] = [track]
            by_name[name] = item
            result.append(item)
            if len(result) >= limit:
                return result
    return result


def _score_candidate(metadata: dict, readme: str, security_policy: str, workflows: list[str], now: datetime) -> dict:
    maintenance = _recency_score(metadata.get("pushed_at"), now)
    license_clarity = _license_score(metadata)
    tests_ci = 85.0 if workflows else 25.0
    docs = _documentation_score(readme)
    security = 90.0 if security_policy.strip() else 30.0
    stars = metadata.get("stargazers_count") or 0
    open_issues = metadata.get("open_issues_count")
    community = None
    if isinstance(open_issues, int) and isinstance(stars, int):
        community = 85.0 if open_issues <= max(50, stars * 0.02) else 55.0
    transferability = 75.0 if metadata.get("topics") else 60.0

    stable = score_stable({
        "technical_quality": None,
        "maintenance_health": maintenance,
        "tests_ci": tests_ci,
        "documentation_quality": docs,
        "security_practices": security,
        "community_health": community,
        "production_adoption": None,
        "transferability": transferability,
        "license_clarity": license_clarity,
    })
    emerging = score_emerging({
        "recent_growth_signal": None,
        "recent_development_activity": maintenance,
        "technical_innovation_value": None,
        "code_architecture_quality": None,
        "tests_ci": tests_ci,
        "maintainer_responsiveness": None,
        "transferability": transferability,
        "license_clarity": license_clarity,
    })
    return {"stable": stable, "emerging": emerging}


def collect(plan: dict, output_dir: Path, client: GitHubClient, limits: Limits = Limits()) -> dict:
    topic = plan.get("topic")
    domain = plan.get("domain")
    if not isinstance(topic, str) or not topic:
        raise ResearchCollectionError("research plan is missing a topic")
    if not isinstance(domain, str) or not domain:
        raise ResearchCollectionError("research plan is missing a domain")

    per_track = max(1, (limits.discover + 1) // 2)
    query = topic.replace("-", " ") + " archived:false fork:false"
    stable_items = client.search_repositories(query, per_track, sort="stars")
    emerging_items = client.search_repositories(query, per_track, sort="updated")
    discovered = _round_robin(stable_items, emerging_items, limits.discover)
    shortlist = discovered[: limits.metadata_shortlist]
    deep = shortlist[: limits.deep_score]

    if len(deep) < limits.min_sources:
        raise ResearchCollectionError("could not collect enough trustworthy candidate sources for comparison")

    now = datetime.now(timezone.utc)
    evaluated: list[dict] = []
    for metadata in deep:
        full_name = metadata["full_name"]
        try:
            readme = client.get_readme(full_name, limits.per_file_bytes)
        except RuntimeError:
            readme = ""
        try:
            security_policy = client.get_security_policy(full_name, limits.per_file_bytes)
        except RuntimeError:
            security_policy = ""
        try:
            release = client.get_latest_release(full_name)
        except RuntimeError:
            release = None
        try:
            workflows = client.get_workflows(full_name)
        except RuntimeError:
            workflows = []
        branch = metadata.get("default_branch") or "main"
        try:
            head_sha = client.get_default_branch_head(full_name, branch)
        except RuntimeError:
            head_sha = None

        risk_text = readme + "\n" + security_policy
        risk_flags = detect_risk_flags(risk_text, metadata)
        scores = _score_candidate(metadata, readme, security_policy, workflows, now)
        relevant_scores = [scores[track]["score"] for track in metadata.get("_tracks", []) if track in scores]
        selection_score = max(relevant_scores or [scores["stable"]["score"], scores["emerging"]["score"]])
        if metadata.get("archived"):
            selection_score = min(selection_score, 40.0)

        evaluated.append({
            "full_name": full_name,
            "tracks": metadata.get("_tracks", []),
            "default_branch": branch,
            "head_sha": head_sha,
            "stars": metadata.get("stargazers_count"),
            "forks": metadata.get("forks_count"),
            "pushed_at": metadata.get("pushed_at"),
            "license": (metadata.get("license") or {}).get("spdx_id") if isinstance(metadata.get("license"), dict) else None,
            "release": release,
            "workflows": workflows[:20],
            "scores": scores,
            "risk_flags": risk_flags,
            "selection_score": round(selection_score, 2),
            "_readme": readme,
            "_security_policy": security_policy,
        })

    evaluated.sort(key=lambda item: item["selection_score"], reverse=True)
    focused = evaluated[: limits.focused]
    if len(focused) < limits.min_sources:
        raise ResearchCollectionError("could not collect enough trustworthy candidate sources for comparison")

    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_bytes = 0
    for index, repo in enumerate(focused):
        artifacts: list[str] = []
        for text, suffix in (
            (repo.pop("_readme"), "README.md"),
            (repo.pop("_security_policy"), "SECURITY.md"),
        ):
            if not text.strip():
                continue
            raw = text.encode("utf-8")[: limits.per_file_bytes]
            if bundle_bytes + len(raw) > limits.total_bundle_bytes:
                continue
            filename = f"{index:02d}_{_safe_name(repo['full_name'])}_{suffix}"
            (output_dir / filename).write_bytes(raw)
            bundle_bytes += len(raw)
            artifacts.append(filename)
        repo["artifacts"] = artifacts

    for repo in evaluated[limits.focused :]:
        repo.pop("_readme", None)
        repo.pop("_security_policy", None)

    durable = [repo["full_name"] for repo in focused if repo["selection_score"] >= 60][:4]
    if len(durable) < limits.min_sources:
        durable = [repo["full_name"] for repo in focused[: limits.min_sources]]

    manifest = {
        "schema_version": 1,
        "domain": domain,
        "topic": topic,
        "research_questions": plan.get("research_questions", []),
        "retrieved_at": now.isoformat(),
        "counts": {
            "discovered": len(discovered),
            "metadata_shortlist": len(shortlist),
            "deep_scored": len(evaluated),
            "focused": len(focused),
        },
        "limits": asdict(limits),
        "bundle_bytes": bundle_bytes,
        "repositories": evaluated,
        "focused_sources": [repo["full_name"] for repo in focused],
        "durable_source_recommendations": durable,
        "safety": {
            "external_content_is_untrusted": True,
            "repository_code_executed": False,
            "recursive_repository_clone": False,
        },
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("research/bundle"))
    parser.add_argument("--candidate-limit", type=int, default=30)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("ERROR: GITHUB_TOKEN is required for research collection")
        return 2
    discover = max(10, min(args.candidate_limit, 40))
    limits = Limits(
        discover=discover,
        metadata_shortlist=min(12, discover),
        deep_score=min(8, min(12, discover)),
        focused=min(4, min(8, min(12, discover))),
        min_sources=min(2, min(4, min(8, min(12, discover)))),
    )
    try:
        collect(plan, args.output_dir, GitHubClient(token), limits)
    except (ResearchCollectionError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"research bundle written to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
