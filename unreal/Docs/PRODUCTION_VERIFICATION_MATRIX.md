# Unreal production verification matrix — updated November 2, 2026

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
