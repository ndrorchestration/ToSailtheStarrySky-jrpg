# Aureate Wake V3 — wing-root fairing and bridge interior (review only)

**Visual authority:** Creator-approved November 1 four-form ship image, SHA-256 `03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13`. This V3 is not approved artwork, nor a game-ready or physical mechanical simulation.

## Motivation and boundaries

[#690](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/690) provided four real Unreal D3D11 views of the V2 white hull, geodesic blue bridge and four wing meshes. They established native compositional feasibility, but showed exposed skinny wing root supports and an empty glass cockpit. This V3 addresses two specific review defects without editing the V2 generated meshes, changing gameplay, shipping art, or touching the Orbiter/Moon Bridge gate.

## New standalone assets

`unreal/ArtSource/ShipReview/build_aureate_detail_v3.py` deterministically outputs:

- `AureateWake_RootFairing_V3_REVIEW.glb` — an approximately 54 cm local +X, elliptical ivory/gold tapered joint sleeve around a navy actuator with cyan resonance details. Four independent copies can be positioned and stretched along the currently reviewed hull-support-to-wing-root vectors; no physical hinge or collision authority is implied.
- `AureateWake_BridgeInterior_V3_REVIEW.glb` — blue-black deck, golden supports, ivory helm, two crew chairs, a navigation table and cyan-lit displays located inside the geodesic dome's current provisional footprint. Seats are visual placeholders; crew scale, walkability and hull pressure sealing are not proven.
- `AureateWake_DetailV3_Manifest.json` — source SHA-256 receipts, approved-image reference, explicit status `NONCANONICAL`, no gameplay/Orbiter authorization.

Each mesh has **four separate source materials** and preserves Unreal centimetre X-forward/Z-up to glTF metre Y-up conversion. Geometry is intentionally isolated from V1/V2 root assets and ship code.

## Engine-free verification

```powershell
python unreal/ArtSource/ShipReview/build_aureate_detail_v3.py --build --output-dir unreal/Saved/AureateDetailV3
python unreal/ArtSource/ShipReview/build_aureate_detail_v3.py --verify --output-dir unreal/Saved/AureateDetailV3
python -m unittest discover -s unreal/Tests -p test_aureate_detail_v3.py -v
```

Dedicated GitHub CI validates all four material sections, actual glTF BIN attributes and triangles, deterministic hashes, safe output refusal, original V2 byte identity, exact source authority and absence of Unreal/gameplay mutations.

## Native review acceptance gates

1. Generate exact V3 hashes in a detached source worktree. Import to **two fresh empty isolated Unreal review folders**, never overwrite the existing ship components or accepted reference.
2. Retain `V2_Skyborne_Assembly_V1`; save a **new** `V3_Skyborne_Details_Studio` map with four fairing visual actors and one interior actor. Keep all four existing wings and structural supports. This is an isolated **StaticMeshActor layout**, not a compiled native wing-rig gameplay actor.
3. Check real Unreal centimetre bounds, native materials and geometry visibility. Capture the same four camera views at 1920×1080 D3D11, verify PNG bytes, compare against V2 and the approved art. Visible details are required; a code-only proof is insufficient.
4. Art still needs an approved sculpt, wing articulation and root fairing geometry integrated with the ivory/gold hull, usable bridge interior, real lights and material translucency, crew scale and physical/collision verification. No automatic production admission.

**Preserve** earlier screenshots and `.umap`; `Orbiter` stays story-locked; no releases or merges without review.
