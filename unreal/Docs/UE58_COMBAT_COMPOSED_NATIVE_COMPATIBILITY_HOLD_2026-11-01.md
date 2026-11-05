# Unreal 5.8.4 combat composition — known native compatibility defects

**Review-only**, 2026-11-01. Stacked on draft PR #681 exact head `e9c8e35c63198ecb1fcbb1b8bc482fa6e7861110`. No protected-main merge, creator art acceptance, gameplay or public build promotion.

## Verified host reconnaissance

Authorized Windows `neontic` Remote Desktop Commander session reconnected and reported **Online** (device ID `bcce7514-436c-4530-8f45-3b446e98a4b3`). Verified locally:

- Installed `C:\Program Files\Epic Games\UE_5.8\Engine\Build\Build.version`: Unreal Engine **5.8.4**, changelist 58902052.
- Visual Studio 2022 Build Tools installed, MSVC directory `14.44.35207`, Windows SDK `10.0.26100.0`.
- Clean, separate checkout `C:\TSTSS_Unreal_Combat_PR681_Native_20261101` at exact source head `e9c8e35c63198ecb1fcbb1b8bc482fa6e7861110`; Git status clean and **23 required native automation names registered**.
- The portable `check_combat_design_only_compiled.py` on this Windows host cannot find `g++`/`clang++` on PATH, **not** evidence that MSVC or Unreal Build Tools are absent. Its 22/22 source C++ checks previously passed on hosted GitHub CI.
- Remote terminal security checks blocked invoking the repository's `Verify-Unreal.ps1` script. **No new UE 5.8.4 Editor build or native automation was executed**. Do not translate the successful RDC connection into a native PASS.

## Exactly reused from historically native-verified PR #650

[Draft #650](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/650) verified UE5.8.4 native Editor build and 12/12 automation tests on the earlier foundation branch. PR #681's composition still had known original defects. This isolated follow-on review changes only:

1. `ToSailTheStarrySkyEditor.Target.cs`: `BuildSettingsVersion.V5` → **V7**; explicitly sets `IncludeOrderVersion.Unreal5_8`.
2. `ToSailTheStarrySky.Target.cs`: same UE5.8 target update.
3. `TSTSSWaterContactAdapter.cpp`: replaces removed `UStaticMeshComponent::GetComponentBounds` with `GetBounds().Origin` and `GetBounds().BoxExtent` without relaxing the invalid-world-bounds guards.

### Known unresolved test harness blocker

The exact PR #681 source additionally still contains `Save->PartyRoster.Add(Save->PartyRoster[0])` in `TSTSSRulesTests.cpp`, which caused an actual Unreal TArray self-aliasing assertion in historical PR #650. That prior fix copied the member to `const FTSTSSCombatant DuplicateMember` before `Add`; it has **not** been ported to this branch because the GitHub editing action was blocked. Do not run the full 23-case suite and claim PASS without applying/reviewing this known test-only fix and successfully completing exact-head native automation.

## Validation and next action

This branch is review-only and does not inherit #650's native PASS because the source graph contains an additional combat adapter, DataTable, turn manager and two new native tests. The smallest next step is clean exact-head Windows Unreal 5.8.4 Editor build followed by the required 23 native automation cases, with independent JSON report receipt. **Do not merge** until its own native proof, outstanding test-only alias defect resolution and owner approval. The Five Lights remain story affinities, not automatically granted combat spells.
