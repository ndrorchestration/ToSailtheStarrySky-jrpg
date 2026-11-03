# V2 First Wake → Splashdown native integration convergence (review only)

**Review stack:** [Draft PR #734](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/734) is pinned to [draft PR #713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713) commit `f7b58df09bafc8eec04e463c9a2e82cbff7606e3`; it ports the smallest actor/state/water-gate test from independent [draft PR #730](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/730). **No merges, art promotion, Starbourne gate change, dependency install, or player SaveGame change.**

## What this draft implements

- One new proposed **Unreal C++ automation test** `TSTSS.FirstWake.InteractionToSplashdown` using actual transient `ATSTSSMilestoneActor`, `UTSTSSFirstWakeState`, `UTSTSSWaterLandingGate`, and in-memory `UTSTSSSaveGame` instances. This is not a scene test.
- Validates flyer → Ionia hiring → Aureate boarding → lift/pressure/reserve inspections → engineering signoff → launch, rejecting skipped and duplicate interactions.
- Verifies a generic milestone cannot produce `SeaContact` or `FlotationConfirmed`. A *synthetically supplied* 180 cm/s water-impact sample only marks contact. One second of calm then a gap does not count; two seconds of continuous stable contact are required before the existing Chapter 1 Act 1 boundary becomes true. This is **water-gate arithmetic/authority**, not proof that a ship collided with water in a real map.
- Continues through empty reserve and berth recovery, validates a version-2 in-memory save payload, restores a separate story state and proves Reset returns to Prelude. Does not write any disk save slot or mutate the user's playthrough.
- On this integrated branch only, also asserts actual **read-only review-objective text** for the flyer, Ionia, boarding, every inspection, launch, sea contact, Splashdown and recovery; rejected interactions preserve the prior objective. No HUD/PIE screenshot or player-input claim.

## Integrated proof rules: 25 → 26

The parent V2 Prelude branch had **25 named required native automations**, with historical 25/25 native success only at its previously recorded exact commit. The proposed added test makes **26** names. On this draft:
- `unreal/Tools/Verify-Unreal.ps1` requires the new test in the exact-head native JSON report.
- `unreal/Tools/Assert-NativeAutomationReport.ps1` now refuses reports not evaluated against exactly 26 unique required names.
- `unreal/Tools/Test-NativeAutomationReportFixtures.ps1` exercises genuine validator semantics with positive and deliberately corrupt *synthetic JSON* fixtures. This does not run Unreal.
- The new `test_firstwake_integration_contract.py` and existing `check_integrated_review_contract.py` explicitly fail closed if the 26th name, objective assertions, physical gate or Chapter 1 boundary protections drift.
- Historical documents and their `NATIVE_AUTOMATION_25=NOT_TESTED` baseline are **retained as historical evidence**. The composed check separately reports `native_automation_26=NOT_TESTED` until a real current-head native report is accepted.

## Evidence matrix

| Verification dimension | State at proposal |
| --- | --- |
| Cross-stack source reconciliation and 26-name registration | REVIEW IMPLEMENTED |
| Local/hosted Python authority tests, source inventory and PowerShell synthetic fixtures | Require exact-head results; do not infer native execution |
| Exact-head UE5.8.4 Windows Editor C++ compile | NOT_VERIFIED |
| Exact-head 26/26 real native automation JSON, including the new test | NOT_EXECUTED |
| Exact-head native Editor V2 Prelude seven-actor/map admission | NOT_VERIFIED |
| Actual P01–P13 mouse/keyboard PIE traversal | NOT_TESTED |
| Physical overlap, immersion, sustained flotation measured in Unreal | NOT_VERIFIED |
| Ender static-model integration / authored likeness and rig | NOT APPROVED; separate draft PR #643 |
| Chapter 1 cinematic visuals, HUD and save-to-disk | NOT VERIFIED |
| Main branch merge, art/canon promotion, Starbourne unlock or release | NOT AUTHORIZED |

On November 3, an authorized workstation sample showed a conservative resource gate **PASS** (7.54 GiB physical free, 8.929 GiB commit headroom) **but** existing Unreal Editor and Live Coding sessions were still active. The strict native launcher must therefore remain **BLOCKED**. No session was terminated and no competing UE process launched.

## Next smallest reversible milestone

On an idle authorized Windows workstation, in a fresh clean detached exact-head checkout of this draft, run the strict UE 5.8.4 Win64 Editor build and full **26-test** automation with a unique validated JSON report; then separately perform PR #713's native V2 map-admission tool without PIE and record a distinct receipt. Only after those two actual native proofs, execute the P01–P13 in-Editor player controls and genuine ship/water-contact capture. Distinguish all source/proxy checks from native, physical, visual and playable acceptance.
