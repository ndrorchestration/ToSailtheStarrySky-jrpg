# Native Windows verification

Run from PowerShell on a Windows machine with licensed Unreal Engine 5.8 installed:

```powershell
powershell -ExecutionPolicy Bypass -File unreal/Tools/Verify-Unreal.ps1 -EngineRoot "C:\Program Files\Epic Games\UE_5.8"
```

This script fails closed if the engine is absent, build fails, the automation process fails, or an expected JSON report is missing/incomplete. It records logs and Git HEAD under `unreal/Saved/MigrationEvidence` (do not commit logs). It is **not** a substitute for native graphics captures, a playable level, installer checks or full QA. `-SkipTests` is a diagnostic option and must not count as release verification. The editor's report schema may need adjustment based on an actual engine run; no run is claimed here.

## Fast source-only preflight (Python 3; no Unreal installation)

From repository root run `python unreal/Tools/check_automation_registry.py`. This verifies that every named test required by `Verify-Unreal.ps1` has a unique native C++ automation registration, catching name drift before an expensive UE build. It does **not** compile, execute tests, inspect game visuals, or replace exact-head Windows evidence. It can run in a low-cost developer environment before invoking the Windows gate.

The registry preflight checks **both directions**: a required test must have a C++ registration, and every registered `TSTSS.*` automation test must appear in the native verification list. This prevents newly added tests from silently being excluded. A source-level inspection on October 31, 2026 found twelve matching registered/required names before the stricter check was committed; the Python command and native Unreal suite have not been executed in this session.

## Preflight self-tests

Run `python unreal/Tools/test_automation_registry.py` (stdlib-only). Five temporary-directory fixtures assert the checker accepts matching names and rejects missing, unlisted, and duplicate native registrations or duplicate required names. The test creates and deletes temporary directories and does not touch Unreal project saves. These fixtures are authored but were **not executed** in the committing environment: the remote Windows device is offline and direct local retrieval of the branch was unavailable. A passing checker self-test would not establish C++ compilation or native UE automation success.

## Independent Python fixture execution — 2026-10-31

The five `test_automation_registry.py` scenarios were reconstructed from the then-current GitHub source in an isolated Python environment and executed: **5 tests, 0 failures**. This supports the preflight checker's fixture logic, but was **not** an exact repository-checkout run (GitHub raw retrieval was unavailable in that execution environment), was not a native Unreal build, and does not establish current-head compile or game-test status. Re-run `python unreal/Tools/test_automation_registry.py` and `python unreal/Tools/check_automation_registry.py` on the pinned branch checkout before consuming native evidence.
