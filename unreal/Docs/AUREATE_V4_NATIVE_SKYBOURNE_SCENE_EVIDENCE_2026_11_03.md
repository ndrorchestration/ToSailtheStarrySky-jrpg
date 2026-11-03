# Aureate Wake V4 — Native Skybourne pilot and hero scene
**Separate subsequent sibling work:** The same isolated Unreal5.8.4 sandbox now contains **three additional saved noncanonical review maps**: Seabourne (20 actors), Submersible (15), and private static Starbourne (14), in addition to this genuine Skybourne (18). Exact checked hashes and level boundaries are in [all-four evidence](AUREATE_V4_ALL_FOUR_NATIVE_REVIEW_MAPS_2026_11_03.md). No V4 GPU screenshot has been captured; no Starbourne player unlock or production scene promotion.


**Date:** November 3, 2026. **Scope:** one noncanonical ship in isolated Unreal 5.8.4 development sandboxes, not the playable game. This supersedes the old headless actor-spawning blocker only for the full Editor execution method. No review art promotion or Starbourne player access.

## Native full Editor single-actor proof — PASS

- Exact native engine: 5.8.4-58902052+++UE5+Release-5.8.
- New disposable project: C:\tmp\TSTSS_AureateV4_ActorPilot_20261103\AureateActorPilot.
- Method: full Unreal Editor ExecutePythonScript startup with NullRHI, not the fast headless PythonScript commandlet.
- Result: ONE_ACTOR_PILOT_NATIVE_PASS, process exit 0, one actual StaticMeshActor and saved map. SHA-256: 3dc35f6deedee2b34dce7b59016deccc15cfe5f0c78f0b8355ca34711604f6d1.
- An initial preflight refused to launch with under 4.2 GiB free RAM. After browser tabs were reduced, the guarded native test succeeded, without altering the user's active Editor.

## Native Skybourne V4 scene assembly — PASS (not GPU rendering)

- Existing disposable V4 import sandbox with five previously verified native StaticMeshes.
- Separate full Editor method with NullRHI; a NEW level only, no production level write.
- Result: SKYBOURNE_STAGE_NATIVE_PASS, process exit 0, one saved native UE5.8.4 scene at /Game/TSTSS/Review/Scenes/AureateCinematicV4_Skybourne_Hero_20261103_FullEditor.
- Saved map SHA-256: **16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40**.
- **18 actors**: shared hull proxy, V4 imported shared trim, central living quarters proxy, forward geodesic bridge proxy, open observation deck proxy, four membrane proxy actors paired with four actual V4 imported wing-filigree mesh actors, four role cameras and one directional key light.
- Wing identity slots are exactly FORE_PORT, FORE_STARBOARD, AFT_PORT and AFT_STARBOARD. The paired visual/detail layers are not extra principal wings. Four camera labels: THREE_QUARTER, TOP, PROFILE and BRIDGE.
- The actual imported V4 mesh candidates used here are SharedExteriorTrim and SkybourneWingFiligree. All of the hull/dome/quarters sizes and wing angles are temporary visual proposals. No rotation mechanics, continuous swept clearance, physical simulation, accepted human scale or final creator visual approval.
- Evidence receipt remains on the workstation at C:\tmp\TSTSS_AureateCinematicV4_Native_20261103\full_editor_skybourne_stage_receipt.json. These generated Unreal asset files are NOT committed and should never be portrayed as production art.

## Native D3D11 Skybourne screenshot — HOLD

Three distinct events, all without an accepted PNG:

1. First D3D11 run completed engine startup but a false-negative scripted precheck searched for a nonexistent WING_ prefix on wing labels, despite the scene correctly storing four named wing identities. Host receipt marked NATIVE_GPU_CAPTURE_NOT_VERIFIED. Fixed the source check to match the exact four labels. No screenshot.
2. Corrected second launch was refused by the 4.2 GiB free-RAM preflight. No native process launched.
3. Third corrected D3D11 run, attempt review03, launched with about 5.53 GiB available but GPU startup caused a low-RAM watchdog stop. Host reported exit 1, no native screenshot receipt, no PNG and STOPPED_BY_TIME_OR_MEMORY_WATCHDOG. Runtime approximately 19 seconds was far below the 170-second timeout. The runner stopped only its own child. A later independent SHA read proved the saved Skybourne map unchanged at 16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40. No orphan commandlet remained.

**GPU-only safety correction:** require **6.5 GiB free RAM before GPU launch**, monitor with a **1.5 GiB free-RAM stop threshold**, keep a separate attempt-token log/receipt. Lightweight NullRHI Editor staging retains its previously proven 4.2 GiB preflight. Do not lower resource limits or terminate unrelated user software just to force a screenshot.

This checkpoint does not produce a V4 native image, so the older independent black-sky issue #705 and creator art acceptance remain held. Prior other-form screenshots are not transferable as V4 GPU evidence.

## Development/dependency follow-through

- Draft PR #732: https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/732. Old exact-head baseline 3859663cc30d70ca0feea7fa9580ae734cf1d6ab included five native StaticMesh import readbacks and 19 source/safety tests plus seven hosted workflows; the new staging and GPU evidence is a separate head requiring separate CI.
- Add full Editor pilot, one-form staging, D3D11 capture script and resource-gated runners as source-only review code. Preserve raw failed native logs and all receipts separately, outside Git. No Unreal assets, licensed binaries or user images are committed.
- Pure Python generators and deterministic four-form layout plan need no new pip package. Unreal editor plugins remain confined to isolated review projects. No production engine, C++ gameplay module, npm package/lock, SaveGame schema, player gate or protected main change.
- Separate unmerged approvals: wing/foil #724/#695, central coupled bridge and quarters #702/#706, auroral/ocean #705 and original creator-approved four-form art.

## Next smallest safe step

When available free RAM is at least 6.5 GiB and disk space at least 14 GiB, take exactly one GPU screenshot against the checksum-pinned Skybourne map with a **new unique attempt token**, independently inspect PNG dimensions, hash, color distribution and silhouettes. If valid, move to comparative Seabourne/Submersible scenes and private Starbourne visual studies. Starbourne developer work is OPEN but its player story/reveal gate stays CLOSED. Never equate a passing source or asset test with cinematic/model approval.
