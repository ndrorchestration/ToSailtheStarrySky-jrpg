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


## Subsequent progress — independently verified Harbor recovery intake

The original PR #766 Harbor sandbox remains a native staging HOLD, but that is not the only evidence available. Separate isolated workstation directory C:\TSTSS_EnvironmentHarborRecovery_20261105 contains an already saved UE5.8.4 Harbor review World and independent native readback receipts. Do not erase or relabel either original workspace's historical receipts.

Read-only recovery facts:
- Source recovery commit 7c3293babc8d4b39c4d99696ff302211f27028c5.
- Saved Harbor World SHA256 073edd19e7ebdcee48b65fb3428fb19d8c8b8c6ca1b95cc4c6f04ed6ea4dd621.
- Actual Unreal Editor host stage exit 0, initial asset World hash preserved, original 34 actors plus 50 native Harbor actors.
- Separate Unreal Editor readback host exit 0 verified 84 actors and eight saved materials, with protected config hashes preserved. Not GPU/PIE verification.

New private asset transfer:
- Source implementation: unreal/Tools/transfer_first_wake_harbor_review.py.
- Only six required imported native cast/ship dependency asset groups, the native Harbor material directory, two .umap files and four private stage/readback receipts were allowlisted.
- Strict exact source head, original stage/readback hash and actor-count checks; path traversal and Starbourne/Submersible source directories are explicitly refused. Copy uses new-file-only writes and verifies SHA256.
- Actual transfer into the isolated object worktree: 92 private files, 7,137,822 bytes, SHA256 checks 92/92 PASS. No tracked production content, previous source data or user saves overwritten. Private custody receipt is local and untracked: unreal/Saved/FirstWakeSliceObjectsV1/harbor_private_intake_manifest.json.
- No local .uasset/.umap is uploaded to GitHub. The six previously staged ship/cast asset source mesh families remain noncanonical.

Further authoring: unreal/Tools/run_first_wake_slice_objects_readback.py is a separate host-controlled one-child native Editor readback launcher. It refuses non-exact source/map/receipt evidence, existing prior outputs, user Editor/LiveCoding conflicts, low physical RAM/disk, user saves, or altered tracked configs. The readback can report success only for a genuinely saved 115-actor object World with one PlayerStart, seven native milestones, 31 no-collision new props and 22 distinct native StaticMeshes, not source-only proxies.

Verification: focused source tests now include 8/8 original 3D GLB tests and 11/11 private transfer/readback contract tests, including negative mutations. Actual native 22-mesh import, object map save, independent native 115-actor readback, D3D rendering and PIE are NOT RUN.

Current safety blocker: NEONTIC had existing UnrealEditor.exe and LiveCodingConsole.exe running, so the guarded native object stage preflight returned HOLD_NO_EDITOR_LAUNCHED. Do not close or compete with those sessions. When naturally idle, run from the isolated worktree: py -3 unreal/Tools/run_first_wake_slice_objects_native.py --check, then --stage. After a successful real stage, run: py -3 unreal/Tools/run_first_wake_slice_objects_readback.py --check, then --readback. Each native gate still requires at least 5 GiB free physical RAM, 14 GiB C: free and exact receipt/config custody. Separate genuine player-POV D3D and PIE acceptance are mandatory. Do not merge draft #795 based only on source checks or a copied native Harbor World.
