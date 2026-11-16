# TSTSS hybrid JRPG encounters — native V2 review evidence

**Date:** November 11, 2026. **Review-only scope:** detached TSTSS enemy branch. Not a production map, canon approval or shipping feature grant.

## Source/asset custody

- Exact source HEAD when compiled, native-tested and map-authored: `c9d5fc2b9b49050585060cbc7b87921d3764c3d7`.
- Unreal Engine 5.8.4 Win64 Editor native build PASS; UHT/UBT completed successfully.
- Existing 32-name native automation suite: **32 passed / 0 failed / 0 not-run**, 32 unique full paths.
- Native suite local evidence: `unreal/Saved/MigrationEvidence/c9d5fc2b9b49-20261111T154547708Z-f7caf4d1/` (head, build log, automation log and AutomationReport JSON).
- Separate source-exact Win64 Editor build-only receipt: `Saved/MigrationEvidence/c9d5fc2b9b49-20261111T154505145Z-d8033262/`.
- New map: `/Game/TSTSS/Review/JRPGHybridEncounterReview_V2`.
- Repository asset: `unreal/Content/TSTSS/Review/JRPGHybridEncounterReview_V2.umap`.
- 305242 bytes, SHA-256 `df5be5fa9a1f66c890f37a05bfea068304bd3cdde025b33b06aa89dd2d395cc8`.
- Authoring status: `NATIVE_HYBRID_MAP_SAVED_NOT_PIE`; native UnrealEditor-Cmd returned 0 errors / 0 warnings.
- V2 native authoring receipt: `unreal/Saved/EnemyGalleryV2/hybrid-receipt.json` (local retained).
- Independent native reload/readback status: `NATIVE_V2_HYBRID_MAP_RELOAD_AND_GATES_PASS_NOT_PIE`; 0 errors / 0 warnings.
- V2 independent readback receipt: `unreal/Saved/EnemyGalleryV2/hybrid-native-readback.json` (local retained).
- Historical V1 battle-map SHA preserved `108c7582ef8f8073907fbd9d78bd7f487a98b5fb6df927335fadb0fb500f4250`.
- Historical V0 15-actor-gallery SHA preserved `deb70ffeecedf572c8bd5b2fab3a515e748d95d27fb2d31f8c0bef2f34c0a022`.

## Native V2 scene readback

- Exactly 15 existing enemy actors, 1 native battle console, 1 native walking exploration actor.
- Walking actor has C++ `UTSTSSJRPGEncounterDirector` component, its review-only opt-in enabled, required safe/noncanonical tags and its own camera.
- Physical test-floor, camp floor marker and camp label present once each.
- Native reflected methods for biome, party stage, encounter-rate and scripted-wave selection are present.
- Calling the return-to-exploration method before any battle is **denied**.
- Requesting a scripted encounter in editor non-PIE state is **denied**.
- Native reloading did not mutate or overwrite any V0/V1/V2 map file.

## System features (source-tested, not all tested with keyboard)

- Deterministic biome weighted random selection: Harbor, Woodland, Coast, Highlands (two review wave options per biome).
- At least 1800 cm eligible walking before a random encounter and hard cap of 5700 cm; escalating chance checked at 300 cm movement buckets.
- Safe zones, cinematics, ship travel, battle-active, unauthorized traversal and teleport suppress random encounters.
- Accessible encounter-rate cycling (Off, Reduced, Normal, Increased); independent scripted encounter permission with biome-scoped wave presets.
- Ticket acknowledgment/cancellation/completion protects the battle handoff; finite turn manager and AI govern attacks.
- Playable *review intent* W/A/S/D walk, 1/2/3 party stage, V simulated biome, P encounter rate, F2 scripted preview, J/K battle targeting and Enter to return.
- Returning after victory retains the walking actor's position; defeat/draw return to safe camp; no SaveGame or progression changes.

## Not yet established

- Actual keyboard input-to-movement and transition in **Play-in-Editor (PIE)** is not independently tested here.
- GPU D3D12 screenshots, framerate and cinematographic art approval are not established. The commandlets used NullRHI.
- This is a functional **review sandbox** built from provisional UE BasicShapes, not finished 3D enemies, rigging, animations, authored materials or real game FX.
- Sound properties are optional hooks, not fully authored/mapped environment and combat audio.
- Biome encounters, scripted boss placement, quest progression, XP/reward/save pipelines and First Wake production integration remain separately gated.
- All native passes are source-exact at the SHA above; a later commit containing this binary map requires its own final-head verification.

**Disposition:** native build, full 32-test automation and V2 map reload PASS; PIE/GPU/production/canon acceptance OPEN; keep PR draft and unmerged.
