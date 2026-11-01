# Level 1 protagonist stats — isolated native review slice (2026-11-01)

**Status: creator-approved RELATIVE ORDER, provisional numeric fixture, NOT implemented in production combat.**

This branch stacks on draft #601, whose native GDScript battle contracts define `hp/max_hp` and `mp/max_mp` but have no playable Level 1 core-roster stat table. The action resolver uses explicitly supplied `power`, checks MP/stamina and clamps hit points; it **does not have an approved magical attack or healing scaling formula**. The existence of an MP resource field is not proof of an approved starting MP economy. MAG is not a field in the current draft roster transaction. This is separate from the historical browser model, where `aetherAttack` exists but conventional `MP` is absent.

## Creator contract (strict Level 1 ranks)

- **MAG:** Ender > Lyra > each of Ionia, Reson, Aepex.
- **Maximum starting MP:** Ender > Lyra > each of Ionia, Reson, Aepex.
- **Maximum starting HP:** Lyra < Ender < each of Ionia, Reson, Aepex.
- The order among the other three remains **unspecified**.
- These values are unmodified initial Level 1 baseline maximum stats, before equipment, buffs, statuses or story-energy effects.

## Minimal review-only slice

- `godot/scripts/combat/level_one_rank_review.gd`: pure profile validation over five IDs, `level`, `max_hp`, `max_mp`, `mag`; fail closed for missing/extra members, invalid types/ranges, duplicates via dictionary keys, Level 1 violations and all rank ties or inversions.
- `godot/tests/level_one_rank_review_test.gd`: positive and negative fixtures, immutability and fail-closed checks.
- No change to `turn_transaction.gd`, `ability_turn_adapter.gd`, `turn_queue.gd`, `roster_battle.gd`, saves, story, default map or gameplay HUD.

## Provisional numbers used ONLY in the test fixture

| Character | Max HP | Max MP | MAG (candidate alias) |
| --- | ---: | ---: | ---: |
| Ender | 101 | 64 | 27 |
| Lyra | 86 | 52 | 19 |
| Ionia | 112 | 28 | 8 |
| Reson | 123 | 20 | 9 |
| Aepex | 108 | 38 | 11 |

These are **illustrative fixture values, not creator-approved game balances**. HP/legacy aether attack are anchored to historical browser formula values where possible; Ionia and Aepex HP are raised solely to satisfy the explicit new order. MP is a free-standing proposed reservoir until costs, recovery, save serialization and spell permissions are decided. The exact MAG formula and damage/healing authority are unresolved, so the `MAG` column is not automatically wired into the native action `power`.

## Minimal verification

Run on an isolated checkout of this exact branch with **Godot 4.7.2**:

```sh
godot --headless --path godot --editor --quit
godot --headless --path godot --script res://tests/level_one_rank_review_test.gd
```

Expect `NATIVE_LEVEL_ONE_RANK_REVIEW_PASS`, zero process exit code and no script errors. Before engine execution, this is only an authored source/test candidate. Do not treat any JavaScript validation or unrelated native CI as proof of a Godot pass.

**Next gate:** Decide canonical MP recover/cost rules, MAG scaling, character growth and gear modifiers, then review Level 1 numbers, add actual starting roster initialization and serialization regressions on the chosen Godot combat authority. Unreal adoption requires equivalent tests and independent review. No automatic merge, canon promotion or release.

References: [creator rank contract in Notion](https://app.notion.com/p/3e0f5bad238b817b9ad4da4a2c0cb40f) • [parallel docs PR #657](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/657) • [native draft #601](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/601).
