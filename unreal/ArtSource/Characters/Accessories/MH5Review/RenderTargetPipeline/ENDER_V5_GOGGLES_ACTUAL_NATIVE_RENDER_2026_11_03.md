# Ender V5 + brass goggles — first successful native Unreal combined render

**Evidence date:** 2026-11-03. **Engine:** Unreal Engine 5.8.4 (58902052), D3D11 on authorized NEONTIC Windows device. **Milestone:** actual transient 3D Ender MetaHuman + separate imported goggles rendered together using a GPU `SceneCaptureComponent2D` and `TextureRenderTarget2D` export. **Canon:** HOLD; **art approval:** NOT ESTABLISHED.

## What changed, and what this replaces

Previous `AutomationLibrary.take_high_res_screenshot` calls in the review editor repeatedly generated no screenshot and timed out, including the earlier combined V5+goggles test (`MH5Review/Evidence/native_visual_combined01.json`). Its **failed receipt remains unchanged**.

A new **render-to-texture** test was created using the documented Unreal `SceneCaptureComponent2D.capture_scene()` and `RenderingLibrary.export_render_target` methods. These export an image independently of the earlier HighResShot screenshot task. All experiments used disposable content-only projects. No gameplay file or existing canonical art was promoted.

1. Lightweight 320×180 **native cube** in the original isolated `Cast643Review.uproject`: `SceneCapture2D` exported an actual 3D scene PNG. The first strict PNG validator flagged it `DIAGNOSTIC_FAILED`, because the exporter added **14,364 bytes after the valid PNG IEND chunk**, not because the image failed to render. The original validator failure is preserved in `Evidence/cube_capture_initial_validator_failed.json`.
2. A **Pillow and per-chunk CRC** second opinion verified the cube image: normal PNG header, dimensions 320×180, all chunk CRCs valid, IEND complete, varied nonuniform pixels depicting the engine's lit BasicShapes cube. It generated a separate byte-preserving clean PNG by trimming only the trailing data, leaving original source untouched. Its receipt is `Evidence/cube_png_second_opinion.json`.
3. Next, a clean **bounded native V5 + goggles test** in `C:\MH5\CastAllSandbox` loaded the real green-iris V5 `MetaHumanCharacter` and transient `MetaHumanDefaultEditorPipelineActor` containing `Face` and `Body` preview skeletal components. It also loaded the separately imported **actual 3D goggles StaticMesh**. Temporary SceneCapture2D camera and three PointLights were created only in RAM.
4. **Source-verified proposed goggles transform**: `Pitch=90°, Yaw=180°, Roll=0°`, trial placement relative to V5 origin `[0,9.5,171.5] cm`, resulting native world bounding dimensions **18.21768 cm wide × 15.35 cm deep × 6.10 cm tall**. This is the earlier *provisional above-brow hypothesis*, NOT approved contact or wearable fit.
5. The new capture method successfully generated a **480×320 actual D3D11 native PNG** depicting the pale V5 face and the brass-look goggles positioned above the forehead. Screenshot core CRC/dimension checks succeeded and image was independently opened and visually inspected. Native receipt `Evidence/v5_goggles_native_rt_capture.json` gives `NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED`. The program's original output contained **1,555 trailing bytes after IEND**. A second verified copy strips *only those bytes*, without touching PNG pixel data or original source, and a third lossy WebP copy was generated solely for compact review. `Evidence/v5_goggles_png_integrity.json` logs the exact hashes and postprocessing.
6. The only stopped process was the extra isolated MH5 rendering Editor; all source character/map/GLB hashes remain identical. No scene, MetaHuman source, rig, or game content was saved by the capture, and the user-owned unrelated Unreal Editor was left alone.

## Native evidence and provenance

These **private** files remain on NEONTIC in `C:\MH5\CastAllSandbox\Saved\CharacterLookdev\GogglesFitV1\RenderTargetCombined02`. They are **not checked into the game repo** as artwork.

| Artifact | SHA-256 / result |
|---|---|
| Original native UE screenshot `ender_v5_goggles_rt_front.png` | `6fa6d7ee088554b3af114e32b1df2ba5ecf65d88e52ac6a7983c57ff8f24d624` |
| Pixel-identical clean PNG `ender_v5_goggles_rt_front_clean.png` | `212041ad0b39fc7eefc5f479bd3dae4427aa04ffcf4e497ec95283123407f808` |
| High-quality recompressed review WebP `ender_v5_goggles_rt_front_review.webp` | `412b5b2ca48d167c3c79ca25eee04a69044785533b1aef108a2268381e6561e0` |
| Smaller mobile-review WebP `ender_v5_goggles_native_review_mobile.webp` | `b7025eb9e883e78bab28448349434f6e84d372efc599c2727a28f1a14b624f99` |
| Original MH5 V5 character UAsset, pre- and post-render | `2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d` |
| Review map, pre- and post-render | `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a` |
| Original authored goggles GLB, pre- and post-render | `76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae` |

**Important source/evidence distinction:** This repo contains the Python scripts and authentic JSON receipts, but **not the native screenshot pixels**; hosted CI can check that source receipts are internally consistent and noncanonical, **not independently reconstruct pixels or render Unreal**. A readable compressed preview was made available in the originating ChatGPT conversation. The genuine original stays on the user's computer.

## Art review: useful evidence, not cinematic completion

Visual inspection of the actual native render establishes:

- A recognizable pair of circular brass-like goggles appears in the same frame as Ender's **real 3D V5 face**, placed **high above the brow and partially across the scalp silhouette**. Their current position is a trial; strap/scalp intersection, wearing physics, eye clearance and movement fit remain unproven.
- Material/exposure defect: metal rims are overbright/white-gold; the lens design's intended green tone and translucency do not read reliably. Automated camera exposure and test lighting need calibration, *not invented visual acceptance*.
- MetaHuman defect: Ender currently appears bald, pale and minimally textured. The portrait has not been matched to the earlier creator-approved face authority. More Core Data, author-sculpted facial resemblance, hair/goggles fit, wardrobe and proper rigging are required.
- The composite **does not establish a skeletal attachment or an animation-ready rig**; the preview contains temporary debug skeletal components. No playable/cinematic production asset has been accepted or merged.

**Verified technical milestone:** `NATIVE_GPU_SCENE_CAPTURE_EXPORT_PASS`, `V5_GOGGLES_COMBINED_3D_VISUALIZATION_PASS`, `PNG_CHUNK_CRC_PASS`, `SOURCE_ASSET_INTEGRITY_PASS`.

**Outstanding gates:** `PHYSICAL_GOGGLES_HEAD_FIT=NOT_ESTABLISHED`, `SKIN_HAIR_LIKENESS=NOT_APPROVED`, `MATERIALS_GREEN_LENS=NOT_APPROVED`, `META_HUMAN_CORE_DATA=NOT_INSTALLED`, `CLOUD_RIG=BLOCKED_BY_EPIC_AUTH`, `PLAYABLE_CHARACTER_RIG=NOT_VERIFIED`, `CANON_PROMOTION=NOT_AUTHORIZED`.

## Fastest safe next artist/dev slice

Prioritize exposure calibration and material readability using **one new isolated render-target session**, not the defunct HighResShot approach. Keep identical source UAsset/GLB with unique output receipts; inspect metal and lens texture visually before changing actual material/geometry. For fitting, first test a modestly lower forehead trial, but do not apply it to the stored MetaHuman or gameplay assets until an artist reviews front/profile angles for clipping and frame proportions. Preserve first approved faces as character likeness authority; later group-deck image secondary. Hair-color conflict remains unresolved. Install MetaHuman Creator Core Data and finish user's own Epic authentication before production cloud rigging and higher-fidelity skin/hair workflows. Avoid repeated heavy parallel Editors on the Intel Iris Xe shared-memory GPU.

Reproduction source here: `native_render_target_cube_diag01.py`, `native_rt_png_postcheck.py`, `native_rt_ender_v5_goggles01.py`, `verify_native_rt_v5_goggles.py`, and `make_rt_preview_mobile.py`, plus the four evidence JSON records and engine-free fail-closed tests.

Official references: [Unreal 5.8 Export Render Target](https://dev.epicgames.com/documentation/en-us/unreal-engine/BlueprintAPI/Rendering/ExportRenderTarget), [SceneCaptureComponent2D Python](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/SceneCaptureComponent2D?application_version=5.8).

**PR remains DRAFT / OPEN / UNMERGED.** No canonical art, face sculpt, or gameplay change.
