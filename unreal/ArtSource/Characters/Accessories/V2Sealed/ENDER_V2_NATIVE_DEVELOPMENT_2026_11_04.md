# Ender V2 — sealed aviator goggles: Unreal native 3D import and three GPU review views

**Evidence date:** November 4, 2026 (America/New_York). **Engine:** Unreal Engine 5.8.4 D3D11. **Project:** To Sail the Starry Sky. **Status:** `V2_GLTF_REPRODUCED / NATIVE_STATICMESH_IMPORT_PASS / NATIVE_3_VIEW_RENDER_PASS / MATERIALS_AND_FIT_NOT_APPROVED / CANON_HOLD`.

## Why this V2 replaces the prior *design* (but not its evidence)

The creator rejected the thin spectacle-style V1 as **glasses**, not goggles. V1's native import, source and genuine GPU screenshots remain historical QA evidence, but **V1 is not accepted as Ender's goggles**. V2 is a separate genuine 3D accessory with **deep sealed optical barrels**, padded face seals, enclosed metal side guards, green convex lenses, stitched edges, gold/brass accents, and one continuous strap curving behind the head. Its shape is intended for aviator/workshop eyewear; no spectacles-style temple arms. V2 is still author-unapproved, unrigged and detached.

## Source origin and actual NEONTIC rebuild

- User-visible original V2 GLB: `Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL.glb` from prior source package, **SHA-256 `e46af39346a953c36c010e6f103ff700b8d13ed32a41cf44c0af3b69f0c296d0`**, 1,412,976 bytes, validated with a 3D mesh loader before this milestone.
- Exact normalized Python geometry source was securely transferred to NEONTIC using LZMA/base64 and independently verified by SHA **`de026e100b3e26cda801501609fecdb35fd2427bcb97836bc32396813a0d1fc9`**. A *disposable per-project* `trimesh 4.11.1` dependency was installed under the review workspace, not into the user's global Python. The repository generator now supports `TSTSS_V2_OUTPUT_DIR` for Windows/CI, rather than assuming `/mnt/data`.
- NEONTIC generated a fresh local GLB with **the same 57,288 triangles, 29,792 vertices, 11 material primitives/names and 19.20 × 19.171 × 8.02 cm model dimensions**. Its SHA is `5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb`, also 1,412,976 bytes. The two GLB files are **structurally equivalent, NOT byte-identical**, due to cross-Python/numpy/serialization behavior. No source binary hash was fabricated.
- Source and independently generated geometry validation report are committed under `Accessories/V2Sealed/`; the native binary stays in the authorized workstation review folder and is **not** presented as approved art.

## Real native Unreal StaticMesh import — PASS

One guarded `UnrealEditor-Cmd.exe -nullrhi` test imported the NEONTIC V2 GLB into **only** the disposable `C:\MH5\CastAllSandbox\CastAllSandbox.uproject` project, under `/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/Accessories/SealedGogglesCandidateV2`. The import explicitly refused an occupied destination or changed source hash and never wrote the MetaHuman, review map or playable game. The imported Unreal leaf name was sanitized by the GLB importer; exact mesh path is in the native receipt.

`Evidence/native_import_v2.json` status: `NATIVE_V2_SEALED_GOGGLES_STATICMESH_IMPORT_PASS_FIT_PENDING`, exactly **one native StaticMesh, 11 Unreal material slots**, imported bounds **X=19.20, Y=8.02, Z=19.171 cm** (source axes converted at import). The source V5 character UAsset hash `2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d`, review map `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`, and GLB `5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb` were unchanged after import. V1 was not overwritten or relabeled.

## Native V2 orientation and trial face proximity — PASS only as broad-phase

An independent `-nullrhi` Unreal run loaded the **actual transient** MetaHuman preview `Face` and `Body` skeletal components plus V2 goggles StaticMesh. Corrected actor rotation `[Pitch,Yaw,Roll]=[90°,180°,0°]` restores the model-space **width/depth/height** as **19.20 × 19.171 × 8.02 cm**.

The immutable original 79-point face atlas was used as unlabeled XYZ coordinates for **outer axis-aligned bounding-box** proximity checks:

| Trial position relative to MetaHuman origin (cm) | Points inside outer V2 bounds | What this proves |
|---|---:|---|
| Eye height `[0,11.4,164.5]` | 22/79 | Broad bounding-box proximity only |
| Above brow `[0,9.5,171.5]` | 1/79 | Broad bounding-box proximity only |
| Lower forehead `[0,9.5,168.5]` | 6/79 | Broad bounding-box proximity only |

The full strap contributes empty/internal volume to the bounds. **These are not mesh-on-skin collisions, nose clearance, goggle seals, actual scalp contact, rig attachment, or creator-approved wearable fitting.** `Evidence/native_spatial_v2.json` records the exact engine-native measurements, source hashes and negative approval flags. The transient trial actors were never saved to the map.

## Three native GPU renders of the real V2 + MetaHuman — PASS technically

The established UE 5.8.4 D3D11 **SceneCaptureComponent2D → transient TextureRenderTarget2D → RenderingLibrary.export_render_target** pipeline captured three independent real **480 × 320** PNGs of Ender's *actual* V5 3D MetaHuman preview and imported V2 goggles. Each passed native PNG core integrity and separate source-hash checks. All V2, MetaHuman and map source hashes remained unchanged.

| Image | Technique / placement | Valid PNG core SHA-256 |
|---|---|---|
| `RenderTargetV2Combined01` | Front, above brow `z=171.5` | `9e032f7350f3013e646619ab8d86280bce0b7c08ef191729d749562e015b2990` |
| `RenderTargetV2LowerForehead02` | Same camera, 3 cm lower `z=168.5` | `dc9116e68a5404ebb4b377b78f443a902a5a4521734ad5533e94793e104fc709` |
| `RenderTargetV2ThreeQuarter03` | Three-quarter +X camera, `z=168.5` | `3608f2405ba4e667d020df25a187029614133d6dd9e1494d6541d6c89da48bb9` |

The first two frontal images visibly differ in position and are preserved in a **private, clearly labeled montage** `C:\MH5\CastAllSandbox\Saved\CharacterLookdev\GogglesFitV2\Ender_V2_Native_Unreal_Comparison_20261104.png`, SHA `793faf3879989370f4960f3dfd951be9e860b0e7c299e5259853a83f9c8e4cba`. The montage is only a layout of actual Unreal PNGs with captions; it is **not an additional native render**, a generated character likeness, or higher-resolution source data. The third image shows the **real deeper eyecup barrels and enclosed side construction** from an oblique angle, distinguishing V2 from the rejected spectacles V1.

**Art defects still open:** brass is blown out/very pale, emerald green glass reads nearly black, strap/hair contact and clipping cannot be judged yet, goggles sit high, MetaHuman skin is very pale and hair unfinished. The transient debug skeletal preview is **not a production game rig**. Face likeness to the creator's first approved portrait is not established. These screenshot PNGs and review montage remain in authorized NEONTIC private `Saved` files; only JSON receipts and source scripts, **not the PNG binaries**, were committed to GitHub. Hosted CI checks evidence consistency, not the uncommitted image pixels.

## Resource, authority and next gate

When another unrelated MH5 Editor was active, V2 native tests **refused to launch**; they resumed only once that process exited and RAM recovered. All completed review Editors were closed after capture. Other user's Unreal work, original character UAsset/map, V1 historical evidence, gameplay projects, and approved references were left untouched.

**Next smallest reversible milestone:** a native close-up of V2 side/rear strap with a more reliable exposure/material diagnostic (the prior V1 −2 EV postprocess experiment did not affect pixels), then a genuine mesh-level contact and strap clearance test and a first-approved-face comparison. Only after creator review and a verified production rig should any socket attachment or gameplay import be considered. MetaHuman Creator Core Data/Epic cloud authentication remain separate prerequisites.

**Gate:** `V2_SEALED_GLB_3D_SOURCE=PASS / NATIVE_STATICMESH_IMPORT=PASS / NATIVE_ORIENTATION=PASS / THREE_NATIVE_GPU_PNGS=PASS / SHADER_AND_STRAP_QA=FAIL_OR_PENDING / PHYSICAL_FIT=UNVERIFIED / ART_ACCEPTANCE=HOLD / GAME_INTEGRATION=NOT_AUTHORIZED`.

All work remains **draft, unmerged and noncanonical**, tracked through [PR #721](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/721) and [character QA #649](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/649).
