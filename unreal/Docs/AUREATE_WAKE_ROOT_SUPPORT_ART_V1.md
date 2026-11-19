# Aureate Wake — Four-Wing Root Supports: 3D Asset and Unreal Visual Rig v1

Status: **SOURCE-BUILT REVIEW CANDIDATE, NOT PRODUCTION ART OR NATIVE UNREAL VERIFIED** (2026-10-31). Stacked upon [draft PR #626](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/626). Does not merge or release the playable Godot game or Unreal.

## Fixed design/visual problem

The existing 280-cm true-geometry wing starts at a root approximately ±112 cm across the hull, but the interim hull surface is around ±75 cm. The resulting ~37-cm **centerline lateral offset** had no structural connector. This increment creates **four independent animated hull-to-wing support components** and a single reusable, 100-cm long, GLB 2.0 review mesh (no extra wings).

The support is a telescoping **visual link**, not a physically implemented telescoping hinge or maritime structural engineering claim. Authored PBR lookdev has three material sections: blue-steel sleeve, polished brass couplers, and four pale blue luminous filaments. The 3D support asset includes actual closed tubular mesh geometry and details; no marketplace model, proprietary art or paid credits are required. The corrected generator emits glTF meters from source centimeters.

## Native Unreal visual behavior (coded; not yet compiled in Unreal)

- `AAureateWakePreviewActor` retains exactly four wing components and two hydrofoils and gains four separately named `WingRootSupport_1..4` `UStaticMeshComponent` entries on the same `VesselRoot`. They do not count as extra dragonfly wings.
- Each invisible-by-default support has collision disabled and never acts as a gameplay or landing trigger. Actor property `AuthoredRootSupportMesh` is optional. Support visibility requires **all**: `bUseRootPivotedWingPose`, `AuthoredWingMesh`, `AuthoredRootSupportMesh` and a non-Orbiter current form.
- Every `SnapToForm` and animated `Tick` updates four struts from a hull-side anchor at `(wingRoot.X, sign * 73 cm, 18 cm)` directly to the matching moving wing-root location. The support mesh extends along its local +X axis from 0 to 100 cm; C++ rotates it toward the endpoint and scales the local X axis to the required length. That covers the ordinary forms without a second ship animation authority.
- No story unlocks, Moon Bridge access, contact/buoyancy/sea-landing physics, character appearances, class changes, combat, save-state changes or release behavior. Original centered Cube wing preview is unchanged unless true wing and root-pivot mode are deliberately enabled.
- Authored-wing transitions to and from Orbiter remain blocked by the previous actual-geometry clearance finding, even if the hidden-mode preview is explicitly opted into. The Moon Bridge remains canon but its mechanics/route require separate approval.

## Reproduce and inspect source GLB

```powershell
py -3.11 -m unittest discover -s unreal/Tests -p "test_author_aureate_root_support.py" -v
py -3.11 -m unittest discover -s unreal/Tests -p "test_import_aureate_root_support.py" -v
py -3.11 unreal/Tools/author_aureate_root_support.py --output-dir C:\TSTSS_Review\RootSupportCandidateV1
py -3.11 unreal/Tools/import_aureate_root_support_review.py --check --glb C:\TSTSS_Review\RootSupportCandidateV1\AureateWake_RootSupport_Lookdev.glb --manifest C:\TSTSS_Review\RootSupportCandidateV1\AureateWake_RootSupport_Manifest.json
```

The output contains `AureateWake_RootSupport_Lookdev.glb` and `AureateWake_RootSupport_Manifest.json`. The generator refuses overwriting a nonempty directory. The import preflight checks GLB 2.0 length/chunks, SHA-256, noncanonical provenance, corrected linear scale, 1-meter local +X bounds, 3 material sections, normal/UV attributes and luminous detail. It **does not** attest visual beauty or physics.

Run the same importer with `--import-review` inside Unreal Editor Python **only** after enabling the appropriate Python and Interchange plugins. Import destination `/Game/TSTSS/Review/ShipArt/RootSupportCandidateV1` is isolated and an occupied destination is rejected. Do not import or modify existing canonical ship/art folders. Inspect import settings explicitly and the imported StaticMesh orientation, cm bounds, tangents, PBR/translucency, emissive energy, material slots, and shadows.

## Verified evidence

- [Hosted root art + importer workflow](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41185141591): source/build checks **SUCCESS**, 10 source art tests and 8 import-preflight tests, review asset archived with manifest. Native Unreal compile/render **NOT RUN**.
- Independent local Python `trimesh` loading of the actual archived GLB: three material primitives with 50, 200, 88 vertices; 96, 384, 160 triangles respectively. All three primitives were reported watertight and consistently wound; x bounds 0–1 meter. **This is model-geometry parsing, not a real-time in-engine screenshot or aesthetic acceptance.**
- End-point/strut-length algebra covers all four wing roots across all three ordinary forms and sampled transitions. A successful positioning calculation is not a physical strength/swept-volume/collision proof.

## Unreal scene acceptance gate

1. Confirm exact Unreal Engine 5.8 editor C++ compile, and verify `GetWingCount()==4`, `GetRootSupportCount()==4`, `GetHydrofoilCount()==2` in the test world.
2. Import the corrected wing GLB (wing-review gate), then the support GLB (independent support-review gate), each to its own empty review folder. Confirm source units and local pivot orientation, then set `AuthoredWingMesh`, `AuthoredRootSupportMesh` and `bUseRootPivotedWingPose=true` on an isolated `AAureateWakePreviewActor`; no production level writes.
3. Capture front, port, starboard, top and 3/4 views in Skyborne, Seaborne and Submersible. Test both directions for all six ordinary form transitions. Visually verify a convincing root bracket connection, no ferrule floating/gaps, no collision with geodesic bridge, no textures inverting on port, and no bad support elongation or aliasing.
4. Investigate a **known design limitation**: scaling the 100-cm support along X stretches or compresses the brass collars/filaments. If visual quality suffers, replace simple longitudinal scale with an actual two-piece articulated piston without changing player mechanics. No claim of truly telescoping physical geometry has been made.
5. Confirm memory/performance/visual quality, no accidental fifth wing, no gameplay sea-contact authority and default hidden Orbiter. Creator must explicitly approve visual style; technical source and CI success alone do not approve art.

**Next engineering action:** bring PR #625/#626 and this PR into an isolated *fresh* integration branch based on the newest foundation PR #608, compare with the already created `integration/unreal-aureate-reconcile-20261031`, then request native UE 5.8 build/capture from an accessible Windows host. Do not merge main or replace the existing Windows installer.
