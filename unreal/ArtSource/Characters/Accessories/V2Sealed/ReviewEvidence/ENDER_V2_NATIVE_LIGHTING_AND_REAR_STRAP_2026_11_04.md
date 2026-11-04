# Ender V2 goggles — native low-light readability and rear-strap profile

**Evidence date:** November 4, 2026 (America/New_York). **Engine:** Unreal Engine 5.8.4, D3D11 on NEONTIC. **Provenance:** native render captures, exact source SHA receipts, engine-free reproducibility tests. **Status:** REVIEW ONLY / NONCANONICAL / HEAD FIT UNVERIFIED.

## Material readability: actual improvement under reduced temporary lights

A new lower-intensity frontal V2 test already available in the isolated `MH5` review project, `RenderTargetV2LowerForehead04_LightsTenth`, uses the same Ender V5 MetaHuman and genuine imported V2 sealed-goggles StaticMesh as the original front view. Its valid **480 × 320 native PNG core** SHA-256 is `6ef2842848c21207cd17859341b015169e91d8929ea5c9f96a10f3f9aa5efbb2`, with full unmodified exported PNG SHA-256 `3c546fd737a236f969b2cf98574d7acf4ed9290cc826101a51b870b2e6346fa8`. It is a **real GPU render**, not a generated portrait.

Compared with the prior original-lights lower-forehead front image, the reduced lighting visibly restores brass/gold rim coloration, increases the readability of Ender's eyes, nose and face shading, and exposes the turquoise edge around the lenses. The lenses themselves remain nearly black; metallic colors and glass transmission have **not** been artist-approved.

Fixed, identical pixel-region measurements on the two native front screenshots (source: `native_v2_exposure_roi_metrics.json`) quantify the clipping reduction:

| Fixed rectangular region | Nearly white RGB pixels (all channels above 245), previous | Reduced lighting | Difference |
|---|---:|---:|---:|
| Goggles x=115..365,y=40..155 | 7.896% | 0.097% | **−7.80 percentage points** |
| Face x=145..338,y=154..300 | 72.298% | 0% | **−72.30 percentage points** |

These are **image-exposure metrics**, not physical shader validation or face similarity metrics. The former V1 `-2 EV` post-process experiment had zero effect; the current visible improvement comes from an actually different temporary studio lighting setup.

## Newly captured true native rear-side view

A separate reversible `MH5` D3D11 native render launched for the first time in this review lane with a **rear-side +X/−Y camera**, 44° field of view, looking at upper head; original corrected goggles rotation `[Pitch,Yaw,Roll]=[90,180,0]`, lower-forehead trial relative position `[0,9.5,168.5] cm`, and temporary point-light intensities `[11,6.5,5.2]`. This view was captured at 480 × 320 using the working SceneCapture2D / transient RenderTarget export pipeline, not HighResShot.

- Native status: `NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED`.
- Core PNG SHA-256: `3876c933e281831417613a3ced8d24beb1527c593b28170efc4cd06d74fc7c60`.
- Original exported PNG SHA-256: `f48509c14a4493251c5d8996c1f1e41c284d1fc35cfdb03dade8ea62d8f3bf1b`.
- Original source hashes remain unchanged after native render: V5 MetaHuman UAsset `2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d`, review map `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`, V2 goggles GLB `5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb`.
- The isolated Editor was terminated after the valid receipt; no map, character, goggles, or gameplay assets were saved.

**Visual inspection:** The 3D eyecup barrel is evident in profile. A strap-like element extends rearward near the side of the scalp, but the narrow angular silhouette and lack of authored hair make it impossible to conclude that the strap wraps correctly around the skull without penetration or floats. It is NOT proof of strap tension, scalp contact, socket-based attachment, physical wearability, rigging, or approved character likeness.

## What the actual V2 glTF materials contain

A read-only parsing of the **exact NEONTIC GLB** lists 11 GLTF materials and no `images` or `textures`: base-color factors, metallic, roughness and (for glass) alpha blending are specified but no authored detailed texture maps are embedded.

- `AgedBrass` base factor `[0.49,0.295,0.095,1]`, metallic `0.82`, roughness `0.34`.
- `BrushedGold` base factor `[0.8,0.54,0.19,1]`, metallic `0.91`, roughness `0.24`.
- `EmeraldGlass` base factor `[0.034,0.32,0.27,0.79]`, metallic `0.13`, roughness `0.12`, alpha mode `BLEND`.
- `TurquoiseAccent` base factor `[0.065,0.48,0.4,1]`.

A GLTF translucency declaration is **not** proof of a physically correct Unreal imported shader, absorption, refraction or eye visibility. The dark lens appearance may reflect imported material configuration and/or insufficient scene/eye illumination; don't assert a single cause without inspecting Unreal's imported `EmeraldGlass` material. Only material-parameter inspection and a fresh reversible material study should decide whether to adjust the lens itself.

## Source strap geometry versus physical wearing

The V2 generator actually defines a continuous rear band using a half-ellipse with model-space `a=0.088 m` (lateral semi-axis), `b=0.109 m` (backward semi-axis) and `ribbon_curve(...width=0.027 m,thickness=0.004 m)`. Thus the **source band is approximately 2.7 cm wide and 4 mm thick** and extends around the rear in *source-model space*. The rendered apparent thinness may be due to its edge-on orientation, shading or head penetration; the source formula alone cannot resolve those issues. The earlier 79 facial atlas points only sample a limited unlabeled face set, not a verified full head/scalp collision mesh.

## Private evidence and next gate

Only verified source scripts, precise JSON receipts and an engine-free regression test are checked into `V2Sealed/ReviewEvidence/`. The three input PNG binaries and a labeled side-by-side **review-only montage**, `Ender_V2_Native_Light_And_Strap_Review_20261104.webp` (SHA-256 `5819d9e1bf267ed5849d96088c845bae1f1f465282cd17357a28128581947d7c`), remain in the user's authorized private workstation directory:

`C:\MH5\CastAllSandbox\Saved\CharacterLookdev\GogglesFitV2`

The montage is assembled from genuine native captures with resizing and labels, *not a new game render*. No shot is promoted to canonical art. The previous V1 glasses prototype remains explicitly rejected for the goggles role.

**Next safe development slice:** inspect imported Unreal `EmeraldGlass` blend mode and lens material in **read-only / isolated** UE, then experiment with an independent material candidate only if the diagnosis justifies it; test the V2 rear-band/contact using a full scalp/head mesh with both front and back views rather than just the 79-point face atlas. Use the creator's **first approved Ender face** as likeness authority, preserve the newer ship-deck group image as secondary costume reference, and defer production rig/animation until MetaHuman Core Data and authorized Epic rigging are available.

**Gate:** `V2_NATIVE_LOW_LIGHT_IMAGE=PASS / V2_REARSIDE_GPU_IMAGE=PASS / SOURCE_HASH_INTEGRITY=PASS / BRASS_READABILITY=IMPROVED / EMERALD_LENS_SHADER=NOT_VERIFIED / STRAP_AND_SCALP_FIT=NOT_PROVEN / CINEMATIC_FACE=NOT_APPROVED / PRODUCTION_CANON=HOLD`.
