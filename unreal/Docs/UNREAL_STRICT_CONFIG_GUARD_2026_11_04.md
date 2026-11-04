# Unreal 5.8.4 strict automation — guarded generated configuration

Status: isolated review-only verification improvement; no production runtime, asset or gameplay change. 2026-11-04.

## Why

Draft #742 at `dbd199609b91c11c633c8ce0a44ea7cd7d777528` successfully built in UE 5.8.4 and produced **25/25 Success** native automation JSON, but the initial canonical `Verify-Unreal.ps1` run returned **exit 1** because the Editor generated changes in two tracked settings files: `unreal/Config/DefaultEngine.ini` and `unreal/Config/DefaultInput.ini`. That earlier failed strict receipt remains historical evidence and must not be relabeled PASS.

A subsequent **manual** experiment at the exact same commit made **only those two settings files temporarily read-only**, ran the *unmodified* strict verifier, and achieved **exit 0** with all **25/25 tests Success** and unchanged source. Both original writable attributes were restored, and postflight Git status was clean. Neither experiment altered protected main or production art.

## Reproducible opt-in guard

`unreal/Tools/Verify-Unreal-ConfigGuard.ps1` wraps the existing unchanged `Verify-Unreal.ps1`. It:
1. Resolves exactly two tracked `.ini` paths and fails closed if either is already read-only or missing.
2. Records SHA-256 digests of both files before test.
3. Sets their read-only attributes while invoking the original strict verifier. The original checker still enforces clean Git status at both ends, pinned commit, native Editor build, complete native automation JSON, 25 required test names with individual Success states, and zero failed/not-run.
4. Uses `finally` to restore original **writable** attributes even when tests fail, and checks both content digests again. A missing/changed config or nonzero verifier exit is a wrapper failure.
5. Does not suppress log warnings, waive missing test results, reset config content, change `.gitignore`, disable plug-ins, modify build environment or authorize game features.

Run only from a clean isolated checkout with sufficient available RAM and no competing Unreal job:

```powershell
pwsh -NoProfile -File .\unreal\Tools\Verify-Unreal-ConfigGuard.ps1 -EngineRoot 'C:\Program Files\Epic Games\UE_5.8'
```

Keep native logs and `Saved/MigrationEvidence/AutomationReport/index.json` outside source commits. If a process is externally terminated before its `finally` executes, check attributes and restore them manually with `attrib -R` on the two known files; recheck Git status and SHA against trusted source before resuming. Do not blindly revert unrelated changes.

## Scope limitations

- Hash and clean-state checks protect only the two named config files and Git-tracked worktree. Unreal build artifacts, engine state, saved private logs and other OS behavior need separate controls.
- No runtime class selection, new class canon, equipment permissions, spells, SaveGame migration, character visuals, ship mechanics or Starbourne player unlock.
- The guard does not prove gameplay, balance, cinematic visual acceptance or a shipped vertical slice.
- Exact-commit results for the wrapper itself must be recorded only after its own native run; the previous manual success does not prove the new wrapper.
