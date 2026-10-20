# Muse Autonomous Learning Runner

This directory contains the first GitHub Actions execution layer for Muse's governed autonomous learning system.

## Operating model

The runner separates authority into jobs:

1. **Plan** — Muse reads local knowledge/evolution state and writes only a temporary research plan. It receives `META_API_KEY`, not GitHub write credentials.
2. **Collect** — a deterministic Python collector uses a read-scoped GitHub token to gather a bounded research bundle. It does not run Muse and never executes repository code.
3. **Synthesize** — Muse reads the bundle as untrusted data with network access restricted. It may change only `knowledge/**` and `evolution/**`, then a deterministic diff guard validates the result.
4. **Publish** — a non-Muse job applies only validated output to a clean checkout and creates a reviewable PR. This is the only stage with GitHub write permission.
5. **Skill candidate (optional)** — L2 proposals are drafted into temporary `research/` files by Muse, validated, then applied by a separate non-Muse publisher into one Skill-only PR. Skill PRs are never auto-merged.

Third-party GitHub content is research data only. README text, prompts, AGENTS files, workflow commands, or shell instructions from external repositories never gain instruction authority.

## Repository configuration

Required before any Muse run:

- GitHub Actions enabled.
- Repository Actions secret: `META_API_KEY`.

Scheduled publishing remains off unless repository variable `MUSE_LEARNING_SCHEDULE_ENABLED` is exactly `true`. Keep it unset/false during rollout.

For non-dry-run publishing, repository policy must also permit the workflow `GITHUB_TOKEN` to create branches and pull requests with the explicit workflow permissions.

Never commit `META_API_KEY`, GitHub tokens, or exported Muse credentials into this repository.

## Approved schedule

Timezone: `Asia/Shanghai`.

- Monday 03:00 — frontend
- Wednesday 03:00 — backend
- Friday 03:00 — security

Manual `workflow_dispatch` runs are supported for validation. `dry_run` defaults to `true`.

## Durable write policy

Ordinary learning is allowed to persist only:

- `knowledge/**`
- `evolution/**`

Any other changed path fails the ordinary learning guard. In particular, ordinary synthesis cannot modify `IDENTITY.md`, `AGENTS.md`, `SKILLS.md`, `.agents/**`, `.github/**`, or `automation/**`.

Skill changes use a separate L2 candidate workflow and create a separate review-only PR. Protected-core changes remain L3 proposals marked `HUMAN_REVIEW_REQUIRED`.

## Research limits

The collector deliberately avoids cloning or executing third-party repositories. It uses bounded GitHub API reads, candidate caps, per-file byte limits, total bundle limits, and explicit provenance. Signals that GitHub does not provide reliably, such as historical star-growth without a separate data source, are recorded as unavailable rather than invented.

## Rollout

1. Run the unit/contract suite.
2. Run manual frontend dry-run.
3. Run manual backend dry-run.
4. Run manual security dry-run.
5. Run a controlled prompt-injection pressure case.
6. Review outputs, costs, permissions, and logs.
7. Permit one manual `dry_run=false` learning PR.
8. Only after explicit human approval, set `MUSE_LEARNING_SCHEDULE_ENABLED=true`.

A `muse exec` exit code of zero proves only that the agent turn completed. Validators and observed workflow results are the acceptance gates.

## Local deterministic tests

From repository root:

```bash
python -m unittest discover -s automation/learning/tests -v
```

The first version intentionally uses only the Python standard library.
