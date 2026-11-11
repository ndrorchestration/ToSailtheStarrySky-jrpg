# First Wake native review-camera rotation — v0.1 repair and visual QA hold

**Date:** 2026-11-11
**Scope:** Unreal 5.8.4 review-only shoreline staging; draft branch stacked on PR #799.
**Authority:** SOURCE REPAIR ONLY. No gameplay, creator art, canonical, or protected-main approval.

## Observed failure and root cause

At the historical, separately native-verified scene commit `b5ef5a0a6251ed43af32dea559a5a5345baab2fd`, an independent fresh-Editor map inspection measured the saved overview camera at **(-5300,-6200,2850) cm**, but **pitch +45°, yaw 0°, roll -18°**. Intended shot: **pitch -18°, yaw +45°, roll 0°**.

The old source passed `unreal.Rotator(-18, 45, 0)` to the Unreal **Python** constructor, whose positional signature is **(roll, pitch, yaw)**. This differs from C++ `FRotator(InPitch, InYaw, InRoll)`. The correction uses **named Python fields**, `unreal.Rotator(roll=0.0, pitch=-18.0, yaw=45.0)`, then *reads back and refuses* any mismatch. Source tests prevent regression to the positional form.

Reference: Epic [Unreal Python Rotator](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/Rotator?application_version=5.6) and [Unreal C++ TRotator](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Core/TRotator/__ctor).

## Native reproduction and controlled correction

- Historical composited shore map: `/Game/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review`, SHA-256 `fec410d08244ec5ac71965af2df98434411591aa8a280dfefe8ea038ae50357f`; **preserved**, with its 222-file content-addressed manifest unchanged.
- Isolated Neontic worktree: `C:\TSTSS_VisualAudit_20261111`, detached at `b5ef5a0...`.
- Disposable corrected map **only in that isolated review checkout**: `/Game/TSTSS/Review/VisualAudit/L_VS06_CameraCorrected_Review`, SHA-256 `5b27050cbe59953497c37a21ebacd05746691f7698bbd84e3c76a4269d87fd2f`. An independent UE 5.8.4 Editor reopen confirmed 43 total actors, 26 review actors, camera at expected position and rotation, all expected actor classes, and unaltered original map/configuration hashes. The corrected copy has **not** been committed, promoted to gameplay, or visually approved.

The historic, content-addressed snapshot `Docs/Evidence/firstwake_multipath_native_scene_snapshot_20261111.json` and its verifier are **not to be silently overwritten**. A future corrected native 3D package needs its own distinct review namespace, exact-head rebuild/readback, immutable provenance record, and creator assessment before any route or asset change.

## GPU visual QA: independent outstanding blocker

| Native D3D12 diagnostic | Result | Meaning |
|---|---|---|
| Original camera + AutomationLibrary 1280×720 | 100% white | No useful visual acceptance |
| Original camera + offscreen SceneCapture2D 1280×720 | 100% white | No useful visual acceptance |
| Corrected camera + explicitly positioned SceneCapture2D | 100% white | Incorrect camera orientation **was not the only fault** |
| Transient large Engine cube at corrected camera, BaseColor | 21 unique RGB values, visible mesh | Actual GPU scene geometry capture functions |
| Same cube, FinalColor LDR | 277 unique RGB values, 72.792% near white | Severe bright final-color rendering |
| **Actual native basalt-cliff closeup**, BaseColor | 24 unique RGB values, geometry visible | Review environment geometry genuinely renders |
| Same actual cliff, manual-exposure FinalColor LDR (bias -4) | 616 unique RGB values, **89.405% near white** | Postprocessing/lighting still unsuitable, despite native image output |

All native GPU checks were disposable and source-locked; test meshes and temporary capture actors were never saved. Diagnostic PNGs, native logs, and checksummed host reports remain under the isolated checkout's ignored `unreal/Saved/VisualAudit/GPUReview/`. The cliff screenshot is not a cinematic-quality or approved environment.

**Next bounded actions:** verify scene lights/sky/fog and postprocess contributions in native Editor; use controlled exposure and close foreground geometry; compare genuine Lit images against BaseColor and source/cinematic framing; then independent PIE gameplay and First Wake story progression. Do not confuse pixel diversity with artistic quality. If review content cannot be rendered with exposure and intentional framing, hold approval.

## Story and governance

Ender + Ionia are the pre-splashdown party; Lyra is recruitable only after splashdown. Three review enemy silhouettes, nine Ender cue actors, and static equipment props in this map grant no inventory, class progress, spells, or encounter victories. Reson and Aepex are not available here. Starbourne remains locked. Nothing in this source repair authorizes merge, artistic promotion, game production release, or scientific/governance-state changes.
