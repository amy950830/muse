"""Detect accidental persistence of the Muse API secret in generated artifacts."""

from __future__ import annotations

import argparse
import base64
import os
from pathlib import Path


def _secret_variants(secret: str) -> tuple[bytes, ...]:
    raw = secret.encode("utf-8")
    variants = {
        raw,
        base64.b64encode(raw),
        base64.urlsafe_b64encode(raw),
        raw.hex().encode("ascii"),
    }
    return tuple(value for value in variants if value)


def _iter_files(paths: list[Path]):
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            yield path
            continue
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and ".git" not in child.parts:
                    yield child


def find_secret_leaks(secret: str, paths: list[Path]) -> list[str]:
    if not secret:
        raise ValueError("secret must be non-empty")
    variants = _secret_variants(secret)
    leaks: list[str] = []
    for path in _iter_files(paths):
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if any(variant in data for variant in variants):
            leaks.append(str(path))
    return sorted(set(leaks))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--secret-env", required=True)
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()
    secret = os.environ.get(args.secret_env, "")
    if not secret:
        print(f"ERROR: required secret environment variable {args.secret_env} is missing")
        return 2
    leaks = find_secret_leaks(secret, [Path(value) for value in args.paths])
    if leaks:
        # Never print the secret itself, only the paths that contain a recognized representation.
        for path in leaks:
            print(f"ERROR: generated artifact contains protected secret material: {path}")
        return 1
    print("generated artifacts contain no recognized secret representation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
