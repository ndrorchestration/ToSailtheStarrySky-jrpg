# TSTSS First Wake — bounded 3D vertical-slice object construction

**Scope:** Prelude harbor and hiring → Aureate Wake engineering/bridge → flight equipment and emergency splashdown. **Authority:** original GLB source art built on NEONTIC and tested; NOT imported into Unreal, NOT native-rendered, NOT playable-verified, NOT canonical-art approved, NOT merged.

## What exists

Source: isolated review/ue58-vslice-objects-20261110 branch at C:\TSTSS_VSliceObjects_20261110, based on existing harbor draft PR #766 head 5469084559ab18569823204d07aee61fbff97634.

The original procedural source-art generator (unreal/Tools/generate_first_wake_slice_objects.py) defines **22 multi-part static-mesh prefabs** and **31 visual-only placements**. They are serialized as 22 original, deterministic **glTF 2.0 GLBs** in unreal/ArtSource/VerticalSliceObjectsV1/ (24,092 triangles total, about 2.7 MB) with multiple physically-based material roles, normals, UVs and manifest SHA-256 values.

| Narrative function | Constructed object prefabs |
| --- | --- |
| Harbor opening | MooringBollard, MooringCleat, HarborLantern, CargoCrate, RopeCoil, FlyerPodium, CaptainDesk, GangwayAnchor |
| Engine inspections | EngineeringWorkbench, LiftResonator, PressureRegulator, ReserveTank, SignoffPlinth, HarmonicEngineCore, ToolRack |
| Bridge and vessel detail | BridgeHelm, BridgeOrrery, DeckRailModule, GeodesicJunction, WingHinge |
| Emergency flight and landing | EmergencyBeacon, FlotationBuoy |

Reuse, DO NOT duplicate: PR #752's private native Aureate Wake and static Ender/Ionia review models, PR #766's 47 harbor set-dressing actors, and the existing seven native interaction milestones and PlayerStart. New object meshes have no collision and no authority to write story, disk SaveGames, physics, water contact, class or spell unlocks. The 3 distinct interactive engineering marker actors remain authoritative; object geometry is visual accompaniment only. No premature Lyra encounter, Wise Woman, Reson/Aepex recruitment, full planetary level, Starbourne unlock, post-splashdown city, or full combat area.

Materials are original hard-surface *review* styles: patinated bronze/brass, dark iron, wood, canvas, porcelain, teal/amber glass and ruby indicator. Model parts include concentric rings, handrails, gauge housings, rivets, mechanical spokes and ship bridge fittings. Planar UVs are authored to enable subsequent texturing. Finished production PBR textures, animation, wear/decals, lighting and high-fidelity mesh replacement require native art QA.

## Exact next native import stage — currently HOLD

1. Native PR #766 harbor map MUST first exist as a verified saved UE5.8.4 World with matching native_harbor_stage.json receipt. Its source-only harbor recipe does not satisfy this gate. The 84-actor parent map and receipt may be copied to their same relative paths in this new sandbox only after checking original hashes and ensuring no collisions.
2. The guarded runner unreal/Tools/run_first_wake_slice_objects_native.py --check refuses wrong branch/root, dirty tracked files, wrong UE version, missing parent World/receipt, existing outputs/SaveGames, competing Editor/LiveCoding, RAM below 5.0 GiB or C: disk below 14 GiB. It never shuts down a user's Editor.
3. When and only when admitted, running the same tool with --stage creates Unreal StaticMesh assets in /Game/TSTSS/Review/Objects/FirstWakeSliceV1 and a **NEW** scene /Game/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1. Original maps, 84 actors, seven native E interaction targets, one PlayerStart and sea physics must remain unchanged. Expected new World actor count = **115** (84 inherited +31 new visual props). The operation requires imported single StaticMesh per source GLB, preserved source+config hashes and no collision on new props.
4. A later separate native world readback, real GPU screen captures, actual PIE movement/interactions, float physics and creator visual acceptance are mandatory; no source pass substitutes for these.

## Exact verified status — 2026-11-10

- Generated 22 original GLB files with 24,092 total triangles and 31 placement records, plus manifest and source generator; generated file hashes checked.
- Ran **8/8 focused source/GLB integrity unit tests: PASS**. Engine-free stage --validate: PASS with explicit NATIVE_OBJECT_IMPORT_NOT_RUN status.
- Physical RAM approximately 3.6 GiB free, below guarded native UE staging minimum; original native Harbor stage prerequisite also unavailable in this isolated sandbox.
- **Not performed:** UE asset import, native map save, second-process readback, Unreal automation/PIE, genuine D3D render, physical water landing, production art promotion or merge. Review branch only.

Coordination/authority: TSTSS P0 owner issue #754; existing harbor PR #766; asset assembly PR #752. Preserve all locally held original binary assets, SaveGames, config hashes and provenance. Do not combine these source-only review claims with native evidence from another commit or worktree.
