# Unreal 5.8.4 — cross-agent combat integration (23-test review branch)

**Status: SOURCE-ONLY REVIEW / NATIVE UE BUILD NOT ESTABLISHED / DO NOT MERGE.** All skills and character numbers in native test fixtures are noncanonical.

## Exact pinned source ancestry

- Base: [PR #672](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/672), exact starting head `b4dad1a01a696b910421f88b6ac308ffd19b7c40`. This contains [PR #671](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/671) and its 20 existing tests, plus one progressive recruitment test (21 names total).
- #671 contains unchanged seven data-contract files from Claude [PR #665](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/665), and is based on [PR #666](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/666) (which itself builds on gated skill [PR #662](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/662)).
- Selectively copied the **three adapter source/header/test files** unchanged from parallel [PR #674](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/674) exact donor head `d63476a089c666924a7e6983a00273c7451a5fc1`. The donor's 7 overlapping #665 files and its older verifier were **not** recopied, to avoid overwriting #671/#672 tests.
- Reconciled `unreal/Tools/Verify-Unreal.ps1` additively, preserving 21 inherited tests and requiring `TSTSS.CombatData.NonExecutableSkillReconciliation` and `TSTSS.CombatIntegration.AdapterRowsRemainDesignOnlyInExecutor`. **23 required test names**, subject to exact-head hosted source registration and eventual native execution.
- Added one new cross-layer native test in `TSTSSCombatAdapterAdmissionTests.cpp` which passes a truly `Proposed` DataTable row through the actual `FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly` adapter and then the actual higher-level `FTSTSSBattleSkillSystem::TryUseRow`. It checks the denied action does not change output state, cue, source combatant HP or resource, even when learning, story-affinity metadata, dummy mastery and equipment are present. The only intended authorization is an independently reviewed, manually authored `ReviewExecutable` row, which the adapter **does not** generate.

## Authority and safety

| Contract | Implementation source | Hold |
| --- | --- | --- |
| Five protagonists, Five Lights story tags, baseline HP/MP/MAG rank | Creator / #665 | No approved exact numeric stats or automatic elemental mastery |
| One to three recruited characters for early story review; exactly three for complete standard-party data | #666 / #672 versus #665 | No forced unrecruited characters, no implicit production-party rule change |
| School mastery, explicit learned skills, weapon class, cooldown, admission, failed-output invariance | #662 / #671 | Runtime executor cannot be replaced by low-level ability catalog |
| Proposed/Placeholder/CreatorApproved vs DesignOnly/ReviewExecutable | #665 vs #662 and donor #674 | **No automatic promotion** from creator data provenance or level unlock to executable permission |
| Story First Wake through Splashdown, save continuity, art and Orbiter lock | Established game canon | No changes from this composition |

## Check status and native acceptance

Source registration inventory and CI workflows must be read at the **current integration head**; successful checks for #672/#674 individually do not verify their combination. The authorized `neontic` Remote Desktop Commander device was **offline** during this source composition; genuine UE 5.8.4 UBT/UHT Win64 C++ build, full per-test Editor automation, DataTable import and gameplay verification are **OPEN**.

Native next gate: pull the exact review head into a clean disposable Windows checkout; run `unreal/Tools/Verify-Unreal.ps1 -EngineRoot 'C:\Program Files\Epic Games\UE_5.8'`; preserve build and automation JSON receipts and report every failed test, without weakening controls. Do not interpret source-only CI, an AI review, or successful text preflight as native Unreal proof. No merge, no art promotion, no unapproved spells or release.
