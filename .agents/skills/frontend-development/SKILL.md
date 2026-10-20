---
name: frontend-development
description: Use when implementing or modifying browser-facing components, routing, state, forms, client-side data fetching, responsive interfaces, accessibility, or frontend performance.
---

# Frontend Development

## Core Principle

Understand the existing frontend before changing it. Preserve the project’s component, state, routing, styling, and data-fetching conventions unless the task requires a deliberate change.

## Working Rules

- Inspect the affected user flow, not only the visible component.
- Keep presentation, state, and data access responsibilities clear.
- Handle loading, empty, success, disabled, and error states where relevant.
- Preserve responsive behavior and keyboard/accessibility expectations.
- Avoid duplicated or conflicting client state.
- Treat API failures and stale data as normal cases that need explicit behavior.
- Do not expose credentials, private keys, server secrets, or privileged operations in client code.
- Treat frontend permission checks as UX controls only. Real authorization belongs on trusted server boundaries.
- Prefer existing components and utilities before adding new abstractions or dependencies.
- Optimize rendering or bundle behavior only where the change is measurable or clearly justified.

## API Integration

When frontend work depends on an API, verify the actual request and response contract. Do not invent fields or assume server behavior from UI requirements alone. Preserve meaningful error messages without exposing sensitive internals.

## Verification

Use the project’s available checks that match the change, such as targeted component tests, type checking, linting, frontend tests, or a production build. Shared components and routing changes deserve broader verification than isolated visual adjustments.

## Boundaries

Use `backend-development` for server-side behavior or authorization enforcement. Use `database-engineering` for substantial schema or migration work. Use `application-security` for broad security review or sensitive security changes. Combine with `systematic-debugging` when diagnosing unexplained frontend failures.

## Common Mistakes

- Fixing only the happy path.
- Hiding an action in the UI and assuming the resource is secure.
- Replacing established project patterns without need.
- Adding framework-specific dependencies for problems the existing stack already solves.
- Declaring success after visual inspection without checking behavior.