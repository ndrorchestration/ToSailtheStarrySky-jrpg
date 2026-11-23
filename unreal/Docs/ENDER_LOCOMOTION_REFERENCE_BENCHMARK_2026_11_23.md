# Ender movement quality: reference benchmark and reuse plan (2026-11-23)

**Status:** technical measurement plan, not a completed equivalence/ranking against a shipped game. **Authority:** private draft PR #890, exact source SHA `1e25dbb45ed390bbd643c9a11c03efefdd738144` at the time of the review. Future validation must pin its own exact HEAD and protect 25 review assets. No merge, release, default gameplay switch or new license is authorized.

## Answer to the design question

Yes, a shipped JRPG or a properly licensed engineering sample can provide a locomotion **reference**; a public gameplay clip is not an animation asset you can import or extract by default. Keep the three categories separate:

1. **Mechanical scaffold:** Epic's free official [Game Animation Sample Project for UE 5.8](https://www.unrealengine.com/tech-blog/download-the-latest-game-animation-sample-project-now-updated-for-ue-5-8) (updated August 12, 2026), [official documentation](https://dev.epicgames.com/documentation/en-us/unreal-engine/game-animation-sample-project-in-unreal-engine), [Fab listing](https://www.fab.com/listings/880e319a-a59e-4ed2-b268-b32dac7fa016), and existing Unreal 5.8 mannequin template assets already staged locally. The project covers motion matching, transition starts/stops and pivots, stride/pose warping, interaction, and slopes. Components/animations can be evaluated for lawful reuse inside Unreal, but require proper license review and actual retarget + QA.
2. **Animation engineering reference:** [Epic Lyra: locomotion blending and distance/stride/orientation warping](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-in-lyra-sample-game-in-unreal-engine) and [Epic's forward-facing Lyra adaptation](https://www.unrealengine.com/tech-blog/adapting-lyra-animation-to-your-ue5-game). Reuse the process of diagnosing acceleration/pivots/stop timing and slide. Do NOT copy a combat-aiming shooter posture or an incompatible root-motion policy into a JRPG engineer.
3. **Creative motion reference only:** [Final Fantasy VII Rebirth](https://www.youtube.com/watch?v=GL33pUIwZ5U) for readable cinematic third-person momentum and camera/character relationship; [Tales of Arise](https://www.bandainamcoent.com/games/tales-of-arise) for stylized JRPG movement silhouettes. Public footage is for observation; its commercial animations and control systems are not a source of transferable animation files or code.

## Existing work means we should NOT start over

The project's historical [private retarget provenance](Ender_Private_Retarget_Implementation_2026_11_17.md) records five SHA-checked **official Unreal 5.8 mannequin template assets** staged in review-only Git-excluded paths: Manny mesh, mannequin skeleton, `MM_Idle`, `MF_Unarmed_Walk_Fwd`, `MF_Unarmed_Jog_Fwd`. Their source package is an Unreal template, **not established to be the full GASP distribution**. The present 152-bone Genesis9 preview and spine-corrected walk/jog clips are already retargeted draft studies. The private `BS_EnderIdleWalkRun_V1_NONCANONICAL` and `ABP_EnderIdleWalkRun_V1_PRIVATE` use those existing clips; the native 5.8.4 PIE route to flotation passes when runtime sample cache is resampled. The two generated assets remain local binary studies, not portable public releases.

At source SHA `1e25dbb...`, one completed full PIE replay verified animated walk, exact private preview ownership in two scenes, 9/9 native screenshots, 25/25 unchanged protected assets, and native physical flotation. A matched earlier route showed walking near-low-toe XY velocity proxy roughly **21.86/22.25 cm/s** for legacy direct clips versus **23.66/23.31 cm/s** for Blend Space, left/right. Later read-only bracketed visibility collision queries gave walking median toe-to-first-blocker clearance **3.58/4.02 cm** (left/right; 60 frames; not verified planted-ground collision). Neither metric proves a good or poor transition compared with games.

## How to conduct a valid like-for-like comparison

Keep evaluation isolated: same skeleton where feasible, same 260 cm/s walk and 600 cm/s run, same camera FOV and frame rate, same travel distances, same surface and fixed input sequence. Use at least three repeat captures per condition. Compare first against **GASP/Lyra in a separate sandbox**, and only against commercial JRPG footage for subjective style and posture. Benchmark scenarios:

| Scenario | What to measure | Review gate |
|---|---|---|
| Idle → walk | time to first weight shift, hand/torso jerk, acceleration-vs-pose onset | no A-pose/pop, plausible initiation |
| Walk → run → walk | synchronized pose/playrate, cadence against capsule speed, foot-slide proxy | no snap or foot skate in contact windows |
| Walk → idle and run → stop | stopping distance vs clip root trajectory, braking pose and recovery to stillness | no skating or abrupt freeze |
| Walk → 90° and 180° pivot | capsule velocity vector vs pelvis/root yaw, crossover steps, camera follow | facing aligns without torso twist or taffy |
| Uneven terrain / slope / stairs | identified **floor collider**, two-foot contact curves, toe clearance and IK | no clipping, floating, knee hyperextension |
| First Wake boarding/repair/storm | stance changes, staff/hand IK targets, turn-to-interact and bracing | recognizable Ender, readable engineer body language |

Capture side-by-side motion under matched camera and controls, then collect actual **time-coded video or dense per-frame pose telemetry**. Static screenshots and a few toe points cannot measure perceived movement fluidity, temporal acceleration, cross-fades, or turn responsiveness.

### Proposed technical scorecard (0–3, NOT measured yet)

- **Start/stop quality:** 0 = reference pose/snaps, 1 = abrupt foot/body transitions, 2 = coherent transitions with small flaws, 3 = controlled weight shifts and braking.
- **Direction and pivot:** 0 = broken facing, 1 = mismatch or snapping, 2 = correct turning but slide/pose issues, 3 = aligned rotation and believable steps.
- **Feet, floor and stride:** 0 = clipping/hovering, 1 = frequent sliding, 2 = minor contact uncertainty, 3 = grounded foot plant with repeatable traces.
- **Upper body and storytelling:** 0 = disconnected mesh, 1 = mannequin-like, 2 = cohesive body motion, 3 = distinctive Ender engineer gesture/weight/gear.
- **Robustness:** 0 = fails native run, 1 = isolated functioning pose, 2 = full guarded PIE route, 3 = continuous human + packaged and regression evidence.

Do not award a total score until the same suite is played and reviewed under equivalent inputs. Current evidence supports **robustness level 2 only for the private controlled PIE route**, not a rating for published-quality animation or likeness.

## Fastest safe path

1. **Reuse** the existing exact-skeleton 3-clip private Blend Space; no fresh rig/scaffold rebuild.
2. **Verify** the ignored Blend Space and AnimBP custody/topology with `unreal/Tools/Invoke-EnderPrivateBlendAudit.ps1`; initially read-only. Turn their private authoring scripts into a deterministic clean-room generator separately, in a disposable empty worktree, before any binary handoff.
3. **Benchmark** short 60 fps idle/walk/sprint/stop/pivot clips and skeleton/toe telemetry against one licensed sample, favoring existing local UE template assets first.
4. **Correct** the dominant visible defect (start/stop/pivot or foot IK) within the guarded private branch. Keep the original working clips as reversible baseline. Do not implement full motion matching until existing 3-clip locomotion clearly fails the vertical-slice acceptance need.
5. **Only then** rerun full First Wake route, native automations, test snapshot/hash protection and Notion SSoT. Reuse the technical scaffold for Ionia/Lyra after their independent skeleton/retarget checks.

**Constraints:** Neontic currently has about 26 GiB disk and 7.4 GiB free RAM; do not initiate a full GASP download or duplicate Unreal project merely to benchmark style without first checking actual download size/storage, licensing, available movement clips and device headroom. The Fab listing has an **“Allows usage with AI: No”** attribute; do not input the sample's content into an AI training/generation workflow without an independent rights check.

## Outcomes required to close this reference task

- One logged baseline video plus GASP/Lyra licensed sample run under comparable camera/control conditions, or document why not possible.
- Quantitative stop/pivot/plant contact deltas with error bounds; visual review, not arbitrary 'AAA parity' claims.
- Source-locked, repeatable private binary asset checks and a negative-case/fail-closed proof.
- No conversion of an inspiration video into copied proprietary motion data; artist/creator acceptance remains separate.
