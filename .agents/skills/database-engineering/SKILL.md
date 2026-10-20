---
name: database-engineering
description: Use when designing or modifying schemas, migrations, indexes, transactions, constraints, query performance, concurrency behavior, retention, or database integrity.
---

# Database Engineering

## Core Principle

Protect data integrity first. Understand the current schema, query patterns, and deployed consumers before changing persistence behavior.

## Working Rules

- Inspect existing tables/collections, relationships, constraints, indexes, migrations, and affected queries before proposing changes.
- Consider compatibility with existing records and independently deployed services.
- Prefer backward-compatible migration sequences when practical.
- Use constraints to enforce durable invariants where the database is the right authority.
- Use transactions when multiple writes must succeed or fail together.
- Reason explicitly about concurrent updates, locking, isolation, retries, and idempotency when contention matters.
- Add or change indexes based on real query patterns, not guesswork.
- Review query plans or measured behavior when performance is the reason for a change and tooling is available.
- Keep rollback or recovery implications visible for consequential migrations.
- Do not redesign an entire data model for a small local change unless the existing structure makes the requested behavior unsafe or unmaintainable.

## Migration Safety

Before a consequential migration, determine:

- What happens to existing rows/documents?
- Can old and new application versions coexist during rollout?
- Is a backfill required, and can it be resumed safely?
- What is the failure/rollback strategy?
- Could locks, long transactions, or table rewrites affect production availability?

Never perform destructive production database operations without explicit authorization and appropriate recovery safeguards.

## Verification

Use available migration tests, integration tests, representative queries, constraint checks, and query-plan/performance tools as appropriate. Verify both schema state and application behavior; a migration that applies successfully can still break consumers.

## Boundaries

Use `backend-development` for ordinary data-access code and service behavior. Use `application-security` for tenant isolation or sensitive-data security concerns. Combine with `systematic-debugging` for data corruption, deadlocks, race conditions, or unexplained query behavior.

## Common Mistakes

- Writing a destructive migration before checking existing data.
- Adding indexes without understanding selectivity or write cost.
- Relying on application code for invariants that require durable database enforcement.
- Ignoring concurrent writers.
- Treating a successful migration command as proof the rollout is safe.