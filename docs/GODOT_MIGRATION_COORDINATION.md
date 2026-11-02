# Godot production direction and parallel-agent coordination

> **2026-11-01 creator direction — supersedes earlier engine-selection statements below:** **Unreal Engine 5.8.4 is the active primary development engine** for *To Sail the Starry Sky*. Godot and the browser/NW.js material are preserved as legacy/reference implementations and sources of existing story/system contracts, **not the forward engine**. Reconcile provenance and narrative canon before porting; never delete the reference runtimes without verified migration and save compatibility. Current Unreal ship, character and gameplay changes are in separately reviewed draft branches, not automatically in `main`. A prior, exact-head Unreal foundation build and 12/12 native automation passed, but **the newer central bridge-and-living-quarters PR #702 only has engine-free source/geometry proof and 15 native test registrations; its exact-head native build/test run is still pending**. Neither CI nor placeholder screenshots grant art, gameplay, install or release approval. See [Unreal development](../unreal/README.md), [dependency baseline](../unreal/Docs/UNREAL_DEPENDENCY_BASELINE_2026-11-01.md), [verification](../unreal/Tools/README.md), and the [creator's coupled-bridge constraint](../unreal/Docs/AUREATE_CENTRAL_ROTATING_BRIDGE_HABITATION_DESIGN_2026-11-01.md).


> **2026-10-28 Windows native verification:** A detached clean worktree at `4d2ec5fb` passed Godot 4.7.2 import, five bounded Chapter 1 scripts and nine real OpenGL frames. The legacy migration review scene still starts Ender + Lyra and exposes Ionia-first only as an opt-in prototype. Separate the canonical normal-F5 entry acceptance from legacy scene QA. The active visual branch evolved during testing and was not modified or validated by this receipt. [Integration audit](CHAPTER_1_NATIVE_INTEGRATION_AUDIT_2026-10-28.md).

> **2026-10-28 scheduling update:** [Chapter 1 beta roadmap](CHAPTER_1_BETA_ROADMAP.md) governs the solo integration and review milestones. The branch inventory below is a **dated historical snapshot**; do not use its 2026-10-24 PR heads as current. Re-query the remote before integration. The native Ionia-first sequence takes priority over legacy Lyra-first browser onboarding. No merge/release authorized.

**Creator-selected 2026-10-24:** Stop expanding p5.js/JavaScript gameplay; continue development in **Godot 4.7.2 + GDScript**. This is the authoritative **forward development decision**, not retroactive proof that the full JRPG, save data, world, art or Windows release has already migrated.

## Branch/track separation (as last inspected)

- **`main`:** historical functioning JS/p5/NW.js game and documentation baseline. Do not destroy; use its content, equations and tests as migration reference.
- **Native Chapter I stacked line:** e.g. `feat/godot-first-wake-party-combat-authority-20261022`, reported head `74fe1bce7a8a02eb3cbf30f725fa2af0925ba670` by Hyperagent's local inspection. Verify remote head before each change. Stacked native work PRs #306–347 not assumed merged.
- **Hyperagent local UI candidate:** `work/godot-native-ui-validation-20261024`. Hyperagent reports branding, CanvasLayer modal occlusion, wrapped labels, repeatable test runner, CI aggregate and evidence (34 checks, nine native captures) **locally**, but **not yet pushed**. Treat as agent-reported and unadmitted until exact bytes/source/logs are available to verify.
- **Native planet/flight track:** [draft PR #364](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/364), head observed `567594e25fc0a1b9eb9f4d8b86b4080f5f8246b7` at this handoff, based on the native Chapter I line. Isolated Godot geometry, flight, globe; not a finished integrated world.
- **Earlier JS planetary studies:** draft [#349](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/349), [#363](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/363). Preserve as evidence/visual reference; **no additional JS gameplay development**.
- **Standalone higher-fidelity Godot artifact line:** tracked separately in Notion and #350. Do not reconstruct from textual hashes or assume the exact renderer ZIP is already in this GitHub repository.

## Safe integration sequence

1. Fetch branch/PR states and the *exact* sources (not just agent summaries); choose a common ancestry, avoid overwriting other agents' changes.
2. Stabilize Godot Chapter I: correct opening/quest/party/combat/save state, editor import, headless native tests, real scene captures.
3. Integrate Hyperagent's **actual** local patch once published; diff against native Chapter I and preserve test/evidence provenance.
4. Introduce planet/flight as separate scenes/systems with isolated world state; verify chapter and save compatibility **before** coupling.
5. Replace primitive art through creator-reviewed source/converted assets, genuine native screenshots and Blender/Godot visuals.
6. Performance/Windows export/installed-launch/player acceptance and release permission are distinct; no silent promotion.

## Evidence categories

- **SOURCE:** branch + commit SHA, changed paths, provenance.
- **NATIVE CONTRACT:** exact Godot 4.7.2 version, headless import, native tests, scene instantiation.
- **NATIVE VISUAL:** real Godot runtime frames, controls, pixel/occlusion and shader/lighting checks, exact capture manifest.
- **TARGET PLATFORM:** hardware/renderer/FPS/VRAM + Windows packaging / installed launch.
- **CREATOR ACCEPTANCE:** distinct human art/scene/gameplay approval.
- **RELEASE:** separately authorized action; default HOLD.

Documentation and canon descriptions do not upgrade any of these evidence categories. Notion/Drive may hold detailed receipts, but the GitHub branch/PR must link them explicitly when required. Verify the head again: these SHAs are dated pointers, not immutable branch locks.


## October 28 prototype-to-production handoff consolidation

The six distinct 2026-10-27 public-safe equipment, ship-pose, VFX, perceptual-biome, character-motion and enemy-visual admission documents are now navigable through the [Agent Handoff Index](AGENT_HANDOFF_INDEX.md#consolidated-prototype-to-production-admission-handoffs-2026-10-28-review-only). They were sourced from proposals #498, #499, #500, #501, #502 and #505. Bringing review text together does **not** integrate those six runtime branches, approve their source artwork, certify performance, freeze numerical combat mechanics, or authorize Windows distribution.

Always bind an actual admission to the exact currently tested Godot head, supported source assets, creator-directed Ionia-first story order, physical native player behavior, and explicit visual review. Preserve this consolidation as documentation only until it passes its own link and provenance checks and is separately reviewed for merge.
