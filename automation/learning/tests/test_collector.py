import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError

from automation.learning.collect_github_research import Limits, ResearchCollectionError, collect
from automation.learning.github_client import GitHubClient


class FakeResponse:
    def __init__(self, payload, status=200, headers=None):
        self.payload = payload
        self.status = status
        self.headers = headers or {}

    def read(self, limit=-1):
        raw = json.dumps(self.payload).encode("utf-8") if not isinstance(self.payload, bytes) else self.payload
        return raw if limit == -1 else raw[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class GitHubClientTest(unittest.TestCase):
    def test_client_uses_only_api_github_com(self):
        seen = []

        def opener(request, timeout=0):
            seen.append(request.full_url)
            return FakeResponse({"items": []})

        client = GitHubClient("secret-token", opener=opener)
        client.search_repositories("frontend", 3)
        self.assertEqual(len(seen), 1)
        self.assertTrue(seen[0].startswith("https://api.github.com/"))
        with self.assertRaises(ValueError):
            client._request_json("https://evil.example/data")

    def test_http_error_is_sanitized(self):
        def opener(request, timeout=0):
            raise HTTPError(request.full_url, 403, "rate limit", {"X-RateLimit-Remaining": "0"}, None)

        client = GitHubClient("super-secret", opener=opener)
        with self.assertRaisesRegex(RuntimeError, "GitHub API request failed") as ctx:
            client.search_repositories("backend", 2)
        self.assertNotIn("super-secret", str(ctx.exception))


class FakeClient:
    def __init__(self, count=10, readme_size=100):
        self.count = count
        self.readme_size = readme_size
        self.calls = []

    def search_repositories(self, query, per_page, sort=None):
        self.calls.append(("search", query, per_page, sort))
        items = []
        for i in range(min(self.count, per_page)):
            items.append({
                "full_name": f"example/project-{sort or 'none'}-{i}",
                "default_branch": "main",
                "stargazers_count": 1000 - i,
                "forks_count": 50,
                "open_issues_count": 5,
                "archived": False,
                "fork": False,
                "license": {"spdx_id": "MIT"},
                "pushed_at": "2026-10-19T00:00:00Z",
                "topics": ["frontend"],
            })
        return items

    def get_readme(self, full_name, max_bytes):
        self.calls.append(("readme", full_name, max_bytes))
        return ("Useful engineering documentation. " + "x" * self.readme_size)[:max_bytes]

    def get_security_policy(self, full_name, max_bytes):
        self.calls.append(("security", full_name, max_bytes))
        return "# Security\nReport vulnerabilities responsibly."[:max_bytes]

    def get_latest_release(self, full_name):
        self.calls.append(("release", full_name))
        return {"tag_name": "v1.0.0", "published_at": "2026-10-01T00:00:00Z"}

    def get_workflows(self, full_name):
        self.calls.append(("workflows", full_name))
        return ["ci.yml"]

    def get_default_branch_head(self, full_name, branch):
        self.calls.append(("branch", full_name, branch))
        return "a" * 40


class CollectorTest(unittest.TestCase):
    def plan(self):
        return {
            "domain": "frontend",
            "topic": "resilient-ui-error-recovery",
            "research_questions": ["How do mature projects recover from UI failures?"],
            "candidate_tracks": ["stable", "emerging"],
        }

    def test_candidate_and_bundle_limits_are_enforced(self):
        client = FakeClient(count=50, readme_size=1000)
        limits = Limits(discover=10, metadata_shortlist=6, deep_score=4, focused=2, per_file_bytes=80, total_bundle_bytes=5000, min_sources=2)
        with tempfile.TemporaryDirectory() as tmp:
            manifest = collect(self.plan(), Path(tmp), client, limits)
            self.assertLessEqual(manifest["counts"]["discovered"], 10)
            self.assertLessEqual(manifest["counts"]["deep_scored"], 4)
            self.assertLessEqual(manifest["counts"]["focused"], 2)
            for path in Path(tmp).glob("*.md"):
                self.assertLessEqual(path.stat().st_size, 80)
            self.assertLessEqual(manifest["bundle_bytes"], 5000)
            self.assertTrue((Path(tmp) / "manifest.json").exists())

    def test_collector_never_requests_recursive_clone_or_tree(self):
        client = FakeClient(count=4)
        with tempfile.TemporaryDirectory() as tmp:
            collect(self.plan(), Path(tmp), client, Limits(discover=4, metadata_shortlist=4, deep_score=4, focused=2, min_sources=2))
        call_names = {call[0] for call in client.calls}
        self.assertNotIn("clone", call_names)
        self.assertNotIn("tree", call_names)
        self.assertNotIn("execute", call_names)

    def test_manifest_records_provenance_scores_and_missing_signals(self):
        client = FakeClient(count=4)
        with tempfile.TemporaryDirectory() as tmp:
            manifest = collect(self.plan(), Path(tmp), client, Limits(discover=4, metadata_shortlist=4, deep_score=4, focused=2, min_sources=2))
        self.assertGreaterEqual(len(manifest["repositories"]), 2)
        repo = manifest["repositories"][0]
        self.assertIn("full_name", repo)
        self.assertEqual(repo["head_sha"], "a" * 40)
        self.assertIn("license", repo)
        self.assertIn("scores", repo)
        self.assertIn("missing_signals", repo["scores"]["emerging"])
        self.assertIn("retrieved_at", manifest)

    def test_insufficient_sources_fail_clearly(self):
        client = FakeClient(count=0)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ResearchCollectionError, "enough trustworthy candidate sources"):
                collect(self.plan(), Path(tmp), client, Limits(discover=4, metadata_shortlist=4, deep_score=4, focused=2, min_sources=2))


if __name__ == "__main__":
    unittest.main()
