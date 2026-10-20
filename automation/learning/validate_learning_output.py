"""Guard ordinary learning output so only approved durable paths can change."""

from __future__ import annotations

import argparse
import sys
from pathlib import PurePosixPath

from automation.learning.contracts import ORDINARY_AUTO_WRITE_ROOTS


def _normalize_candidate(path: str) -> tuple[str | None, str | None]:
    raw = path.strip()
    if not raw:
        return None, None
    normalized = raw.replace("\\", "/")
    if normalized.startswith("/"):
        return None, "absolute paths are not allowed"
    parts = PurePosixPath(normalized).parts
    if ".." in parts or "." in parts:
        return None, "path traversal is not allowed"
    canonical = "/".join(parts)
    if not canonical:
        return None, "empty path is not allowed"
    return canonical, None


def validate_changed_paths(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for original in paths:
        canonical, problem = _normalize_candidate(original)
        if canonical is None:
            if original.strip():
                errors.append(f"{original}: {problem}")
            continue
        if not any(canonical.startswith(root) for root in ORDINARY_AUTO_WRITE_ROOTS):
            errors.append(f"{original}: ordinary learning may write only knowledge/** or evolution/**")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--changed-files", help="Optional newline-delimited changed-file list. Reads stdin when omitted.")
    args = parser.parse_args()
    if args.changed_files:
        with open(args.changed_files, encoding="utf-8") as handle:
            paths = handle.read().splitlines()
    else:
        paths = sys.stdin.read().splitlines()
    errors = validate_changed_paths(paths)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("learning output paths valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
