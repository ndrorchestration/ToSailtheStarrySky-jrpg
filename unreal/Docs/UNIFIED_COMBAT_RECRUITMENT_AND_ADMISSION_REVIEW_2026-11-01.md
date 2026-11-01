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
