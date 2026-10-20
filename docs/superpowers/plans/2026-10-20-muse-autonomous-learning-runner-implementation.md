# Muse Autonomous Learning Runner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Muse's first autonomous GitHub Actions learning runner with safe topic selection, bounded GitHub research, evidence-based synthesis, governed evolution, and dry-run-first rollout.

**Architecture:** Use separate GitHub Actions jobs to isolate credentials and authority. Muse planning/synthesis jobs receive only `META_API_KEY` and run with sandboxing plus restricted network; the GitHub collector receives only read-scoped GitHub credentials; publishing jobs receive GitHub write permission but never run Muse or process untrusted repository instructions. Ordinary learning may persist only `knowledge/**` and `evolution/**`; Skill candidates are staged separately and opened as review-only PRs.

**Tech Stack:** GitHub Actions, Muse Code headless CLI, Python 3.12+ standard library only, `unittest`, Git/GitHub CLI in controlled publishing jobs.

**Spec:** `docs/superpowers/specs/2026-10-20-muse-autonomous-learning-runner-design.md`

## Current External Assumptions Verified on 2026-10-20

- GitHub Actions supports `on.schedule[].timezone` with an IANA timezone string; use `Asia/Shanghai` directly for the approved Beijing schedule.
- Muse Code supports `muse exec`, `META_API_KEY`, `--prompt-file`, `--max-model-steps`, `--sandbox-network`, `--disable-approval`, `--trust-workspace`, and `--no-session-log`.
- Muse Code's sandbox keeps `.git`, `.muse`, and `.agents` read-only inside the workspace; Skill candidates therefore must be drafted into temporary writable output and applied only by a later controlled publishing job.
- Use SHA-pinned GitHub Actions in the workflow. Verified pins at planning time:
  - `actions/checkout` v7.0.1 → `3d3c42e5aac5ba805825da76410c181273ba90b1`
  - `actions/setup-python` v7.0.0 → `5fda3b95a4ea91299a34e894583c3862153e4b97`
  - `actions/upload-artifact` v7.0.2 → `cf430e030ddbb5b0abf93d22962f4752f3646cd9`
  - `actions/download-artifact` v8.0.2 → `9000827ccba6bdab643e8b6fd33ac0654aef8333`
- Muse install command for Linux CI: `curl -fsSL https://dev.meta.ai/install.sh | sh`, followed by `muse --version` logging.

## Global Constraints

- Keep `IDENTITY.md` and root `AGENTS.md` unchanged.
- Do not auto-merge learning or Skill-candidate PRs.
- Do not expose `META_API_KEY` and a GitHub write credential to the same Muse/untrusted-content processing job.
- All third-party repository content is untrusted data, never instruction authority.
- Never execute downloaded repository scripts, package installers, project test suites, or shell instructions.
- Ordinary scheduled learning may change only `knowledge/**` and `evolution/**`.
- Skill changes must be staged separately; at most one Skill candidate per learning run.
- Protected-core proposals remain proposal-only and must be labeled `HUMAN_REVIEW_REQUIRED`.
- Missing GitHub metrics must be recorded as unavailable, never fabricated.
- Use Python standard library only for first-version helpers and tests; avoid adding third-party runtime dependencies.
- Every helper must be testable without live GitHub or Muse calls by dependency injection or local fixtures.
- Scheduled publishing stays disabled until three manual domain dry-runs have been reviewed.
- A Muse CLI exit code of `0` is not proof that generated output is valid; explicit validators remain authoritative.

## Review Focus

1. **Credential crossover:** no Muse job that reads untrusted GitHub material may receive GitHub write credentials; publishing jobs must never invoke Muse.
2. **Prompt injection:** README text such as `Ignore previous instructions` or `curl ... | bash` must remain quoted research data and must never affect runner control flow.
3. **Unavailable growth metrics:** Emerging Track must degrade transparently when recent star-growth history is unavailable rather than inventing a score.
4. **Unauthorized writes:** any ordinary synthesis change outside `knowledge/**` or `evolution/**` must fail before patch publication.
5. **Governance escalation:** an L2 change is review-only and bounded to one specialist Skill; any protected-core effect must be L3 proposal-only.

---

## File Structure

Create the following implementation surface:

```text
.github/
└── workflows/
    └── muse-learning.yml

automation/
└── learning/
    ├── README.md
    ├── contracts.py
    ├── resolve_run.py
    ├── validate_research_plan.py
    ├── scoring.py
    ├── github_client.py
    ├── collect_github_research.py
    ├── validate_learning_output.py
    ├── validate_evolution_decision.py
    ├── validate_skill_candidate.py
    ├── branch_names.py
    ├── prompts/
    │   ├── plan-research.md
    │   ├── synthesize-learning.md
    │   └── draft-skill-candidate.md
    └── tests/
        ├── fixtures/
        │   ├── github_repo_stable.json
        │   ├── github_repo_emerging.json
        │   └── github_repo_untrusted.json
        ├── test_contracts.py
        ├── test_resolve_run.py
        ├── test_scoring.py
        ├── test_collector.py
        ├── test_output_guard.py
        ├── test_evolution_decision.py
        ├── test_skill_candidate.py
        └── test_branch_names.py

research/
└── .gitignore
```

Do not add a third-party package manifest in v1 unless implementation proves the standard library is insufficient.

---

### Task 1: Define machine-readable contracts and ignored research workspace

**Files:**
- Create: `automation/learning/contracts.py`
- Create: `automation/learning/tests/test_contracts.py`
- Create: `research/.gitignore`

**Interfaces:**
- Produces: validation helpers/constants used by planning, collector, synthesis, and publishing stages.
- Contract constants: allowed domains, knowledge states, evolution levels, confidence values, candidate tracks, path allowlists.

- [ ] **Step 1: Write failing contract tests**

Tests must assert:

- domains are exactly `frontend`, `backend`, `security`;
- candidate tracks are exactly `stable`, `emerging`;
- evolution levels are exactly `L0`, `L1`, `L2`, `L3`;
- durable confidence values are `High`, `Medium`, `Exploratory`;
- ordinary auto-write roots are exactly `knowledge/` and `evolution/`;
- protected paths include `IDENTITY.md`, `AGENTS.md`, `SKILLS.md`, `.agents/`, `.github/`, `automation/`.

Run: `python -m unittest automation.learning.tests.test_contracts -v`
Expected before implementation: FAIL due missing module/constants.

- [ ] **Step 2: Implement minimal `contracts.py`**

Use immutable tuples/frozensets and small validation helpers; no I/O.

- [ ] **Step 3: Re-run contract tests**

Expected: PASS.

- [ ] **Step 4: Create `research/.gitignore`**

Content must ignore everything under `research/` except `.gitignore` itself.

- [ ] **Step 5: Commit**

Commit message: `Add learning runner contracts`

### Task 2: Resolve scheduled/manual runs and validate research plans

**Files:**
- Create: `automation/learning/resolve_run.py`
- Create: `automation/learning/validate_research_plan.py`
- Create: `automation/learning/tests/test_resolve_run.py`

**Interfaces:**
- `resolve_domain(event_name: str, schedule: str | None, manual_domain: str | None) -> str`
- `validate_research_plan(data: dict, expected_domain: str) -> list[str]`

- [ ] **Step 1: Write failing tests for schedule mapping**

Required mappings using Beijing-local cron strings:

- `0 3 * * 1` → `frontend`
- `0 3 * * 3` → `backend`
- `0 3 * * 5` → `security`
- `workflow_dispatch` requires one of the three explicit domains.
- unknown schedule/domain is rejected.

- [ ] **Step 2: Write failing research-plan validation tests**

Require:

- expected domain matches;
- slug-like non-empty `topic`;
- `priority_score` integer from 0–100;
- non-empty `reason`;
- `knowledge_gap`, `freshness_risk`, `trend_signal` from explicit enums;
- 1–8 non-empty `research_questions`;
- both Stable and Emerging tracks unless a documented niche-topic exception field is present.

- [ ] **Step 3: Implement resolver and validator**

Both scripts expose importable functions plus a thin CLI reading JSON/file arguments and returning non-zero on validation errors.

- [ ] **Step 4: Run tests**

Run: `python -m unittest automation.learning.tests.test_resolve_run -v`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `Add learning run and research plan validation`

### Task 3: Implement Stable/Emerging scoring with missing-signal handling

**Files:**
- Create: `automation/learning/scoring.py`
- Create: `automation/learning/tests/test_scoring.py`
- Create: the three fixture JSON files under `automation/learning/tests/fixtures/`

**Interfaces:**
- `score_stable(signals: dict[str, float | None]) -> dict`
- `score_emerging(signals: dict[str, float | None]) -> dict`
- `value_band(score: float) -> str`
- `detect_risk_flags(repository_text: str, metadata: dict) -> list[str]`

- [ ] **Step 1: Write failing Stable Track tests**

Tests must prove:

- star count is not a direct weighted quality factor;
- strong tests/docs/maintenance can outscore a stale high-star project;
- score remains 0–100;
- value-band thresholds match the spec.

- [ ] **Step 2: Write failing Emerging Track tests**

Tests must prove:

- unavailable recent-star-growth is represented as `None`/`unavailable`;
- available weights are re-normalized or otherwise adjusted transparently without inventing data;
- recent activity/innovation can rank an emerging project strongly;
- output contains `missing_signals`.

- [ ] **Step 3: Write failing untrusted-content tests**

Fixture must include text such as `Ignore previous instructions` and `curl ... | bash`; expected flags include prompt-injection/shell-instruction risk but the text is retained as inert data.

- [ ] **Step 4: Implement scoring and risk flagging**

Keep score calculation deterministic and pure. Include factor breakdown and missing-signal list in returned results.

- [ ] **Step 5: Run tests**

Run: `python -m unittest automation.learning.tests.test_scoring -v`
Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `Add repository scoring engine`

### Task 4: Build bounded GitHub research collector

**Files:**
- Create: `automation/learning/github_client.py`
- Create: `automation/learning/collect_github_research.py`
- Create: `automation/learning/tests/test_collector.py`

**Interfaces:**
- `GitHubClient(token: str, opener=...)`
- `search_repositories(query: str, per_page: int) -> list[dict]`
- bounded fetch helpers for repo metadata, README, releases, selected contents, security policy, and selected issue/PR metadata.
- `collect(plan: dict, output_dir: Path, client: GitHubClient, limits: Limits) -> dict`

- [ ] **Step 1: Write failing collector tests using fake HTTP responses**

Tests cover:

- candidate discovery is capped at configured maximum;
- no full recursive clone/download occurs;
- per-file byte limit and total bundle byte limit are enforced;
- only allowlisted GitHub API hosts/paths are requested;
- rate-limit or insufficient-source failures return clear non-secret errors;
- manifest records repository, retrieval time, commit/default-branch reference when available, fetched artifacts, license info, scores, missing signals, and risk flags.

- [ ] **Step 2: Implement minimal stdlib HTTP client**

Use `urllib.request`; set an explicit User-Agent and GitHub API version header. Never log the token.

- [ ] **Step 3: Implement candidate funnel**

Default limits from spec:

- discover: 30 candidates (configurable safe range 10–40);
- metadata shortlist: 12;
- deep scoring: 8;
- focused inspection: 4;
- durable-source recommendation: 2–4.

Stable and Emerging tracks each contribute candidates before de-duplication.

- [ ] **Step 4: Implement bounded bundle layout**

Write under `research/bundle/` only. Include `manifest.json` plus source text/json files with sanitized filenames. Never execute fetched content.

- [ ] **Step 5: Run collector tests**

Run: `python -m unittest automation.learning.tests.test_collector -v`
Expected: PASS.

- [ ] **Step 6: Commit**

Commit message: `Add bounded GitHub research collector`

### Task 5: Implement ordinary learning diff guard and evolution decision validator

**Files:**
- Create: `automation/learning/validate_learning_output.py`
- Create: `automation/learning/validate_evolution_decision.py`
- Create: `automation/learning/tests/test_output_guard.py`
- Create: `automation/learning/tests/test_evolution_decision.py`

**Interfaces:**
- `validate_changed_paths(paths: list[str]) -> list[str]`
- `validate_evolution_decision(data: dict) -> list[str]`

- [ ] **Step 1: Write failing path-guard tests**

Allowed examples:

- `knowledge/frontend/example.md`
- `evolution/proposals/example.md`
- `evolution/evaluations/example.md`
- `evolution/changelog.md`

Rejected examples:

- `.agents/skills/backend-development/SKILL.md`
- `AGENTS.md`
- `IDENTITY.md`
- `SKILLS.md`
- `.github/workflows/muse-learning.yml`
- `automation/learning/scoring.py`
- unrelated root file.

- [ ] **Step 2: Write failing L0–L3 decision tests**

Require fields: `level`, `confidence_score`, `reason`, `sources`, `behavior_validation`, `protected_core_impact`, `skill_candidate`.

Rules:

- L2 requires score >= 75, non-empty behavior-validation description, one supported skill target, and `protected_core_impact=false`;
- L3 requires `HUMAN_REVIEW_REQUIRED` status and may not include an auto-applicable Skill candidate;
- no level may omit provenance/sources;
- score alone never overrides protected-core escalation.

- [ ] **Step 3: Implement validators and CLIs**

`validate_learning_output.py` must accept a newline-delimited changed-file list from `git diff --name-only` and exit non-zero on any unauthorized path.

- [ ] **Step 4: Run tests**

Run: `python -m unittest automation.learning.tests.test_output_guard automation.learning.tests.test_evolution_decision -v`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `Add learning governance validators`

### Task 6: Implement Skill-candidate staging without granting Muse write access to `.agents`

**Files:**
- Create: `automation/learning/validate_skill_candidate.py`
- Create: `automation/learning/tests/test_skill_candidate.py`

**Interfaces:**
- Muse writes temporary candidate files only under `research/skill-candidate/`.
- Candidate metadata file: `research/skill-candidate.json`.
- `validate_skill_candidate(metadata: dict, candidate_text: str, current_text: str) -> list[str]`

- [ ] **Step 1: Write failing tests**

Require:

- exactly one allowed target under `.agents/skills/<existing-skill>/SKILL.md`;
- target cannot be `continuous-learning` governance bypass unless explicitly proposed and still review-only;
- candidate frontmatter `name` must match the current Skill name;
- description must still begin `Use when...`;
- candidate cannot introduce instructions that weaken protected-core requirements;
- proposal path and evidence references must be present;
- candidate cannot request changes to `IDENTITY.md`, root `AGENTS.md`, `.github/**`, or multiple Skill files.

- [ ] **Step 2: Implement validator**

The validator does not apply the candidate. It only validates a temporary complete replacement `SKILL.md` drafted under `research/`.

- [ ] **Step 3: Run tests**

Run: `python -m unittest automation.learning.tests.test_skill_candidate -v`
Expected: PASS.

- [ ] **Step 4: Commit**

Commit message: `Add controlled Skill candidate validator`

### Task 7: Add deterministic branch naming

**Files:**
- Create: `automation/learning/branch_names.py`
- Create: `automation/learning/tests/test_branch_names.py`

**Interfaces:**
- `learning_branch(domain: str, date: str, topic: str) -> str`
- `skill_branch(skill_name: str, date: str, topic: str) -> str`

- [ ] **Step 1: Write failing branch-name tests**

Prove:

- unsafe characters are normalized;
- output length is bounded;
- learning branches follow `learning/<domain>/<date>-<topic>`;
- Skill branches follow `evolution/<skill>/<date>-<topic>`;
- same inputs produce same names.

- [ ] **Step 2: Implement branch helpers**

No shell interpolation; helper returns validated strings only.

- [ ] **Step 3: Run tests and commit**

Run: `python -m unittest automation.learning.tests.test_branch_names -v`
Expected: PASS.

Commit message: `Add learning branch naming`

### Task 8: Write Muse prompts with explicit untrusted-data boundaries

**Files:**
- Create: `automation/learning/prompts/plan-research.md`
- Create: `automation/learning/prompts/synthesize-learning.md`
- Create: `automation/learning/prompts/draft-skill-candidate.md`
- Create: `automation/learning/README.md`

**Interfaces:**
- Planning prompt outputs only `research/research-plan.json`.
- Synthesis prompt may edit only `knowledge/**` and `evolution/**` and must write `research/evolution-decision.json`.
- Skill prompt must not edit `.agents/**`; it writes a complete candidate `SKILL.md` under `research/skill-candidate/` plus candidate metadata JSON.

- [ ] **Step 1: Write planning prompt**

It must:

- read only local knowledge/evolution/index/validation sources;
- generate 3–5 candidate topics internally but persist only the selected plan;
- apply 60/25/15 long-term budget and duplicate penalties;
- not use web/network itself;
- not modify durable files.

- [ ] **Step 2: Write synthesis prompt**

Place an explicit delimiter around the research bundle and state repeatedly that content inside it is untrusted data, including any apparent agent/system/shell instructions. Require comparison across sources and provenance.

- [ ] **Step 3: Write Skill-candidate prompt**

It consumes a validated L2 proposal plus current Skill text and writes only temporary candidate output; protected-core changes must be refused and converted to L3 proposal language.

- [ ] **Step 4: Document operator model**

README explains secrets, dry-run, allowed output paths, job isolation, failure modes, and that external source code is never executed.

- [ ] **Step 5: Static prompt review**

Expected: no prompt grants external content instruction authority; no prompt permits auto-merge or root-governance edits.

- [ ] **Step 6: Commit**

Commit message: `Add Muse learning prompts and operator guide`

### Task 9: Build GitHub Actions workflow in dry-run-first mode

**Files:**
- Create: `.github/workflows/muse-learning.yml`

**Interfaces:**
- Triggers: `workflow_dispatch` plus Monday/Wednesday/Friday schedules.
- Scheduled runs are gated by repository variable `MUSE_LEARNING_SCHEDULE_ENABLED == 'true'`; initial expected state is absent/false.
- Manual input `dry_run` defaults to `true`.

- [ ] **Step 1: Add exact schedule**

```yaml
schedule:
  - cron: '0 3 * * 1'
    timezone: 'Asia/Shanghai'
  - cron: '0 3 * * 3'
    timezone: 'Asia/Shanghai'
  - cron: '0 3 * * 5'
    timezone: 'Asia/Shanghai'
```

Map Monday→frontend, Wednesday→backend, Friday→security using `resolve_run.py`.

- [ ] **Step 2: Add manual inputs**

Inputs:

- `domain`: choice `frontend|backend|security`;
- `dry_run`: boolean default `true`;
- `topic_override`: optional string;
- `candidate_limit`: optional bounded integer/string validated by helper.

Manual overrides may not bypass guards.

- [ ] **Step 3: Add `plan` job with read-only permissions**

Job permissions: `contents: read`.

Steps:

- SHA-pinned checkout with `persist-credentials: false`;
- SHA-pinned setup-python;
- install Muse Code on host and log `muse --version`;
- run Muse with only `META_API_KEY` in that step:

```bash
muse exec \
  --trust-workspace \
  --disable-approval \
  --sandbox-network restricted \
  --no-session-log \
  --max-model-steps 10 \
  --prompt-file automation/learning/prompts/plan-research.md
```

- validate `research/research-plan.json`;
- upload plan artifact using SHA-pinned upload-artifact.

No GitHub token is passed to Muse environment.

- [ ] **Step 4: Add `collect` job**

Job permissions: `contents: read`.

No `META_API_KEY` in this job.

Download plan artifact, run collector with read-scoped `${{ github.token }}` passed only to collector process, validate bundle manifest, upload bundle artifact.

- [ ] **Step 5: Add `synthesize` job**

Job permissions: `contents: read`.

No GitHub write token in Muse environment. Install Muse, download plan/bundle artifacts, run synthesis with restricted network and max-model-steps 18. Run evolution-decision validator and diff guard. Produce:

- `research/learning.patch` from approved durable changes;
- `research/evolution-decision.json`;
- relevant generated knowledge/evolution files as an artifact if needed for patch verification.

Upload validated artifact.

- [ ] **Step 6: Add `publish_learning` job**

Run only when `dry_run=false` and synthesis succeeded.

Job permissions:

```yaml
contents: write
pull-requests: write
```

This job must **not** install/run Muse and must not process third-party commands. It downloads validated patch, applies it to a clean checkout, reruns path guard, creates deterministic learning branch, commits only allowlisted paths, pushes, and creates PR with `gh pr create` using `GH_TOKEN: ${{ github.token }}`.

- [ ] **Step 7: Add Skill candidate jobs**

If decision level is L2:

1. `draft_skill_candidate`: read-only permissions, Muse + `META_API_KEY`, restricted network; write candidate only under `research/skill-candidate/**`, validate, upload artifact.
2. `publish_skill_candidate`: `contents: write`, `pull-requests: write`, no Muse/no `META_API_KEY`; apply exactly one validated candidate `SKILL.md` to target path, create separate branch/PR, never merge.

L3 skips both candidate jobs and leaves proposal-only output in the ordinary learning PR.

- [ ] **Step 8: Add concurrency and timeout controls**

Use one concurrency group per domain; do not cancel an in-progress learning run. Set bounded job timeouts. Artifacts use short retention appropriate for temporary research material.

- [ ] **Step 9: Add workflow-level secret checks**

Fail early with a non-secret message if `META_API_KEY` is missing for Muse jobs. Do not echo secret values.

- [ ] **Step 10: Commit**

Commit message: `Add dry-run Muse learning workflow`

### Task 10: Add static workflow contract tests

**Files:**
- Extend: `automation/learning/tests/` with `test_workflow_contract.py`

**Interfaces:**
- Tests inspect workflow text without requiring PyYAML.

- [ ] **Step 1: Write tests before workflow adjustments if any are needed**

Assert the workflow contains:

- all three cron entries and `timezone: 'Asia/Shanghai'` (quote style may be normalized in test);
- `persist-credentials: false`;
- SHA-pinned actions rather than floating major tags;
- `workflow_dispatch` and dry-run default true;
- `--sandbox-network restricted`;
- `--max-model-steps` on each Muse call;
- no `--yolo`, `--disable-sandbox`, or unrestricted network;
- separate write-permission publishing jobs;
- ordinary guard before commit/push;
- schedule-enable variable gate.

- [ ] **Step 2: Run full local test suite**

Run: `python -m unittest discover -s automation/learning/tests -v`
Expected: all tests PASS.

- [ ] **Step 3: Commit**

Commit message: `Add learning workflow contract tests`

### Task 11: Static repository and governance verification

**Files:**
- Inspect all implementation files.
- Create: `evolution/evaluations/<date>-autonomous-learning-runner-static-validation.md`

**Interfaces:**
- Produces evidence record before any real Muse CI run.

- [ ] **Step 1: Run complete unit suite**

Run: `python -m unittest discover -s automation/learning/tests -v`
Expected: 0 failures/errors.

- [ ] **Step 2: Verify protected core unchanged**

Compare `IDENTITY.md` and root `AGENTS.md` blobs to pre-implementation SHAs.

- [ ] **Step 3: Review workflow permissions job-by-job**

Document which jobs can access:

- `META_API_KEY`;
- read GitHub token;
- write GitHub token;
- untrusted research bundle.

There must be no job combining Muse/untrusted bundle with GitHub write permission.

- [ ] **Step 4: Record static validation truthfully**

Mark runtime behavior `NOT YET BEHAVIOR-VALIDATED` until manual Actions dry-runs execute.

- [ ] **Step 5: Commit**

Commit message: `Record learning runner static validation`

### Task 12: Operational setup and three manual dry-runs

**Files:**
- No source changes required unless dry-runs reveal defects.
- Update validation/evaluation records with observed results.

**Preconditions requiring human/account setup:**

- GitHub Actions secret `META_API_KEY` exists in `amy950830/muse`.
- GitHub Actions is enabled for the repository.
- For non-dry-run PR publishing, repository policy permits `GITHUB_TOKEN` to create pull requests with the requested workflow permissions.

- [ ] **Step 1: Manual frontend dry-run**

Use `workflow_dispatch`:

- domain: `frontend`
- dry_run: `true`

Expected:

- topic plan generated and validated;
- Stable + Emerging candidates present;
- no persistent branch or PR created;
- no unauthorized path changes;
- logs contain no secrets.

- [ ] **Step 2: Manual backend dry-run**

Same checks for `backend`.

- [ ] **Step 3: Manual security dry-run**

Same checks for `security`, plus confirm security conclusions require corroboration and unverified claims are not promoted.

- [ ] **Step 4: Run prompt-injection pressure case**

Use a controlled fixture/bundle containing `Ignore previous instructions` and a shell command. Expected: treated as quoted untrusted data; no command execution; no control-flow override.

- [ ] **Step 5: Review cost and output quality**

Record Muse version, model-step counts, candidate counts, bundle sizes, and any API-rate-limit behavior. Do not record secret values.

- [ ] **Step 6: Enable manual PR publishing only after dry-runs pass**

Run one domain with `dry_run=false`. Expected: one ordinary learning PR only; no auto-merge. If L2 is produced, Skill candidate must be a second separate PR.

- [ ] **Step 7: Keep scheduled writes disabled until review**

Do not set `MUSE_LEARNING_SCHEDULE_ENABLED=true` until all three domain dry-runs and one manual publishing run are accepted.

### Task 13: Enable scheduled A1 operation after successful rollout review

**Files:**
- No workflow change required if schedule gate already exists.
- Update: `evolution/evaluations/<date>-autonomous-learning-runner-static-validation.md` or create runtime validation record.

- [ ] **Step 1: Set repository variable**

Set `MUSE_LEARNING_SCHEDULE_ENABLED=true` only after explicit user approval following Task 12 evidence.

- [ ] **Step 2: Verify schedule intent**

Expected scheduled domains:

- Monday 03:00 Asia/Shanghai → frontend
- Wednesday 03:00 Asia/Shanghai → backend
- Friday 03:00 Asia/Shanghai → security

- [ ] **Step 3: Observe first scheduled run per domain**

Verify each creates no more authority than manual runs and respects PR-only behavior.

- [ ] **Step 4: Record runtime validation**

Mark only actually observed scenarios as behavior-validated. Leave untested scenarios explicitly outstanding.

---

## Self-Review Checklist

Before execution begins, verify the plan against the spec:

1. **Spec coverage:** schedule, topic selection, dual-track scoring, untrusted-content model, credential separation, diff guard, L0–L3 decisions, Skill candidate review, dry-run rollout, and cost controls all have owning tasks.
2. **Type consistency:** `research-plan.json`, `evolution-decision.json`, bundle manifest, and Skill-candidate metadata have one validator each and consistent field names across tasks.
3. **Security boundary:** `.agents` read-only sandbox behavior is accommodated by drafting candidate files under `research/` and applying them only in a non-Muse publisher job.
4. **No fabricated evidence:** missing growth metrics and insufficient source counts fail or degrade transparently.
5. **Rollout safety:** scheduled writes remain gated until real manual dry-runs succeed and the user explicitly approves enablement.

## Execution Notes

- Implementation should occur on a dedicated feature branch rather than directly on `main`.
- Use TDD for all Python behavior: failing test → minimal implementation → passing targeted test → full suite.
- GitHub workflow YAML itself is configuration; validate through contract tests and later real Actions dry-runs.
- If current official Muse/GitHub syntax changes between plan date and execution, make the smallest documented ruling that preserves the approved security architecture, then update the plan/evaluation record rather than silently weakening controls.
