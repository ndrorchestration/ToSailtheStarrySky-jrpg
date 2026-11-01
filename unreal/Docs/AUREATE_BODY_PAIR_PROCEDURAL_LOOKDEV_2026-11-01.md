# Aureate Wake — continuous-hull and geodesic-canopy offline lookdev pair

**2026-11-01 • Unreal 5.8.4 target • NONCANONICAL REVIEW SOURCE ONLY**

This asset-authoring slice sits on top of draft [PR #682](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/682) at `6bcb9b8c2cceefa361ca378a902f64bba205dc15`. It does **not** edit the existing Aureate Wake actor, gameplay, story, ship transformations or Orbiter gate.

## What has been implemented

`unreal/Tools/author_aureate_body_pair.py` generates **two independent, deterministic glTF 2.0 GLB review assets** with an exact SHA-256 manifest, using the existing tested wing GLB serializer and only Python's standard library:

- `AureateWake_HullCandidateV1.glb`: a long ~10.4m tapered white-ivory central hull, two gold sheerlines, a keel accent and a separate raised azure open forward deck. Three material sections. Origin is the original Unreal ship actor hull pivot; source units centimeters are corrected to GLB meters.
- `AureateWake_BridgeDomeCandidateV1.glb`: approximately 2.3m footprint panoramic hemispheric cyan translucent glazing, gold rib lattice with triangulated panels and an ivory lower collar. Three material sections. Local origin is for the ship actor's existing forward bridge component.
- `AureateWake_BodyPair_Manifest.json`: two exact SHA-256 checksums, separate allowlisted review intake destinations, coordinate scale, reference-image provenance and explicit noncanonical limitations. No runtime gameplay or cinematic acceptance.

The geometry is intentionally **procedural lookdev**, not a professionally sculpted and rigged production mesh. The approved original four-form 1536×1024 ship design image (SHA-256 `03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13`) remains an aesthetic reference, **not** a blanket art approval for this procedural pair.

## Generation and tests

From the repository root with ordinary Python 3:

```powershell
python unreal/Tools/author_aureate_body_pair.py --output-dir .review/aureate-body-20261101
python -m unittest discover -s unreal/Tests -p test_author_aureate_body_pair.py -v
```

The generator **refuses to overwrite a populated output folder**. Its helper already orients manifold surface winding. The test verifies deterministic identical bytes, exact GLB header/chunk integrity, two meshes, three material sections each, real-world centimeter-to-meter scale, 10.4m hull length, glass transparency, no-gameplay status and overwrite refusal.

The files above are generated *only* when running the script. The public GitHub PR contains **source and tests**, not falsely labeled actual UE import assets. After source validation, stage candidate GLBs in the two matching local Unreal review directories under `/Game/TSTSS/Review/ShipArt/HullCandidateV1/` and `/Game/TSTSS/Review/ShipArt/BridgeDomeCandidateV1/` using a separately verified import. Do not overwrite an occupied directory or automatically bind to a live game scene.

## Required native acceptance

1. Run the generator and check SHA-256 receipts; inspect manifoldness, normals and imported vertex counts.
2. Import both parts into an isolated Unreal 5.8.4 review project and check true cm bounds and +X/+Z orientation.
3. Compile the latest actor with `RefreshBodyReviewMeshes` and default-off display settings; run native `Automation RunTests TSTSS` at the exact head.
4. Render fixed camera angles for Skyborne, Seaborne and Submersible. Check silhouette against the approved design, deck connection to dome, gold rib shape, glass transmission, wing-root geometry, and the latest hydrofoil struts.
5. Test all six ordinary directed form transitions for continuous swept interference and hull/bridge obstruction. Static screenshots alone do not prove safe motion.
6. Keep Orbiter locked, all art review-only, no protected merges or public release without creator authorization.

**Workstation condition:** `neontic` remains offline at authorship; no native UE compile, actual editor import or D3D12 screenshot was achieved in this slice. Hosted source validation is not native Unreal verification.
