# Ender V5 + V2 sealed goggles — native illumination correction

**November 4, 2026. UE 5.8.4 D3D11. DRAFT / NONCANONICAL / NOT ART APPROVED.** Strictly stacked on `80574adde52d37288428b4e1f631c0b50eb129d0` (genuine V2 sealed goggles three-quarter review). This is a V2 **visual diagnostic**, not a production authoring or geometry/rig milestone.

## Native experiment — same lower-forehead V2 sealed goggles

An isolated Windows native SceneCapture2D RenderTarget test was performed in the existing disposable `C:\MH5\CastAllSandbox`. The same MetaHuman V5 transient face and genuine V2 imported StaticMesh were used at the existing lower-forehead trial transform `[0,9.5,168.5] cm`, native world extents `[19.2,19.17101,8.02] cm`. **Only the temporary three pointlight intensities changed**, from the original values to 10% each. The camera, field of view, 480 × 320 export, V2 goggles, character source, map, GLB, pose and output material parameters remained unchanged. Original PNG and receipt retained; unique output directory created. No level, MetaHuman, gameplay actor, or source GLB was saved or replaced.

| Actual native V2 front render | Near-white pixels in fixed (110,38)-(370,319) crop | Original PNG core SHA-256 |
|---|---:|---|
| Existing normal-light V2 lower-forehead (`RenderTargetV2LowerForehead02`) | **33.5177%** | `dc9116e68a5404ebb4b377b78f443a902a5a4521734ad5533e94793e104fc709` |
| New **0.1× temporary-light V2** (`RenderTargetV2LowerForehead04_LightsTenth`) | **0.0383%** | `6ef2842848c21207cd17859341b015169e91d8929ea5c9f96a10f3f9aa5efbb2` |

Near-white = all three 8-bit RGB channels ≥245. The difference is a **33.4794 percentage-point reduction** in overbright pixels in this fixed crop. This is a diagnostic pixel count, **not** a material rating, verified wearable fit or cinematic likeness score. Lower-light native screenshot clearly resolves the brass/deep cup silhouettes and teal/emerald border, but lenses still appear extremely dark; the provisional goggles float above a bald, unfinished MetaHuman face. The face has not been matched to the creator's earliest approved portraits. Other focal areas may be underlit.

The independently executed `verify_v2_lower_light_native_20261104.py` parsed actual PNG CRC/chunks and 480×320 dimensions; checked PNG-core SHA against each native receipt; decoded independent Pillow RGB pixels; verified the source-only single-variable script diff and unchanged 3 source SHA values; checked fail-closed false approval fields; and emitted `Evidence/native_v2_lower_light_review_20261104.json` with **`NATIVE_V2_SEALED_GOGGLES_LOW_LIGHT_IMPROVES_READABILITY_ART_HOLD`**.

The Unreal exporter appends byte sequences after valid PNG IEND; original native files are preserved, CRC/pixel validation applies to authenticated PNG cores, and no screenshot PNGs are checked into GitHub. CI may compile scripts and validate source/receipt semantics, but **does not reproduce or inspect native GPU images**.

## Preserved provenance and hold conditions

- V5 MetaHuman source `2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d` (same before and after).
- Saved review map `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a` (same).
- V2 sealed 3D goggles GLB `5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb` (same); on-host semantic regeneration, **not claimed byte-identical** to the original separately packaged V2 offline asset `e46af393...`.
- Detached review copy only, never V1 glasses promotion. V2 has **11 imported material slots**, genuine native screenshots, but no verified physical head/gasket/strap contact or scalp fit, no real rig/attachment, no clothing, hair or approved skin/lookalike, no gameplay replacement and no canon promotion.

**Next authorized visual milestone:** in one further isolated test, retain V2 geometry and camera; assess lens/readability via intentionally tuned separate light ratio or explicitly authored material preview, then front/profile/three-quarter contact and strap/scalp collision checks against reference-guided Ender head. Do not call it approved before actual reference-based artistic review. The user's first approved face references remain primary. Core Data/rig and creator acceptance stay blocked separately.
