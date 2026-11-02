# First Wake Unreal dependencies — exact-source reconciliation and handoff

**Current November 2 cross-discipline handoff (integrated [draft #713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713)):** This document's older #712 and #685 SHAs are historical, not the active test result. The authorized Windows `neontic` workstation is **online** and its installed `UE_5.8/Engine/Build/Build.version` reports **5.8.4**, with MSVC 14.44 and Windows SDK 10.0.26100. An isolated detached checkout at `fd0b68c28e6289d45f8b8c70228631c24577a352` **passed native Win64 Editor compilation**. A subsequent native Editor automation report contained **25 distinct Success entries / 0 failed / 0 not run**, but the strict post-run clean-tree gate **FAILED**, because Unreal rewrote tracked `DefaultEngine.ini` and `DefaultInput.ini` in that isolated worktree. The first file gained generated Android File Server settings including a local token. **Do not stage, publish or copy any generated token or config diff into documentation or a PR. Do not reset the worktree without reviewing its forensic state.** Native 25/25 acceptance is **HOLD — CONFIG_MUTATION**, despite successful test entries; P01–P13 interactive PIE remains **NOT TESTED**. The log/report evidence is local to the isolated worktree's non-overwriting `unreal/Saved/MigrationEvidence/` path; source SHA and outcome are separated from the now-moving review PR HEAD. **Never infer a newer documentation head has the same native receipt.** See [integrated review gate](INTEGRATION_GATE_2026-11-02.md), [save-safety notes](FIRST_WAKE_REVIEW_OBJECTIVES_2026-11-02.md) and [native test commands](UNREAL_TEST_COMMANDS.md).

**2026-11-02 · Draft PR #712 integration review only.**
This register documents **source declarations on the #712 stack**, not an
engine install audit, installed package inventory, vulnerability scan,
license approval, merge/release readiness, or proof that Windows can launch
a cooked Unreal game.

## Current declared dependency boundary

| Domain | Source-of-truth input | Observed declaration | Handling |
| --- | --- | --- | --- |
| Unreal version family | `unreal/ToSailTheStarrySky.uproject` | `EngineAssociation: "5.8"` | Preserve; 5.8.4 is historical Windows review patch, not a project-pinned installer |
| Native runtime module | `Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs` | `Core`, `CoreUObject`, `Engine`, `InputCore` | Engine-provided modules; no third-party runtime package added |
| Build targets | `Source/ToSailTheStarrySky.Target.cs`, `Source/ToSailTheStarrySkyEditor.Target.cs` | `BuildSettingsVersion.V7`, `EngineIncludeOrderVersion.Unreal5_8` | Do not change without native Game and Editor compilation |
| Editor authoring plugin | `ToSailTheStarrySky.uproject` | `PythonScriptPlugin` enabled | Editor map staging/testing; *packaged/runtime need not established* |
| Review test implementation | `unreal/Tools` | Python **stdlib**, portable C++17 tests with compiler API doubles; engine Python via plugin | Do not conflate hosted checks with real UE5.8 native automation |
| Legacy desktop/browser toolchain | root `package.json` and lockfile v3 | `nw ^0.116.0`, `nwjs ^1.4.4`, `nw-builder ^4.5.0`, `playwright ^1.63.0` | Historical JS/NW.js workflow **not Unreal runtime**; do not automatically npm install/update |
| Host build requirements | UE host installation + MSVC, Windows SDK, PowerShell and Python | Exact installed paths/patches **not freshly observed** | Workstation offline; do not infer host state from source declarations |

Machine-readable source contract:
`unreal/Tools/first_wake_dependency_contract.json`.
Checker:
`python3 unreal/Tools/check_first_wake_dependency_contract.py`.
It compares the full explicit project-plugin array (including disabled
entries), public/private/dynamically loaded and include-path C++ module
declarations, both targets' extra-module lists, runtime module loading phase
and npm lockfile root record. Newly introduced **nonliteral** module
declarations fail closed rather than silently disappearing from the audit.
Negative-control tests modify **in-memory** representations, never the real
project or lockfile. A success means **source agreement only** and cannot
enumerate engine-transitive dependencies or prove plugin packaging.

## Other review ownership and conflicts

[Dependency and evidence reconciliation draft #711](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/711)
already owns the cross-branch dependency register
`unreal/Docs/DEPENDENCY_AND_EVIDENCE_REGISTER_2026-11-01.md` and a
branch-specific baseline/checker. Do **not** blindly replace its checker with
this #712-specific declaration contract or cherry-pick its other ancestors.
On the inspected #712 manifest the Python editor plugin is explicitly enabled,
matching the #708/711 branch variant, **not** the plugin-free #707/#709
variants. Choose a single canonical register after an explicit lineage
review; avoid two simultaneous authoritative dependency policies.

Root engine-authority drafts #657/#707/#709 must be reconciled separately.
The historical root Godot-forward text **is stale** for current creator-directed
Unreal-first work, but editing it on this #712 gameplay branch would race
those already-open root documentation proposals. The active Unreal guide
records the creator's current choice without deleting the dated Godot QA.

## Admitted changes and non-admitted updates

**Done in this review:** align Unreal README, native test instructions,
production matrix and playable-level instructions with current exact-head
evidence; add a declaration snapshot and drift/negative controls.
**No dependency version was upgraded**, no plugin was enabled or disabled,
and no lockfile, `.uproject`, `Build.cs` or toolchain file was modified.

**Not admitted without new evidence:** Engine 5.8 family/patch migration;
PythonScriptPlugin scope change; new NuGet/pip/npm modules; blind upgrades to
historical NW.js; platform C++ standard change; Starbourne form unlock;
production 3D character/ship import or packaging. For each change record
target/impact, source and licenses, exact versions and hashes, relevant
CVE/advisory (where claimed), Game+Editor UBT logs, **all 25 named native
automations**, P01–P13 PIE proof, render/package acceptance if relevant,
and an explicit scoped creator approval.

## Gate status at inspection

- Parent of #712: [#704](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/704) exact
  `d0dc6b44c4c0b90c1caa543de5026daff0012d79`.
- Last fully green #712 head **before this documentation update**:
  `a1b07b64841c2cb6b735fdd66f2ecd6426cab016`:
  3/3 hosted workflows and source-extracted 16 objective + 12 quicksave
  C++ cases passed; negative controls detected deliberate mutations.
- **This documentation update has a new HEAD**; never reuse those
  CI results as checks for the new revision without rerunning.
- UE Editor compile and 25/25 per-test native report for #712: **NOT TESTED**.
- Actual keyboard E/J/F5/F9 and P01–P13 on native V2 map: **NOT TESTED**.
- Packaged executable, visual art, physical sea landing and
  Chapter 1 Act 1: **NOT AUTHORIZED**.
- Authorized remote Windows workstation: offline at latest check.

This document and its source checker are an upgrade-readiness ledger,
**not a justification for silently upgrading dependencies**.

## November 2 continuation — closed declaration blind spots

The earlier contract compared only the enabled plugin names and the
first public `Build.cs` dependency range. It could therefore miss new
disabled project-plugin entries, an extra literal `Add` call, or added
private/dynamic C++ modules. The bounded checker now inspects these
declaration surfaces and both target `ExtraModuleNames` lists. Added
negative tests must fail on each such drift and on a nonliteral module
declaration. No dependency manifest or installed package has changed.

**Independent authority finding:** [draft #657](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/657)
already corrects root `AGENTS.md` to Unreal-first, but its root
`README.md` still describes Godot as the forward target at its
inspected head `a79a63a29babf3b1a1dc3522245d8b26f8eb3167`.
That mismatch should be fixed **on #657's own authority branch**,
not by rewriting root files in the First Wake gameplay draft.
