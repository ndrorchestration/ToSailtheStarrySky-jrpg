# Unreal Engine 5.8 — active forward-development review track

**Fresh native evidence (November 2, 2026):** On an isolated exact-head PR #713 checkout (`fd0b68c28e6289d45f8b8c70228631c24577a352`), **Unreal 5.8.4 Editor compiled successfully**. The engine reported 25 named automation successes, but the all-green native verifier **refused acceptance** after discovering tracked INI rewrites. Preserve the generated Android File Server token as local secret evidence; never stage, distribute or display it. **Native automations = HOLD (post-run source mutation); P01–P13 PIE = NOT TESTED.** [Verification matrix](Docs/PRODUCTION_VERIFICATION_MATRIX.md), [integrated gate](Docs/INTEGRATION_GATE_2026-11-02.md) and [dependency handoff](Docs/FIRST_WAKE_DEPENDENCY_HANDOFF_2026-11-02.md) are the current cross-discipline status, not older #712 receipt claims below.

**Combined review orientation:** [PR #713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713) is the current integrated **draft** of #712 First Wake, scoped #657 creator authority and #711 dependency register. See [review integration gate](Docs/INTEGRATION_GATE_2026-11-02.md). This branch has not passed native UE build or gameplay acceptance and is not merged to main.

**2026-11-02 · Unreal-first decision · review/experimental; not a completed native game.**
UE **5.8.4** is the observed Windows development patch within the project's
`EngineAssociation: "5.8"` family. The preserved Godot and browser projects
remain historical implementations and regression sources, not the selected
forward gameplay engine. No automatic engine or legacy-save migration is approved.

**Evidence, with scope:** The native Game and Editor targets have compiled
and 23/23 Editor automations ran on [draft #685](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/685)
**at that older head**. Draft [#694](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/694)
tracks a real, isolated, seven-marker V2 Prelude `.umap`; draft [#704](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/704)
addresses third-person camera/range interaction. The current stacked
[draft #712](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/712)
adds read-only objectives, E/J cues, separate PIE F5/F9 review slots and
additional source/portable-C++ tests. At its inspected **`a1b07b64841c2cb6b735fdd66f2ecd6426cab016`** head,
three GitHub source workflows were green. **Native Editor build, all
25 registered automations, E/J/F5/F9 Play In Editor, renderer acceptance,
sea-contact physics, full Splashdown and a Windows packaged launch remain
unverified at #712's head.** Draft ancestors and older test receipts do not
establish the new revision as playable or production ready.

Start with [First Wake V2 PIE acceptance matrix](Docs/FIRST_WAKE_V2_PIE_ACCEPTANCE_MATRIX_2026-11-02.md),
[review objective and save behavior](Docs/FIRST_WAKE_REVIEW_OBJECTIVES_2026-11-02.md),
and [current source/dependency handoff](Docs/FIRST_WAKE_DEPENDENCY_HANDOFF_2026-11-02.md).
Root `AGENTS.md` and `README.md` still contain dated Godot-first instructions
on this **unmerged** branch; reconcile engine-authority changes separately
through the existing [#657](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/657)
and [#711](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/711)
review tracks. These root files are **not** used as the current engine
decision for new work.

## Earlier foundation setup (preserved for provenance)

## Windows setup

1. Install Unreal Engine 5.8 and the compatible Visual Studio C++ game-development toolchain.
2. Open `unreal/ToSailTheStarrySky.uproject` through the Unreal Editor or generate project files and compile the Editor target.
3. Verify successful editor launch, then add authored maps, assets, runtime systems, automated functional tests and packaging rules in separate, reviewable changes.

This repository now contains an isolated noncanonical V2 Prelude review map
and source-level character/ship blockouts on separate review branches. The
approved 2D cast reference does **not** automatically approve these 3D models,
their rigs, materials or any cinematic result. A reviewed older-build receipt
is not evidence that this branch has compiled or rendered.

## Migration constraints

- **Art lock:** User explicitly approved the latest full-cast artwork on October 30, 2026. Treat its designs as the authoritative visual target; do not substitute pixel/legacy sprites. Source image files, individual face references and asset licensing/provenance must be attached or linked before producing game-ready meshes.
- **Story lock:** First Wake starts with Ender finding Ionia's flyer, hiring her, boarding the Aureate Wake, doing engineering checks, launching, sea landing/flotation and inspecting empty reserves. Lyra and Talen's reunion/salvage requires authored acceptance; do not invent it as complete.
- **Party lock:** Ender → Ionia → Lyra → Reson → Aepex. Three active combat members planned. Party resonance is story energy, not automatic combat magic.
- **Five Lights:** Ender/Spirit, Ionia/Earth, Lyra/Water, Reson/Fire, Aepex/Air are narrative affinities, not mandatory magic classes.
- **Game systems:** Preserve deterministic, transactional combat semantics and data-driven stats, costs and skills. Define UE native serialization IDs and versioned save migrations before replacing Godot saves.
- **Ship/world:** The four player-facing Aureate Wake configuration names are **Skybourne, Seabourne, Submersible, Starbourne**. The early code may retain older enum identifiers for backward serialization. Starbourne remains fail-closed; ship form transitions, hydrofoils and rotating geodesic bridge/living quarters are independently gated visual/physics review prototypes. Planet and moon traversal are future milestones.
- **Quality:** Prioritize creator-approved cinematic art with documented budget and performance targets. A technical compile or frame capture is not art approval.

## Next admission step — actually playable Prelude

A seven-stop V2 review map and native milestone source now exist. The **smallest
reversible next step** is to compile draft #712 at its exact HEAD with the
Win64 Unreal Editor, run `unreal/Tools/Verify-Unreal.ps1` with **25 exact
named automation results**, then perform P01–P13 in a **disposable** PIE
checkout. Do not create a synthetic sea-contact marker to manufacture
Splashdown: actual contact and stable flotation require separate native
physics evidence. Any success must include source SHA, logs, evidence
and unmodified original map/save files. Do not merge based on this README.
