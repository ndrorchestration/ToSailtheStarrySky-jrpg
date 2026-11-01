# Aureate Wake V3 — noncanonical tangent / UV repair

**Scope:** Reversible and isolated review-only geometry shading fix for the two V3 wing-root fairing and bridge interior GLBs. Does not change the creator-approved visual reference, V1 or V2 assets, original V3 geometry, existing Unreal maps, gameplay actor, First Wake or Orbiter.

## Verified defect

Actual native Unreal 5.8.4 Interchange import of draft #693 (2026-11-01) logged **nearly zero binormals** for the V3 fairing and interior, and **degenerate tangent bases** for the bridge interior. The underlying V3 generator used the common `Surface.tri` UV projection onto the same global two axes for every polygon. Faces perpendicular to one of those axes had collapsed UV triangles, preventing MikkTSpace from constructing reliable tangents. This is an import/render-quality defect, **not** proof of catastrophic mesh corruption.

## Isolated fix

- New `unreal/ArtSource/ShipReview/build_aureate_detail_v3_uvfix.py` uses the exact unchanged original V3 procedural surfaces, normals, vertex positions and triangle indices.
- For each nondegenerate triangle, select the face normal's dominant axis and map its UV coordinates to the other two coordinates, preserving positive UV orientation. Scale by 20 UV units per metre to avoid near-zero texture gradients on fine gold trim.
- Outputs **two new filenames in a separate review output folder**: `AureateWake_RootFairing_V3_UVFIX_REVIEW.glb` and `AureateWake_BridgeInterior_V3_UVFIX_REVIEW.glb`. Never overwrite original `AureateWake_RootFairing_V3_REVIEW.glb` or `AureateWake_BridgeInterior_V3_REVIEW.glb`.
- A manifest pins both the old V3 SHA-256 identities and the new V3 UVFIX hashes; explicitly states **art/model acceptance and native warning resolution NOT VERIFIED** until separate native import log review.
- `unreal/Tests/test_aureate_detail_v3_uvfix.py`: **8 source-only regression tests** verify original V3 byte-identical SHA-256, original vertex/normal/index equality, all per-triangle UV areas in source and encoded GLB, provenance, deterministic export, tamper refusal, and no editor/gameplay calls.

## Standalone commands

```powershell
python -m unittest discover -s unreal/Tests -p test_aureate_detail_v3_uvfix.py -v
python unreal/ArtSource/ShipReview/build_aureate_detail_v3_uvfix.py --build --output-dir unreal/Saved/AureateDetailV3UVFix
python unreal/ArtSource/ShipReview/build_aureate_detail_v3_uvfix.py --verify --output-dir unreal/Saved/AureateDetailV3UVFix
```

Native review must import into **two new empty review folders** (`RootFairingUVFixCandidateV3`, `BridgeInteriorUVFixCandidateV3`), validate native bounds and material sections, and check the real Unreal import log for the absence of the former tangent/binormal warnings. Do not infer that warning resolution passed from a successful source test. If native import passes, make a separate saved V3-UV review map using the same four Skyborne cameras, verify all four nonblank unique real D3D11 PNGs, and compare to original V3 frames. No automatic art acceptance.

## Previous native evidence (distinct from this fix)

The original V3 two meshes successfully imported to Unreal 5.8.4 and a distinct `/Game/TSTSS/Review/V3_Skyborne_Details_Studio` map was saved. D3D11 `Editor.Python.AureateWakeNativeQA.test_v3_skyborne_render` completed successfully (exit 0) and generated four distinct 1920×1080 PNGs with independently verified byte integrity:
- Three-quarter: `769ceced4bf5fc508c970bc9d07040bba0b96a82bf6ac0236dd23bf4109c1d42`
- Port side: `7bcdf78c384bceaf240c9009d85b43995d0447f54bee0ce55a2a651a85139893`
- Dorsal: `02f77084acb1d8c0ee1c5b0526a15a5be4573da4d4b6bca3df46f35591fe0dd8`
- Bow: `da8b3d0acae95fd21f3d0cb3294352e40c7d8f2da030b0540e46e8b39cfc190f`

Local private contact sheet: `C:\TSTSS_Unreal_V2NativeQA_20261101\NativeArtReviewSandbox\Saved\ReviewReceipts\AureateWake_V3_Skyborne_UE58_NativeFourView.png`.

**Creative QA HOLD:** Four wing-root fairings and new bridge furniture are visible only within the still-simplified Skyborne vessel. Against the approved image, the primary hull remains a slab-like proxy, the cockpit interior lacks cinematic fidelity, root articulation and pressure/crew-scale remain unverified. This is static review geometry, not a full form-transition-capable ship. Orbiter and Moon Bridge remain locked; no production art promotion, main merge, installation or release.
