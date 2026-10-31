# Aureate Wake — Wing Mesh and Metamaterial Integration Gate

Status: C++ binding available in draft PR #610. No production wing mesh, material asset, UE compile, or render acceptance.

## Implemented source
- `AuthoredWingMesh` allows one validated reusable dragonfly wing static mesh to replace all four cube stand-ins, **without changing four-wing identity**. The authored mesh must use a consistent pivot and forward local X orientation; inspect scale and orientation in every form.
- `WingMaterial` feeds four dynamic material instances. Blueprint material must define scalar parameter `OrbiterSailBlend` (0 = atmospheric dragonfly membrane, 1 = Orbiter science-fiction photovoltaic / light-sail appearance). `BeginPlay` now calls mesh and material refresh.
- `GetWingCount` and `GetHydrofoilCount` expose inspection hooks; two hydrofoils remain Seaborne-only and all four wing components persist in Submersible.
- `bAllowOrbiterPreview` is false by default, not story progression authorization.

## Authored mesh requirement
A tapered, veined dragonfly-inspired membrane with gold structural spars and a non-rectangular organic profile. Four reusable physical wings with stable attachment and front-facing bridge. UV0 for surface cell topology; optional UV1 for moving iridescent vein mask. PBR proper roughness/normal/metallic textures required. Do not use opaque cube geometry as accepted wing art.

## Orbiter material design (not built yet)
Build an actual Unreal material using viewing-angle Fresnel iridescence and diffraction-like color shifts as a cinematic art-directed approximation, **not physically verified metamaterial simulation**. Blend atmospheric translucency toward high-tech photovoltaic cell texture + reflective light sail. Avoid excessive bloom, jagged shimmering / temporal aliasing; test from front, side, under and behind. Wings remain exactly four and equal size arranged up/down/port/starboard, no satellite dish ring or extra vanes.

## Editor QA
1. Compile UE 5.8 Windows Editor target. Spawn `AAureateWakePreviewActor` in isolated map and confirm wing count 4, hydrofoil count 2.
2. Assign reviewed wing static mesh and master material on a derived Blueprint, execute `RefreshWingMeshes` and `RefreshWingMaterials` if changing during PIE.
3. Test Skyborne → Seaborne and hydrofoil stow/deploy; Seaborne → Submersible and visible wing remnants.
4. With explicit preview opt-in, test Orbiter and 4 cardinal positions, positive X nose remains forward. Test reverse transformations.
5. Film captures and verify moving mesh pivot clearance, seam continuity, silhouettes, shader parameter evolution, and no texture warping.
6. Human visual acceptance is separate from passing source contracts; no merge into protected main without native proof.

Current implementation is a **noncanonical render scaffold** and cannot be called a finished ship model.

## Original procedural art asset — implementation checkpoint (October 31)

Source additions on draft PR #610:
- `unreal/Tools/generate_aureate_wing.py`: generate original OBJ, MTL, 1024px color and packed ORM maps with Pillow.
- `unreal/Tests/check_aureate_wing_geometry.py`: check UV/triangle indices, material slots and bounds.
- `unreal/Tools/import_aureate_wing.py`: guarded Unreal Editor OBJ/PNG import and procedural preview Material Graph with OrbiterSailBlend/Fresnel glow.
- `unreal/Tests/check_aureate_preview_source.py`: updated static expectations for four hull-hinged wings, Orbiter rotations, and art integration.

Reproduce asset outside Unreal (Python + Pillow required only for regeneration):
```sh
python -m pip install Pillow
python unreal/Tools/generate_aureate_wing.py --output wing_asset --resolution 1024
python unreal/Tests/check_aureate_wing_geometry.py wing_asset
```

Local generation and integrity checks completed: 6,584 OBJ vertices, 13,080 triangles, UV coordinates, 3 named materials, 2 PBR prototype textures. Local trimesh analysis found closed geometry with consistent winding. This is source/asset structural validation only.

To import in Unreal Editor after it is installed: enable Python Editor Script Plugin; set environment variable `TSTSS_AUREATE_ASSET_DIR` in the Editor process to the generated asset folder; execute `unreal/Tools/import_aureate_wing.py` inside Editor Python. The script refuses to overwrite an existing populated `/Game/TSTSS/Ships/AureateWake/PrototypeWing` folder. Assign mesh to actor `AuthoredWingMesh` and material to `WingMaterial` in a test Blueprint. `OnConstruction()` displays selected art in the editor; `BeginPlay()` applies dynamic blend control.

Unreal import, shader compilation, material quality, mesh smoothing, physical hinge clearances, cinematic lighting and four-form screenshots are NOT yet verified. The original model is root-hinged static geometry, NOT skeletal wing rigging or a final art-approved mesh. The edge-glow shader is an artistic Fresnel approximation, not actual spectral diffraction or photovoltaics. The hull and bridge remain BasicShapes. Keep Orbiter story-gated and do not merge/release on source results alone.
