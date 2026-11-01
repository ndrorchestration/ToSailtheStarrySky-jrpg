# Aureate Wake — authored-body V1 for Unreal Engine

**REVIEW ONLY / NOT CANON ART / NOT GAMEPLAY / NO ORBITER UNLOCK**

The four actual UE 5.8.4 D3D11 ship screenshots in draft PR #655 proved the cyan-and-gold four-wing review assets render, and exposed the large gray box hull and bridge. This separate reversible slice supplies a streamlined, faceted hull and triangulated geodesic glass dome as **two distinct deterministic glTF 2.0 candidates**. The actor and original playable maps are unchanged.

## Source and safety

- Generator: `unreal/ArtSource/ShipReview/build_aureate_body_review.py`.
- Fail-closed offline checker and opt-in importer: `unreal/ArtSource/ShipReview/import_aureate_body_review.py`.
- Outputs: `AureateWake_Hull_Lookdev.glb`, `AureateWake_BridgeDome_Lookdev.glb`, and `AureateWake_Body_Manifest.json` containing two SHA-256 receipts.
- Author in Unreal **centimetres, X forward, Z up**. Export glTF in **metres, Y up**, using explicit axis remap `(X,Z,-Y)`. This does **not** establish how UE 5.8 Interchange will actually orient these meshes; native inspection is mandatory.
- V1 hull follows the current preview's approximately 7.98m-long envelope without moving four existing wing roots. Chinelines, tapered shoulders, dorsal spine and a small open forward deck are appearance only.
- Dome has icosphere-derived triangular tinted panes and brass frame struts, a lower collar, and separate glass material. **Pressurization and walkability are NOT simulated.**
- The importer accepts only exact provenance/units/bounds/material sections and an SHA-matched GLB pair. It refuses unexpected or occupied asset directories and never binds actors or saves levels.
- Target folders are `/Game/TSTSS/Review/ShipArt/HullCandidateV1` and `/Game/TSTSS/Review/ShipArt/BridgeDomeCandidateV1`. They are NOT gameplay assets.

## Reproducible engine-free commands

```powershell
python unreal/ArtSource/ShipReview/build_aureate_body_review.py --build --output-dir unreal/Saved/BodyReviewCandidateV1
python unreal/ArtSource/ShipReview/build_aureate_body_review.py --verify --output-dir unreal/Saved/BodyReviewCandidateV1
python unreal/ArtSource/ShipReview/import_aureate_body_review.py --check --folder unreal/Saved/BodyReviewCandidateV1
python -m unittest discover -s unreal/Tests -p test_aureate_body_lookdev.py -v
```

Source-only verification on November 1, 2026: two deterministic outputs; hull 1,554 triangles and dome 4,948 triangles; three material sections each; third-party GLB scene parser opened both; no degenerate faces reported; offline manifest preflight PASS and **9/9 negative/positive tests PASS**. These figures describe the source-only generated candidates, **not native Unreal imports**.

Exact generator output SHA-256 values from the local source verification:
- Hull: `a549c6737d59416645f1ead0a9d6531f6f314ba6bb774cbdd56b19b65a03ba22`.
- Dome: `c2043ae7eaf94d4fa2aa42bfbd5e147918bc4344b21e3798b7d9bc4b726224f3`.

## Strict native admission hold

The connected Windows workstation was unreachable when this slice was authored. **No UE import, UE 5.8 C++ build, screenshots of these two new parts, or creator approval has been established.** The previous four-wing screenshots are not images of these body candidates.

In a fresh isolated Unreal review project: run preflight, opt in to import, verify source-to-native axes and mesh bounds, retain distinct material slots, review glass opacity and geodesic frame, bind only to review duplicate components, capture all four PR #655 camera angles, and visually compare. Validate at human scale and verify wing-to-hull gap, submersible tuck, permitted transitions and the Orbiter hold. Perform real physics and clearance tests before gameplay admission. Do not replace the production ship or infer any sea-contact authority from a rendering.

**Canonical ship direction (not accomplished by this V1):** a refined dragonfly-derived Aureate Wake, four wings, forward geodesic dome, accessible open deck, seaborne hydrofoil, slightly visible tucked submarine wings, and story-gated four-radial-sail Orbiter. No automatic narrative progression or mode unlock.
