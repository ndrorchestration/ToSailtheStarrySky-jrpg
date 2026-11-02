# Unreal production verification matrix — 2026-10-31

> **Evidence reconciliation — November 1, 2026.** The initial "no native build" hold below is historical, not universally current. [#685](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/685) independently demonstrated Game+Editor UBT and **23/23** NullRHI automation checks at exact head `813abdce`. [#704](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/704) adds a **24th** required native test; Game-target compiler/link proof exists at C++ ancestor `0a6160b4`, but Editor 24-test JSON and PIE remain held. The directly launched uncooked Windows executable logged a premade asset-registry/BufferReader **crash**, so runtime/packaging is explicitly **FAIL / NOT VERIFIED**; it does not negate Game target compilation proof. No D3D12 artistic acceptance or player-facing First Wake exists at those exact heads. See [current dependency/evidence register](DEPENDENCY_AND_EVIDENCE_REGISTER_2026-11-01.md) and maintain the separate branch-specific gates below.

### Historical matrix (2026-10-31)

The original planning contract follows; interpret it at its authored date.


Status: workflow contract, not executed evidence. Applies to draft PR #608; Godot is unchanged. Creator-approved story/art authority takes priority over historical engine assumptions.

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
