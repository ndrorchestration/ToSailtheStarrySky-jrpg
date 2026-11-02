# Unreal Engine 5.8.4 — primary development and review tracks

**Creator-selected primary development engine as of 2026-11-01: Unreal Engine 5.8.4.** The Godot and browser/NW.js prototypes remain intact as historical gameplay/story-system references; preserved evidence and migration contracts do not make Godot the forward engine.

**Verified, source-scoped status:** [The native foundation receipt](Docs/UE58_NATIVE_BUILD_VERIFICATION_2026-11-01.md) documents a successful Win64 Unreal Editor build and **12/12 native automation tests at its own pinned source revision**. Separate later ship branches have additional image/build evidence, which **cannot automatically validate newer drafts**. The coupled rotating bridge and living-quarters assembly is implemented in [review draft #702](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/702): source checks and a noncanonical 126-pose geometry screen passed, and 15 native test names are registered. **Native C++ compilation, 15/15 native automation, real V2 assembled collision and creator art approval remain pending at that source head.**

See [dependency inventory](Docs/UNREAL_DEPENDENCY_BASELINE_2026-11-01.md), [current source/native verification](Tools/README.md), and [central bridge/habitation design](Docs/AUREATE_CENTRAL_ROTATING_BRIDGE_HABITATION_DESIGN_2026-11-01.md).

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
