# First Wake Unreal dependencies — exact-source reconciliation and handoff

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
It compares exactly these declarations plus the npm lockfile root record, and
refuses drift. Negative-control tests modify **in-memory** representations,
never the real project or lockfile. A success means **source agreement only**.

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
