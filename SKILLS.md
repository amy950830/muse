# Muse Skills Index

Muse uses specialist skills on demand. `IDENTITY.md` defines who Muse is and root `AGENTS.md` defines default engineering behavior; skills refine technique for specific task classes and must not weaken those protected rules.

| Skill | Use when | Path |
|---|---|---|
| `frontend-development` | Browser-facing components, routing, state, forms, data fetching, responsive UI, accessibility, or frontend performance | `.agents/skills/frontend-development/SKILL.md` |
| `backend-development` | APIs, server-side business logic, auth integration, authorization enforcement, jobs, caching, rate limits, or external services | `.agents/skills/backend-development/SKILL.md` |
| `application-security` | Security review, auth changes, sensitive data, hardening, vulnerability investigation, or abuse-resistant design | `.agents/skills/application-security/SKILL.md` |
| `database-engineering` | Schema design, migrations, indexes, transactions, constraints, concurrency, query performance, or data integrity | `.agents/skills/database-engineering/SKILL.md` |
| `systematic-debugging` | Failed tests, regressions, runtime errors, inconsistent output, integration failure, or unexplained behavior | `.agents/skills/systematic-debugging/SKILL.md` |
| `continuous-learning` | GitHub research, source evaluation, reusable pattern extraction, knowledge revalidation, or Muse capability-improvement proposals | `.agents/skills/continuous-learning/SKILL.md` |

Load only the smallest useful skill set. Multiple skills may be combined when a task genuinely spans domains; for example, an API authorization bug may require `systematic-debugging`, `backend-development`, and `application-security`.

Skills never override `IDENTITY.md`, root `AGENTS.md`, authorization boundaries, privacy rules, data-integrity rules, secret-handling rules, or production-safety requirements.