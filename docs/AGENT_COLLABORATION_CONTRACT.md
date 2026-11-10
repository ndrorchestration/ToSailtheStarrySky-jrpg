# To Sail the Starry Sky — ChatGPT / Hermes collaboration contract

**Status (2026-10-24):** manual GitHub issue/PR handoff protocol demonstrated through a full bounded pilot and correction cycle. Read-only handshake #351 is complete; tests-only AW-HERMES-002 produced draft PR #354 and its requested symlink hardening, current head `7fe36dba04188b8909784e18a2d25df533dec283`, with source-review hold satisfied but no merge authorization. ChatGPT-authored stacked draft PR #357 (`f1d949e131da4d7c44b5f94ad9be81004eb91247`) adds the test to smoke CI; independent Hermes peer review remains assigned as AW-HERMES-003 on #356. Read-only native-prerequisite probe #355 is AW-HERMES-004 and remains unclaimed. **Owner:** creator. **Canonical repository:** `ndrorchestration/ToSailtheStarrySky-jrpg`, public, stable repository ID `1372641872`. **Source of truth:** current `main` plus `docs/DEVELOPMENT.md`; Notion Operational Control Center for decision context. This protocol is not authorization to run, merge, deploy, release, expose secrets, change canon, or override established acceptance gates.

## 1. What is connected — and what is not

GitHub issues and reviewable draft pull requests serve as a durable handoff record. A matching capability receipt for challenge `AETHERWAKE-HERMES-20261023-01` is visible in [issue #351](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/351), and the first tests-only claim is visible in [issue #353](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/353). Both comments were posted using the owner's GitHub account; they establish observable GitHub communication, **not independent proof of Hermes' host identity, installed tooling, or authenticated execution**. A pasted chat message and a GitHub claim likewise do not prove a live subscriber or automatically trigger an agent. `GITHUB_HANDSHAKE=OBSERVED`, `HERMES_RUNTIME_ATTESTATION=UNVERIFIED`, `AUTOMATED_DISPATCH=NOT_CONFIGURED`.

The Zeta-Pell Autonomous Lattice ([separate research repository](https://github.com/ndrorchestration/AHG-Zeta-Pell-Autonomous-Lattice)) is experimental. Its PID/Kalman/Pell simulations and historic benchmark claims are **not** game-build attestation, runtime agent coordination, a production scheduler, or authorizing governance. A possible future adapter needs a separate reviewed design and empirical admission test; no such adapter is established by this collaboration contract.

## 2. Hard boundaries

- `main` is the authoritative game source and **must be treated as protected by policy**. GitHub's branch metadata inspected 2026-10-23 reports `protected: false`; do **not** assume a server-side protection rule currently enforces reviews or blocks direct pushes. Until GitHub branch rules are independently confirmed/enabled, all agents must refrain from direct `main` writes or merges. `dev/progression-build` is historical, not automatically an up-to-date executable game. Reconcile Hermes' local checkout to the exact source SHA **before** making a patch.
- **First priority** is playable First Wake / Chapter I Preview 0.1 and its honest Windows installation, save/close/relaunch/Continue, native scene evidence, first-frame readiness and uncoached human acceptance. Do not divert the release lane with new world/globe features.
- The native Godot Chapter I track and the isolated cinematic/planetary globe experiment are different product/evidence scopes; scripts, manifests, source SHA and renderer tests do not cross-certify.
- No agent may modify game saves, migration contracts, game canon, character art approvals, CI protection, desktop deploy copies, published installers, credentials, or production configuration without separate explicit creator approval and verified relevant tests.
- Canonical authored cast: Ender, Lyra, Ionia, Reson and Aepex. Any unresolved action, combat authority, reveal, or likeness must remain unresolved rather than invented.
- Protect the existing `docs/PREVIEW_0_1_ACCEPTANCE.md` exact-candidate binding and any later authoritative verified supersession. Do not automatically declare player acceptance based on a smoke test, simulated render, or agent summary.
- No writing to the Zeta-Pell research repo is required for Aetherwake task routing.

## 3. Responsibility split

| Participant | Provisional responsibility | Not permitted by this document |
| --- | --- | --- |
| Creator | Goals, final canon/art decisions, permission grants, release acceptance | Delegation does not itself prove QA passed |
| ChatGPT | Decompose tasks, reconcile Notion and GitHub authority, write bounded issue specs, independently review evidence and draft PRs where possible | Cannot attest it operated the Hermes host or measured a real GPU without evidence |
| Hermes (only once connected/authorized) | Read assigned issues, claim a distinct branch, make scoped changes, run actually available tools, post reproducible evidence and a draft PR | Cannot merge, release, promote canon, access secrets or change save formats |
| GitHub | Issues as mailbox; source history/PRs/CI as immutable links with commit/hash context | Issue comment alone is not agent identity attestation |
| Notion | Decisions, acceptance gates, links and ongoing context | Not an executable code or test authority |

## 4. Handoff protocol (one task, one writer)

1. Create or reuse one issue for one bounded objective. Include `task_id`, exact repository/base SHA, branch owner, allowed files, forbidden files, verification commands, evidence outputs, rollback strategy and checkable definition of done. Do **not** assign or launch an agent merely because the issue exists.
2. Confirm receipt. The actual Hermes instance posts `RECEIVED` with issue number and an **observed** local checkout SHA/branch, tool availability and declared blockers. An unverified pasted message is a useful hint, **not** this GitHub receipt.
3. Post a claim: `CLAIMED by Hermes; branch=agent/hermes/<issue>-<slug>; base_sha=<sha>` or `CLAIMED by ChatGPT; branch=agent/chatgpt/<issue>-<slug>; base_sha=<sha>`. Claims are advisory, **not atomic locks**. Conflicting writers stop and coordinate.
4. Implement on a *distinct* branch, ideally from current `main`, with the minimal necessary files. The owner posts commits, commands, executed test results and any screenshot/log hashes. Avoid edits to deploy copies or source-of-truth docs without explicit scope.
5. Open a **draft** pull request. Reviewer independently inspects diff/base/head SHA, tests and the evidence's provenance, checks the issue's exclusions and surfaces unknowns. Use `TESTED` only for commands actually run on stated platform/commit. Separate `STATIC_PASS`, `SYNTHETIC_PASS`, `NATIVE_PASS`, `ART_REVIEW`, `PLAYER_ACCEPTANCE` and `RELEASE_APPROVAL` — no implied promotion.
6. Await creator/reviewer authority for merge/release. If a task is blocked, record `BLOCKED` plus exact missing capability instead of publishing substitute evidence.
7. Record resolution in the existing Aetherwake Notion Operational Control Center with issue/PR links; do not duplicate the canon or release tracker.

**Suggested task states:** `PROPOSED → ASSIGNED → RECEIVED → CLAIMED → IMPLEMENTED → TESTED → REVIEWED → ACCEPTED`, with `BLOCKED` and `CANCELED` as explicit branches. State advancement requires an issue/PR comment recording owner and observed evidence. This is a human-readable workflow, not an installed state machine.

## 5. Minimum verifiable receipt

```yaml
task_id: AW-HERMES-<issue>
actor: Hermes # a self-reported label, not proof of identity
transport: GitHub issue comment
source_repository: ndrorchestration/ToSailtheStarrySky-jrpg
observed_branch: <branch>
observed_head_sha: <full sha>
work_branch: <branch-or-none>
files_changed: [] # read-only handshake: empty
operations_executed: [] # list exact commands that actually ran
test_results: [] # command, platform, exit code and evidence location
artifacts: [] # exact filenames and sha256, when applicable
not_run: [] # e.g. native Godot 4.7.2, actual Windows install
blockers: []
requested_next_action: <review | permission | clarification | none>
status: OBSERVED # otherwise PARTIAL or BLOCKED
```

Avoid posting API tokens, SSH material, environment dumps, personal machine metadata, credentials or private user data. Minimize log content and sanitize artifact paths. Recheck all claims against the remote repository where possible.

## 6. Current baseline / first handshake

- As inspected through GitHub on 2026-10-23: `main=7364d43c202b2186e2d4eb3c752367afe61ee408`.
- A user-provided Hermes handoff states `dev/progression-build=46b4d73e699fdc4d4c02408753b25c4c06408505`, `npm run test:all` passing, and deploy/build intentionally unsynced. That commit exists, **but those local tests and permissions were not independently observed**. Current `main`'s `package.json` does not define `test:all`. The branch history is divergent; do **not** merge the historical branch or treat its test report as current-main verification.
- The read-only challenge [#351](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/351) received a matching owner-account Hermes-style reply. It reports a local historical checkout at `65a42f43eb8a27d35093b6c6c8effb31a0f4cc07` with untracked `cache/`, and an `origin/main` SHA matching live GitHub. Node, Git, Python, Playwright and missing Godot are **reported observations**, not independently witnessed host checks.
- First scoped write exercise [#353](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/353) (`AW-HERMES-002`) is complete at bounded source-review level. Hermes-style work produced draft PR #354; the first head exposed a top-level symlink gap, the same branch was corrected, and exact head `7fe36dba04188b8909784e18a2d25df533dec283` now closes that source-review defect. Hermes-reported Windows Node checks are evidence from that agent, not independently rerun Windows proof. PR #354 remains draft/unmerged.
- Reciprocal CI trial [#356](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/356) is `AW-HERMES-003`: read-only Hermes review of stacked ChatGPT draft PR #357. It is a review task, not an automatic dispatch or merge gate.
- Native prerequisite probe [#355](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/355) is `AW-HERMES-004`: read-only check for trusted Godot 4.7.2 and the exact v0.7.5 prototype ZIP on an authorized Windows host. It does not authorize extraction or execution.

## 7. Cross-repository coordination and future automation gate

- **To Sail the Starry Sky queue:** #351 is the completed read-only handshake; #353/AW-HERMES-002 is the completed bounded tests-only pilot with draft PR #354; #356/AW-HERMES-003 is the reciprocal read-only review queue for PR #357; #355/AW-HERMES-004 is the read-only native-prerequisite probe. Use this repository's issues and **draft** PRs for implementation.
- **AHG/Zeta-Pell research queue:** [AHG issue #6](https://github.com/ndrorchestration/AHG-Zeta-Pell-Autonomous-Lattice/issues/6) is the active Hermes ↔ ChatGPT coordination record for AHG research. [AHG issue #7](https://github.com/ndrorchestration/AHG-Zeta-Pell-Autonomous-Lattice/issues/7) is closed and reference-only. They are **not** alternate Aetherwake assignment channels. Shared process vocabulary does not transfer scientific evidence or execution authority across repositories.
- **Recommended issue comment tokens:** `HANDOFF/ASSIGN`, `HANDOFF/CLAIM`, `HANDOFF/RESULT`, `HANDOFF/REVIEW`, `HANDOFF/BLOCKED`. A task comment cannot spawn Hermes unless an external, explicitly authorized agent actually reads it.
- **Manual activation:** For new, unclaimed tasks, the user can invoke their configured Hermes session with the issue URL; if using [Nous Research Hermes Agent](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron), an explicitly authorized one-shot scheduler can be considered. Completed/claimed task IDs must never be reused. The assignment/claim comments alone do **not** demonstrate task execution or provide automatic agent delivery.
- **Hermes native scheduling is a capability, not a verified connection:** The documented `hermes cron create` command supports one-shot and recurring jobs, and Hermes documents event-triggered cron. This repo has **not** demonstrated any installed cron entry, a running Hermes gateway, authenticated notification receiver, webhook, or automatic GitHub-to-agent delivery. Do not represent it as an operational ChatGPT↔Hermes bridge.
- **No unattended bridge confirmed:** Before automatic GitHub→Hermes→ChatGPT dispatch is advertised or enabled, verify authenticated least-privilege agent invocation, GitHub webhook-signature checking, idempotency/replay prevention, exact task/repository allowlisting, source-SHA checks, secrets isolation, event/receipt logging, user stop controls and a witnessed end-to-end dry run. Do not create a public unauthenticated agent endpoint, poll continuously without permission, or let a scheduler merge/release.
- **Platform policy:** [Aetherwake issue #303](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/303) already owns the private-repo `main` branch-protection governance gap. GitHub returned `protected=false`; `GET /rulesets` returned a plan-access 403, not proof of active protection. Do not create a duplicate control-policy issue; do not make the private repo public to access branch rules. Until enforcement is independently demonstrated, manual no-direct-main-write holds remain mandatory.

## 8. Revocation and recovery

Creator can revoke an agent's repository permissions or pause tasks at any time. On ambiguous commands, missing rights, unexpected dirty working tree, changed source SHA, conflicting claim, test failures or potentially sensitive data, agents **stop**, report an exact blocker and leave release/merge untouched. Work remains reviewable in draft PRs, not a hidden local edit.


## 9. Repository rename and public-source boundary

- Canonical repository is now `ndrorchestration/ToSailtheStarrySky-jrpg`, stable GitHub repository ID `1372641872`, visibility **PUBLIC**. The legacy `aetherwake-jrpg` slug redirects to the same repository.
- Public source visibility does **not** grant release, merge, deploy, package, canon or secret-disclosure authority.
- Historical task IDs, receipt labels, artifact filenames and immutable evidence may retain `AETHERWAKE`/Aetherwake wording. Do not rewrite hashes or historical evidence for branding consistency.
- Active issue/PR/document links should use the canonical current slug when practical; legacy URLs may be retained when they are themselves part of historical evidence.
- Public exposure adds a separate hygiene responsibility: secrets, licensed assets, unpublished spoilers, releases, Pages, webhooks and repository security settings require review. That responsibility does not replace the existing Windows/native, Defender, CI and human-acceptance gates.
