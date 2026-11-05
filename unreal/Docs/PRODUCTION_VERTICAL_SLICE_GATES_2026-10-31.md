# TSTSS — professional production gates for the First Wake vertical slice
**Status:** planning and evidence contract, not implementation acceptance. **Date:** 2026-10-31.

## Production intent
Demonstrate one complete, polished, playable interaction loop in Unreal Engine 5.8 while protecting the original Godot playable project. Preserve the creator-approved cast reference, Ionia's curly long blonde hair, the canonical Aureate Wake and First Wake event order. The Five Lights are narrative affinities and do not automatically grant combat skills.

## Disciplines and hand-offs
| Discipline | Smallest deliverable | Objective gate | Creative gate |
| --- | --- | --- | --- |
| Engineering | Exact-head Win64 Editor build; TSTSS automation and clean SaveGame round trip | Real compiler and per-test receipts, no missing required tests | None—technical pass isn't visual approval |
| Narrative/level | Flyer → Ionia hire → boarding → three engineering inspections → launch → measured sea contact → flotation → reserve inspection → return | PIE video, state assertions; no milestone shortcuts | Creator checks timing, character writing and emotional feel |
| Combat | Three active participants max, learned-ability authority, enemy encounter, victory/defeat, HUD | Executed automated and packaged-game functional tests; input/state integrity | Combat feedback/readability approval |
| Art/animation | Licensed approved cast meshes/hair/rigs, dragonfly ship forms, material and VFX authoring | Import manifest (source/license/hash), functional animations, renderer captures | Side-by-side stills; no concept sheet treated as production asset |
| Audio | Opening theme and feedback routed through actual game event triggers | Clean playback/mix evidence in runtime | Music and mood approved |
| Performance | Captured representative coastal/ship/combat scenes on target Windows machine | Unreal Insights CPU/GPU timings, frame-time distributions, memory, shader hitches | Cinematic fidelity held to visual reference |
| QA/delivery | Cold-launch Windows build, save/reload, recoverable failure paths, install/uninstall | Exact binary, signed/unsigned status, automated smoke where possible | User can install and play without Godot setup |

## Fast production loop (one vertical slice; avoid parallel feature sprawl)
1. **Gate 0 — Native truth:** Run `unreal/Tools/Verify-Unreal.ps1` from an isolated pinned clean checkout; archive full SHA, Build.bat output and Unreal automation JSON. A successful Godot or source-only CI run is not a UE PASS.
2. **Gate 1 — Functional First Wake:** Wire real input, physics and milestones to a small native map. Add a feature-level test that walks the intended path. Do not pretend enum tests equal physical landing.
3. **Gate 2 — Review the ship/character art in engine:** Recheck stacked PR #610 against the exact current #608. Recover original #609 images only as licensed references. Replace default geometry with reviewed authored models and cinematic materials, not generated thumbnails as runtime textures.
4. **Gate 3 — Player-facing playable slice:** Put a bounded combat encounter and pause/save/load into the same real level path. Run controller/keyboard navigation and UI accessibility QA.
5. **Gate 4 — Fidelity and frame budget:** Capture matched-camera screenshots and Unreal Insights data using a repeatable route, same graphics preset and same machine. Proposed starting budgets for **review only**, to be confirmed against target hardware: 30 fps = 33.3 ms/frame cinematic minimum; 60 fps = 16.7 ms/frame preferred. Capture p50/p95/p99 frame times and hitches; do not claim a target is achieved without measurements.
6. **Gate 5 — Packaged Windows acceptance:** Test an actual exported binary, exact SHA, Defender-on behavior, install/launch/relaunch/save/uninstall, crash recovery and user-facing first-run experience. Keep source and test evidence adjacent to the build.

## Dependency and risk management
- PR #608 is the baseline; PR #610 is stacked onto it; PR #609 contains reference-asset provenance; Godot PR #601 supplies behavior vectors only. **No automatic merge** from parallel streams.
- Use **one owner and acceptance receipt per gate** even when multiple agents work in parallel. Avoid handoffs based only on code commits or mockups.
- High-risk blockers: no native Unreal 5.8 build proof, approved artwork not yet rigged/imported, ship visuals still preview geometry, no validated packaged First Wake.
- Design review: change one variable per visual A/B capture; keep camera, exposure, resolution, graphics preset and engine version fixed when judging materials/lighting.
- Test teardown: test slots must be isolated and cleaned, with stale-slot failures handled explicitly. No test may overwrite player saves.
- Completion means *measured and reviewed*, not merely code present. Don't retire Godot until a native Unreal build passes and is accepted.

## External professional references
- Epic Unreal Engine 5.8 Automation Test Framework: https://dev.epicgames.com/documentation/unreal-engine/automation-test-framework-in-unreal-engine
- Epic Unreal Engine 5.8 Gauntlet: https://dev.epicgames.com/documentation/unreal-engine/running-gauntlet-tests-in-unreal-engine
- Epic Unreal performance profiling: https://dev.epicgames.com/documentation/unreal-engine/introduction-to-performance-profiling-and-configuration-in-unreal-engine
- AMD GPUOpen Unreal performance guide: https://gpuopen.com/learn/unreal-engine-performance-guide/
