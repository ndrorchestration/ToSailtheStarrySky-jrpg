# Ender — detachable brass goggles: genuine 3D accessory prototype

**Development date:** November 3, 2026. **Art status:** NONCANONICAL, NOT FITTED, STATIC LOOKDEV ONLY. **No face edits, no playable game modification, no character rig**.

## What was actually built

An original, dependency-free Python mesh generator creates editable 3D steampunk/solarpunk goggles: two toroidal aged-brass lens frames; second gold filigree rims; dark metal lens seats; slightly curved transparent green glass discs; padded oiled-leather gaskets; central arched brass bridge with rivets; articulated temple hinges; three-dimensional leather head strap with subtle stitches and adjusters.

The candidate is **actual mesh geometry**, not a generated 2D concept or a planar texture. It uses **nine PBR material definitions**, 8,562 vertices and **15,920 triangles**. In design-model space (meters), **X** is temple-to-temple, **+Y** is lens front, **+Z** is up. Approximate full bounding dimensions: **18.22 cm width × 15.35 cm front-to-back × 6.10 cm tall**. The free source generator is `tstss_ender_goggles_generator.py`, without paid/free-credit services, purchased assets, or external code libraries.

### Source artifacts

- An independently generated `.glb` from the same generator on the assistant's artifact runtime was validated by actual `trimesh` loading as a nine-primitive 3D scene with 15,920 triangles. **Artifact-runtime GLB SHA-256:** `92aabd10c8aa442718532a98e478e8accad71f358a3604f737ef5694fd16317e`, bytes `403940`.
- The exact source Python generator was separately recovered onto NEONTIC (source SHA-256 `9cd83cc466b56e08782321e266d3136d171c841a0fb0e677d68d99543cccb205`) and generated the same 8,562 vertices, 15,920 triangles, nine materials, and bounds. **NEONTIC GLB SHA-256:** `76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae`, bytes `403940`. Small cross-environment differences in floating-point serialization produce **different byte hashes**; **do not claim binary parity**. Compare model topology, bounds and material inventory, not cross-machine SHA.
- A **geometry-faithful 1600×900 offline VTK preview** of the original artifact-runtime GLB was made for visual inspection. This is **not an Unreal screenshot** or approved character art. The source `.glb` and VTK PNG were shared within the originating ChatGPT conversation; only the generator and reproducible code are checked into this draft.

## Actual Unreal Engine 5.8.4 intake — PASS

A separate prior **content-only** review project at `C:\Users\Admin\work\TSTSS-Cast643-UEImport-Sandbox-20261101\Cast643Review.uproject` imported the NEONTIC GLB via `UnrealEditor-Cmd.exe -nullrhi -ExecutePythonScript=...`, safely refusing to replace an existing destination.

**Receipt:** `Saved\CharacterLookdev\GogglesCandidateV1\native_import01.json`

| Native field | Verified result |
|---|---|
| Native status | `STATIC_3D_GOGGLES_NATIVE_IMPORT_PASS_FIT_NOT_VERIFIED` |
| Imported objects | Exactly one `StaticMesh` and nine material assets |
| Unreal material slots | **9** |
| Imported asset | `/Game/ArtLookdev/Characters/Ender/Accessories/GogglesCandidateV1/Ender_goggles_noncanonical/StaticMeshes/Ender_goggles_noncanonical.Ender_goggles_noncanonical` |
| Unreal imported bounding extents | **X=18.218, Y=6.100, Z=15.350 cm** |
| Shader render/material appearance | **NOT VERIFIED** |
| Character head fit or animation socket | **NOT VERIFIED** |

**Coordinate caution:** the importer has remapped source X/Y/Z into Unreal; the imported Z dimension is the original front-to-back band depth. A reversible orientation correction (likely around the actor's X axis) is required for any head-fitting review. Never interpret a valid bounding box as proof the goggles are correctly oriented, sized against Ender's face, or wearable. The screenshot must show that the glass and straps render correctly before approval.

### Native Unreal screenshot — FAIL, preserved

A separate non-saving D3D11 review Editor attempted a temporary standalone goggles StaticMeshActor rotated 90° around its X axis, with a three-point lighting setup and an 800×450 screenshot request. Its screenshot callback **timed out without writing a PNG**, and the recorded receipt is `TIMED_OUT` at `Saved\CharacterLookdev\GogglesCandidateV1\native_visual_review01\capture_receipt.json`. The sandbox-only Editor was closed after the failure. **No native goggles screenshot or visual/PBR shader PASS may be claimed**. The native import and source asset remained intact. Avoid another resource-heavy Editor trial without diagnosing the screenshot pipeline and ensuring RAM headroom.

The 3D source and native import are separately verified, but there is **no proof of a correct Unreal material render, fitting, skeletal attachment or animation**. Generated materials use PBR metallic/roughness base-color values but no purchased textures; shader fidelity awaits a real native render.

## Safe next steps

1. Inspect the **imported** StaticMesh orientation in a native review viewport, test X-axis corrective rotation, and confirm face-relative fit against the current Ender V5 head *without* altering its source asset. Confirm anatomical forehead, no collision/clipping, and compatibility with goggles worn or resting on the head.
2. When available, obtain one correctly lit Unreal asset screenshot, compare it against the true 3D offline geometry render, and adjust lens translucency, leather and brass materials based on evidence.
3. Create a reversible attachable variant (likely socket or component on a future **verified skeletal mesh**, not the transient `DebugSkelMeshComponent`). Test consistent positioning under idle/walk/head turns; do not claim animation support before rig/assembly.
4. Preserve the earliest creator-approved face as facial authority, keep new group photo for selective costume/material inspiration, and leave Ender's green-versus-copper hair conflict on hold. No candidate is canonical until creator art acceptance.

**Gate:** `GLB_3D_GEOMETRY=PASS`; `NATIVE_STATICMESH_IMPORT=PASS`; `NATIVE_MATERIAL_RENDER=NOT_VERIFIED`; `HEAD_FIT=NOT_VERIFIED`; `PRODUCTION_RIG=BLOCKED`; `GAME_INTEGRATION=NOT_AUTHORIZED`. Keep PR draft/unmerged and original MetaHuman assets unchanged.

## Scripts and QA

- `tstss_ender_goggles_generator.py` — standalone original 3D mesh, PBR material and GLB authoring.
- `test_ender_goggles.py` — engine-free structural and negative-control unit tests; intentionally checks mesh topology and dimensions rather than cross-platform binary hash.
- `native_import_goggles_v1.py` — exact-hash/folder-gated native StaticMesh importer, sandbox-only.
- `native_visual_goggles01.py` — bounded experimental D3D11 screenshot script, **known failure**, for review only; do not run blindly over earlier receipts.
