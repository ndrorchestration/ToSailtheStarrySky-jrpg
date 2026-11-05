# Unreal runtime integration contract (draft)

## First Wake

Use `UTSTSSFirstWakeState` as an ordered gate. For each actual player-driven event (flyer discovery, Ionia hired, boarding, engineering checks, launch, sea contact, confirmed flotation, empty-reserve inspection and return), attempt to advance exactly once. Never advance from a camera transition alone. The C++ state is not yet connected to interactable actors or level scripting.

## Persistence

`UTSTSSSaveGame` is version 1; `UTSTSSPersistence` exposes `SaveProgress`, `LoadProgress` and `IsValidSlotName` to Blueprints. Persist milestone and roster through deliberate assignment. Local slot uses user index 0; no remote/cloud sync, write-atomicity guarantee, migration from Godot, user profile separation, or crash-recovery guarantee is claimed. A corrupt or unsupported loaded payload returns null. Invalid payloads do not initiate writes. Loading must be connected to game-flow UI and tested in a real Unreal runtime before playable acceptance.

## Combat

`UTSTSSCombatRules::TryApplyAction` is a pure transaction across a copied roster. UI and animations must commit `OutRoster` only when true. Reject absent IDs and unaffordable costs. This is an early deterministic approximation rather than the final JRPG damage/balance model.

## Character art

No source images have been imported into Unreal. Creator-approved art remains the only artistic target; avoid substituting generic marketplace models and calling them canonical.

## Acceptance

Native compile, automated test results, save/load round-trip, rendered First Wake footage, visual approval, then Windows packaging. Preserve the existing Godot release while Unreal is unverified.

## Combat migration verification — 2026-10-30

Godot draft PR #601 is a **reference implementation**, not permission to copy its provisional rules as final canon. The Unreal module already contains `UTSTSSCombatRules::TryApplyAction` with transactional roster output. An additional Unreal automation test, `TSTSS.Combat.RejectsInvalidActionsWithoutMutation`, now covers unaffordable actions, unknown targets, negative power, duplicate unit IDs, and output preservation on failure.

These tests are **source committed but Unreal-native execution has not been verified**. Run the Unreal Editor automation suite in the pinned UE 5.8 environment and retain exact-head logs before UI, encounter, or release promotion. Combat formulas, learned-ability authorization, turn sequencing, factions, party eligibility, and presentation binding still require an explicit UE design and verified implementation. The approved cast art and First Wake story are unchanged.

## Isolated Unreal turn authority — 2026-10-30

- `Public/TSTSSCombatTurns.h` and `Private/TSTSSCombatTurns.cpp` implement deterministic ordered participants, active-actor enforcement, copy-on-write roster action updates, incapacitation skipping, round rollover and accepted-action count, calling the existing `UTSTSSCombatRules` primitive.
- `Private/Tests/TSTSSCombatTurnsTests.cpp` provides Unreal automation regression coverage for out-of-turn rejection, knockout, skipped-final-participant round rollover, input immutability, and invalid order rejection.
- **All test results remain unverified.** Compile and run the `TSTSS.Combat.TurnOrderAndAtomicity` automation test under Unreal Engine 5.8 before accepting the semantics. Review invalid/unsupported ability targets, encounter authority, learned skills, participant allegiance, incapacitated allies and save serialization separately.
- This is a noncanonical engineering prototype; it does not connect to player-facing First Wake, combat HUD, game art, enemy AI, chapter events or shipping installers. The Godot branch and approved characters remain unchanged.

## Unreal learned-ability authorization — 2026-10-30

The isolated `FTSTSSCombatAbilities` adapter receives explicit ability specs, learned-by-character records and faction mappings. It rejects unknown/unlearned abilities, invalid factions and incompatible self/ally/enemy targets before delegating to `FTSTSSCombatTurns::TryAction`. Regression coverage is authored under `TSTSS.Combat.AbilityAuthorization`.

**Execution/acceptance boundary:** Unreal 5.8 compilation and tests have not been demonstrated. The ability catalog and learning records in tests are synthetic fixtures, not canonical skills or character progression. No encounters, HUD, VFX, scene entry, balance acceptance or release authority is implied. Native Editor tests and exact-head build logs are required before promotion.

## Ability gate negative-path regression extension

The Unreal `TSTSS.Combat.AbilityAuthorization` fixture now checks missing target faction, negative ability cost, out-of-turn action rejection, and preservation of the previously accepted output after failures. These tests remain **authored, not engine-executed**. No HUD, encounter, canonical learning progression, or cast asset change is authorized by this work.
