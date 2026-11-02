# Unreal Engine 5.8 — active draft implementation

> **2026-11-01 update:** Unreal 5.8.4 is now the creator-directed implementation target. The scaffold-only wording below is historic: specific draft PRs have genuine native Editor builds, 13/13 automation checks, GLB imports and D3D12 screenshots. The latest atmosphere preview still has a black-sky visual HOLD; no creator-approved shipping port is claimed. See [engine and dependency register](Docs/UNREAL_DEPENDENCY_AND_AUTHORITY_REGISTER_2026-11-01.md). Starbourne remains gated.


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
