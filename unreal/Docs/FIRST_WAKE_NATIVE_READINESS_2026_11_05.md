# PR #769 — read-only native acceptance readiness gate

**Engine:** Unreal Engine 5.8.4, Windows. **Authority:** `ndrorchestration/ToSailtheStarrySky-jrpg`, **OPEN DRAFT / UNMERGED**. This utility makes no changes to game/runtime code, SaveGames, source files, maps, configurations, Unreal processes, or Git history. It creates **no receipt**, and its green status cannot be cited as native acceptance.

## Usage (run on NEONTIC only)

In a PowerShell terminal, replace `<EXACT_40_CHARACTER_PR769_HEAD>` with the latest pinned 40-character GitHub PR #769 head. Do not use an older head or a working tree that contains untracked artifacts.

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$Root = 'C:\TSTSS_P0CombinedF6Objectives_20261104'
$Engine = 'C:\Program Files\Epic Games\UE_5.8'
$Head = '<EXACT_40_CHARACTER_PR769_HEAD>'
python "$Root\unreal\Tools\check_first_wake_native_readiness.py" --repo $Root --engine-root $Engine --expected-head $Head --phase build
# After exact-head native automations + independent map QA are admitted, run:
python "$Root\unreal\Tools\check_first_wake_native_readiness.py" --repo $Root --engine-root $Engine --expected-head $Head --phase pie
```

The script returns JSON on standard output, **exit code 2** on `status=HOLD`, exit 0 only on `READ_ONLY_PREFLIGHT_PASS_NOT_NATIVE_EVIDENCE`. Do not proceed if output status is HOLD. A pass means only **environment and source-custody prerequisites appeared safe**, not that any native UE build or 29-gameplay native automations succeeded.

## Exact checks

- The **exact named disposable worktree**, Git top-level identity, full source SHA and completely clean tracked/untracked Git status.
- SHA-256 of the tracked First Wake V2 map must equal `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`.
- UE5.8.4 installed engine version plus GUI/commandlet exe presence; **29 distinct required native automation names** in `Verify-Unreal.ps1`, not the older 26-test subset.
- No existing `*.sav` files in the **candidate** project `unreal/Saved/SaveGames`. Never delete, move, rename, overwrite or adopt another project's player saves to pass this check.
- No running UnrealEditor, UnrealEditor-Cmd or LiveCodingConsole.
- Build admission: at least **5 GiB free physical RAM** and **14 GiB disk**. Full-Editor PIE admission: at least **6.5 GiB free physical RAM** and **14 GiB disk**. A live Unreal process blocks both phases even if memory is otherwise sufficient. These resource checks are also implemented independently inside `Verify-Unreal.ps1` (before evidence directory/UBT), `Invoke-NativePreludeMapQA.ps1` (before native commandlet/preflight receipt), and `Start-FirstWakeReview.ps1` (before opening the GUI). Five new negative source tests reject RAM/disk downgrades in these native launch paths.
- PIE also requires exact-head native automation and native map **receipt candidates**. Existence alone is **not approval**: each must undergo the existing strict independent receipt/schema validators and the original `Start-FirstWakeReview.ps1` checks before Editor start.

## Verification and limitations

`test_first_wake_native_readiness.py` supplies **18 engine-free positive/negative fixtures**, including wrong SHA/map/engine, duplicate or missing native test names, existing saves, active Unreal processes, low memory/disk, wrong roots, missing PIE receipts, and unchanged user-file guarantees. CI runs the unit fixtures **without calling the live machine probe**. The probe performs only local file reads, Git read operations, Python disk-usage queries, and Windows process-name/free-RAM queries. No Unreal Editor, commandlet, build, SDK installer, renderer, Level, player input or actual SaveGame operation is launched by the probe.

Current observed host blocker before this change: UnrealEditor and LiveCodingConsole running, 5.72 GiB free RAM, 14.83 GiB C: space. This is **not** native test evidence. When normally saved and closed by the user, rerun the read-only readiness check and, only after PASS, the existing guarded `Verify-Unreal.ps1` native build/test lane followed by native map QA and controlled F5/Shift+F5/F6/F9 PIE input acceptance. Preserve all previous QA receipts, original art and Starbourne's locked gate.
