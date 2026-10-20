---
name: systematic-debugging
description: Use when investigating failed tests, regressions, runtime errors, inconsistent output, integration failures, intermittent behavior, or unexplained system problems.
---

# Systematic Debugging

## Core Principle

Do not guess repeatedly. Gather enough evidence to identify the smallest plausible root cause, test that explanation, then make the smallest correct fix.

## Debugging Sequence

1. Understand or reproduce the symptom.
2. Trace the relevant execution path and recent changes.
3. Gather concrete evidence from code, logs, tests, requests, state, or data.
4. Separate the visible symptom from the likely cause.
5. Form the smallest plausible hypothesis that explains the evidence.
6. Test the hypothesis with the narrowest useful experiment.
7. Apply the smallest fix that addresses the root cause.
8. Re-run the original failing case and relevant regression checks.

If the failure cannot be reproduced, document what evidence is missing rather than pretending the cause is known.

## Working Rules

- Change one causal variable at a time when possible.
- Compare working and failing paths to reduce the search space.
- Read actual error output instead of relying on memory or summaries.
- Check boundaries between systems when each subsystem appears correct in isolation.
- Preserve diagnostics until the cause is understood, then remove temporary debug instrumentation before completion.
- Use timeouts, retries, and exception suppression only when they are part of the real fix, not to hide instability.

## Anti-Patterns

Avoid:

- Several speculative edits before re-running the failure.
- Broad rewrites before understanding the cause.
- Disabling tests, swallowing exceptions, or loosening validation simply to make output green.
- Treating correlation as causation.
- Declaring a bug fixed because the code looks reasonable.

## Verification

The original symptom must be rechecked after the fix. Run the smallest relevant regression set first, then broaden verification according to the risk and shared impact of the change.

## Combining Skills

This is a process skill and commonly combines with:

- `frontend-development` for browser/UI failures.
- `backend-development` for API/service failures.
- `application-security` for security defects.
- `database-engineering` for transaction, migration, locking, or query problems.

Use the domain skill for technical decisions and this skill for the investigation method.