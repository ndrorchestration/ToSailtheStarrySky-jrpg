# First Wake asset assembly — native staging handoff (2026-11-04)

## Intent and authority
Stage **existing imported Unreal assets** in an independent level containing the First Wake V2 seven-stop gameplay foundation. This is **NONCANONICAL / REVIEW-ONLY**. Source parent: draft PR #750 plus its local native-map verification fixes, at `11063930de397c056b5058a048af88be96c804b1`. Not a production level, not an art promotion, and **not a playable acceptance**.

## Worktree and assets
Disposable isolated workspace: `C:\TSTSS_AssetAssembly_20261104`; source `C:\TSTSS_GameAssembly_20261104` remains untouched.

Native packages copied into the disposable game's `Content` with their original `/Game` paths, from:
- Ship V4 native review sandbox: `C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\AureateCinematicV4Sandbox\Content\TSTSS\Review\ShipArt`.
- Ionia and EnderV2 native static mesh lookdev: `C:\TSTSS_CastAllSandbox_20261101\Content\ArtLookdev\Characters`.

Copied assets remain local/unmerged. These include Aureate Wake shared trim, four authored leaf wings, curved quarters, geodesic dome and **hull proxy**, plus Ionia and Ender static mesh review models. The ship hull is **not approved** final geometry; these character static meshes are **not rigs, animation assets, or playable pawns**. The gameplay input still controls the original ExplorerCharacter proxy.

## Native staging procedure
`unreal/Tools/stage_first_wake_asset_scene.py` runs within Unreal 5.8.4 in the named isolated workspace. It reads existing native StaticMeshes, requires actual material slots, duplicates the original First Wake V2 map into `/Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW`, and adds 10 no-collision asset actors.

The new World retains the original seven ordered interactive milestones and one PlayerStart; the ship is offset toward the visual ocean and Ionia placed beside the hiring marker. EnderV2 is an explicitly labeled **static model review**, not a second player character. Only the original ExplorerCharacter has actual movement and interaction bindings. No NPC dialogue, combat interaction, rig or AI behavior is implied by art staging.

The script refuses an existing destination or receipt, checks the exact original V2 .umap SHA-256 `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`, checks for protected save files, and verifies unchanged configs and base map after staging. The native stage verifies current-session actor identities and saves a new World. **Independent saved-map reload and milestone/asset readback require a separate Editor process** before reporting native-map acceptance.

## Claims and gates
A successful native map save proves the **real asset packages were loaded and a new review map was serialized**; independent reload, visual acceptance, and gameplay are separate gates. The next gates are:
1. Launch the **new map** in a disposable Editor session with sufficient RAM and screen capture. Confirm the actual rendered meshes and believable scale/lighting, camera obstruction, human-height readability and the distinction between static Ionia/Ender and the playable proxy.
2. Run real **Play in Editor** WASD/mouse, E, J, F5/F9, complete the seven-stop order, and validate save isolation. Do not import old exact-head receipts for this new map.
3. Author actual skeletal Ender rig, animation and staff grip, and a real Ionia conversation trigger attached to current milestones before declaring character integration.
4. Attach one player-controlled combat encounter and preserve class/job/equipment ownership checks and save schema. No automatic class unlock or new combat canon.
5. Review physical ocean, ship clearance/scale, cinematic lighting, contrast, character likeness and performance in native captures before art sign-off.

**HOLD:** Launch and Splashdown scene transition, actual seawater/hydrofoil physics, class UMG interactivity, Ender skeletal animation, Ionia dialogue, cinematic-quality weather/atmosphere, Starbourne player gate, main merge and release. Treat all existing character/ship packages as unapproved review assets unless separate creator approval establishes canon.

## Safe native command (separate from graphical review)
With no other Unreal Editor open and a clean tracked source snapshot, run from the isolated workspace:

```powershell
python C:\TSTSS_AssetAssembly_20261104\unreal\Tools\run_first_wake_asset_stage.py
```

The launcher requires UE 5.8.4, at least 5 GiB free RAM for **NullRHI** and 14 GiB free disk, verifies each source-to-sandbox native `.uasset` SHA, protects project configs and stops its own Editor process if RAM or elapsed-time guards are tripped. It refuses to overwrite earlier receipts. Native and host output go to `unreal/Saved/AssetAssemblyEvidence/`. A successful script produces only a saved and reloaded Unreal World, **not** a graphical screenshot or Play in Editor acceptance. The separate 6.5 GiB graphics gate is not relaxed by the NullRHI-only process.

## Preserved failed attempt and V2 correction
The original stage attempt, exact source head `ab70e4a1301869a2616adcd900eb1c90dd69910a`, terminated with native Unreal Editor **exit 3 / World Memory Leaks**, while loading a duplicated World in the same Python frame that retained World/Actor references. Original .umap and config SHA checks survived; **no new .umap existed** afterward. Its failed log and host HOLD receipt are retained under `Saved/AssetAssemblyEvidence/` (original filename without `v2`). This is an observed native failure, not a PASS.

V2 instead uses Unreal's `LevelEditorSubsystem.new_level_from_template()` to create and open the V2-derived map in one operation, and **does not reload that map from its own staging Python frame**. It uses new, non-overwriting `*_v2_20261104` receipts and a separate destination map ending `_REVIEW_V2`. A second independent native process must verify reload before success is claimed; the source tests cannot substitute for that test.

### V2 preserved failed attempt and native map diagnosis
V2 `new_level_from_template()` **did create an independent 24-actor native map** (`..._REVIEW_V2.umap`, SHA-256 `8c987699d7b069cae72b61acbb0a049dfb04219d6c8cb5933e948aa7e3ac540b`), and the full Editor exited 0. The source script correctly withheld PASS because its milestone filter counted both `TSTSS_PRELUDE_REVIEW_FlyerDiscovery` and `TSTSS_PRELUDE_REVIEW_SIGN_FlyerDiscovery` as matches (suffix collision). A separate native `UnrealEditor-Cmd` read-only diagnostic loaded that saved template map and observed **24 actors**, including the milestone and associated sign. No asset actors were added in V2. V2 host HOLD and log are preserved. V3 fixes actor selection by full exact label (`TSTSS_PRELUDE_REVIEW_<Stop>`) and creates a third, unique map and receipt without overwriting V1/V2 evidence.

## V3 native asset assembly — verified local evidence (November 4, 2026)

The V3 run at exact stage source HEAD be9bc0e42d3cdf4f52a5c6bc3bcc8273a0d7e94d completed using **Unreal Editor 5.8.4 / NullRHI** with process exit **0** and a saved 74,293-byte review map, /Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3. Its SHA-256 is 54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5.

The ignored native receipt is Saved/AssetAssemblyEvidence/first_wake_asset_scene_native_v3_20261104.json; the host receipt is host_asset_stage_v3_20261104.json. They record **10 newly staged noncanonical StaticMesh actors**, preserved original map and config digests, and no saved-map reload/PIE/GPU/Starbourne access during staging.

### Separate native saved-map readback

A **second UnrealEditor-Cmd 5.8.4 NullRHI process** loaded the exact saved V3 map, exited **0**, and produced Saved/AssetAssemblyEvidence/first_wake_asset_scene_readback_v3_20261104.json with status INDEPENDENT_NATIVE_SAVED_WORLD_READBACK_PASS_NOT_PIE.

- **34 native actors:** 24 inherited First Wake actors plus 10 visual assets.
- All **7 exact reflected TSTSSMilestoneActor** labels and one PlayerStart survived.
- The 10 staged StaticMeshActors have independently verified expected native mesh paths and **collision disabled**: four authored wing leaves, V4 hull trim, bridge, quarters, an unfinished hull proxy, static Ionia and static EnderV2.
- No Starbourne actor exists in the resulting map. Original and new saved map SHA-256s as well as both config hashes remained unchanged during readback.

**Log-custody caveat:** The dedicated console redirect readback_asset_world_v3_native.log did **not** echo Unreal's logging sentinel, so the conservative initial PowerShell host check ended in **HOLD** despite successful process exit, valid 34-actor readback receipt and preserved SHA custody. The actual **Unreal project log** Saved/Logs/ToSailTheStarrySky.log does contain TSTSS_FIRST_WAKE_ASSET_MAP_INDEPENDENT_READBACK_PASS with matching map digest and actor counts. The console commandlet log separately confirms Python script executed successfully with 0 errors and 0 warnings. Keep this divergence on record; subsequent host verification must inspect both log channels.

The reproducible script is unreal/Tools/verify_first_wake_asset_scene_native.py. Its successful native execution used a byte-identical working copy under ignored Saved/AssetAssemblyEvidence/verify_asset_world_v3_readonly_native.py. New source commits are **not** retroactive native evidence for their new HEAD.

### Next observable integration gates

1. Render the V3 map in GPU Unreal with the >=6.5 GiB graphics RAM gate. Capture actual pixels, check crew scale, lighting, wing/dome occlusion, horizon and composition against approved references.
2. Perform a real **Play in Editor** walkthrough of the seven ordered First Wake interactions and test WASD/mouse, E, J, F5/F9 with disposable saves.
3. Replace proxy visuals only after authored Ender skeletal rig, facial likeness/hair, costume, sealed goggles and staff-grip review; create Ionia dialogue presentation driven by existing milestones.
4. Drive one encounter from real UI/controller with the existing class/equipment and combat foundation. Keep ship physics, Starbourne and save-schema changes separately gated.

**Binary custody:** All imported native assets, saved .umap worlds, screenshots and original source references remain local/untracked in the isolated workstation. Source and documentation only are proposed for GitHub review. No protected-main merge or release; none of the lookdev art has been promoted to canon.
