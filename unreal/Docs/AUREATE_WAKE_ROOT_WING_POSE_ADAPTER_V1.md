# Aureate Wake — root-pivoted wing geometry adapter v1

**Status:** source candidate only. Unreal 5.8 native C++ build, map/transform screenshots and clearance testing **PENDING**. Do not merge or release from source-level tests.

This draft is stacked atop the authored wing GLB [PR #625](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/625) and the First Wake review benchmark [#622](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/622). The ship actor remains one `AAureateWakePreviewActor` with exactly four wing components and two Seaborne hydrofoils. No new ship runtime authority.

## New integration path

- `bUseRootPivotedWingPose = false` by default, preserving all legacy 100-cm-centered Cube preview positions.
- When `AuthoredWingMesh` is present **and** `bUseRootPivotedWingPose` is explicitly enabled, `WingPoseForMesh` selects a root-pivoted arrangement authored for the current **280-cm +X span** asset.
- Front roots at approximately +155 X, aft at -180 X; port and starboard roots at +/-112 Y; four wing roots, not four overlapping 100-cm preview cubes.
- Skyborne: wings project broadly outboard with distinct forward/rear sweep. Seaborne: wings fold above the waterline in review only. Submersible: wings tuck lengthwise and remain visible. Orbiter: four equal-scale sails directed +Z, -Z, -Y and +Y with forward hull/bridge unchanged.
- `RefreshWingMeshes()` recomposes existing form after new artist mesh assignment when not transitioning; both `SnapToForm` and transition interpolation use the mesh-aware pose. A missing authored wing refuses new form changes while the opt-in flag is true.
- The old `bAllowOrbiterPreview=false` default and `RequestForm` preview guard remain untouched. The hidden form is not a player unlock.

## Mandatory Unreal/native acceptance

1. Build the exact PR head with the UE 5.8 Windows C++ toolchain and correct all compiler/Unreal API errors.
2. Import the generated one-wing GLB to a distinct review path. Verify it imports as a StaticMesh with three material slots, correct Unreal axis and unit handling. Set `AuthoredWingMesh` on an isolated preview actor and **manually** opt into `bUseRootPivotedWingPose`.
3. Compare the legacy Cube preview with authored wing at the same actor transform, test all four Sky/Sea/Submersible/Orbiter modes in an isolated test level, respecting Orbiter opt-in; visually inspect **all four wing root joins**, bridge/deck clearances, wing intersections, foils, scale, imported alpha and silhouette.
4. Repeat transformations in both directions and interrupt mid-transition; confirm no popping/interpenetration after refresh, and no story sea-contact or flotation event emitted by form requests.
5. Capture actual UE 5.8 rendered screenshots (not generated geometry previews), with fixed cameras, engine SHA and frame-time traces.
6. Get creator aesthetic approval and independent native physics QA before considering promotion into the playable First Wake.

**Limitation:** Current poses are review geometry guesses, NOT physically engineered hinge kinematics, seaworthy sealing, buoyancy or a cinematic art pass. User-approved art and ship design still govern all final proportions.

[Unreal wing art GLB review document](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/blob/feat/unreal-aureate-wing-glb-artpack-v1/unreal/Docs/AUREATE_WAKE_WING_GLB_ART_REVIEW_V1.md)


## Corrected asset import gate — October 31, 2026

The original wing v1 GLB is **retired for import**: it encoded centimeter geometry as glTF meters and could appear **100× too large**. The [corrected generator](../Tools/author_aureate_wing_glb.py) writes positions in meters (0.01 × source-centimeter coordinate), preserving unit normals. Expected full X bounds are approximately -0.16 to +2.804 meters (about 296.4 cm including the rear brass hinge). The prior v1 GLB is not valid review input.

New [fail-closed review importer](../Tools/import_aureate_wing_review.py) and [import regression tests](../Tests/test_import_aureate_wing_review.py) check the exact corrected manifest SHA-256, glTF meter-scale metadata, 2.8-m membrane span, 3-section material layout and empty candidate destination.

Offline check (can run without Unreal Engine):

```powershell
py -3.11 unreal/Tools/import_aureate_wing_review.py --glb "C:\\TSTSS_Review\\AureateWake_Wing_Lookdev.glb" --manifest "C:\\TSTSS_Review\\AureateWake_Wing_Manifest.json" --check
```

Editor-only workflow: enable Python Editor Script Plugin and Unreal Interchange, run the same script inside Unreal Editor Python with `--import-review` instead of `--check`. The editor must present its pipeline options for explicit operator inspection; destinations with existing assets are refused, and no actor/map is modified. Validate imported centimeters, Z-up conversion, normals, mesh sections, material transparency and pivot before manually linking to `AuthoredWingMesh` in an isolated map. **Unreal native execution NOT VERIFIED; source checks cannot satisfy this acceptance gate.**

Source references: [Khronos glTF 2.0 units](https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc); [Epic Unreal Interchange import](https://dev.epicgames.com/documentation/unreal-engine/importing-assets-using-interchange-in-unreal-engine).

## Four-wing sampled geometric regression (2026-10-31)

An actual corrected 2.8-m wing GLB revealed an unsafe authored-wing route: naïve eased quaternion interpolation from ordinary forms to hidden Orbiter sends facets through the temporary hull/bridge proxies. The default Orbiter unlock/reveal remains disabled, and **authored-wing transitions into or out of Orbiter are now explicitly rejected in `RequestForm`** even if the separate preview opt-in is enabled. The existing cube-only preview remains independently gated by `bAllowOrbiterPreview` for review use. This is a reversible safety hold, **not** a cancellation of the story-locked Moon Bridge.

The previous `RefreshWingMeshes` could select a 280-cm root-origin mesh while still using centered 100-cm Cube transforms. It now shows `OriginalCubeWingMesh` unless both `AuthoredWingMesh` and `bUseRootPivotedWingPose` are explicitly selected; `RefreshWingMeshes` reapplies the existing pose only while not transitioning. This preserves the unmodified default scene and prevents malformed oversized wing presentation during accidental asset assignment.

A reproducible, dependency-free **offline** audit `unreal/Tools/audit_aureate_wing_clearance.py` reads source SHA-256-verified GLB geometry and compares the C++ constants to the three ordinary forms. It checks all **six directed** transitions at multiple discrete times using transformed vertex bounds and cuboid proxies: hull X ±400/Y ±75/Z ±32.5 cm; bridge at (240,0,95) with half-extents (105,55,55) cm. Wing/wing envelope overlaps are checked too. In local testing with 1,240 sampled source vertices and 13 time samples per transition, no ordinary route violated the conservative 10-cm clearance threshold; minimum box clearance ~19.94 cm and minimum wing/wing AABB separation ~189.85 cm. Hosted [workflow #41183423514](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41183423514) **SUCCESS** for source/tests and generated GLB audit at commit `4f5c71338f351f49290b0bf0a88effaa9ca77b53`. GitHub artifact includes a machine-readable clearance report.

**Still not cleared:** geometry samples and temporary convex boxes are *not* continuous-time swept collision proofs, physically engineered hinges, or gameplay. The root hardware also sits approximately **28 cm from the current provisional hull side** without an approved connecting spar. Do not close the artistic/engineering gate until a real bracket and hull geometry are authored, the four form transitions run and render in UE 5.8 Windows, and the user reviews accurate cinematic images. Do not confuse a valid trial rig with final ship art.

Run source-only:

```powershell
py -3.11 unreal/Tools/audit_aureate_wing_clearance.py --glb "C:\\TSTSS_Review\\AureateWake_Wing_Lookdev.glb" --manifest "C:\\TSTSS_Review\\AureateWake_Wing_Manifest.json" --cpp unreal/Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp --header unreal/Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h --samples-per-primitive 900 --steps 20
```
