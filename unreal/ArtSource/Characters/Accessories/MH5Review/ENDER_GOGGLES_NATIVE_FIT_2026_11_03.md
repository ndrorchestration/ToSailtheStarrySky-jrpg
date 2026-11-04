# Ender V5 goggles — native orientation and provisional on-head staging

**Evidence date:** November 3, 2026. **Engine:** Unreal 5.8.4, authorized NEONTIC workstation. **Branch:** draft PR #721, review-only. **Art status:** `NATIVE_IMPORT_PASS / NATIVE_ORIENTATION_PASS / TWO_BOUNDS_HYPOTHESES_RECORDED / ACTUAL_HEAD_FIT_NOT_PROVEN / NOT_CANONICAL`.

## New reversible native development

1. Created an *additional* clean content-only MetaHuman sandbox, `C:\MH5\CastAllSandbox`, by copying the exact known MH4 green-eye MetaHuman and source review map. Initial SHA-256 checks passed for both originals: MetaHuman `2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d`, map `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`. The original MH2 V5 asset remains separate.
2. Imported the verified original NEONTIC Ender goggles GLB SHA-256 `76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae` into `/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/GogglesCandidateV1/...` **inside MH5 only**, where it can now be inspected alongside the actual V5 MetaHuman source.
3. Native import receipt `native_import01.json`: `MH5_NATIVE_GOGGLES_IMPORT_PASS_POSITIONING_PENDING`; exactly one `StaticMesh`, nine material slots, mesh extents **18.21768 × 6.10 × 15.35 cm** in imported Unreal local X/Y/Z. This is import proof, **not worn-fit or material-render proof**.
4. A first native placement attempt used an assumed `Rotator(Pitch=0,Yaw=180,Roll=90)` and **failed correctly**, because the resulting world-space bounds were **6.10 cm wide × 18.21768 cm deep × 15.35 cm tall**. This false orientation is retained unchanged as a negative-control failure: `native_spatial_review01.json` = `SPATIAL_REVIEW_FAILED`. Both source asset/map hashes remained unchanged.
5. Replaced guessed orientation with a native engine enumeration of all 64 orthogonal Euler rotations (angles 0/90/180/270). Exactly **8** rotations restored the desired world envelope, and **2** passed the additional forward/up axis tests: `[Pitch,Yaw,Roll] = [90,180,0]` and the equivalent `[270,0,180]`. They map imported local `+X → -world X`, `+Y → +world Z`, and `+Z → +world Y`, restoring the candidate's design convention **X temple-to-temple, +Y forward, +Z up**. Receipt: `native_axis_search01.json` = `NATIVE_AXIS_SEARCH_PASS_PREFERRED_AVAILABLE`.
6. Using the verified **[90,180,0]** native transform, a fresh read-only session loaded the *actual* `MetaHumanDefaultEditorPipelineActor` with separate `Face` and `Body` skeletal preview components, then spawned a disposable StaticMeshActor for the goggles. The scene was **not saved**. At both staged positions the goggles world envelope measured **18.21768 cm wide × 15.35 cm deep × 6.10 cm tall**.
7. The native placement run also loaded the original immutable 79-point native facial atlas, SHA-256 `9abcca28c03b21c13a5a1f35bc5b2126393debbc63c494e268c6df18d74eafed`, as **unlabeled model-space XYZ coordinates**, *not anatomical landmark names*. A preliminary broad-phase AABB test classified which existing points fell inside the outer box and within 1 cm of that box:

| Provisional trial | Actor location (cm, relative to MetaHuman preview origin) | World AABB Y range | World AABB Z range | Indexed points inside outer AABB |
|---|---|---|---|---|
| At approximate eye height | `[0,11.4,164.5]` | `-2.01..13.34` | `161.45..167.55` | **18/79**; 28/79 within 1 cm |
| Resting at approximate upper brow/forehead | `[0,9.5,171.5]` | `-3.91..11.44` | `168.45..174.55` | **1/79**; 1/79 within 1 cm |

**Important:** These are **outer AABB contact classifications**, not mesh intersection, scalp contact, strap tension, nose clearance, or a proof that any position is wearably correct. AABB includes substantial empty space within the strap and outside the lenses. Fewer indexed points inside an AABB **cannot be interpreted as a verified better fit**. The above-brow position is only a useful *first position to inspect visually*, consistent with the goggles-on-forehead direction. The underlying 79-point atlas lacks approved eye/nose/chin semantic labels and is not a comprehensive head surface mesh. A head-and-goggles GPU screenshot remains absent for this MH5 pairing.

## Exact evidence and execution boundaries

All reviewed primary evidence is checked into `Accessories/MH5Review/Evidence/`:

- `native_import01.json` — native imported mesh and nine material slots, no fit claim.
- `native_axis_search01.json` — 64 native rotation trials, two axis-correct transforms.
- `native_spatial_review01.json` — retained **negative control** for erroneous orientation; explicitly FAIL.
- `native_spatial_review02.json` — corrected genuine MetaHuman preview and goggles staged in two temporary positions, only bounds and proximity evidence.

The corresponding `native_import_goggles_to_MH5.py`, `native_goggles_axis_search.py`, `native_goggles_spatial01_negative_control.py`, and `native_goggles_spatial02.py` scripts are source-controlled and fail-closed on project and input hashes. The `test_native_goggles_fit_receipts.py` engine-free regression rejects wrong rotation, rewritten negative controls, altered source hashes, and any false claim that placement, face fit, GPU render, game rig or canonical art was approved. **All native executions exited; no source character, green-eye base, review map or playable project was edited or promoted.** The only new saved Unreal assets are detached goggles review files inside `MH5`.

## Combined native V5 + goggles GPU screenshot attempt — TIMEOUT, not a PASS

A single further bounded D3D11 live-Editor capture was attempted in `MH5`, using the **confirmed corrected rotation [Pitch,Yaw,Roll]=[90,180,0]**, the **provisional above-brow location [0,9.5,171.5] cm**, and a frontal (+Y) native CameraActor. The script placed the *real imported goggles StaticMesh* into the scene with the *real transient MetaHuman Face/Body preview actor*. Before requesting the image, Unreal checked goggles bounds against 18.21768 × 15.35 × 6.1 cm and kept all source assets loaded with exact hashes.

The screenshot task was requested and the bounded tick runner eventually recorded **`TIMED_OUT`** with **zero PNG captures**. No combined face-and-goggles screenshot exists. The only terminated process was the disposable `MH5` render Editor; the earlier user Editor was not terminated. After the timeout, fresh checks confirmed:

- MetaHuman UAsset SHA-256 unchanged: `2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d`.
- Review map SHA-256 unchanged: `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`.
- Original goggles GLB SHA-256 unchanged: `76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae`.
- `Saved/CharacterLookdev/GogglesFitV1/native_visual_combined01/capture_receipt.json` contains the terminal `TIMED_OUT` and `captures=[]`; a mirrored engine-native receipt is checked in as `Evidence/native_visual_combined01.json`.
- The capture source is saved as `native_goggles_combined_capture01.py`. A new negative test rejects reporting any resulting screenshot or character-fitting approval based on this failed run. No scene or V5/goggles source asset was saved, and no game art promoted.

**Rendering remains the outstanding separate gate.** Do not spend additional source or ArtQA credit on repeated attempts with the same screenshot pipeline without first diagnosing the suspended GPU screenshot task, Windows UI/session permissions, or D3D11 editor capture behavior. A fallback could be a separate RenderTarget export or an authorized Editor viewport capture, clearly distinguishing its proof strength from a HighResShot. These alternatives have **not** been tested in this milestone.

## Visual approval and next 3D milestone

Keep the first approved Ender faces authoritative, and the later ship-deck group image secondary. Hair-color disagreement remains unresolved. Core Data and Epic-account authentication prerequisites for the MetaHuman production rig remain blocked.

A native Unreal viewport check of the **corrected [90,180,0]** goggles on the V5 head should compare both trial positions, full head profile, lens transparency and leather-to-scalp fit, preferably in one bounded render without simultaneously running multiple heavy Editors. After actual visual + close geometry checks, record a provisional attachment transform/socket anchored to a *verified* rig; do **not** attach to the transient debug skeletal preview or merge into gameplay as a production-ready accessory. Capture face/eyes and approved-ref comparison before changing Ender's facial sculpt.

**Status:** `3D_SOURCE_GLTF_PASS / MH5_NATIVE_STATICMESH_IMPORT_PASS / CORRECTED_NATIVE_AXIS_MAPPING_PASS / PRELIMINARY_WORLD_BOUNDS_PASS / PHYSICAL_FIT_UNVERIFIED / MATERIAL_GPU_RENDER_UNVERIFIED / RIG_UNVERIFIED / CANON_HOLD`.
