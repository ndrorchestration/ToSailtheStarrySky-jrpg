# Unreal 5.8: Chapter I performance and vision admission gates

Status: **DRAFT PLAN / NOT ENGINE VERIFIED**. This file belongs to the unmerged Unreal migration stack based on PR #608. Godot remains the working legacy playback reference until Unreal has demonstrably equivalent playable functionality. Never infer native UE compilation, visuals, performance or acceptance from this document.

## Canon and reference locks
- Use creator-approved October 30 cast reference for Ender, Ionia, Lyra, Reson and Aepex; Ionia retains long curly blonde hair (captain updo is optional), and Ender's staff geometry remains recognizable.
- Five Lights: Ender–Spirit; Ionia–Earth; Lyra–Water; Reson–Fire; Aepex–Air. These are narrative affinities, **not automatic combat spells**.
- Party joins Ender → Ionia → Lyra → Reson → Aepex. Three active combat members; retain save/load and conventional JRPG combat plans.
- First Wake: flyer, Ionia's hiring and inspection, launch, physical sea landing, reserve investigation, shoreline/salvage and subsequent Lyra/Talen reunion. Do not shortcut narrative or rewrite earlier irreversible receipts.
- Aureate Wake: open forward deck, geodesic dome bridge, canonical sky/sea/submersible/hidden fourth traversal capability; do not reveal hidden traversal prematurely.
- Planetary globe, layered altitude and auroral routes are architecture targets, **not promises that full globe is ready for Chapter I beta**.

## P0 sequence: fastest path to a visually honest playable slice
1. **Bootstrap proof**: on Windows UE 5.8 open `unreal/ToSailTheStarrySky.uproject`, compile editor and game targets, package a Development build, and preserve command, toolchain version, full logs, output SHA and exact commit. Gate: opens without missing C++ classes/assets.
2. **First Wake story/interaction seam**: implement UE data-driven quest progression and a minimal deterministic test map; test Ionia-first dialogue and party join order. Do not claim a port from a scripted mock.
3. **Shared gameplay contracts**: define serializable party/save, inventory, level, combat action and story-event schemas independently from view actors. Seed and compare expected combat outcomes. Validate save/load round-trip, transaction rollback on invalid actions, and version migration.
4. **Hero shot production**: import only licensed, attributable creator-approved cast sources; use actual meshes/rigs/materials, real lighting and Niagara. Compare documented native captures against approved reference; no replacement placeholders promoted as finished art.
5. **Ship + environment traversal**: keep PR #610 four-form preview explicitly a blockout. Build one true physical ship/deck/water interaction with camera, collision, transitions, and one shoreline location. Treat moon/submersible reveals as feature-gated.
6. **Windows player acceptance**: clean-machine package install/launch, fresh save → playable First Wake → sea landing → berth/shore → reload; creator visual approval and traceable release signature/hash before any promotion.

## Profiling test matrix (targets are proposals, not measurements)
Test Windows Development and packaged builds separately at 1920×1080. Capture at least 120 seconds each: dock daytime, sunset ocean, ship motion, First Wake cinematic transition, 3-active combat with one high-cost FX event. Record CPU Game/Draw/RHI, GPU, frame-time p50/p95/p99, memory peak, VRAM/streaming, asset load hitch duration, package size and shader compilation time.

Initial **candidate** target: 60 FPS median (16.67 ms frame time) at an agreed midrange hardware profile; p95 frame time <= 25 ms; no transition hitch over 100 ms after shaders warm. Freeze hardware and acceptance targets only after creator review and first baseline captures. Do not substitute editor viewport FPS for packaged proof.

Use `stat unit`, `stat gpu`, `stat streaming` and Unreal Insights with exact source/build receipts. Only optimize a demonstrated bottleneck. Explore Nanite for appropriate static geometry, Lumen quality/scalability, HLOD/World Partition for distant chunks, async asset loading and tick reductions; do not turn all on by default. Large spherical worlds may require a planet-specific coordinate/streaming strategy: **prototype and test** World Partition compatibility and precision rather than assume a flat-world partition can serve a globe without adaptation.

## CI and evidence requirements
- Repository static checks: no missing required project/module files; no accidental engine binaries/caches; no tracked expired asset URLs or unlicensed art; preserve canonical character/ship/plot assertions.
- Windows runner: Unreal build + automation tests + commandlet smoke, attach logs and exact SHA. Report **UNVERIFIED** if the runner lacks UE rather than passing a stub.
- Capture native 3D screenshots and short gameplay video; compare technical, visual and narrative gates independently.
- Do not merge, publicly deploy or claim final art without creator approval.

## Dependencies and risk
PR #608 (unverified bootstrap) → compile gate → PR #610 (unverified four-form preview) + PR #609 (concept atlases only) → real asset import/collision → story/combat/save integration → packaged First Wake acceptance. A passing Godot test is useful reference evidence, not UE5 test evidence. Treat the May 2027 beta date as a planning hypothesis requiring reforecast after Unreal baseline, not a demonstrated delivery commitment.

## Proposed first review ticket
Run UE 5.8 bootstrap on the creator's Windows machine; log the exact compile/map-open errors (if any), then fix the smallest blocker. Follow with an automated deterministic Ionia-first quest test and one native screenshot.