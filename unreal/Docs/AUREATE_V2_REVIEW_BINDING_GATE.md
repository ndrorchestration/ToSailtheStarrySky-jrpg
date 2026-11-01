# Aureate Wake V2 binding — isolated Unreal review only

The separate V2 hull and bridge assets generated in draft PR #679 are imported into `IvoryHullCandidateV2` and `BlueGlassBridgeCandidateV2` review asset folders. The old `RefreshBodyReviewMeshes()` actor accepted only V1 candidate folder paths. That made a successfully imported V2 mesh impossible to bind via the existing review API.

## Reversible actor interface

`bUseAuthoredBodyReview` remains **false by default**. New `bPreferFidelityV2BodyReview` is also **false by default**. In the default opt-in preview, the actor accepts only a V1 hull + V1 bridge. When both flags are deliberately enabled, it accepts only a V2 ivory hull + V2 glass bridge. A V1/V2 hybrid pair, wrong folders, missing parts, live transformation or Orbiter state must fail **before touching either mesh**. Disabling body review restores unchanged original cube and bridge transforms.

This is an *imported static-mesh look-development path*, not an artistic acceptance or canon/production promotion. There is no material approval, physical crew-space validation, pressure or waterline proof, and no Orbiter unlock.

## Test and native verification gate

Run `python unreal/Tests/check_aureate_body_binding_logic.py` on the exact branch. The compiled, source-extracted C++ harness now runs **31 isolated cases** (original 18 plus V2 allowed forms, refusal during transitions, rejection of V1/V2 hybrids and missing assets, default OFF, rollback, and Orbiter refusal). This executable is NOT an Unreal Header Tool or Editor compile.

To verify in a separate native Unreal 5.8.4 review map, install no new software: generate and perform the complete V2 binary audit, import static meshes into the exact isolated V2 candidate folders, select both new review properties only on a duplicate preview actor, call `RefreshBodyReviewMeshes`, check resolved asset paths and actor transforms, capture and visually review the four matching cameras. **Do not copy or merge** this branch into the playable scene until a native exact-head build and creator visual comparison pass. All Orbiter/First Wake story gates remain untouched.

Approved reference SHA-256: `03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13`. The original uploaded reference is not replaced.
