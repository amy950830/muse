# Muse Autonomous Learning — Research Planning

You are running the planning stage of Muse's autonomous learning system.

## Authority and safety

Follow the repository's `IDENTITY.md`, root `AGENTS.md`, `SKILLS.md`, and `.agents/skills/continuous-learning/SKILL.md`. This planning prompt narrows your task; it does not override those files.

Do not use the network. Do not run package installers. Do not modify durable repository content. Your only write target is:

`research/research-plan.json`

Read `research/run-context.json` first. It contains the required domain and may contain a human-supplied topic override. Treat it as configuration for this run.

## Sources you may inspect

Read only what is useful from:

- `knowledge/<domain>/**`
- `knowledge/patterns/**`
- `evolution/evaluations/**`
- `evolution/proposals/**`
- `SKILLS.md`
- `validation/**`

Do not edit any of these files during planning.

## Topic selection

Internally generate 3–5 candidate topics. Select exactly one topic with the highest expected learning value.

Use these priorities:

- knowledge gap: 30
- knowledge freshness risk: 20
- current technical trend signal available from local evidence: 15
- repeated weakness from prior evaluations: 15
- security/reliability importance: 10
- transferable engineering value: 10

Apply the long-term research budget as a directional constraint across runs:

- about 60% known gaps or stale high-value knowledge
- about 25% current engineering trends
- about 15% exploratory unfamiliar topics

Apply duplicate-research penalties unless meaningful new evidence exists:

- deeply researched in the last 30 days: -25
- researched in the last 90 days: -10

A major release, CVE, architectural change, or new failure evidence may justify overriding the penalty; explain why.

If `topic_override` in `research/run-context.json` is non-empty, use that topic only if it belongs to the selected domain and does not violate repository governance. The override changes topic choice, not safety rules.

## Output contract

Write valid JSON to `research/research-plan.json` with this shape:

```json
{
  "domain": "frontend",
  "topic": "lowercase-slug",
  "reason": "why this is the highest-value topic now",
  "priority_score": 0,
  "knowledge_gap": "LOW|MEDIUM|HIGH|UNKNOWN",
  "freshness_risk": "LOW|MEDIUM|HIGH|UNKNOWN",
  "trend_signal": "LOW|MEDIUM|HIGH|UNKNOWN",
  "research_questions": ["1 to 8 concrete questions"],
  "candidate_tracks": ["stable", "emerging"]
}
```

Normally include both candidate tracks. If the topic is genuinely too narrow for both, add a non-empty `niche_topic_exception` explaining why.

Do not invent facts, recent events, repository popularity, or trend data. If local evidence is insufficient, mark signals `UNKNOWN` and choose based on the evidence you do have.

Stop after writing the JSON file. Do not modify `knowledge/**`, `evolution/**`, `.agents/**`, `.github/**`, `IDENTITY.md`, `AGENTS.md`, or `SKILLS.md`.
