# Ender V2 connected cloth + layered hair — native review / not approved

2026-11-01 | **Draft only** | Stacks on [PR #652](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/652) | [Expert issue #649](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/issues/649)

## Design objective and authority

The owner-approved October 30 group artwork is the artistic authority, NOT the procedural v1 study. This V2 is a deliberately reversible source asset refinement, not a professional finished 3D sculpt or a claim of direct likeness. The exact references have not been registered as source-space topology landmarks. No protected `main`, playable Godot game, accepted cast GLBs, production UE level or existing Ender V1 content is replaced.

Canon locks: **Reson > Aepex > Ender > Ionia > Lyra**, exact heights provisional; Ender is 22 with green eyes, scholarly clothing, goggles, and a practical centered-wrap brass-ferrule fighting staff. Hair stays the existing green lookdev palette as a placeholder; prior conflicting visual references MUST be resolved with an explicit owner-approved asset selection before canonical art admission. Five Lights are story affinities only.

## Authored improvements compared with V1

- Replace the 14 tubular forehead locks and scattered cylindrical side/nape strands with **23 continuous tapered, overlapping front hair cards**, 14 side cards and 17 nape cards, over a smaller crown cap. Hair-color decision remains held.
- Replace the oversized green ellipsoid waistcoat fronts with two **connected cloth-surface grids**, side-sewn with gently curved chest panels, lapel flaps, shaping seams, and four shirt-opening tabs. Existing original clothing remains underneath; this is static art, not simulation or cloth rig.
- Reduce the very large white sclera and iris proportions without changing green eye affinity; retain the previously sculpted face/nose/mouth/goggle detail and centered staff grip.
- Quantize source coordinates and normals before GLB packing to reduce—but **not claim to eliminate**—cross-host trigonometric rounding differences. Preserve strict glTF CRC/metadata/normal/triangle integrity.

## Verified source-level evidence

- Candidate `FidelityCandidates/EnderV2/Ender_ender_fidelity_v2.glb`: SHA-256 **`e36f2f1daedbeefa53c54b92732e6b3498e4ea176c6f74f9f101e935a6b42bf8`**, **359,480 bytes**, **16,182 triangles**, **172 named parts**, **34 material sections**.
- `verify_ender_fidelity_v2.py` checks actual glTF triangle indexes, outward-facing normals, segment boundaries, nonconvex cloth/hair surfaces, material sections, source hash, and necessary V2 feature names.
- Six engine-free `test_ender_fidelity_v2.py` regressions **PASS on the connected Windows machine**, covering byte-verified pinned source, unchanged original/V1 GLBs, material/canon provenance locks, non-overwrite, local determinism, and tampered bytes rejected. This does not prove bitwise Linux parity; hosted CI must be inspected.
- V1 historical render/intake reports remain intact and separate. The V2 candidate has an entirely different asset name/destination, map and task receipts, and it cannot replace the already-imported V1 StaticMesh.

## Unreal verification (gated)

- V2 native import: `intake_ender_fidelity_v2.py` enforces Unreal 5.8, immutable SHA, disposable `CastAllSandbox` only and unused `/Game/ArtLookdev/Characters/EnderFidelityV2`.
- V2 native stage: `stage_ender_fidelity_v2.py` creates unique `/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review` and refuses an existing map.
- V2 native render: `capture_ender_fidelity_v2.py` uses named pitch/yaw/roll camera angles inherited from the previously corrected v1 renderer, fixed exposure and two 1280×720 review screenshots, using Unreal's Python Automation Test plugin in a disposable D3D11 project. Image QA and visual inspection must be repeated on actual V2 output.
- **Art QA remains HOLD** regardless of machine/CI results, until visual comparison with the actual approved cast imagery is performed and owner explicitly signs off.

## Next best professional visual slice

Establish head/eye/ear/nose landmarks against the owner-approved close-up, preferably with real artist-authored retopology for controlled facial expressions. Then model thicker woven clothing with torso deformation rather than layering cloth cards over primitive torso parts. Keep material shader acceptance and rigging separate. Do not proceed to Ionia production changes until Ender provides an approved, reproducible modular approach.

## Native UE5.8.4 D3D11 evidence (completed)

- SHA-pinned V2 imported **PASS** to independent `/Game/ArtLookdev/Characters/EnderFidelityV2`; V1 remains untouched. Import receipt shows staff-inclusive native height ~185.8 cm.
- Unique disposable `/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review` **PASS**. It is not the original lineup map.
- `Editor.Python.CastAllSandbox.test_ender_fidelity_v2_native` **SUCCESS**; both screenshot tasks completed on D3D11 SM5, not NullRHI or raster flips.
- `verify_ender_v2_native_captures.py` **PASS**: actual 1280×720 PNGs, distinct SHA-256, CRC/IDAT and nonblank coverage. Front SHA `b75acb9eb739bffc0cc690f255733f21c69c0b4360ff80dbae6e3bf749aa1d98`; three-quarter SHA `783c5b9d46ff4c3eaf3c8067a158b1862c7d50510fc3715de2415f5e7c088a91`. Nonblack coverage 9.31% and 8.22%.
- Original five-cast lineup saved map SHA remains `6614a8a8c378f8eada5a8ff2788afae9ca49832e507b27ed942a8076a478b49a`. No source or map replacement.
- [V2 native front](ReviewCaptures/2026-11-01/EnderFidelityV2/Ender_v2_front.png) and [V2 native three-quarter](ReviewCaptures/2026-11-01/EnderFidelityV2/Ender_v2_three_quarter.png). These are authentic engine renders, **NOT** artist-approved likeness.

### Visual QA observations

The V2 connected waistcoat faces read more coherently than the V1 disconnected ellipsoids and the tapered strands avoid several tube-like hair clumps. However, the silhouette and face are still decidedly procedural. Flat cloth surfaces do not substitute for thickness, sewing topology or rigged deformation; hair cards currently form a stiff fringe; eyes, ears, lips, facial planes, body proportions and staff pose lack cinematic naturalism. **ART-FIDELITY FAIL/HOLD** regardless of PNG integrity or native importer success. No automatic promotion to canon.
