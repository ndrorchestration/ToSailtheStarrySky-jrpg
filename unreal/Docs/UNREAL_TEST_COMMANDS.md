# Unreal verification — exact-head procedure and historical receipts

**LATEST PINNED UE 5.8.4 NATIVE RESULT (2026-11-02):** Draft #713 commit `e3e3ff5f349c98b2051a18a5f0c3db6097af8040` **passed Win64 Editor compilation and 25/25 actual registered native automation tests**. The real JSON has 25 unique Success entries, 0 failed/NotRun; the isolated review worktree was clean after the run and `Verify-Unreal.ps1` exited 0. Report SHA-256 `243ad1eedaa344cd52dd4a3380e59cbef34fcfcd3e39c61cc1307195921733a5`. In this **disposable** checkout only, read-only attributes prevented Unreal from rewriting tracked `DefaultEngine.ini` and `DefaultInput.ini`. An earlier unprotected run's dirty-config/token evidence is still preserved, not erased. **This native receipt is only for the exact tested SHA; later documentation revisions require their own verification.** The **13 interactive PIE scenarios, genuine seawater/flotation, Splashdown, art approval, packaged installer and release are NOT TESTED/NOT AUTHORIZED**. See [exact-head gate](INTEGRATION_GATE_2026-11-02.md). No save schema, engine dependency, main-branch, art or Starbourne promotion occurred.


**Updated 2026-11-02.** Prior draft #685 had an actual UE5.8.4 Win64 Game
and Editor build and 23/23 native automations **at its own source SHA**.
Draft #704 had a Game build but a raw, uncooked startup failure; later
native test coverage was not run at that exact head. Current draft
[#712](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/712)
registers **25** required native tests. GitHub source workflows and
portable C++ API-double cases passed on inspected commit
`a1b07b64841c2cb6b735fdd66f2ecd6426cab016`; **no native build, 25-test
Editor report or PIE walkthrough exists for that head**.

Run the following on a voluntarily idle Windows UE5.8.4 workstation,
using a disposable exact-head review checkout. Do not modify normal player
save files or terminate parallel Editors to obtain a pass.

1. Generate IDE project files from `unreal/ToSailTheStarrySky.uproject`.
2. Build `ToSailTheStarrySkyEditor Win64 Development` with UnrealBuildTool.
3. Run Editor automation tests using:
   `UnrealEditor-Cmd.exe <absolute-path-to-uproject> -unattended -nop4 -nullrhi -ExecCmds="Automation RunTests TSTSS; Quit" -log`
4. Archive compiler log, automation report and exact commit SHA. A process exit alone is insufficient; inspect per-test results and failures.
5. Run a renderer-enabled scene capture separately. NullRHI proves no visuals.
6. Package a Windows development build only after native runtime/asset imports are verified.

Current review scope includes a tracked V2 Prelude `.umap` with seven
milestone actors and native C++ explorer/milestone/SaveGame logic.
**This does not establish PIE movement, E/J/F5/F9 operation, approved cinematic
characters, true ship-water physics or a cooked/packaged installer.**
Do not infer native PASS from source registration or compiler API doubles.

Testability follow-up: implement round-trip save/load, mirrored Godot combat fixtures and screenshot comparisons, then enforce Windows CI build gates.

## New round-trip regression
The `TSTSS.Save.RoundTripFirstWakeAndParty` editor automation test writes to a dedicated test slot, loads it, checks version, First Wake beat, and Ender's party fields, then deletes the test slot. If that slot already exists, the test fails closed and avoids overwriting it. Run in an isolated test profile/workspace: interrupted test execution could leave the dedicated slot behind. A passing test will not establish crash-atomic writes, corrupt-save repair, or Godot-save compatibility.

## Blocking review gates
- Run UnrealHeaderTool and Win64 editor compilation before any claim that the C++ classes build.
- Verify automation reports rather than only the command exit code; tests added here are not executed by committing them.
- Confirm test cleanup, PIE interaction/camera, true physical First Wake events, and Blueprint milestone hook behavior.
- Capture native UE renderer stills/video and obtain artistic approval of imported cast; prior approved reference artwork is not a rigged character asset.
- Keep migration PR draft and Godot playable until a working Windows packaged build is tested.

## Automation fixture crash-safety gate — 2026-10-30

`TSTSS.Combat.AbilityAuthorization` now aborts its test early if combat initialization or the expected successful action fails, and validates roster size before indexing result entries. This avoids a secondary invalid-array-access failure obscuring the original failed assertion. **The updated test has not been executed in Unreal Engine 5.8.** Collect an exact-SHA Win64 compile log and Editor automation report before interpreting this as a passing test or promoting the draft.

## Combat automation failure-path hardening — 2026-10-30

The transactional-combat and turn-order regression fixtures now stop after failed expected-success assertions, and check result roster sizes before indexing. This prevents a secondary invalid array access from obscuring the first failure. Source committed on the migration draft; **no Unreal compiler or automation run was performed here**. The connected Windows development machine was offline at inspection. Require native Win64 compilation, test-by-test automation results, and an independent renderer-enabled review before any playable promotion.

## Stronger native evidence gate — 2026-10-31

`Tools/Verify-Unreal.ps1` now checks individual automation report entries for nine required named `TSTSS.*` tests in addition to aggregate counters. Every required `fullTestPath` must appear exactly once with `state=Success`; omitted, duplicated, malformed or failing tests block a PASS. This prevents unrelated passing tests from satisfying a stale `succeeded >= 6` threshold. The report schema and names must be validated on an actual UE 5.8 Win64 Editor run; the new script logic is authored but **not executed** on an Unreal workstation. A renderer-enabled artistic review and packaged-game smoke test remain independent gates.

## Verification checkout stability — 2026-10-31

The native verification helper now checks Git HEAD and working-tree cleanliness **again after** its build and test sequence, refusing to report PASS if the branch changed while tests ran. This closes a stale-evidence risk when multiple agents commit concurrently to the Unreal migration branch. Run from a clean, pinned checkout rather than a changing shared working tree. Archive its exact revision, per-test reports and logs together; never promote a successful Godot smoke test to an Unreal build receipt.

**Still pending:** native Unreal Engine 5.8 execution to verify this PowerShell script itself, compiler results, automation JSON schema, and test outcomes. The ship preview branch #610 is stacked on #608 and needs a fresh compatibility review when #608 advances; the SpriteCook #609 references remain subject to original-file rights/provenance review.

## Automation threshold maintenance — 2026-10-31

The verifier no longer uses the obsolete fixed `succeeded >= 6` threshold. It now requires successful aggregate count to be at least the actual number of entries in its named required-test list (currently ten), *and* still demands each named test exactly once with a successful per-test state. Expanding the required set no longer leaves a contradictory hard-coded count. This is source-only, not a successful UE 5.8 test receipt. Validate the report JSON field names on the first native run and retain exact-head artifacts.

## Confirmed engine-free CI result — 2026-10-31

GitHub reported the **Unreal source preflight** workflow as completed/success on exact commit `4c43979883b713697ed0d3f4c09bb3cb0d34a704`, along with successful Unreal source inventory and Aetherwake smoke workflows. This is an actual GitHub Actions receipt for source-level validation, **not** Unreal Engine 5.8 compilation, runtime tests, graphics capture, or a playable installer. Verification must be repeated against the integration commit being promoted. The connected Windows device remained offline at review.

## Current exact-head gate — November 2, 2026

The recommended invocable verification script is
`unreal/Tools/Verify-Unreal.ps1 -EngineRoot "<verified UE 5.8.4 install root>"`,
run from a clean isolated checkout. It checks exact `git HEAD`,
tracked-tree cleanliness before/after, Win64 Editor build, full Unreal
JSON automation output and exactly one success entry for each of the
**25 mandatory named tests**. Do not use `-SkipTests` to claim 25/25;
that mode proves a build only.

After passing that gate, load the independent V2 Prelude map in the
Unreal Editor and execute [P01–P13](FIRST_WAKE_V2_PIE_ACCEPTANCE_MATRIX_2026-11-02.md)
with actual keyboard input and evidence. Test a fresh quicksave slot in a
disposable test profile: the PIE slot is `tstss_prelude_pie_quick`,
distinct from the non-PIE `first_wake_quick` slot. An existing PIE
test slot should cause F5 to refuse a first overwrite in a new session.
Never delete unowned saves. J reads objectives; E has a separate 300 cm
pawn-centered check; F9 cannot adopt a prior session's test slot.

**Distinct evidence labels:** `SOURCE_PREFLIGHT=PASS` means CI/source
tests, `PORTABLE_CPP=PASS` means true C++ methods under API doubles,
`EDITOR_BUILD=PASS` means actual Win64 UBT at exact HEAD,
`NATIVE_25=PASS` requires exact JSON, and `PIE=PASS` requires a
reproducible player run. No field inherits a PASS from another source SHA.
The direct uncooked Game executable's earlier asset-registry/BufferReader
crash is not packaged-runtime proof. See
[dependency/source register](FIRST_WAKE_DEPENDENCY_HANDOFF_2026-11-02.md).

## Integrated draft — safe repeatable evidence retention (2026-11-02)

On a *disposable, source-clean Windows checkout* of the review candidate,
from repo root:

```powershell
$Head = (git rev-parse HEAD).Trim()
.\unreal\Tools\Verify-Unreal.ps1 -EngineRoot "C:\Program Files\Epic Games\UE_5.8" -ExpectedHead $Head
```

Use the **actual installed EngineRoot** rather than assuming the example
directory is correct. The script validates a full 40-character expected
SHA before running, and creates a new private ignored
`unreal/Saved/MigrationEvidence/<sha>-<utc>-<nonce>/` per invocation.
`build.log`, `automation.log`, `head.txt` and native JSON are
retained together. Older failed and successful receipts are never erased.
An invalid SHA, dirty checkout, missing tool, collision or incomplete
automation evidence is a **HOLD**. The `-SkipTests` option cannot be
reported as 25/25 automation acceptance.

The source/CI checks for this exact-head and evidence-retention behavior
are not a substitute for a native Windows PowerShell/UE5.8.4 run.

**Version admission:** The script requires the selected `-EngineRoot` to
contain a readable `Engine/Build/Build.version` whose major/minor/patch is
`5.8.4`. It refuses wrong or malformed metadata **before** any native
process is run. CI now parses the same PowerShell file and executes
only the wrong-engine and wrong-SHA fail-closed paths with temporary
fake host files; this is not native UE runtime verification.

## Native report consistency and synthetic test boundaries

The native verifier uses `unreal/Tools/Assert-NativeAutomationReport.ps1`
to reject invalid or contradictory engine automation JSON rather than
trusting a `succeeded` aggregate. The engine must report all 25 distinct
required test names and exactly matching successful per-test entries.
The companion hosted `Test-NativeAutomationReportFixtures.ps1`
tests this validation with fake JSON reports, including missing, duplicate,
failed, skipped and inconsistent test records. Those hosted fixtures do
**not** constitute a UE Editor build or 25/25 test receipt.

## November 2 native Editor outcome — build PASS, test acceptance HOLD

At exact detached PR #713 snapshot `fd0b68c28e6289d45f8b8c70228631c24577a352`,
the installed Win64 Unreal Engine 5.8.4 **successfully built**
`ToSailTheStarrySkyEditor` with MSVC 14.44 / Windows SDK 10.0.26100.
Running native automation produced a JSON report containing 25
distinct successful test entries (zero failures and no skipped tests).
However, the verification script **correctly refused final PASS** when
`git status` found tracked changes to `unreal/Config/DefaultEngine.ini`
and `unreal/Config/DefaultInput.ini` generated by the Editor.
A locally generated Android File Server security token is present
among those uncommitted changes; treat it as private host state.
Do not add, copy or publish it.

Evidence resides in the isolated worktree's ignored
`unreal/Saved/MigrationEvidence/` per-run folders. This establishes
**native build PASS at the pinned old commit** and 25 successful
individual native entries, but **not** a clean-source, accepted
end-to-end automation run or PIE proof. A later documentation commit
requires its own exact-head evidence. On a fresh *separate* worktree,
test source-protected INIs or another proven non-writing Unreal invocation,
and re-run full checks. No auto-reset or deletion of existing modified
project files is authorized.

## Safe native map admission after Editor sessions are idle

Read [native V2 Prelude map QA instructions](FIRST_WAKE_NATIVE_MAP_ADMISSION_2026-11-02.md) before executing `unreal/Tools/verify_pr713_native_prelude_map.py`. The source-only and Windows negative controls passed, but the first native map-check build attempt was **blocked by Live Coding**. The updated `Verify-Unreal.ps1` now refuses to compete with active Unreal/Live Coding processes **before** creating new evidence or starting UBT. Do **not** close someone else's Editor, disable Live Coding to force a pass, or infer P01–P13 from Python map inspection. Preserve the prior 25/25 exact-head receipt separately.


## New source-locked Prelude Editor map launcher (2026-11-02)

For the next independent native map/actor step, follow
[the full map QA admission guide](FIRST_WAKE_NATIVE_MAP_ADMISSION_2026-11-02.md).
`unreal/Tools/Invoke-NativePreludeMapQA.ps1` checks a named disposable
worktree, exact HEAD, UE 5.8.4, unchanged map/config SHA-256,
existing-save isolation, tracked read-only INIs, and **no active
Unreal Editor/Live Coding sessions** before any execution.
Run `-PreflightOnly` first (no side effects). A successful
`Verify-Unreal.ps1 -SkipTests` at the **same exact HEAD** now creates
`verified-build.json` only after a clean successful native build.
Only then is the opt-in Python Editor map QA runnable via the launcher.
The actual map/actor check is **NOT TESTED** at current integration
head while other Editors remain active. Neither build-only nor map
inspection can satisfy P01–P13 genuine PIE or ship-water physics.
