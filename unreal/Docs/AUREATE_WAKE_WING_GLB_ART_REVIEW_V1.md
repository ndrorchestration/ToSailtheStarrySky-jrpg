# Aureate Wake — Procedural Dragonfly Wing GLB Art Review v1

## Unit-scale correction — 2026-10-31 (v2 asset supersedes v1)

**Do not import the original v1 GLB:** its unscaled numeric coordinates represented 280 centimeters but the glTF 2.0 specification defines positions in meters. Depending on the importer this could produce a 100× oversize wing. Old v1 GLB SHA-256: `6d9a8f24482637378a909c0051ae8547e1a22965919dcaaba5c21d6ca8fc3e7e`, **RETIRED FOR IMPORT**. The generator now serializes every source-centimeter position in meters (factor 0.01), retains unit normal vectors, and includes exact GLB scale regression tests. New glTF body span: 2.8 meters, brass root extends 0.16 meters behind root; overall X bounds approximately -0.16 to +2.804 m. Unreal imported visible bounds should therefore be ~296.4 cm before editorial pose scale (native confirmation pending). Rebuild with the updated script rather than importing the old downloadable v1 package.

**2026-10-31 / Status:** source-built 3D asset study; NOT an approved ship mesh, not a native Unreal render, no gameplay incorporation.

## Why this work
The existing [four-form wing actor draft #610](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/610) has a placeholder Cube wing and procedural thin OBJ shell source; its original flat venation PNG study is insufficient for the desired close-up cinematic look. This new package **reuses the same +X root-to-tip geometry algorithm**, builds an actual GLB review candidate with raised closed volumetric venation, a three-ringed brass hinge, and textured cyan-teal membrane. Three material groups let the brass veins remain legible independently of the membrane. PBR texture uses embedded RGBA albedo and glTF metallic/roughness factors. This is artistic lookdev, **not** a real metamaterial/solar sail simulation.

## Reproduce locally — Python 3.11, zero external packages

```powershell
py -3.11 -m unittest discover -s unreal/Tests -p "test_author_aureate_wing_glb.py" -v
py -3.11 unreal/Tools/author_aureate_wing_glb.py --output-dir C:\TSTSS_Review\WingCandidateV1
```

The generator refuses nonempty output directories. The output contains:

- `AureateWake_Wing_Lookdev.glb` — glTF 2.0 binary mesh, three material primitives with embedded RGBA PNG, in a single self-contained artifact.
- `AureateWake_Wing_Albedo.png` — 1024×512 source appearance image, not a dedicated Unreal shading network.
- `AureateWake_Wing_Manifest.json` — deterministic mesh triangle/vertex counts, SHA-256 checksums, no approval claim.

Generated model geometry is **one wing**, not four separate wings. The canonical ship must continue to maintain exactly **four** independent persistent wings. This generator does not implement Moon Bridge transitions or gameplay access.

## Current automated verification

The offline source unit suite asserts glTF JSON/BIN lengths and padding, buffer alignment, image PNG chunk CRCs, image dimensions, membrane/vein/hinge manifoldness and consistent winding, deterministic bytes, file SHA-256 receipts, authoring dimensions and refusal to overwrite existing output files. These source QA results do **not** replace Unreal Engine validation.

Local geometry inspection using an independent Python trimesh parser verified that the three exported primitives can be parsed as closed, consistently wound meshes, after correcting inconsistent face winding inherited from the earlier membrane topology. Local evidence is relevant only to this generated output, not compiled Unreal.

## Unreal review and integration gates

1. **Source identity:** verify the generated manifest SHA-256 for GLB and albedo. Do not commit source concept references from private artwork, and do not call these files creator-approved.
2. **Review import:** in Unreal Engine 5.8, use Interchange Content Browser Import for GLB into `/Game/TSTSS/Review/ShipArt/WingCandidateV1`, not existing production character/ship folders. Confirm three material sections and one StaticMesh, correct glTF +Y-up conversion and Unreal +X root direction. Check that the imported alpha-translucent material is legible at close/mid/far distances; rebuilding as a proper UE material is still required.
3. **Pivot/scale blocker:** `AAureateWakePreviewActor::WingPose` in #610 uses transforms designed for 100-cm centered Engine Cube meshes. This new wing is 280-cm **root-pivoted** geometry with a -16-cm hinge. **Do not directly assign it to `AuthoredWingMesh` and claim it fits!** The actor needs an authored-wing-specific pivot/scale/pose adapter with correct port/starboard outboard vector, fore/aft root hinge positions, all four forms and collision clearance. That adapter is a separate next gate.
4. **Material gate:** build a UE master material for the membrane and preserve brass material slots. Expose time-of-day iridescent response, bevel-smooth highlights, texture quality/streaming and a slow `OrbiterSailBlend` review hook only after its authoring is verified; do not activate Orbiter gameplay.
5. **Cinematic visual QA:** 1920×1080 fixed camera side-by-side against the approved ship visual bible, verify four-wing silhouette and geodesic forward bridge with complete hull geometry, profile from above/side/underside, acceptable aliasing/transparency, no clip through bridge or deck. Record exact SHA, native engine, frame timing and creator acceptance.

## Creative protection

- Aureate Wake exterior and interiors are not approved by this one asset.
- Never expose the hidden Moon Bridge via render gameplay/UI by default; previews require explicit owner-controlled isolation.
- This asset does not cause sea-contact, buoyancy, story milestones or crew growth.
- The source is deterministic and freely locally reproducible; no free credits or external service accounts required.
- Approved October 30 cast artwork is untouched. Ender/Ionia model creation and native importer remain separate P0 work.

**References:** [Unreal glTF and GLB format support](https://dev.epicgames.com/documentation/unreal-engine/gltf-file-format-support-in-unreal-engine), [Unreal Interchange import reference](https://dev.epicgames.com/documentation/unreal-engine/interchange-import-reference-in-unreal-engine).
