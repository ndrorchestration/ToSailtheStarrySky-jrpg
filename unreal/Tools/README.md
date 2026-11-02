# Native Windows verification

> **As-of 2026-11-01:** A prior pinned UE5.8.4 native foundation build and **12/12 automation tests passed** ([receipt](../Docs/UE58_NATIVE_BUILD_VERIFICATION_2026-11-01.md)), but that evidence does **not** validate newer ship drafts. The current [rotating bridge and quarters draft #702](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/702) requires **15 native tests** in the exact-head report; engine-free registration and proxy-geometry tests are not native execution. Do not launch a competing UBT build while another Unreal Editor/Live Coding session is active.

## Dependency and source-only checks (no installation)

Run from repository root, using Python 3:

```powershell
py -3.14 -B unreal/Tools/check_unreal_dependency_contract.py
py -3.14 -B unreal/Tools/test_unreal_dependency_contract.py
py -3.14 -B unreal/Tools/check_automation_registry.py
py -3.14 -B unreal/Tools/test_aureate_bridge_habitation_source_contract.py
py -3.14 -B unreal/Tools/test_aureate_bridge_habitation_envelope.py
```

The first two are **standard-library only** and enforce the documented engine/C++ module baseline, optional pinned NumPy dependency, and native-report registration count. They do not call pip, download software, compile the game or certify graphics. Full generated-mesh studies require the **optional** [`requirements-geometry.txt`](requirements-geometry.txt) (NumPy 2.5.1 observed with Python 3.14.5 on `neontic`); the dependency file is a declaration, **not an installation or upgrade**. See [dependency update policy](../Docs/UNREAL_DEPENDENCY_BASELINE_2026-11-01.md).


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
