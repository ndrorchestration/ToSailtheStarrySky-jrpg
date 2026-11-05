# TSTSS Unreal — Hybrid job catalog integrity gate

Date: 2026-11-04
Status: DRAFT / REVIEW-ONLY / UNMERGED / NO GAMEPLAY AUTHORIZATION.
Base: draft PR #741 at `0952c949dca2d91d472ef27d6f26d6aa4ee972c1` (stacked on #740 and native combat #685).
This is an additive source and in-memory automation increment, not a production job system.

## Bounded change

The initial Unreal `FTSTSSJobDefinitionRow` DataTable test correctly proved ordinary row import and `DesignOnly` rejection. However, manually collecting `Row->JobId` into a map could silently erase a prior entry if two authored row keys represented one job ID, or use an alias inconsistent with the DataTable row key.

`FTSTSSJobClassSystem::TryReadJobDefinitionsForReview` now builds a temporary catalog from the existing native `UDataTable` and commits the result only after every row passes:
- Exact `FTSTSSJobDefinitionRow` reflection schema.
- At least one row, nonempty DataTable row key and matching nonempty `JobId`.
- Nonempty `DisplayName`.
- No duplicate job IDs in the collected catalog.

Bad input returns false and preserves the entire caller-owned previous map. Both imported fixture jobs remain `DesignOnly`; no unlock, promotion, executable skill, class menu, save field, level award, or class canon is added. Test cases directly inject alias/duplicate identity, blank display, empty catalog and wrong schema and prove output preservation.

## Authority and exclusions

- Unreal Engine 5.8.4 is the active engine; no changes to historical Godot/JS.
- Ender: **Rift Scholar**. Other protagonists' final native profession names stay unresolved.
- Five Lights remain **story identity** and do not grant a magic school or combat class.
- The protagonist roster, Ender -> Ionia -> Lyra -> Reson -> Aepex recruitment order, three active battle slots, independent masteries and review-only ability gates remain unchanged.
- No class/gear/weapon/spell equipment rights, production actor, SaveGame migration, art canon, Starbourne player unlock, or protected-main merge.

## Verification ledger

- Source registration/inventory: 25/25 names; registry self-tests: 5/5 PASS on the isolated dirty worktree (source checks only).
- Native UE 5.8.4 Editor C++ initial dirty-worktree build: PASS (exit 0, no release/production change).
- Native targeted test and exact committed-head complete suite: recorded separately following execution; do not infer results from source checks or build alone.
- Native review output, test JSON and Windows scratch workspace stay private and out of Git.

## Next safe gate

Complete targeted `TSTSS.Design.HybridJobTableReadback` and all 25 native `TSTSS` automations from a pinned clean commit; inspect JSON per-test Success and postflight git status. Only after that may the draft be proposed for review. No gameplay/save integration is authorized by this milestone.
