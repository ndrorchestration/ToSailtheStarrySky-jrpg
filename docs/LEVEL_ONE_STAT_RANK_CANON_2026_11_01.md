# Level 1 protagonist stat ranking — creator-authorized design contract

**Status (2026-11-01): CREATOR-APPROVED RELATIVE RANKINGS / EXACT NUMBERS OPEN / ENGINE IMPLEMENTATION NOT AUTHORIZED BY THIS DOCUMENT.**

This is a public-safe, narrow handoff of the creator's October 31 direction for *To Sail the Starry Sky*. It does not authorize numeric balancing, modified saves, spell admission, art promotion, release, or an unreviewed gameplay rewrite. **Creator correction (2026-11-01): Unreal Engine 5.8.4 C++/Blueprints is the active forward game-development target, NOT Godot.** Former Godot/browser mechanics are legacy reference material, not forward gameplay authority. Historical Godot review PR #658 was closed unmerged as wrong-engine work.

## Canonical ranking, across all five characters

At **Level 1**, compare **unmodified initial values** before equipment, buffs, temporary statuses, party modifiers, or story-energy effects:

| Metric | Strict ranking required | Ranking among the other three |
| --- | --- | --- |
| Magic power (display label MAG, implementation identity still to specify) | Ender > Lyra > Ionia / Reson / Aepex | Not specified |
| Maximum starting magic points (MP) | Ender > Lyra > Ionia / Reson / Aepex | Not specified |
| Maximum starting hit points (HP) | Lyra < Ender < Ionia / Reson / Aepex | Not specified |

Machine-readable *constraints* (not a data file with approved numbers):

```text
MAG[ender] > MAG[lyra]
for c in [ionia, reson, aepex]: MAG[lyra] > MAG[c]

MP[ender] > MP[lyra]
for c in [ionia, reson, aepex]: MP[lyra] > MP[c]

HP[lyra] < HP[ender]
for c in [ionia, reson, aepex]: HP[ender] < HP[c]
```

No other pairwise ranking was specified. Do not infer "Reson highest HP" or particular final MAG/MP/HP numbers from generated character art.

## Source inspection — historical JavaScript model, not forward native balance

Inspected `modules/jrpg-stat-model.js` (default-branch blob SHA `8a91c6c7e1e946cfee424ff9425e5c651f2dc5b5`) and `tests/jrpg-stat-model.test.js` (blob SHA `cad9de9bbb63c2d9e01614499688b7df8507961c`). Its unchanged Level 1 primaries and `derive()` yield:

| Character | Primary Spirit | Derived `maxHp` | Derived `aetherAttack` |
| --- | ---: | ---: | ---: |
| Ender | 12 | 101 | 27 |
| Lyra | 9 | 86 | 19 |
| Ionia | 3 | 92 | 8 |
| Reson | 4 | 123 | 9 |
| Aepex | 3 | 85 | 11 |

The above table is **characterization**, not an approved new numeric target. The legacy `aetherAttack` ordering happens to meet the first/second relationship, but `aetherAttack` has **not** been established as the future MAG stat. The model's `maxHp` violates the newly locked HP hierarchy: Aepex is lower than Lyra, and Ender is higher than both Lyra and Ionia. **No MP-derived field exists in this model**; historical Aether/Echoes resources are not automatically MP.

Existing creator locks include Ender's Level 1 primary Spirit = 12 and Ionia's Presence = 9. Preserve both until explicitly changed. The primary-stat substrate is Might, Grace, Wits, Spirit, Presence, not the arbitrary ATK/DEF/MAG/LCK numbers printed by prior generated mockups.

## Unreal Engine 5.8.4 implementation plan (review-only; not executed by this document)

1. Pin the actual Unreal native combat branch and exact commit; inspect `FTSTSSCombatant`, the combat rules, any approved party DataAsset, SaveGame field mapping, initial roster defaults, growth, and UI projection. Do not assume the old Godot/browser models describe the Unreal implementation.
2. Specify whether "MAG" is a derived power, primary attribute, or distinct independent stat, and whether "MP" maps to Unreal `Resource/MaxResource` or requires its own SaveGame fields and versioned migration. Until decided, never silently relabel generic resources as MP. The Five Lights story affinities grant no automatic spell schools, abilities, or stat boosts.
3. Propose exact numeric Level 1 values with an explicit formula or table, plus rationale for fragile-caster survivability; review progression to Level 175 and recruitment-level scaling. Do not equate the Level 1 ranking with a mandatory same rank at every level.
4. Add Unreal automation tests for strict inequalities; exercise unmodified and starter-equipped profiles separately; verify Level 1, save/load migration, leveling, Blueprint/UI readback, and reproducible native Editor behavior.
5. Run native UE 5.8.4 UBT/UHT Editor compile and TSTSS automation at an exact commit head, then separately review actual gameplay and UI. Require creator approval of numeric balance before canonizing values. Keep work in isolated draft PRs; no automatic merge or release.

## Visual art and communication contract

Future character sheets may label Ender **highest MAG / highest MP / second-lowest HP** and Lyra **second-highest MAG / second-highest MP / lowest HP**. For the others, show **MAG and MP below Lyra; HP above Ender** with no invented ranking among Ionia, Reson, Aepex. If a character art generator insists on numeric panels, mark all values `ILLUSTRATIVE — NOT APPROVED` or omit them entirely. Older cast-art images remain historical visual studies, not source-of-truth stat tables.

Keep Ionia's **long curly blonde hair** whether worn down, partially pinned, or in a captain's updo, and her green-eye character lock. Preserve the established protagonist height order: **Reson > Aepex > Ender > Ionia > Lyra**. These are independent of gameplay stat ranks.

## Source and scope

- [Notion protagonist roster decision (2026-10-31)](https://app.notion.com/p/3e0f5bad238b817b9ad4da4a2c0cb40f)
- [Notion visual addendum](https://app.notion.com/p/405f5bad238b81f2b97bcc4bb9c0c4e6)
- [Existing character/art locks](CHARACTER_AND_ART_AUTHORITY.md)
- [Agent source/approval rules](../AGENTS.md)

**Scope: documentation-only proposal.** No gameplay values, runtime files, 3D assets, or engine permissions are changed by this document.
