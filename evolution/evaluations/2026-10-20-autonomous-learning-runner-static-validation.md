# Autonomous Learning Runner — Static Validation

Date: 2026-10-20
Branch: `feature/muse-autonomous-learning-runner`
Validated head before this record: `ff1b7c78431efe72d9cd5ff44a6e52e13cf507b1`

## Status

**STATIC VALIDATION: PASS**

**MUSE / GITHUB ACTIONS RUNTIME BEHAVIOR: NOT YET BEHAVIOR-VALIDATED**

This record proves deterministic local tests, workflow structure, repository change scope, and protected-core integrity. It does not claim that a real GitHub Actions run has successfully invoked Muse, reached GitHub APIs, generated a research plan, resisted a live prompt-injection attempt, or opened a learning PR.

## Deterministic Test Evidence

Fresh command executed from the implementation workspace:

```text
python -m unittest discover -s automation/learning/tests -v
```

Result on Python 3.13.5:

```text
Ran 49 tests
OK
```

Coverage includes:

- learning-domain and machine-readable contract constants;
- schedule/domain resolution and research-plan validation;
- Stable and Emerging repository scoring;
- explicit missing-signal handling rather than fabricated growth metrics;
- prompt-injection / shell-instruction risk tagging;
- bounded GitHub research collection and sanitized API failures;
- ordinary learning path guard and traversal rejection;
- L0–L3 evolution-decision validation;
- Skill-candidate target/proposal/frontmatter/governance validation;
- target-path validation before current Skill file reads;
- generated-output secret scanning for plain/base64/hex representations;
- deterministic branch naming;
- GitHub Actions schedule, action pinning, sandbox/model-step limits, credential-role separation, immutable post-Muse workspace checks, and pre-push revalidation.

## Workflow Parsing and Exact-Content Check

The workflow was parsed successfully as YAML in the implementation environment.

Local Git blob SHA:

```text
.github/workflows/muse-learning.yml
6ed244caf014091c6b8ba498a24823fb792b765d
```

The GitHub feature branch reports the same blob SHA, preventing a false result where local tests validate content that differs from the committed workflow.

The workflow contract test blob is likewise aligned:

```text
automation/learning/tests/test_workflow_contract.py
9d5cd15cc93c93528228bd906438e8e73a51fb7c
```

## Protected Core Integrity

Protected files remain byte-identical to their pre-implementation versions:

```text
IDENTITY.md
3ccf6840993126858bb250c40b8be36c1b3f6150

AGENTS.md
95a438ec23c430e26f3c61580b8c127d7eb1d138
```

No autonomous-learning implementation commit modifies either file.

A fresh `main` → feature-branch comparison showed the branch only adds the learning workflow, `automation/learning/**`, tests/fixtures, and `research/.gitignore` before this evaluation record. Existing production/governance files were not modified.

## Credential and Authority Matrix

| Job | Muse / `META_API_KEY` | GitHub token authority | Untrusted research bundle | Persistent write authority |
|---|---|---|---|---|
| `plan` | Yes, step-scoped | `contents: read`; no GitHub token passed to Muse | No | None |
| `collect` | No | `contents: read`; token passed only to collector | Produces bundle | None |
| `synthesize` | Yes, step-scoped | `contents: read`; no write token | Yes | None; emits validated artifact only |
| `publish_learning` | No | `contents: write`, `pull-requests: write` | No raw bundle processing | Learning branch + PR only |
| `draft_skill_candidate` | Yes, step-scoped | `contents: read`; no write token | No raw bundle; consumes validated proposal output | None; temporary candidate artifact only |
| `publish_skill_candidate` | No | `contents: write`, `pull-requests: write` | No | One Skill candidate branch + PR only |

The static workflow contract confirms that no Muse job has GitHub write permission and no publishing job invokes Muse or receives `META_API_KEY`.

## Post-Muse Guarding

Repository-resident validators are not trusted until an immutable workflow-level Git check confirms Muse did not modify validator/control files.

- Planning must leave tracked repository files unchanged and may write only ignored `research/**` temporary output.
- Synthesis may modify only `knowledge/**` and `evolution/**`; any other tracked/untracked repository path fails before repository validators execute.
- Skill drafting snapshots the already-validated learning patch before Muse runs and compares it afterward; changes to validated knowledge/evolution content fail. Other unauthorized repository changes also fail.
- Publishing jobs revalidate allowed paths/candidate target immediately before commit/push.

This reduces the risk of an agent modifying its own guard and then using the modified guard to approve the same run.

## Schedule and Rollout Gate

Configured schedule intent:

```text
Monday    03:00 Asia/Shanghai -> frontend
Wednesday 03:00 Asia/Shanghai -> backend
Friday    03:00 Asia/Shanghai -> security
```

Scheduled jobs are gated by:

```text
MUSE_LEARNING_SCHEDULE_ENABLED == 'true'
```

The variable is expected to remain absent/false during rollout. Manual `workflow_dispatch` defaults to `dry_run=true`.

## Remaining Runtime Preconditions

The following are intentionally not claimed by static validation:

1. GitHub Actions secret `META_API_KEY` exists and authenticates successfully.
2. The current hosted runner can install and execute the current Muse CLI using the verified command-line flags.
3. Repository Actions policy permits the requested `GITHUB_TOKEN` branch/PR writes for a non-dry-run publishing test.
4. Frontend, backend, and security manual dry-runs complete successfully with real GitHub/API data.
5. A controlled live prompt-injection pressure case is resisted by Muse synthesis.
6. A manual `dry_run=false` run creates only the intended reviewable PR(s).
7. Scheduled operation has not been enabled and must not be enabled until the above evidence is reviewed and explicitly approved.

## Current Validation Classification

- Deterministic helper/unit behavior: **VALIDATED by local tests**.
- Workflow structural/security contract: **STATICALLY VALIDATED**.
- Protected core integrity: **VALIDATED by Git blob SHA**.
- Real Muse planning behavior: **NOT YET BEHAVIOR-VALIDATED**.
- Real Muse synthesis/prompt-injection behavior: **NOT YET BEHAVIOR-VALIDATED**.
- Real GitHub Actions credential/runtime behavior: **NOT YET BEHAVIOR-VALIDATED**.
- PR publishing behavior: **NOT YET BEHAVIOR-VALIDATED**.
- Scheduled A1 operation: **DISABLED / NOT YET VALIDATED**.

## Next Gate

Before enabling any scheduled writes, merge the statically validated implementation onto the default branch, configure the required secret, and execute the three manual dry-runs defined in the implementation plan. Do not mark runtime scenarios validated unless their Actions evidence has actually been observed.
