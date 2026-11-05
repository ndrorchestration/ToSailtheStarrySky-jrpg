# Combat data contract (Unreal gameplay track, increment 1)

Status: **source-only, not executed in Unreal Engine.** See "Verification" below.

## Baseline this builds on

Audited 2026-11-01 from PR heads (shallow fetch, exact SHAs):

| PR | Head | Combat core present |
| --- | --- | --- |
| #608 foundation | `4b85f0d` | yes (**this work is based here**) |
| #610 ship preview actor | `dc2a188` | rules only (`TSTSSCombatRules`; no turns, encounter-ability gate or ability tests) |
| #626 wing geometry | `4fc7e6f` | rules only |
| #631 supports + importer | `a0be9de` | rules only |
| #643 character lookdev | `6c89eac` | yes |
| #656 ship forms review | `61e02fd` | yes (same combat blobs; this commit also applies cleanly on top of it) |

The combat blobs (`TSTSSCombatRules/Turns/Abilities` .h/.cpp and the Abilities/Turns tests) are byte-identical in
#608, #643 and #656; only `TSTSSRulesTests.cpp` differs. Nothing in `main` contains `unreal/`.

## What already existed (IMPLEMENTED in source, not natively verified)

- `FTSTSSCombatRules::TryApplyAction`: pure, transactional action resolution. Damage is
  `max(1, Power + Attack - Defense)`, healing is `Power + Attack` capped at max HP.
- `FTSTSSCombatTurns`: deterministic turn order, rounds, rollback on invalid action.
- `FTSTSSEncounterGate`: faction-aware outcome evaluation.
- `FTSTSSCombatAbilities::TryUse`: authorization gate (learned set, faction targeting, costs).
  The `FTSTSSAbilitySpec` catalog it consumes existed only inside test fixtures.

## What this increment adds (reversible, additive)

`TSTSSCombatData.h/.cpp`: a DataTable-ready schema, a validator, and a builder that derives the
`TryUse` catalog and per-character learned sets. **No existing runtime file is modified.**
The only existing file touched is `Tools/Verify-Unreal.ps1` (four test names appended).

Loop: *player selects action -> `TryUse` validates and resolves -> HP/resource feedback -> progression
unlocks via level -> new actions available.* This increment owns the data and gating end of that loop.

### Rules enforced

| Rule | Source of the rule |
| --- | --- |
| Exactly the five protagonists, fixed order Ender, Ionia, Lyra, Reson, Aepex | creator directive |
| Affinity: Ender Spirit, Ionia Earth, Lyra Water, Reson Fire, Aepex Air | creator directive |
| Starting magic and MP: Ender highest, Lyra second (strict) | creator directive |
| Starting HP: Lyra lowest, Ender second lowest (strict) | creator directive |
| Active party is exactly 3 distinct protagonists | creator directive |
| Affinity on an action is optional metadata, never a usage restriction | README: affinities are narrative, not mandatory classes |
| Resonance has no field and no cost pool | README: story energy, not automatic combat magic |
| Shipping mode rejects anything not `CreatorApproved` | "do not invent canonical content" |
| Healing that targets enemies, empty learners, duplicate ids, out-of-range values rejected | data-integrity, my assumption |

Ties among Ionia, Reson and Aepex are allowed. Ties at any constrained rank fail (my reading of
"highest" and "second"; relax in `ValidateBaselines` if you intended ties to pass).

## Gameplay Ability System decision

**Not adopted now.** Reasons: (1) combat here is turn-based and must be transactional and side-effect-free;
GAS applies effects by mutating attribute sets in place, which fights the rollback model; (2) the current core
is pure functions testable without a world or ASC, GAS is not; (3) it adds three module dependencies
(`GameplayAbilities`, `GameplayTags`, `GameplayTasks`) for no feature the slice needs.
Revisit if real-time action combat, ship combat, or large buff/debuff stacking arrives. `GameplayTags` alone
may be worth adopting earlier for status and element tagging.

## Known conflicts and gaps (not fixed here)

- **Legacy JS stat model contradicts the approved HP ordering.** Executing `derive()` from
  `modules/jrpg-stat-model.js` on its own level-1 profiles gives max HP Aepex 85, Lyra 86, Ionia 92, Ender 101,
  Reson 123: Lyra is not lowest and Ender is fourth lowest. Its aether attack ordering (Ender 27, Lyra 19, the rest
  below 12) does match the approved magic ordering, and it has no MP stat. Legacy numbers therefore cannot be
  ported as canon. The validator exists partly to catch this class of drift.
- **Single resource pool.** The core has one `Resource` pool. Whether weapon techniques share it with spells is an
  open creator decision. It is not modelled.
- **One magic stat.** `StartMagic` is aggregate until the damage formula separates physical and aether scaling.
- **No status effects, initiative stat, elements-as-damage-types or enemy definitions** in the Unreal core yet.
- **Save integration:** learned sets are derived from `(baseline, level)` and are not persisted. Confirm that against
  the versioned SaveGame schema before relying on it.
- **Open design inputs needed from the creator:** the actual spell/technique/ability lists, per-character starting
  and growth numbers, unlock levels, and the technique resource model.

## Verification

| Check | Result |
| --- | --- |
| UnrealHeaderTool / Win64 compile | **not run** (no Unreal install in the authoring environment) |
| Unreal automation tests (`TSTSS.CombatData.*`) | **not run** |
| Host build against stand-in UE types, g++ `-std=c++17` with ASan/UBSan | built; 4 new + 2 existing combat tests, 151 checks, 0 failures |
| Mutation check (10 deliberate validator defects) | 10/10 caught |
| `check_automation_registry.py` / inventory | PASS on the #608 base with this change (16 names registered and required). **Separate finding:** on the #656 head both checks already fail because `TSTSS.Ship.PreviewFormsAndOrbiterHold` is registered but missing from the verifier list; not touched here |

The host build uses hand-written stand-ins for `TArray/TMap/TSet/FName` and the automation base class. It
checks logic and C++ validity of this code, **not** UHT reflection output, UE API fidelity or editor behaviour.
Run the native steps in `UNREAL_TEST_COMMANDS.md` on the Windows workstation before treating any of this as passing.
