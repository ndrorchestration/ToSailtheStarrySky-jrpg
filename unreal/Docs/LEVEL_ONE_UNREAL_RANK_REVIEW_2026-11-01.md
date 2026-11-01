# Unreal Engine 5.8.4 — Level 1 protagonist stat rank review

**Status (2026-11-01): ACTIVE ENGINE IS UNREAL / CODE REVIEW-ONLY / NO APPROVED NUMERIC STATS.**

Creator superseded the previous Godot-forward plan: develop **To Sail the Starry Sky in Unreal Engine 5.8.4**, with C++/Blueprints as the forward implementation. Legacy Godot and JavaScript records may inform historical comparison, not active code ownership. Wrong-engine [Godot PR #658](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/658) was closed unmerged.

## Source and scope

- Base: `fix/ue58-foundation-native-target-20261101`, the native-compiled Unreal foundation candidate associated with [PR #650](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/650).
- `unreal/Source/ToSailTheStarrySky/Public/TSTSSLevelOneStatRanking.h`: pure C++ review validator, no UPROPERTY/SaveGame/Blueprint schema.
- `unreal/Source/ToSailTheStarrySky/Private/Tests/TSTSSLevelOneRankingTests.cpp`: named `TSTSS.Design.LevelOneStatRanks` UE automation test with illustrative pass/fail fixture cases.
- No changes to `FTSTSSCombatant`, save schema, C++ damage resolution, character assets, game modes, default stats, spell access, Godot files or protected main.

## Creator-approved Level 1 ranking (strict, across five)

- **MAG and MP:** Ender highest; Lyra second highest; Ionia/Reson/Aepex each below Lyra. No relative order among those three.
- **HP:** Lyra lowest; Ender second lowest; Ionia/Reson/Aepex each above Ender. No relative order among those three.
- Validate unmodified maximum Level 1 values, before gear, temporary statuses and story energies. The Five Lights are story affinities, not free stat bonuses or spell licenses.
- All numeric candidate fixtures are **illustrative, not creator-approved**. Historical art sheets containing numbers do not establish implementation values.

## UE integration boundary

At the inspected Unreal foundation, `FTSTSSCombatant` has `Health/MaxHealth` and `Resource/MaxResource`, plus Attack/Defense. **It has no canonical MAG or named MP field.** The test's `MagicPower` and `MaxMagicPoints` are independent **review inputs**; do not silently map MP to generic `Resource` or MAG to `Attack`, and do not change `UTSTSSSaveGame::CurrentVersion`. Separate [starting-party asset draft #640](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/640) contains an opt-in Ender DataAsset; reconciliation should use that policy after exact-branch review and numeric authorization.

## Required native test (not run by authoring)

Run in an isolated exact-head Windows UE 5.8.4 worktree, with approved Build Tools:

```powershell
# Build editor target first (actual project path must be supplied for your checkout).
& "<UE_ROOT>\Engine\Build\BatchFiles\Build.bat" ToSailTheStarrySkyEditor Win64 Development -Project="<CHECKOUT>\unreal\ToSailTheStarrySky.uproject" -WaitMutex -NoHotReloadFromIDE
# Then use UnrealEditor-Cmd with:
# -ExecCmds="Automation RunTests TSTSS.Design.LevelOneStatRanks" -TestExit="Automation Test Queue Empty"
```

Record engine version, UBT/UHT result, automation test count/result, process exit and exact commit SHA before claiming a native PASS. Source inspection or unrelated successful UE builds do not verify this new test.

Next native implementation gate: creator-approved MAG meaning, MP economy/cost and recovery rules, Level 1 numeric balances, 1–175 growth, Unreal starter-party assets, SaveGame backwards compatibility, UI, equipment and later party-join scaling. No merge, ship release, art admission or new ability permission from this review slice.
