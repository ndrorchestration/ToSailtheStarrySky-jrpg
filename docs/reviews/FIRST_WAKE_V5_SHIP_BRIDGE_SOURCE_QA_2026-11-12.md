# First Wake V5 → ship interior: isolated source integration and QA (2026-11-12)

**Authority:** Review-only source candidate; **native Win64 Editor build and two targeted Unreal automation tests PASSED** at exact compiled source revision `505de74c3b958ff8d3ffc084a221418182925b2f`. **NOT yet live-playtraversed, not full suite, NOT creator-art approved, NOT merged.** [Independent native QA and disk-space remediation evidence](FIRST_WAKE_V5_SHIP_BRIDGE_NATIVE_QA_2026-11-12.md).

- Repository: `ndrorchestration/ToSailtheStarrySky-jrpg`
- Protected verified base: `review/ue58-opening-and-dock-rescue-20261111` at `d4d860b4a6565a4791aab557758b895b3540ffd2`
- Isolated child: `review/ue58-v5-ship-route-bridge-20261112`, local `C:\TSTSS_V5RouteBridge_20261112`
- Original implementation commit: `37a1fc524febfb000084d5b8c795e3671420a942`; **exact compiled/tested source commit**: `505de74c3b958ff8d3ffc084a221418182925b2f`.
- Verifiable baseline: [V5 native playability evidence](FIRST_WAKE_V5_NATIVE_PLAYABILITY_EVIDENCE_2026-11-11.md). The published baseline demonstrated New Game → V5, W movement, first E flyer interaction, and non-story-mutating floor-edge rescue at earlier exact source heads. **Do not transfer that native evidence to this new revision.**

## Changes (small, reversible)

1. `UTSTSSReviewShoreTravelSubsystem::NextReviewMap` now plans **V5 prelude → VS02 Aureate interiors**, not directly to sky, only after completed engineering inspections. Original **V2 → VS03 sky** review behavior is explicitly unchanged for historical regression.
2. K from V5 to the ship does **not** grant `Launched`. Only K from the ship (or legacy V2) requests the launch beat after the existing complete-inspection gate, then queues `VS03_FirstWakeSky`. There is no implicit sea contact.
3. `QueueShore` and one-shot `ConsumeShoreArrival` additionally check solo World, Editor-compiled PIE or standalone Game, review package prefix, existing destination and matching arrival name. No new SaveGame format or party grant.
4. `TSTSSMilestoneActor` clears consumed E-marker visibility collision in **named V2/V5 or fuel-shanty review maps**, for PIE and standalone Editor Game, instead of only PIE. Failed V3/V4, production, unrelated and networked Worlds are refused. Same scope applies when reconciling marker collision after an approved restore.
5. Extended the preexisting registered `TSTSS.FirstWake.ReviewObjectivesAreReadOnly` native test source with before-inspection denial, V5→ship, ship→sky and original V2→sky expectations; the two registered review-native tests, including these route assertions, have **now run and passed** at `505de74`. Added five read-only source tests and negative contracts in `test_first_wake_v5_ship_bridge.py`.

## Source verification at source commit

- **106/106 selected Python source tests PASS**, including new bridge tests and existing opening, objectives, dependency contracts, audio contracts and V3/V4/V5 map QA.
- `git diff --check` PASS and the child worktree was clean after the source commit.
- Original V2 map SHA-256: `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80` unchanged.
- Original V5 map SHA-256: `ff2b5c1423a370c4ac318b9b241088d8f20fec5eee993c998c2a5ed335cbb299` unchanged.
- **NO full-suite success claim**: a separate all-discovery attempt did not return a reliable finished result. The 106-test selected run is the accepted source receipt. This does not prove the full inventory.
- **Native compile PASS, two targeted native automation tests PASS** at exact code commit `505de74`; **NO live gameplay test** of the new route. The earlier ~11.46 GiB disk blocker was corrected through strictly generated build-cache cleanup. After build and automation, free C: **15.611 GiB**; audit receipts retained locally. Other worktrees' source and verification evidence remain intact. See linked native QA report.

## Dependencies and integration ownership

This is a **temporary K-driven review bridge**, *not* the [#814](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/814) E-interaction six-map `UTSTSSReviewRouteSession` implementation. #814's separate additive traversal-overlay maps and PIE-only route actors have **not** been copied, compiled or activated here. Choosing a single eventual route authority remains a required integration decision, not something hidden behind two active directors. The six underlying [#794](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/794) map packages are already in the V5 lineage; there is no map overwrite.

[#799](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/799)/[#813](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/813) source convergence, [#808](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/808) Lyra post-splashdown recruitment, #804 audio, #793 inventory and #815 cinematic focus remain **separate**. Nothing here authorizes an additional engine plugin, `CinematicCamera` runtime dependency, sound/music, Ender art, Reson/Aepex party access or Starbourne. No `.uproject`, `Build.cs` or dependency baseline changed.

## Native acceptance checklist (partial; player-traversal gates still open)

- [x] resource-admitted UE5.8.4 UHT/UBT Win64 Editor build at source head `505de74`; two relevant native automation tests PASS (0 failures)
- [ ] complete registered native automation inventory beyond the two targeted review tests
- [ ] launch actual title → V5 and complete all seven ordered E actions; prove consumed markers no longer intercept later E rays in standalone
- [ ] K at pre-inspection state denied; completed V5 → VS02 only, and arrival restores EngineeringChecked + 0x07 without granting Launched
- [ ] VS02 PlayerStart, floor support, visible ship interior, safe collision and camera; **VS02 has not been added to fall-recovery allowlist without native footing proof**
- [ ] K from VS02 to VS03 changes beat to Launched only; no automatic physics/sea-contact advancement
- [ ] sea-to-shanty refuses absent continuously observed, physically supported flotation and preserves two-second stability/adversarial controls
- [ ] restore, F5/F6/F7/F9, Lyra after splashdown, no Starbourne, music/sound ownership and saved-state isolation remain correct
- [ ] actual D3D screenshots, frame timing, visual/material/lighting and creator quality approval

**Disposition:** Child branch native-build and two-targeted-native-test gates passed. The original V5 parent remains intact and remains the last demonstrated native **playable** baseline. Next step: real seven-step standalone W/E progression and V5→VS02→VS03 K route under source-locked evidence, before any promotion.
