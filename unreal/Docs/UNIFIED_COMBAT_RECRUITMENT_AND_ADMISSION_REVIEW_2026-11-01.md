# Unreal combat: unified draft native gates for story recruitment and DesignOnly commands

**Date:** 2026-11-01
**Scope:** source-side C++ integration and native test *declarations*, not a UE Editor run
**Status:** DRAFT / UNMERGED / NATIVE UE 5.8.4 UHT + TESTS NOT YET VERIFIED

## Exact upstream provenance / noninterference

This draft is stacked on PR [#672](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/672) exact head `b4dad1a01a696b910421f88b6ac308ffd19b7c40` (thus also #671 → #666 → #662 → #608 and the additive #665 review-only data contract).

It carries *unchanged* three unique [PR #674](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/674) files read from exact head `b2310c56ed6825cbddc7e484d7c053b58d6e9f73`:
- `Public/TSTSSCombatSkillReconciliation.h`, git blob `7c9f62693d0cebd1d7413ade85056c69135c33af`
- `Private/TSTSSCombatSkillReconciliation.cpp`, git blob `de2cb460cee47ca6b9b449f52970eeac4370f897`
- `Private/Tests/TSTSSCombatSkillReconciliationTests.cpp`, git blob `5f0995b69c738b7dcaca61507f390f04c395bc1e`

No broad cherry-pick. There is no second ability resolver, runtime data hook, SaveGame mutation, job/weapon inventory modification, or newly admitted skill. No party state or playable chapter scene is changed. The source contract `TryPrepareDesignOnly` only converts valid Spell/WeaponTechnique authoring metadata into *non-executable* `FTSTSSBattleSkillRow` entries, atomic on failure.

## New cross-layer negative-control test

`TSTSS.CombatIntegration.DesignOnlyTurnManagerDenial` in `TSTSSDesignOnlyTurnManagerDenialTests.cpp` uses **the real** `FTSTSSCombatSkillReconciliation` output as a `UDataTable` for **the real** `UTSS_CombatTurnManager::SubmitCommand`. Its deliberately noncanonical spell fixture includes a source row marked `CreatorApproved`, an already learned spell, maximum fabricated mastery, and a correctly configured actor/target. It tests that the converted `DesignOnly` row is still denied, then compares phase, round, active actor, each participant's identity/HP/resource against the precommand snapshot. It does not claim actors cannot change roles in real gameplay, because it contains no approved combat content or story integration.

The inherited `TSTSS.CombatIntegration.ProgressiveRecruitmentPartySize` test independently checks opening Ender solo, Ender/Ionia duo and Ender/Ionia/Lyra trio, no phantom bench or unrecruited Lyra. This deliberately **does not** weaken `FTSTSSCombatData::ValidateActiveParty`'s exactly-three *complete-party* gate.

`unreal/Tools/Verify-Unreal.ps1` must require **23** named native automation cases (21 inherited + original #674 DesignOnly converter + new turn-manager denial). That inventory is only source-side until Unreal itself compiles and executes each test.

## Exact validation gates

1. GitHub Actions exact head source registry, inventory and repository smoke PASS; all 23 registration names unique and 11 Unreal C++ test files present. Watch workflow status instead of borrowing parent green.
2. Authorized Windows `neontic` must be online, isolated checkout clean at this exact head, UE **5.8.4**, run `unreal/Tools/Verify-Unreal.ps1 -EngineRoot 'C:\Program Files\Epic Games\UE_5.8'`; save UBT/UHT exit status, Editor `AutomationReport/index.json`, and per-test results.
3. Specifically inspect `TSTSS.CombatIntegration.ProgressiveRecruitmentPartySize`, `TSTSS.CombatData.NonExecutableSkillReconciliation`, and `TSTSS.CombatIntegration.DesignOnlyTurnManagerDenial`. Reject missing/duplicate/non-success records.
4. Separately verify real First Wake solo/duo/trio party progression, stat source approval, player UI, save round-trip and any claimed spell VFX/animation. **Do not infer them from the tests.**

## Priority unresolved design decisions

- The Five Lights are story energies, not automatically elemental spell permissions; avoid inventing abilities or treating resonance as a resource.
- `ETSTSSApproval::CreatorApproved` is **not** interchangeable with `ETSTSSBattleSkillAdmission::ReviewExecutable`. Source-table appearance, unlock level or protagonist affiliation never grants executable combat access by itself.
- One current `Resource` combat pool is not yet a canon MP mapping. Proposed HP/MP/MAG numbers are fixtures only; owner ordering remains Ender highest MAG/MP, Lyra second, Lyra lowest HP, Ender second-lowest.
- Three active slots maximum; early First Wake recruitment Ender → Ionia → Lyra; Reson and Aepex later. Current review manager allows 1–3 active, whereas full-party validation accepts exactly 3. This distinction is documented and tested, not silently “fixed.”
- UE 5.8.4 native combined build, UHT reflection, DataTable authoring, SaveGame migration and rendered gameplay remain NOT VERIFIED while RDC workstation is offline. Previous standalone native success cannot transfer.

**Safe disposition:** retain every component PR as draft, document exact provenance, prohibit merge/canon approval/public release until explicit owner decisions and independent native proof.

## Offline executable C++ review slice — verified at 2026-11-01 exact head

The developer-host PC was still offline, so source-only registration was insufficient. The branch now provides `unreal/Tools/check_combat_design_only_compiled.py`, which **extracts and compiles the actual body** of `FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly` from its C++ source file with a real C++17 compiler under strict `-Wall -Wextra -Werror -pedantic` warnings. The test program supplies minimal Unreal API doubles only for collection, name and source-row types; it cannot fake the adapter's switch/commit logic.

The compiled binary passed **22/22 source-extracted behavioral assertions**, covering supported categories, correct metadata transfer, DesignOnly admission, no inferred mastery/weapon/school, atomic failure for invalid actions/duplicates/unknown categories and targets, no partial output mutation, and replacement of old output on a successful new conversion. Native Unreal data validation is *stubbed*, not tested or claimed by this tool; real `FTSTSSCombatData::ValidateActions` has its separate native tests.

The new `DesignOnlyTurnManagerDenial` native Editor test also contains a **synthetic positive control**. First, a DesignOnly skill must fail at `UTSS_CombatTurnManager::SubmitCommand` with no change to phase, actor, round, HP or resources. Next a **separate test-only** DataTable row is explicitly marked `ReviewExecutable`, with all other metadata and a fresh encounter identical; it must execute, charge 2 resource, inflict 4 damage and advance to the opponent's turn. This isolates the intended admission boundary from a false-positive denial caused by broken game state. This opt-in row never exists in production and grants no canonical ability.

**Verified GitHub exact head `7dfca83b5e6f3a051eea33de6a128e1430791848`:** [Unreal preflight #41348719394](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41348719394) SUCCESS (23 native test registrations across 12 files plus 22/22 source-extracted C++ adapter assertions), [Unreal source inventory #41348719383](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41348719383) SUCCESS, [repository smoke #41348719397](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41348719397) SUCCESS. A documentation commit after this report requires its own exact-head CI review before claiming all green.

**Overlap with alternative draft [#678](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/678):** #678 also composes #674's design-only adapter with #672's recruitment tests and has a 23-name registry; it tests entry through the lower-level guarded battle executor, whereas this PR #681 tests the additional `UTSS_CombatTurnManager::SubmitCommand` boundary and an explicit accepted positive control. Do not treat the two draft PRs as simultaneously additive merges or duplicate executable components. Choose/reconcile one reviewed integration path before any merge. No branch promotions were made.

**Not native proof:** this portable compilation is NOT Unreal C++ compilation, UHT, Editor automation, game SaveGame, VFX/physics or cinematic/gameplay acceptance. The newly added native test is still unrun. The authorized `neontic` workstation remains offline, and release/canon/art gates remain held.
