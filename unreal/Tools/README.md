# Native Windows verification
**All-four-mode scene staging:** native full Editor scene stage has passed in a disposable UE5.8.4 project, with four hash-pinned review maps; see [four-map receipt](../Docs/AUREATE_V4_ALL_FOUR_NATIVE_REVIEW_MAPS_2026_11_03.md). Use the guarded new three-form runner only for a **fresh sandbox** — its original V4 maps are already occupied and cannot be overwritten. This is real scene-actor evidence with NullRHI, not D3D11 rendering, physics, playable Starbourne, or artist signoff. Run source QA before a new native execution; do not reuse the old headless failed actor-spawn method.

**New full Editor Skybourne milestone:** [Native Skybourne exact evidence](../Docs/AUREATE_V4_NATIVE_SKYBOURNE_SCENE_EVIDENCE_2026_11_03.md) confirms 1-actor pilot and an 18-actor saved Skybourne review map. Use the guarded full Editor actor/staging runners for map creation, not the headless PythonScript commandlet. For D3D11 capture only, pass a UNIQUE attempt label and require >=6.5 GiB available RAM; never infer PNG success from an engine exit 0 alone. GPU image evidence is still held. These new scripts run solely in dedicated disposable sandbox projects and are not packaged-game requirements.


**November 3 Aureate V4 review note:** Use [the V4 dependency/acceleration register](../Docs/AUREATE_V4_DEPENDENCIES_AND_ACCELERATION_2026_11_03.md) and [native receipt](../Docs/AUREATE_CINEMATIC_V4_NATIVE_IMPORT_EVIDENCE_2026_11_03.md), distinct from the old verification commands below. Pure stdlib asset and scene-plan tests run without Unreal. Native mesh imports are proven using a disposable UE 5.8.4 project; rendering and real actor assembly are not. The full-Editor pilot source uses the documented ExecutePythonScript startup method and refuses to run under its 4.2 GiB available RAM or 14 GiB free disk preflight thresholds. Do not downgrade to a headless commandlet and claim a successful scene spawn or modify a user Editor process to force results.


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
