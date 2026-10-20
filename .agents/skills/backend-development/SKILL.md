---
name: backend-development
description: Use when implementing or modifying APIs, server-side business logic, authentication integration, authorization enforcement, background jobs, caching, rate limiting, or external services.
---

# Backend Development

## Core Principle

Trace the real request path before changing behavior. Important business rules and security decisions belong on trusted server-side boundaries.

## Request Path

When relevant, reason through:

`request → validation → authentication → authorization → business logic → data access → response`

Inspect the actual route, middleware, service, repository/data layer, and external integrations involved instead of assuming how the system is structured.

## Working Rules

- Validate untrusted input at the appropriate server boundary.
- Enforce resource ownership, role, tenant, or permission checks where the operation requires them.
- Preserve existing API contracts unless the task explicitly changes them.
- Keep business rules out of transport-only code when the project has an established service/domain layer.
- Protect sensitive data in responses, logs, exceptions, and traces.
- Handle timeouts, retries, duplicate requests, idempotency, partial failures, and external-service errors when the operation is exposed to them.
- Use transactions when several state changes must succeed or fail together.
- Prefer existing project infrastructure before introducing new middleware, queues, caches, or libraries.
- Do not leak stack traces, credentials, internal topology, or unnecessary personal data to clients.

## Protected Operations

For authenticated endpoints, test both successful and denied paths when practical. Authentication proves identity; it does not prove permission to access a specific object or action.

## Verification

Use the project’s available targeted tests, integration/API tests, authorization tests, type checks, or service build commands. Confirm both expected responses and important failure behavior.

## Boundaries

Use `database-engineering` when schema design, migrations, indexing, transaction semantics, concurrency, or query performance become substantial. Use `application-security` for dedicated security review or hardening. Combine with `systematic-debugging` for failures or regressions.

## Common Mistakes

- Adding an endpoint without checking object ownership.
- Treating successful authentication as authorization.
- Retrying non-idempotent operations blindly.
- Changing response contracts unintentionally.
- Logging request bodies or tokens without considering sensitivity.