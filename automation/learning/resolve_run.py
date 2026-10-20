"""Resolve a scheduled or manually dispatched learning run to one domain."""

from __future__ import annotations

import argparse

from automation.learning.contracts import ALLOWED_DOMAINS

SCHEDULE_TO_DOMAIN = {
    "0 3 * * 1": "frontend",
    "0 3 * * 3": "backend",
    "0 3 * * 5": "security",
}


def resolve_domain(event_name: str, schedule: str | None, manual_domain: str | None) -> str:
    if event_name == "schedule":
        try:
            return SCHEDULE_TO_DOMAIN[schedule or ""]
        except KeyError as exc:
            raise ValueError(f"unsupported schedule: {schedule!r}") from exc
    if event_name == "workflow_dispatch":
        if manual_domain not in ALLOWED_DOMAINS:
            raise ValueError(f"manual domain must be one of {', '.join(ALLOWED_DOMAINS)}")
        return manual_domain
    raise ValueError(f"unsupported event: {event_name!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--schedule")
    parser.add_argument("--manual-domain")
    args = parser.parse_args()
    try:
        print(resolve_domain(args.event_name, args.schedule, args.manual_domain))
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
