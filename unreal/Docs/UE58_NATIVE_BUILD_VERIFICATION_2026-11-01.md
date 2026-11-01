# Unreal Engine 5.8.4 native verification — 2026-11-01

Status: **local Windows Editor build PASS; TSTSS automation 12/12 PASS on an isolated foundation candidate**. This is not a merge, release, art acceptance, or verification of downstream ship PRs.

## Source and environment
- Baseline: draft foundation PR #608, `feat/unreal-5-8-migration-foundation` at exact head `4b85f0d1d7b8870f09d72420871abf4553e3dfbf`.
- Candidate: `fix/ue58-foundation-native-target-20261101`, based on that exact SHA.
- Machine: Windows `neontic`; installed Unreal Engine 5.8.4 (`Engine/Build/Build.version`), Visual Studio 2022 Build Tools 14.44, Windows SDK 10.0.26100.0.
- Editor build: `Build.bat ToSailTheStarrySkyEditor Win64 Development -Project=<review-worktree>/unreal/ToSailTheStarrySky.uproject -WaitMutex -NoHotReloadFromIDE -MaxParallelActions=1`.
- Automation: `UnrealEditor-Cmd.exe <uproject> -unattended -nop4 -nullrhi -nosplash -NoSound "-ExecCmds=Automation RunTests TSTSS" "-TestExit=Automation Test Queue Empty" "-ReportExportPath=<review-worktree>/NativeAutomationReport2" -log`.

## Actual defects and isolated corrections
1. UE 5.8 rejected old `BuildSettingsVersion.V5` Editor settings sharing build products with `UnrealEditor`. Both Game/Editor targets now explicitly use `BuildSettingsVersion.V7` and `EngineIncludeOrderVersion.Unreal5_8`.
2. Native compiler error C2039 in `TSTSSWaterContactAdapter.cpp`: `UStaticMeshComponent::GetComponentBounds` does not exist. Replaced with `GetBounds().Origin` and `GetBounds().BoxExtent`, corroborated against the installed `SceneComponent.h`. Existing invalid-bounds fail-closed checks remain.
3. First automation attempt crashed at `TSTSSRulesTests.cpp:179`: `PartyRoster.Add(PartyRoster[0])` passed an element of the same TArray as source. Test now copies the member before appending. This fixes the test harness, not production save serialization.

## Native results and retained local receipts
- **Editor compile:** UnrealBuildTool `Result: Succeeded`; shell exit code **0** after fixes.
- **TSTSS automation:** `Automation Test Queue Empty 12 tests performed`, **12 succeeded / 0 failed / 0 not run**, process exit code **0**.
- Complete local JSON report: `NativeAutomationReport2/index.json`; HTML report: `NativeAutomationReport2/index.html`.
- Build log: `ue58-foundation-v7-build-fixed-test-20261101.log`; automation process log: `ue58-foundation-tests-fixed-20261101.log`; editor log: `unreal/Saved/Logs/ToSailTheStarrySky.log`.
- The automation run uses NullRHI: it **cannot** verify visual fidelity, rendering, collisions, animated clearances, 3D character rigs, or actual playability.

## Separate downstream blocker
- Draft Aureate Wake PR #626 at `4fc7e6f7235a22346aed9372df2e5e4a0d1a54d2` remains **unverified natively**. In a separate exact-head review worktree, after the build-target update, UnrealHeaderTool failed because `AureateWakeWaterObserverComponent.h` references `UTSTSSWaterLandingGate`, whose implementation was absent on that branch. The foundation contains a newer water-landing gate and different First Wake state contract; copying only its header is not safe.
- Reconcile story/water dependency contracts on a **separate review branch** before compiling PR #626. Preserve authored Orbiter motion hold and review-only noncanonical art. Do not merge the PR based on this foundation success.

## Limitations / authority
No Unreal Editor visual capture, imported GLB proof, packaged Windows build, complete First Wake cinematic, production art approval, or Godot-to-Unreal gameplay parity is established here. Godot remains story/canon authority. No protected main merge, release, installation, or canonical content change is implied.
