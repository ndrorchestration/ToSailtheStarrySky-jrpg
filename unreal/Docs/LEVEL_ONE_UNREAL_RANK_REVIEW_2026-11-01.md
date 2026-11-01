# Unreal Engine 5.8.4 — Level 1 protagonist stat rank review

**Status (2026-11-01): ACTIVE ENGINE IS UNREAL / CODE REVIEW-ONLY / NO APPROVED NUMERIC STATS.**

Creator superseded the previous Godot-forward plan: develop **To Sail the Starry Sky in Unreal Engine 5.8.4**, with C++/Blueprints as the forward implementation. Legacy Godot and JavaScript records may inform historical comparison, not active code ownership. Wrong-engine [Godot PR #658](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/658) was closed unmerged.

## Source and scope

- Base: `fix/ue58-foundation-native-target-20261101`, the native-compiled Unreal foundation candidate associated with [PR #650](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/650).
- `unreal/Source/ToSailTheStarrySky/Public/TSTSSLevelOneStatRanking.h`: pure C++ review validator, no UPROPERTY/SaveGame/Blueprint schema.
- `unreal/Source/ToSailTheStarrySky/Private/Tests/TSTSSLevelOneRankingTests.cpp`: named `TSTSS.Design.LevelOneStatRanks` UE automation test with illustrative pass/fail fixture cases.
- `unreal/Source/ToSailTheStarrySky/Public/TSTSSLevelOneReviewAsset.h` and `Private/TSTSSLevelOneReviewAsset.cpp`: optional Blueprint-readable Unreal `UDataAsset` with *editor review only* draft HP/MP/MAG fields. `bEnableLocalReview` defaults to false; `IsConsistentForReview()` validates but never sets gameplay state or declares balance approval.
- `unreal/Source/ToSailTheStarrySky/Private/Tests/TSTSSLevelOneReviewAssetTests.cpp`: `TSTSS.Design.LevelOneReviewAsset` native automation test, including disabled-by-default, positive validation, invalid/tied stats, duplicate IDs, and disabling after review.
- `unreal/Tools/Verify-Unreal.ps1`: the native required-test inventory now includes both stat review tests. Source inventory checks fail if a new Unreal test is declared but not added to this list.
- No changes to `FTSTSSCombatant`, save schema, C++ damage resolution, character assets, game modes, default stats, spell access, Godot files or protected main.

## Creator-approved Level 1 ranking (strict, across five)

- **MAG and MP:** Ender highest; Lyra second highest; Ionia/Reson/Aepex each below Lyra. No relative order among those three.
- **HP:** Lyra lowest; Ender second lowest; Ionia/Reson/Aepex each above Ender. No relative order among those three.
- Validate unmodified maximum Level 1 values, before gear, temporary statuses and story energies. The Five Lights are story affinities, not free stat bonuses or spell licenses.
- All numeric candidate fixtures are **illustrative, not creator-approved**. Historical art sheets containing numbers do not establish implementation values.

## UE integration boundary

At the inspected Unreal foundation, `FTSTSSCombatant` has `Health/MaxHealth` and `Resource/MaxResource`, plus Attack/Defense. **It has no canonical MAG or named MP field.** The test's `MagicPower` and `MaxMagicPoints` are independent **review inputs**; do not silently map MP to generic `Resource` or MAG to `Attack`, and do not change `UTSTSSSaveGame::CurrentVersion`. Separate [starting-party asset draft #640](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/640) contains an opt-in Ender DataAsset; reconciliation should use that policy after exact-branch review and numeric authorization.

## Added boundary and presentation regression coverage

The dedicated Unreal C++ tests now also check:

- **Roster array order independence:** swapping five-party entry rows cannot change acceptance; comparisons bind to canonical character IDs.
- **Unconstrained third tier:** Ionia, Reson, Aepex may vary or tie amongst themselves for HP/MP/MAG without being assigned a ranking the creator never approved.
- **Strict boundary behavior:** zero MP/MAG among the lower three is a valid shape when the two higher ranks are strictly greater, while zero HP remains invalid.
- **Fail-closed inputs:** negative or out-of-range inputs, Level 0 or Level 2 entries, duplicate/unknown/missing IDs, strict-rank ties and inversions are rejected.
- **Blueprint-facing review DataAsset:** entries can be reordered without changing the verdict; the opt-in gate can be disabled again. Even an accepted shape remains numeric-design review only.

These are additional **authored automation assertions, not yet proven by Unreal Editor execution**.

## Required native test (not run by authoring)

Run in an isolated exact-head Windows UE 5.8.4 worktree, with approved Build Tools. Run **both** stat review tests (the native verification script's `TSTSS` suite requires both):

```powershell
# Build editor target first (actual project path must be supplied for your checkout).
& "<UE_ROOT>\Engine\Build\BatchFiles\Build.bat" ToSailTheStarrySkyEditor Win64 Development -Project="<CHECKOUT>\unreal\ToSailTheStarrySky.uproject" -WaitMutex -NoHotReloadFromIDE
# Then use UnrealEditor-Cmd with:
# -ExecCmds="Automation RunTests TSTSS" -TestExit="Automation Test Queue Empty"
```

Record engine version, UBT/UHT result, automation test count/result, process exit and exact commit SHA before claiming a native PASS. Source inspection or unrelated successful UE builds do not verify either new test.

## Verification on authored review head (not native)

- The Windows `neontic` workstation was **offline** on November 1, 2026, so no UnrealBuildTool, UnrealHeaderTool, native Editor, or in-engine test ran on this branch.
- `unreal/Tools/check_unreal_test_inventory.py` and `unreal/Tools/check_automation_registry.py` executed successfully in hosted source-only CI at commit `21970d9a084b9ba7b12b0dbedacfdae59d0f2a92` ([inventory #41335189000](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41335189000), [preflight #41335188993](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41335188993)). Those checks validate test registration, not C++ compilation or UHT reflection.
- A separate **local GCC 14.2 host-shim** compilation of the pure rank-contract header and representative positive/negative cases passed; the shim imitates only minimal Unreal container/name types, and is **not UE C++ build or UHT verification**. The new reflected DataAsset was not compiled by that shim.

## Unreal Editor authoring procedure (after native compile)

1. Create a `TSTSSLevelOneReviewAsset` in a noncanonical staging folder; its `Entries` is empty and `bEnableLocalReview=false` by default.
2. Enter all five Level 1 draft profiles; do not copy the example fixture numbers as gameplay canon.
3. Enable `bEnableLocalReview` solely to display `IsConsistentForReview` in a review-oriented Blueprint or inspector. A `true` result means only *relative ordering and input shape* passed, **not** a creator approval.
4. Do not link the review asset to `FTSTSSCombatant`, the First Wake starting-party DataAsset, SaveGame, magic permissions, or combat UI until a separate reviewed integration slice is authorized.


Next native implementation gate: creator-approved MAG meaning, MP economy/cost and recovery rules, Level 1 numeric balances, 1–175 growth, Unreal starter-party assets, SaveGame backwards compatibility, UI, equipment and later party-join scaling. No merge, ship release, art admission or new ability permission from this review slice.
