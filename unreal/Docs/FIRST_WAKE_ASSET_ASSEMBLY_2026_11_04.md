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
