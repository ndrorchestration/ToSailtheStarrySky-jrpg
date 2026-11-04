# Unreal production verification matrix — updated November 2, 2026

**SUPERSEDING NATIVE VERIFICATION RECEIPT — 2026-11-02 (exact SHA `e3e3ff5f349c98b2051a18a5f0c3db6097af8040`):** On an authorized Windows `neontic` workstation, an **isolated detached PR #713 checkout** with its two tracked default INI files protected by read-only attributes passed the **Unreal Engine 5.8.4 Win64 Editor UBT build AND all 25 named native automations**, with zero failed, zero not-run and **a clean tracked source tree after testing**. Full `Verify-Unreal.ps1` exited 0. An independent readback found **25 distinct Success records / 25 unique paths / 0 non-success**. Original engine-generated config-write failure from the first unprotected checkout remains a separate preserved diagnostic, not overwritten or ignored. Report SHA-256: `243ad1eedaa344cd52dd4a3380e59cbef34fcfcd3e39c61cc1307195921733a5` (raw report local to the disposable review machine; never upload generated Android File Server tokens). **Evidence status at that exact SHA: `EDITOR_BUILD=PASS`; `NATIVE_25=PASS`; `SOURCE_CUSTODY=CLEAN`; `PIE_P01_P13=NOT_TESTED`; `PRODUCTION_ART=NOT_AUTHORIZED`; `RELEASE=NOT_AUTHORIZED`.** This is *not* an acceptance of actual 13-scenario keyboard gameplay, sea contact/flotation, Splashdown, D3D12 art, packaged install or release. **A subsequent documentation-only SHA cannot inherit the exact-head receipt without its own verification.** See [integrated review gate](INTEGRATION_GATE_2026-11-02.md), [native command and evidence rules](UNREAL_TEST_COMMANDS.md), and [PR #713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713).


**Current November 2 cross-discipline handoff (integrated [draft #713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713)):** This document's older #712 and #685 SHAs are historical, not the active test result. The authorized Windows `neontic` workstation is **online** and its installed `UE_5.8/Engine/Build/Build.version` reports **5.8.4**, with MSVC 14.44 and Windows SDK 10.0.26100. An isolated detached checkout at `fd0b68c28e6289d45f8b8c70228631c24577a352` **passed native Win64 Editor compilation**. A subsequent native Editor automation report contained **25 distinct Success entries / 0 failed / 0 not run**, but the strict post-run clean-tree gate **FAILED**, because Unreal rewrote tracked `DefaultEngine.ini` and `DefaultInput.ini` in that isolated worktree. The first file gained generated Android File Server settings including a local token. **Do not stage, publish or copy any generated token or config diff into documentation or a PR. Do not reset the worktree without reviewing its forensic state.** Native 25/25 acceptance is **HOLD — CONFIG_MUTATION**, despite successful test entries; P01–P13 interactive PIE remains **NOT TESTED**. The log/report evidence is local to the isolated worktree's non-overwriting `unreal/Saved/MigrationEvidence/` path; source SHA and outcome are separated from the now-moving review PR HEAD. **Never infer a newer documentation head has the same native receipt.** See [integrated review gate](INTEGRATION_GATE_2026-11-02.md), [save-safety notes](FIRST_WAKE_REVIEW_OBJECTIVES_2026-11-02.md) and [native test commands](UNREAL_TEST_COMMANDS.md).

**Applies to the Unreal-first draft development workstream**, not to a
merged, shipping or creator-approved game. This matrix began under #608.
It now also links the stacked #694 → #703 → #704 → #712 First Wake review
sequence and retains the historical Godot/browser evidence as separate.
Creator-approved story and visuals retain authority over generated art.

**Source-scoped evidence:** #685 actually passed Win64 Game/Editor and
23/23 native automations at its own head. At inspected #712 commit
`a1b07b64841c2cb6b735fdd66f2ecd6426cab016`, CI/source work
passed but the current 25 required automation names were **registered,
not run in UE**, and P01–P13 PIE remained **NOT TESTED**. This matrix
itself is not a native verification receipt.


## Quality gates by discipline

| Discipline | Lowest-cost check | Native acceptance evidence | Stop condition |
|---|---|---|---|
| Build/engineering | UHT + Win64 editor compile, exact commit | build log, compiler result, engine version | any unresolved compiler/UHT failure |
| Gameplay design | isolated story and combat rule automation | PIE continuous First Wake traversal, objective visibility, uncoached playtest | softlock, incorrect Ionia-first order, invented magic |
| Physics | collision/inspection/save regression tests | source-bound hull-water overlap, velocity, flotation logs, wave/impact captures | an interaction/caption can award contact; false waterline |
| Cinematic art | manifest against approved cast and ship reference | Unreal engine screenshots/video, light/camera/rig/occlusion review | placeholders presented as approved; wrong face/hair/ship identity |
| UX/accessibility | focus and caption/contrast check | keyboard/gamepad + muted/reduced-motion native walkthrough | audio-only clue or blocking interaction |
| Performance | scripted representative camera journey | Unreal Insights CPU/GPU/memory trace at specified Windows hardware, resolution, RHI | regressions without measured budgets |
| Delivery/security | binary hash, manifest, save replay | fresh Win64 install, launch, checkpoint, uninstall, Defender-on custody | no verified installer provenance or regression |

## Sequence and parallel workstreams

1. **Integration lane (critical path):** clean checkout -> UHT/editor build -> fixed named tests -> PIE vertical slice -> packaged runtime checks. Block further feature expansion on unresolved compile failures.
2. **Rendering lane:** prepare approved reference manifest, correct silhouettes, proportions, lighting values, materials, Nanite/LOD decisions and cinematic camera boards; integrate only after provenance and side-by-side creator review.
3. **Narrative/systems lane:** Godot #547 physics/checkpoints and #548 family/melody are *source contracts*, not merged Unreal features. Apply canon order Ender -> Ionia -> Lyra, then Reson and Aepex. A narrative affinity is not a battle spell.
4. **Physics lane:** keep current approximation disabled by default. Implement real sampled water height, displacement, damping, roll/pitch response, collision continuity and genuine hull geometry; run fixed-step comparisons before promoting.
5. **Release lane:** adapt native Windows install checks from Godot #551 only after a native packaged Unreal executable exists. Release is separate from engine compilation and art signoff.

Each lane must produce a reviewable artifact on a named branch, with source SHA, changes, positive and negative tests, observations and remaining open risks. Avoid multiple agents racing writes to one file or silently merging independent proofs.

## Expert-production references

- [Epic UE5.8 Automation Test Framework](https://dev.epicgames.com/documentation/en-us/unreal-engine/automation-test-framework-in-unreal-engine): distinguish unit, feature, content stress and screenshot comparison; tests must be independent and leave filesystem state clean.
- [Epic UE5.8 Performance Profiling](https://dev.epicgames.com/documentation/unreal-engine/introduction-to-performance-profiling-and-configuration-in-unreal-engine): measure frame time, CPU, GPU and memory on representative target hardware with Unreal Insights; account for profiler overhead.
- [Epic UE5.8 Continuous Integration](https://dev.epicgames.com/documentation/en-us/unreal-engine/continuous-integration-ci): continuously validate changes rather than accumulate uncompiled development.

## Immediate critical issue

At authoring time no actual Unreal editor build, PIE capture, true ship buoyancy validation, Unreal-approved 3D cast, or verified Windows installer is available in this thread. Do not promote source availability, automation test names or this matrix as a native PASS.

## Reconciled November 2 gate ledger (do not infer passes)

| Gate | Valid evidence | Current #712 status |
|---|---|---|
| Engine and native module declarations | `.uproject`, both V7/UE5.8 targets, `Build.cs`, source contract | SOURCE-INVENTORIED; packaged role unverified |
| Hosted source inventory and regression | GitHub workflow completion at exact head | PASS at `a1b07b64841c2cb6b735fdd66f2ecd6426cab016`; rerun on future heads |
| Objective/read-only and PIE slot handlers | 16 + 12 source-extracted C++ behavior checks using stand-ins, mutation controls | PASS at above head; **not native engine results** |
| Win64 Editor native build | UHT/UBT log and SHA-bound, clean-tree receipt | NOT TESTED at #712 |
| Native automation | `Verify-Unreal.ps1` JSON with 25 unique exact successful named tests | NOT TESTED at #712 |
| V2 Prelude player operation | P01–P13, direct PIE input and screen/log evidence | NOT TESTED |
| Source-bound sea landing/Chapter 1 | genuine physics and flotation evidence, no marker bypass | NOT AUTHORIZED |
| D3D12 visual cast/ship approval | source-asset manifests and creator signoff | NOT AUTHORIZED |
| Windows packaged runtime/release | cooked installed launch, hashes, Defender-on and save replay | NOT TESTED |

**Dependencies and controls:** [First Wake dependency handoff](FIRST_WAKE_DEPENDENCY_HANDOFF_2026-11-02.md)
tracks this branch's `5.8` association, Editor Python plugin,
native modules, legacy npm separation, and the other draft register
[#711](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/711).
Do not copy #711's baseline without comparing manifests at the exact
merge candidate SHA. Nothing in this matrix authorizes upgrades or imports.
