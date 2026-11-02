# Unreal Engine 5.8 migration — experimental source track

> **Current Unreal-first development status (Nov 1, 2026).** Unreal Engine **5.8.4** is the creator-selected forward target; the root browser/NW.js project and Godot material are legacy references, not active forward-gameplay dependencies. The separate root-authority change is [draft #657](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/657) and is not merged. See the [dependency and evidence register](Docs/DEPENDENCY_AND_EVIDENCE_REGISTER_2026-11-01.md) for exact versions, roles, and review holds.

**Native evidence is now branch-specific, not absent.** [Draft combat #685](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/685) had Game+Editor builds and 23 native NullRHI tests PASS at its exact verified SHA. [Draft Prelude #694](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/694) contains an actual source-tracked V2 Unreal `.umap`, still blockout/noncanonical. [Draft interaction #704](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/704) Game target compiled at C++ head `0a6160b4`, but its direct un-packaged executable startup **FAILED** with an asset-registry/BufferReader crash; the 24th native Editor test and actual PIE E/F5/F9 remain open. Do not confuse source CI or UBT compilation with playability, package approval, or cinematic signoff.

### Native development entry

Clone the exact draft ref in a **distinct clean Windows checkout**, confirm Git HEAD and UE 5.8.4 + MSVC/SDK, and run `python unreal/Tools/check_dependency_contract.py --repo .` plus the source preflight. Use `unreal/Tools/Verify-Unreal.ps1` for native Editor build and named automation results when Live Coding in other Editor sessions is not active. Review the [verification commands](Docs/UNREAL_TEST_COMMANDS.md) and avoid launching a raw, uncooked Game executable as proof of packaged-game startup.

### Historical scaffold note

The paragraphs below record the initial migration scaffold and must not override the newer dated evidence above.


This is a **native UE C++ project scaffold**, not yet a compiled or playable port. UE 5.8 is the selected initial engine target. The existing Godot project and preserved browser code remain untouched.

## Windows setup

1. Install Unreal Engine 5.8 and the compatible Visual Studio C++ game-development toolchain.
2. Open `unreal/ToSailTheStarrySky.uproject` through the Unreal Editor or generate project files and compile the Editor target.
3. Verify successful editor launch, then add authored maps, assets, runtime systems, automated functional tests and packaging rules in separate, reviewable changes.

No official character meshes/textures, maps, compiled binaries, or approved cinematic sequences are included in this scaffold. A static approved illustration is **not** by itself an importable rigged game character.

## Migration constraints

- **Art lock:** User explicitly approved the latest full-cast artwork on October 30, 2026. Treat its designs as the authoritative visual target; do not substitute pixel/legacy sprites. Source image files, individual face references and asset licensing/provenance must be attached or linked before producing game-ready meshes.
- **Story lock:** First Wake starts with Ender finding Ionia's flyer, hiring her, boarding the Aureate Wake, doing engineering checks, launching, sea landing/flotation and inspecting empty reserves. Lyra and Talen's reunion/salvage requires authored acceptance; do not invent it as complete.
- **Party lock:** Ender → Ionia → Lyra → Reson → Aepex. Three active combat members planned. Party resonance is story energy, not automatic combat magic.
- **Five Lights:** Ender/Spirit, Ionia/Earth, Lyra/Water, Reson/Fire, Aepex/Air are narrative affinities, not mandatory magic classes.
- **Game systems:** Preserve deterministic, transactional combat semantics and data-driven stats, costs and skills. Define UE native serialization IDs and versioned save migrations before replacing Godot saves.
- **Ship/world:** Aureate Wake supports flight, sea, submersible and hidden Moon Bridge modes, staged behind separate feature gates. Planet and moon traversal remain future milestones.
- **Quality:** Prioritize creator-approved cinematic art with documented budget and performance targets. A technical compile or frame capture is not art approval.

## Next thin vertical slice

A single noncanonical test map with a third-person Ender pawn, Ionia interaction, boarding trigger and a sea-contact event; use isolated authored assets and capture Windows packaged-build evidence. Only then port the full First Wake beats and combat UI. Do not merge based on this README/scaffold alone.
