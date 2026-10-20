"""Small GitHub REST client used only by the bounded research collector."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

_API_ROOT = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str, opener=urlopen, timeout: int = 20):
        self._token = token
        self._opener = opener
        self._timeout = timeout

    @staticmethod
    def _validate_url(url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "api.github.com":
            raise ValueError("GitHub client only permits https://api.github.com requests")

    def _open(self, url: str, *, accept: str = "application/vnd.github+json"):
        self._validate_url(url)
        headers = {
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "muse-autonomous-learning-runner/1",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        request = Request(url, headers=headers)
        try:
            return self._opener(request, timeout=self._timeout)
        except HTTPError as exc:
            raise RuntimeError(f"GitHub API request failed with HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("GitHub API request failed due to a network error") from exc

    def _request_json(self, url: str, *, max_bytes: int = 1_000_000):
        with self._open(url) as response:
            raw = response.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise RuntimeError("GitHub API response exceeded the configured byte limit")
        return json.loads(raw.decode("utf-8"))

    def _request_text(self, url: str, *, max_bytes: int):
        with self._open(url, accept="application/vnd.github.raw+json") as response:
            raw = response.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raw = raw[:max_bytes]
        try:
            return raw.decode("utf-8", errors="replace")
        except AttributeError:
            return str(raw)[:max_bytes]

    def search_repositories(self, query: str, per_page: int, sort: str | None = None) -> list[dict]:
        params = {"q": query, "per_page": max(1, min(int(per_page), 100)), "order": "desc"}
        if sort:
            params["sort"] = sort
        data = self._request_json(f"{_API_ROOT}/search/repositories?{urlencode(params)}")
        return list(data.get("items", []))

    def get_readme(self, full_name: str, max_bytes: int) -> str:
        return self._request_text(f"{_API_ROOT}/repos/{full_name}/readme", max_bytes=max_bytes)

    def get_security_policy(self, full_name: str, max_bytes: int) -> str:
        for path in (".github/SECURITY.md", "SECURITY.md", "docs/SECURITY.md"):
            url = f"{_API_ROOT}/repos/{full_name}/contents/{quote(path, safe='/')}"
            try:
                return self._request_text(url, max_bytes=max_bytes)
            except RuntimeError as exc:
                if "HTTP 404" not in str(exc):
                    raise
        return ""

    def get_latest_release(self, full_name: str) -> dict | None:
        try:
            return self._request_json(f"{_API_ROOT}/repos/{full_name}/releases/latest", max_bytes=250_000)
        except RuntimeError as exc:
            if "HTTP 404" in str(exc):
                return None
            raise

    def get_workflows(self, full_name: str) -> list[str]:
        try:
            data = self._request_json(f"{_API_ROOT}/repos/{full_name}/contents/.github/workflows", max_bytes=500_000)
        except RuntimeError as exc:
            if "HTTP 404" in str(exc):
                return []
            raise
        if not isinstance(data, list):
            return []
        return [item.get("name", "") for item in data if isinstance(item, dict) and item.get("type") == "file"]

    def get_default_branch_head(self, full_name: str, branch: str) -> str | None:
        data = self._request_json(f"{_API_ROOT}/repos/{full_name}/branches/{quote(branch, safe='')}", max_bytes=250_000)
        commit = data.get("commit") or {}
        return commit.get("sha")
