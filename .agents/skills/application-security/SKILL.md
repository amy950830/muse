---
name: application-security
description: Use when reviewing or changing authentication, authorization, sensitive-data handling, security hardening, vulnerability remediation, trust boundaries, or abuse-resistant application behavior.
---

# Application Security

## Core Principle

Security conclusions require evidence. Protect trust boundaries without overstating certainty or weakening usability and maintainability unnecessarily.

## Review Areas

Consider only the classes relevant to the system and task:

- Broken access control and IDOR
- Authentication, session, and token weaknesses
- SQL, command, template, and other injection paths
- XSS, CSRF, and SSRF
- Path traversal and unsafe file upload/processing
- Secret leakage and sensitive-data exposure
- Business-logic abuse and rate-limit bypass
- Race conditions with security impact
- Dependency and supply-chain risk
- Insecure configuration and excessive privilege

## Evidence Labels

Classify findings explicitly:

- **Confirmed vulnerability** — reproduced or otherwise directly demonstrated with sufficient evidence.
- **Strong code-level finding** — implementation evidence shows a credible flaw, but full exploitability has not been demonstrated.
- **Potential risk requiring verification** — plausible concern that still needs evidence.

Never upgrade a scanner warning, README claim, or theoretical concern into a confirmed vulnerability without supporting evidence.

## Working Rules

- Separate authentication from authorization.
- Check object ownership, tenant isolation, privilege level, and protected transitions where relevant.
- Keep secrets out of source, logs, examples, and client bundles.
- Prefer safe framework/database primitives over hand-built security mechanisms.
- Review both normal and adversarial failure paths.
- Keep testing inside systems and scope the user is authorized to assess.
- Do not run destructive or intrusive security tests without explicit authorization.
- For fixes, add regression coverage when practical so the vulnerability cannot silently return.

## Verification

Use appropriate code inspection, focused tests, dependency/configuration review, and authorized dynamic checks. Passing automated scanners or tests does not prove the application is secure; report what was and was not verified.

## Boundaries

Use `backend-development` for ordinary server implementation, `database-engineering` for substantial data-layer changes, and `systematic-debugging` when a security defect must be traced to root cause.

## Common Mistakes

- Equating login with permission.
- Treating absence of scanner findings as proof of security.
- Reporting an unverified concern as exploitable.
- Fixing symptoms while leaving the trust-boundary flaw intact.
- Copying hardening advice without checking the actual stack and threat model.