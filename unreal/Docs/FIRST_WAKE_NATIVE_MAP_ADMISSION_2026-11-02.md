# First Wake V2 native Editor map-admission review — November 2, 2026

**Status: REVIEW ONLY, not P01–P13 Play In Editor acceptance.**

## Why this gate exists

PR [#713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713)
already has exact-head UE5.8.4 Win64 Editor build and 25/25 native automation
verification at `52e13aedaa8bda900cece849b54eae570179c838`.
Those tests do **not** load the real V2 Prelude level as an editor map,
confirm every placed collision target, or exercise a player's WASD/mouse/E/J/F5/F9
input path.

The narrowly separate `unreal/Tools/verify_pr713_native_prelude_map.py`
inspects the **actual UE Editor loaded world** and **actual reflected C++
actor methods** without using a fabricated keyboard/PIE transcript.

## Source custody and execution

Use **only** a fresh isolated, detached Windows checkout named
`C:\TSTSS_PR713_NativeMapQA_20261102`, pinned to the exact PR head under
inspection. Do not run this script in the user's real project, personal
save directory, main branch, or another live Editor session.

This script requires the environment variable
`TSTSS_REVIEW_EXPECTED_HEAD` to contain the entire 40-character SHA
matching Git HEAD; it checks a clean tree and the SHA-256 of the tracked
V2 `.umap`, refuses potentially present normal/PIE SaveGame files, and
checks all tracked map/config hashes and Git HEAD again after inspection.
It writes one exclusive receipt under **ignored**
`unreal/Saved/NativePreludeMapQA/`. No existing receipt is overwritten.

On an already compiled Unreal 5.8.4 Editor environment, from PowerShell,
adjusting paths to the explicitly named disposable checkout:

```powershell
$Review = "C:\TSTSS_PR713_NativeMapQA_20261102"
$env:TSTSS_REVIEW_EXPECTED_HEAD = (git -C $Review rev-parse HEAD).Trim()
$Editor = "C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
$Project = Join-Path $Review "unreal\ToSailTheStarrySky.uproject"
$Script = Join-Path $Review "unreal\Tools\verify_pr713_native_prelude_map.py"
& $Editor $Project "-run=pythonscript" "-script=$Script" -unattended -nop4 -nullrhi -log
```

The script is an Editor Python **commandlet**, not a runnable in-game Python
controller. The project must already have `PythonScriptPlugin` available.
Use a dedicated private log and verify a real
`TSTSS_NATIVE_PRELUDE_MAP_QA_PASS` sentinel, JSON receipt and zero process
exit; if any is absent, **HOLD**. Do not weaken guards to accommodate a
different checkout or engine patch. Startup may change tracked INI files:
in the disposable review checkout only, protecting the two tracked
`DefaultEngine.ini` and `DefaultInput.ini` from writes is an approved
experiment. Retain failed logs and avoid publishing generated Android File
Server tokens. No dependency installation/upgrade is authorized.

## Bounded checks

The script verifies actual level load, seven distinct C++
`ATSTSSMilestoneActor` instances and their visible collision components,
actual review spawn/floor/no-collision ocean, GameMode's native explorer
pawn class, native read-only initial objective, rejected out-of-order Ionia
and engineering signoff, ordered flyer → Ionia → boarding, duplicate
inspection rejection, all three independent engineering bits, successful
signoff and no false Chapter 1 Act 1 transition. It records actor origin
coordinates and spawn-to-flyer distance **for later geometry QA**, not as
proof that a player can see or click a marker. The script has **no calls
to save map/content, create/delete disk SaveGame slots, inject gameplay
input, activate Play In Editor or enter the shipping runtime**.

A positive result establishes `NATIVE_EDITOR_MAP_AND_REAL_ACTORS_PASS_NOT_PIE`,
not the P01–P13 human input matrix. In particular it does not establish
camera line traces/occlusion, actual 300 cm reach, E/J feedback rendering,
F5/F9 story persistence in PIE, stale-session isolation, sea-contact
or flotation physics, Lyra onboarding, visual quality, art acceptance,
installer security, a release or permission to unlock Starbourne.

The existing strict [P01–P13 review matrix](FIRST_WAKE_V2_PIE_ACCEPTANCE_MATRIX_2026-11-02.md)
remains **NOT TESTED** until genuine in-Editor player interaction is
observed and recorded. A source-only GitHub preflight for
`test_pr713_native_prelude_map.py` verifies this script's admission
guards and negative controls; those tests do not load the Unreal level.

## Failure handling

If the commandlet cannot load the level, a Python reflection API is
missing, the state transition fails, or the source/map/config hashes
change, retain the original log and checkout for review. Do not promote
partial or synthetic results to native gameplay acceptance, reset
unexamined files, or change plugin/build dependencies to force a pass.

## 2026-11-02 native map admission status — safe execution blocked

- Source-only native map verifier `verify_pr713_native_prelude_map.py` and its
  **eight** source/admission tests passed on the actual Windows checkout
  (review HEAD `a06f203902fcb1594e1b55e43d1ec9f27d9ed583`).
- A subsequent native Win64 build attempt at that exact head was **BLOCKED
  BY ACTIVE LIVE CODING**, before a real Editor map could be loaded. Other
  Editor sessions were active, including a separate character-review task;
  none was terminated or modified.
- To avoid wasting system resources and interfering with parallel work,
  `Verify-Unreal.ps1` now fails closed **before build or evidence creation**
  when `UnrealEditor`, `UnrealEditor-Cmd`, or `LiveCodingConsole`
  is running. At pinned `cfb88a9edf582b57ca95db1f731b68d79da3a22c`,
  this check was actually invoked on Windows and correctly **refused**
  execution: no additional receipt directory, tracked files unchanged.
  Its **13 Windows source-safety tests** passed, and **four hosted
  GitHub workflows** were SUCCESS at the same head.
- The previously accepted **25/25 native Editor automation receipt at
  `52e13aedaa8bda900cece849b54eae570179c838` remains valid for
  that earlier exact source**, but cannot be transferred to the new
  map-checker revision.
- **Next evidence gate:** once the authorized workstation is idle, repeat
  the Win64 5.8.4 build in the dedicated, source-clean PR713 map QA
  checkout and then execute the Python Editor commandlet. Require
  actual `TSTSS_NATIVE_PRELUDE_MAP_QA_PASS`, a unique local JSON receipt,
  unchanged map/config SHA-256 and clean tracked tree. The script itself
  does **not** run or pass P01–P13 PIE keyboard/visual cases; those remain
  separately NOT TESTED. Never alter Live Coding or terminate someone
  else's Editor to unblock a review.


## 2026-11-02 continuation — safe, repeatable native commandlet launcher

**Preferred source-locked execution path** is the opt-in
`unreal/Tools/Invoke-NativePreludeMapQA.ps1` PowerShell launcher, rather
than manually guessing the project/Editor commandline. In a *pre-existing*,
isolated `C:\TSTSS_PR713_NativeMapQA_20261102` checkout pinned to its
full current SHA, use:

```powershell
$Review = "C:\TSTSS_PR713_NativeMapQA_20261102"
$Commit = (git -C $Review rev-parse HEAD).Trim()
$VersionedUE = "C:\Program Files\Epic Games\UE_5.8"
& "$Review\unreal\Tools\Invoke-NativePreludeMapQA.ps1" -EngineRoot $VersionedUE -ExpectedHead $Commit -PreflightOnly
& "$Review\unreal\Tools\Verify-Unreal.ps1" -EngineRoot $VersionedUE -ExpectedHead $Commit -SkipTests
& "$Review\unreal\Tools\Invoke-NativePreludeMapQA.ps1" -EngineRoot $VersionedUE -ExpectedHead $Commit
```

Only execute the second/third command **after** the first admits a
voluntarily idle workstation. Neither command may run while another
`UnrealEditor`, `UnrealEditor-Cmd`, or `LiveCodingConsole` process
is active. Do not terminate the user's character-preview or other
Editor work. The displayed `-PreflightOnly` mode creates no output
receipt, launches no Editor and does not certify gameplay.

The build-only script now emits an **exclusive**
`Saved/MigrationEvidence/<SHA>-<timestamp>-<nonce>/verified-build.json`
**only after** UBT succeeds and Git HEAD plus a clean worktree pass
post-build. The map launcher requires that exact-SHA
`WIN64_EDITOR_BUILD_PASS_CLEAN_SOURCE` receipt; an empty/stale
`build.log` is explicitly insufficient. The launcher rechecks
source/map/config hashes, an empty SaveGames test directory, read-only
tracked default INI files, engine patch **5.8.4** and idle Editor
processes. Its actual Editor commandlet must produce a **new** exclusive
JSON report plus the `TSTSS_NATIVE_PRELUDE_MAP_QA_PASS` sentinel,
with source SHA, seven actors and **PIE NOT TESTED**; false/duplicate
results fail closed. Each invocation preserves a separate ignored
private log under `Saved/NativePreludeMapQA/LauncherReceipts/`.

**Current evidence status:** This launcher has source/PowerShell
syntax and preflight negative controls only; no valid native map
inspection has yet completed. In the last authorized Windows check
other Unreal and Live Coding sessions were active. Native 25/25
belongs to earlier exact tested SHA
`52e13aedaa8bda900cece849b54eae570179c838`.
A future positive map-admission check still **does not** establish
P01–P13 genuine keyboard PIE, physical splashdown or approved art.
