# Unreal 5.8.4 — Windows native first-build handoff (2026-10-31)

**Decision status:** DRAFT, SOURCE-VERIFIED. Unreal 5.8.4 is being installed on `neontic` by its owner, but it was **not complete at inspection**. A native Unreal editor compile, game render, combat scene and First Wake splashdown are **not verified**. Do not merge protected main or publish installer.

## Current code authority and dependency reconciliation

- [Draft integration PR #642](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/642) was created from exact updated First Wake [foundation PR #608](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/608) commit `622d1843a69e4c5a10b7cfb9de247f78857b6c3f`, preserving its newest Explorer character and water-contact adapter C++/header and setup docs.
- Reconciled **58 noncolliding Unreal/CI paths** from previously source/Windows-verified draft PR #637 head `98138ad759803f711c0eeaa3931f0da3efb6fd84`. Existing corrected wing and root-support GLB source, optional review actor, hidden Orbiter guard, separate waterline observer default-off, First Wake benchmark and source tests remain intact. This is an isolated branch, not a production merge.
- The native verification script `unreal/Tools/Verify-Unreal.ps1` now **requires** `unreal/Tools/Check-UnrealHost.ps1 -RequireReady` to pass *before* any Build.bat invocation, both in `-SkipTests` and normal native automation modes. A directory named UE_5.8 alone is insufficient.

## Exact host evidence

Tested RDC device `neontic`, Windows 11, isolated checkout `C:\TSTSS_Unreal_Windows_QA_PR642`. At source SHA **`c0889c40fb187a9e17ab17160ae8403aa41a19de`**:

- **94/94** Windows Python tests passed with Python 3.14.5; tests include integrations of First Wake story/ship safety, art intake, collision gates and native-host prerequisite source contracts.
- **7/7** native Windows PowerShell `Check-UnrealHost.Tests.ps1` cases passed. Verified rejection of fake 5.7, 5.8.3, 6.0, corrupt `Build.version` and missing build tools. Valid 5.8.4 and future 5.8.x version metadata were recognized as **version-compatible only**; faked binaries never earned a build-ready PASS. The intentionally rejected strict test returns exit 2, while the completed test suite exits 0.
- Invoking the actual `Verify-Unreal.ps1` failed **before starting UnrealBuildTool** because the host check returned exit 2. This negative-control behavior was directly verified on the Windows host.
- Isolated Git checkout remained clean after testing. [GitHub integrated source workflow at the same commit](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41195232713) succeeded with the independent real C++17 compiled geometry and RequestForm probes, 94 source tests, review asset reproduction, and wing clearance screens. Linux C++ source tests **are not Windows/MSVC/Unreal builds**.

As observed during installation, `C:\Program Files\Epic Games\UE_5.8` existed but `Engine/Build/Build.version`, `Build.bat`, `UnrealEditor.exe` and `UnrealEditor-Cmd.exe` were not yet present. `vswhere` reported no Visual Studio installation with MSVC x64 C++ workload, and Windows SDK headers were also absent.

## Minimal technical prerequisites

Per [Epic's UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes):
- Unreal **5.8.4** engine binaries with matching `Engine/Build/Build.version` MajorVersion 5, MinorVersion 8, PatchVersion at least 4.
- Visual Studio **2026** recommended; alternatively **Visual Studio 2022 v17.14+**, including **Desktop development with C++**, MSVC x64, and Windows SDK. Microsoft Visual Studio Build Tools are an alternative to the full IDE. Minimum MSVC 14.38; 14.50 preferred.
- Windows SDK **10.0.22621.0 minimum**, **10.0.26100.0 recommended**.

Do not run a second installer against a currently active Epic engine installation. An Unreal license/account acceptance and VS prerequisite install may involve OS-level prompts; no system installation is performed by this PR.

## Reproducible native verification when installed

From a **fresh clean isolated checkout** of the reviewed PR SHA, run from PowerShell:

```powershell
& .\unreal\Tools\Check-UnrealHost.ps1 -EngineRoot 'C:\Program Files\Epic Games\UE_5.8' -RequireReady
& .\unreal\Tools\Verify-Unreal.ps1 -EngineRoot 'C:\Program Files\Epic Games\UE_5.8'
```

The first check verifies UE `Build.version`, editor/build binaries, MSVC x64 toolset and Windows SDK. The second attempts a real UnrealEditor Win64 Development build and the project's declared **14 named Unreal automation tests**. These tests must produce valid native test reports. Unexpected failures should be preserved as evidence and repaired in a separate draft PR, not skipped or masked.

After engine/compiler success, import corrected wing and root-support GLBs into separate empty review folders, run the guarded ship art-binder **only in the isolated FirstWake benchmark map**, and collect real screenshot/video + shader/material/frame-time/physical sea-contact evidence before discussing visual acceptance. The user-approved Five Lights, current cast references, ship four-form canon, and protected First Wake content remain unchanged.

**The project target is cinematic UE 5.8.4 Chapter I, not a claim that native engine build or creator art acceptance already occurred.**

## 2026-10-31 continuation: newest First Wake foundation merged, free C++ tooling prepared

- The latest inspected foundation head `e62ce435b36189f055b2edfba4aeead9260c48c5` carried three additional commits involving `DefaultInput.ini`, `TSTSSExplorerCharacter.cpp` and `TSTSSExplorerCharacter.h`. Review branch PR #642 received a **real two-parent Git merge commit** `55c4bff044a8712ed547f1c7bfb031587d91e29e`. No overlapping file changes were detected; all 61 earlier review-branch changes were preserved and three newer upstream files were retained.
- On Windows RDC `neontic`, isolated checkout `C:\TSTSS_Unreal_Windows_QA_PR642`, commit `95add61218cb62ed3c44324609178d35b9bdea76`: **97/97** Python source tests passed under Python 3.14.5. The opt-in toolchain preparation script `unreal/Tools/Prepare-UnrealBuildTools.ps1` was **run in its no-install, plan-only mode** and exited 0. No Visual Studio or Unreal installation was started/modified by this script; working tree remained clean. The real `Check-UnrealHost.ps1` still reported `ready_for_native_build_attempt=false`.
- [`TSTSS-UE58.vsconfig`](../Tools/TSTSS-UE58.vsconfig) records three exact **free Microsoft Visual Studio Build Tools** components: `Microsoft.VisualStudio.Workload.VCTools`, `Microsoft.VisualStudio.Component.VC.Tools.x86.x64`, `Microsoft.VisualStudio.Component.Windows11SDK.26100`. [`Prepare-UnrealBuildTools.ps1`](../Tools/Prepare-UnrealBuildTools.ps1) supports read-only planning by default and requires explicit `-Install -AcceptPackageAgreements` for an actual `winget` setup. The latter has **not** been run. The Windows setup command does not install the Unreal engine.
- Microsoft lists these components in its [Visual Studio 2026 Build Tools workloads](https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools?view=vs-2022) and recommends using a `.vsconfig` file with `winget install`. This configuration is a plan for setup, not proof of a successfully installed toolchain.
- The [Unreal README](../README.md) was corrected to reflect active C++ ship/First Wake assets rather than its historical scaffold-only introduction, without claiming native Unreal compilation or already approved cinematic visuals. Keep Godot playable authority until UE native visual/play verification is established.

**Current remaining hard blocker:** UE 5.8.4 editor/build binaries, Visual Studio MSVC x64 compiler, and Windows SDK are still missing at the last RDC inspection. Execute no native Unreal target until `Check-UnrealHost.ps1 -RequireReady` passes on a clean reviewed commit. No main merge or installer release authorized.
