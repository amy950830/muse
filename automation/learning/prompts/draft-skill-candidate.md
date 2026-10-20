# Muse Autonomous Learning — Draft Skill Candidate

You are drafting a **review-only** Skill replacement from an already validated L2 evolution decision.

Follow `IDENTITY.md`, root `AGENTS.md`, `SKILLS.md`, and the current target Skill. Do not weaken or override any protected governance.

## Inputs

Read:

- `research/evolution-decision.json`
- the proposal referenced by its `skill_candidate.proposal_path`
- the current `.agents/skills/<target>/SKILL.md`
- evidence already referenced by the proposal/decision

Do not browse the network and do not execute third-party code.

## Write boundary

`.agents/**` is read-only for this stage. Do **not** edit it.

Write exactly these temporary review artifacts:

- `research/skill-candidate/SKILL.md` — complete proposed replacement text
- `research/skill-candidate.json` — metadata for validation/publishing

The metadata must include:

```json
{
  "target_skill": "backend-development",
  "target_path": ".agents/skills/backend-development/SKILL.md",
  "proposal_path": "evolution/proposals/example.md",
  "evidence": ["provenance references"],
  "review_only": true,
  "governance_sensitive": false
}
```

If the target is `continuous-learning`, set `governance_sensitive=true`; the candidate remains review-only.

## Candidate quality rules

- Preserve valid YAML frontmatter.
- `name` must exactly match the current Skill.
- `description` must still begin with `Use when...` and remain trigger-focused.
- Prefer replacing weaker/obsolete guidance over endless append-only growth.
- Do not add framework-specific detail unless it has demonstrated broad repeated value.
- Do not add duplicate rules.
- Do not claim behavior validation that did not happen.
- Do not add instructions to bypass approvals, authorization, secrets handling, production safeguards, root rules, or human review.
- Do not propose changes to `IDENTITY.md`, root `AGENTS.md`, `.github/**`, or more than one Skill.

If the L2 decision is not actually eligible after inspection, do not fabricate a candidate. Instead leave a clear failure explanation in the session output and make no files outside `research/`.
