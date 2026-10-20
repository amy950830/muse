# Muse Core Skills Design

## Purpose

This document defines the first professional skill layer for Muse.

Muse already has two root-level foundations:

- `IDENTITY.md` defines Muse as a senior full-stack software engineer with integrated application security responsibility.
- `AGENTS.md` defines Muse's default engineering execution rules.

The next layer is a small set of reusable, task-triggered skills that give Muse specialized guidance without forcing every engineering session to load one oversized instruction file.

The design goal is to make Muse more capable in real development work while preserving the existing principles of correctness, security, efficiency, evidence-based verification, and low process overhead.

## Scope

Create exactly five initial engineering skills:

1. `frontend-development`
2. `backend-development`
3. `application-security`
4. `database-engineering`
5. `systematic-debugging`

Also create a root `SKILLS.md` index that explains when each skill should be used and how the skill layer relates to `IDENTITY.md` and `AGENTS.md`.

The initial skill set intentionally excludes broader future capabilities such as architecture design, code review, deployment, testing strategy, and performance engineering. Those can be added later after the core skill layer is stable.

## Repository Structure

The target structure is:

```text
muse/
├── AGENTS.md
├── IDENTITY.md
├── SKILLS.md
│
└── .agents/
    └── skills/
        ├── frontend-development/
        │   └── SKILL.md
        ├── backend-development/
        │   └── SKILL.md
        ├── application-security/
        │   └── SKILL.md
        ├── database-engineering/
        │   └── SKILL.md
        └── systematic-debugging/
            └── SKILL.md
```

Each skill has one required `SKILL.md` file. Supporting files are not part of this first implementation unless testing demonstrates that a skill genuinely needs them.

## Skill Design Rules

Every `SKILL.md` must:

- Use YAML frontmatter with `name` and `description`.
- Use lowercase hyphenated skill names.
- Start the description with `Use when...`.
- Describe triggering conditions only in the frontmatter description; do not summarize the entire workflow there.
- Stay concise enough to load on demand without creating unnecessary context cost.
- Avoid duplicating rules already defined in `AGENTS.md` unless repetition is required for task-specific judgment.
- Prefer technology-agnostic guidance unless the skill's purpose requires framework-specific behavior.
- Define clear boundaries so Muse can distinguish neighboring skills.
- Include concrete verification expectations.
- Never imply that a tool, test, scanner, or deployment action occurred unless it actually occurred.

## Skill Discovery and Invocation

`SKILLS.md` serves as a human-readable map of the skill layer.

Muse should load a skill only when the current task matches its trigger conditions.

The intended relationship is:

```text
IDENTITY.md
  → who Muse is

AGENTS.md
  → how Muse works by default

SKILLS.md
  → what specialist skills exist

.agents/skills/<name>/SKILL.md
  → how to handle a specialized class of task
```

Skills supplement `AGENTS.md`; they do not replace it.

More specific skill guidance may refine engineering technique but must not weaken repository-level safety, authorization, privacy, data-integrity, or production-safety rules.

## Skill Responsibilities

### frontend-development

Use for work involving browser-facing application behavior, including components, routing, state, forms, client-side data fetching, responsive layout, accessibility, and frontend performance.

The skill should emphasize:

- Reading the existing frontend structure before modifying it.
- Preserving component and state-management conventions.
- Handling loading, empty, success, and error states.
- Treating frontend authorization checks as user-experience controls only, never as the security boundary.
- Avoiding client-side secret exposure.
- Testing shared UI changes with the project's available build, type-check, and frontend test commands.
- Keeping visual polish subordinate to functional correctness and accessibility.

It should not own backend authorization, database migrations, or general security audits except where those concerns directly affect frontend behavior.

### backend-development

Use for server-side application behavior, APIs, services, business logic, authentication integration, authorization enforcement, external integrations, background work, caching, rate limits, and error handling.

The skill should emphasize:

- Tracing request flow from entry point through validation, authentication, authorization, business logic, data access, and response.
- Enforcing important business rules on the server.
- Preserving API compatibility unless the task explicitly requires a contract change.
- Handling retries, timeouts, duplicate requests, partial failures, and error responses when relevant.
- Protecting sensitive data in responses and logs.
- Verifying both allowed and denied paths for protected operations.

It should defer deep schema design and migration reasoning to `database-engineering` when those concerns become substantial.

### application-security

Use for security reviews, authentication and authorization changes, sensitive-data protection, security hardening, vulnerability investigation, permission-boundary work, and abuse-resistant design.

The skill should cover relevant classes such as:

- Broken access control and IDOR
- Authentication and session weaknesses
- SQL and command injection
- XSS and CSRF
- SSRF
- Path traversal
- Unsafe uploads and file processing
- Secret leakage
- Sensitive data exposure
- Business-logic abuse
- Rate-limit bypass
- Race-condition security impact
- Dependency and configuration weaknesses

The skill must distinguish:

- Confirmed vulnerabilities
- Strong code-level findings
- Potential risks that still require verification

It must never claim that passing automated checks proves the application is secure.

Security testing must remain inside the user's authorized scope.

### database-engineering

Use for schema design, data-model changes, migrations, query performance, indexes, transactions, constraints, concurrency, retention, and database integrity.

The skill should emphasize:

- Understanding existing schema and query patterns first.
- Preserving data integrity.
- Using constraints and transactions deliberately.
- Reviewing migration compatibility with existing records and deployed services.
- Preferring backward-compatible migrations where practical.
- Identifying rollback or recovery implications before consequential changes.
- Never performing destructive production operations without explicit authorization.
- Verifying query and migration behavior with available tooling or tests.

It should not turn every small data-access change into a full database redesign.

### systematic-debugging

Use when there is a bug, failed test, unexpected behavior, inconsistent output, regression, integration failure, or unexplained runtime problem.

The skill should emphasize:

- Reproducing or clearly understanding the symptom before changing code.
- Tracing the relevant execution path.
- Gathering evidence before forming conclusions.
- Distinguishing symptom from root cause.
- Testing the smallest plausible explanation first.
- Making the smallest correct fix.
- Re-running relevant checks after the fix.
- Avoiding repeated speculative edits and error suppression.

This skill may be combined with any domain skill. For example, an API bug may require both `systematic-debugging` and `backend-development`.

## Cross-Skill Rules

Multiple skills may apply to one task.

When that happens:

- Process-oriented skills should guide the investigation or implementation method.
- Domain skills should guide the technical decisions in their area.
- Muse should load only the smallest useful combination.
- Muse should not duplicate the same checklist across multiple skills.

Typical combinations include:

- UI data bug → `systematic-debugging` + `frontend-development`
- API authorization bug → `systematic-debugging` + `backend-development` + `application-security`
- Slow transactional endpoint → `backend-development` + `database-engineering`
- Access-control migration → `application-security` + `database-engineering`

## Verification Strategy

Skill creation itself must be tested as behavior guidance rather than treated as successful merely because Markdown files exist.

For each skill, define at least one pressure scenario that represents a likely failure mode without the skill.

Examples:

- Frontend: agent fixes a protected button in the UI but forgets server-side permission implications.
- Backend: agent adds an endpoint without validating resource ownership.
- Security: agent reports a scanner warning as a confirmed exploitable vulnerability without evidence.
- Database: agent proposes a destructive migration without checking existing records or rollback.
- Debugging: agent makes several speculative edits before reproducing the failure.

The expected validation cycle is:

1. Record baseline behavior without the new skill when practical.
2. Write the minimal skill guidance that addresses observed failure patterns.
3. Re-run the same scenario with the skill available.
4. Refine wording only where the scenario reveals ambiguity or loopholes.
5. Verify frontmatter syntax, names, trigger descriptions, and repository paths.

Where the current environment cannot run a real Muse behavior test, the implementation must report that limitation explicitly and must not describe the skill as behavior-validated.

## SKILLS.md Requirements

`SKILLS.md` should remain short and serve only as an index.

It should include:

- The purpose of the skill layer.
- A table containing skill name, trigger summary, and path.
- A note that skills are loaded on demand rather than all at once.
- A note that `IDENTITY.md` and `AGENTS.md` remain authoritative for identity and default execution behavior.
- A note that multiple skills may be combined when a task genuinely spans domains.

It should not duplicate full skill instructions.

## Quality Constraints

The first implementation should optimize for clarity and low context cost.

Constraints:

- No large reference manuals inside the initial skills.
- No framework-specific dependency recommendations unless necessary.
- No unsupported claims about Muse runtime behavior.
- No unnecessary directories or placeholder files.
- No automated security claims based only on static text inspection.
- No artificial development phase labels in user-facing documentation.
- No requirement for repetitive confirmation during safe, reversible engineering tasks.

## Non-Goals

This work does not yet create:

- Architecture-design skill
- Code-review skill
- Deployment skill
- Dedicated testing strategy skill
- Performance-engineering skill
- CI/CD workflows
- Automated Muse runtime integration tests
- A plugin distribution package

These may be added in later work after the core skill layer is exercised in real Muse development sessions.

## Success Criteria

The work is successful when:

- All five skill directories exist at the agreed paths.
- Every skill has valid frontmatter and clear trigger conditions.
- Responsibilities are distinct enough to avoid unnecessary overlap.
- `SKILLS.md` accurately indexes the available skills.
- The skill wording is consistent with `IDENTITY.md` and `AGENTS.md`.
- Validation scenarios exist and are used where the available runtime permits.
- Any unperformed behavior validation is clearly disclosed.
- The repository remains minimal and understandable.
