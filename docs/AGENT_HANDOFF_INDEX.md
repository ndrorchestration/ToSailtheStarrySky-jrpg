# Agent handoff — documentation routing

> **2026-11-01 creator direction — supersedes earlier engine-selection statements below:** **Unreal Engine 5.8.4 is the active primary development engine** for *To Sail the Starry Sky*. Godot and the browser/NW.js material are preserved as legacy/reference implementations and sources of existing story/system contracts, **not the forward engine**. Reconcile provenance and narrative canon before porting; never delete the reference runtimes without verified migration and save compatibility. Current Unreal ship, character and gameplay changes are in separately reviewed draft branches, not automatically in `main`. A prior, exact-head Unreal foundation build and 12/12 native automation passed, but **the newer central bridge-and-living-quarters PR #702 only has engine-free source/geometry proof and 15 native test registrations; its exact-head native build/test run is still pending**. Neither CI nor placeholder screenshots grant art, gameplay, install or release approval. See [Unreal development](../unreal/README.md), [dependency baseline](../unreal/Docs/UNREAL_DEPENDENCY_BASELINE_2026-11-01.md), [verification](../unreal/Tools/README.md), and the [creator's coupled-bridge constraint](../unreal/Docs/AUREATE_CENTRAL_ROTATING_BRIDGE_HABITATION_DESIGN_2026-11-01.md).


> **Latest QA routing (2026-10-28):** Consult [native integration audit](CHAPTER_1_NATIVE_INTEGRATION_AUDIT_2026-10-28.md) before claiming the Chapter 1 story is integrated. At pinned `4d2ec5fb`, five Godot scripts and nine Windows renderer frames passed, but the inspected legacy review scene still starts Lyra-first and displays Ionia-first as opt-in; UI/art acceptance is pending. Validate normal F5 canonical entry separately.

> **Current P0 schedule:** [Chapter 1 beta roadmap](CHAPTER_1_BETA_ROADMAP.md) — prioritize consolidation of native First Wake, berth, narrative, save and Windows packaging before broader visual or planetary expansion. Dates are targets, not admission evidence.

**Status:** Public-safe cross-agent reference; created 2026-10-25 from current creator direction, GitHub contracts, and selected Notion records. This is a **navigation and reconciliation layer**, not an approval to integrate, publish or expose restricted story material.

## Required reading by task

| Agent work | Read before implementation |
|---|---|
| Any game change | [../AGENTS.md](../AGENTS.md), [Godot coordination](GODOT_MIGRATION_COORDINATION.md), [../SPEC.md](../SPEC.md) (legacy baseline) |
| Story, character dialog, reveals | [Canon and reveal](CANON_AND_REVEAL_POLICY.md), [Notion source index](NOTION_SOURCE_INDEX.md), [../SPEC.md](../SPEC.md) |
| Character models, sprites, portraits, animations | [Character and art authority](CHARACTER_AND_ART_AUTHORITY.md), [CHARACTER_ART_DIRECTION.md](CHARACTER_ART_DIRECTION.md), [VISUAL_BIBLE.md](VISUAL_BIBLE.md) |
| Ships, world map, terrain, sky, aurora, flight | [World / ship](WORLD_SHIP_VISUAL_DIRECTION.md), [VISUAL_BENCHMARK_SCENE.md](VISUAL_BENCHMARK_SCENE.md), [VISUAL_BIBLE.md](VISUAL_BIBLE.md) |
| Magic, battle, skills, class progression | [MAGIC_SYSTEM.md](MAGIC_SYSTEM.md), [../SPEC.md](../SPEC.md); port semantics before rewriting balance |
| Cinematics | [CINEMATIC_CLIP_CONTRACT.md](CINEMATIC_CLIP_CONTRACT.md) and benchmark scene |
| Builds / validation / release | [DEVELOPMENT.md](DEVELOPMENT.md), [PREVIEW_0_1_ACCEPTANCE.md](PREVIEW_0_1_ACCEPTANCE.md), [Godot coordination](GODOT_MIGRATION_COORDINATION.md) |

## Cross-agent collaboration protocol

**Hermes / Hyperagent Spellcraft / Muse Herald:** do not rely on your own chat memory or a private Notion connection to discover canon. Read this GitHub handoff and follow source links if authorized. A file linked in a draft PR is not in `main` until merged.

- Identify exact branch/commit and whether the task changes *story canon*, *visual direction*, *runtime behavior*, *tests*, or *documentation only*.
- For new content, state the content authority and conflict check (especially character likeness, family relationships, the Dragonfly, map geography and late-game routes).
- Implement GDScript/Godot for new runtime work. Existing JS behavior can serve as a bounded test oracle, not a new gameplay destination.
- Keep chapter-one native work, planetary Godot PR #364, and JS planetary prototypes #349/#363 distinct until deliberate integration.
- Provide proof as **observed facts**, never substitute source static checks for rendered graphics or native Windows acceptance.
- Do not merge drafts or publish binaries based solely on this document.

## Highest-value shared gaps (not accomplishments)

1. Ender and Ionia creator-quality source art / directional animation and grounded First Wake scene, including actual settled native visual evidence.
2. Chapter I complete native scene/quest/party/combat/save parity, not just technical unit contracts.
3. Planetary Godot scene with production-credible ocean/clouds/atmosphere, scale and terrain LOD; global navigation and local horizon must remain distinct.
4. Dragonfly original silhouette, in-engine material and rig, five-character shipboard context.
5. Creator visual/player review, representative performance and Windows export/installed-launch verification.

The existing canonical repository is public: https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg. Review actual branch states before making status claims.


## Consolidated prototype-to-production admission handoffs (2026-10-28, review only)

The six distinct source documents below are preserved without overwriting one another's historical evidence. They provide **review criteria, not production authorization**, and do not claim that the underlying Godot scenes, shaders, art, mechanics or item systems were merged into `main`.

| Discipline | Admission contract | Original draft |
| --- | --- | --- |
| Equipment and item lifecycle | [Equipment prototype-to-production](design/EQUIPMENT_PROTOTYPE_TO_PRODUCTION_PIPELINE_2026-10-27.md) | [#498](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/498) |
| Aureate Wake geometry and transformations | [Ship-pose admission](SHIP_POSE_PROTOTYPE_TO_PRODUCTION_ADMISSION.md) | [#499](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/499) |
| Engine-warning and combat VFX | [VFX admission](VFX_PROTOTYPE_TO_PRODUCTION_PIPELINE_2026-10-27.md) | [#500](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/500) |
| Snow, sand, wet earth and mist | [Perceptual biome materials](design/PERCEPTUAL_BIOME_MATERIAL_PROMOTION_2026-10-27.md) | [#501](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/501) |
| Character movement and artwork | [Character motion admission](design/CHARACTER_MOTION_PROTOTYPE_TO_PRODUCTION_PIPELINE_2026-10-27.md) | [#502](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/502) |
| Enemy silhouette and scene VFX | [Enemy visual admission](reviews/ENEMY_VISUAL_PROTOTYPE_TO_PRODUCTION_2026-10-27.md) | [#505](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/505) |

**Source-of-truth rule:** the newer creator visual reference and actual Ionia-first playable route outrank provisional historical design assumptions; no checklist is closed without exact-head native evidence and appropriate creator/art review. Keep the original PR discussions for provenance. This consolidated document index changes no runtime, canonical story, save schema, installer or published release.
