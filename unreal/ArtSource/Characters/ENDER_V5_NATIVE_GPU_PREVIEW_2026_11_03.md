# Ender V5 — first native MetaHuman face-and-body GPU preview

**Evidence date:** November 3, 2026. **Game:** To Sail the Starry Sky. **Status:** `NATIVE_TRANSIENT_PREVIEW_RENDER_PASS / VISUAL_LIKENESS_FAIL / PRODUCTION_RIG_NOT_VERIFIED`. No art is canonical as a result.

## Exactly what Unreal 5.8.4 verified

All activity occurred in the independently isolated `C:\MH4\CastAllSandbox` content-only review project on the authorized NEONTIC workstation. The original `MH2` Ender V5 asset and game projects were not modified. The edited `MH4` MetaHuman Character holds the independently verified green-iris parameter experiment; that visual color has **not** been approved.

Using the installed Epic MetaHuman Creator Python API, `MetaHumanCharacterEditorSubsystem.spawn_meta_human_actor(character)` successfully generated a **transient preview actor**, class `MetaHumanDefaultEditorPipelineActor`. Native component enumeration confirmed two **`DebugSkelMeshComponent` skeletal preview components** named `Body` and `Face`, an `LODSyncComponent`, `RetargetComponent`, and six `GroomComponent` instances. These are native 3D character-preview components, **not** evidence of a finished cloud-generated rig, animation-ready game actor, or assembled UE Cine / Optimized character.

After a corrected read-only probe, the first GPU render was attempted in its **own** Unreal Editor 5.8.4 D3D11 session with a temporary CameraActor and three review-only PointLights. The non-overwriting screenshot task used an Editor Slate post-tick callback and succeeded:

| Receipt | Verified evidence |
|---|---|
| Folder | `C:\MH4\CastAllSandbox\Saved\CharacterLookdev\V5NativeScreens\ender_v5_green_preview01` |
| Native screenshot | `face_threequarter.png` |
| Size | `800 × 450` |
| PNG bytes | `102,707` |
| PNG SHA-256 | `d6f95a2d285320b282d5fad32b098c6e7b563142be7265f2d8e2da762f486bf5` |
| Status | `NATIVE_PNG_CAPTURED_VISUAL_UNREVIEWED` |
| Enlarged review crop | `face_crop_review_only.png`, SHA-256 `e3a66a0aec58341692981c37d30a47b6fccce4a162df2b4e1c6f012adcf26486` |

The enlarged crop is only interpolation of existing screenshot pixels, **not** additional rendered facial detail. Both screenshot files and JSON receipt remain on the private workstation and were not committed to this GitHub repository or promoted to art.

The original `MH4` UAsset SHA-256 stayed `2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d`. The V2 review map remained `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`. The capture script explicitly avoids saving either asset or level, and the receipt independently confirms both hashes after the render. The experimental GPU Editor process was stopped after capture. No user's other Unreal Editor process was terminated.

## Artist visual assessment: **FAIL / needs work**

The source screenshot **does contain a real 3D head, face, neck, shoulders and torso**, but the current preview appears as a pale, bald/covered-head, largely featureless mannequin with a visible underlying body mesh. Its material and hair rendering are incomplete. Facial silhouette and eye sockets can be inspected, but the iris hue and approved youthful Ender facial likeness cannot be reliably judged under this preview material and lighting. This is **not** a cinematic character portrait. The image has a black background, some blown-out skin regions, and the face occupies a small portion of the 800 × 450 frame. A face crop exposes the quality gap; it does not solve it.

The native log still reports **`MetaHuman Optional Content folder not found`**. The separate `MH3` test previously reached Epic authentication rather than completing a cloud joints-only rig. These exact blockers remain; no cloud rigging, texture synthesis, groom approval, clothing fit, eye visual approval, expression rig, animation or playable game assembly can be claimed.

## Reproducible source and next safe slice

Committed, fail-closed scripts:
- `native_ender_v5_transient_preview_probe.py`: original asset/map SHA guards, transient actor creation, inspection of face/body skeletal components; no asset saves.
- `native_ender_v5_transient_preview_capture.py`: guards exact isolated MH4 source hashes, confirms preview face/body components, creates transient review lights and camera, captures one native 800 × 450 PNG with integrity receipt, refuses overwrites, does not save art or level.

The render temporarily consumed substantial RAM while Unreal compiled the skeletal preview (system free memory dipped below 1 GB). Avoid parallel Unreal Editor launches when there is insufficient free memory; keep the native screenshot a single-camera bounded experiment.

**Smallest next steps:** owner closes unused Unreal Editors, installs/enables MetaHuman Creator Core Data in the installed UE 5.8 Options and completes Epic authentication; then inspect the existing MetaHuman preview with proper materials and hair, select **the earlier approved Ender face** as primary artist likeness authority, visually confirm 2D landmark features and their native 3D index correspondences, and only then attempt small reversible sculpt, cloud rig, textures and eventual UE Cine / Optimized assembly. Treat the newer group ship-deck image as secondary clothing/material guidance only. Ender's hair-color conflict remains HOLD. Do not merge this PR or promote any current character model into the game.

**Canon hold:** `PREVIEW_COMPONENTS=VERIFIED`; `V5_NATIVE_GPU_PNG=VERIFIED`; `CINEMATIC_LIKENESS=NOT_ESTABLISHED`; `META_HUMAN_CORE_DATA=MISSING`; `CLOUD_RIG=BLOCKED`; `PLAYABLE_3D_CHARACTER=NOT_AUTHORIZED`.
