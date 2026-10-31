# Windows RDC verification — Unreal Engine 5.8 native readiness (2026-10-31)

**Result:** Remote Desktop Commander machine **neontic was ONLINE and inspected**. The Windows-side source and asset checks succeeded, but **the machine is not ready to compile or render UE5.8**. No game, UE map, installer, or main-branch modification occurred.

## Evidence bound to source commits

- Isolated Git checkout: `C:\TSTSS_Unreal_Windows_QA_PR637`, developer branch `fix/unreal-first-wake-waterline-observer-gate-v1`. No existing working tree was modified. Initial exact checkout `c7b42f59a4c7b1209f96d17ba0d3a5fe813c50cd`.
- Windows 11, PowerShell 5.1, Python **3.14.5**, Git 2.56, desktop online.
- After the portable QA fixes, the checkout at **`63561978635d25d11952a37888c4203c19ad8e7d`** ran **90/90** `python -m unittest discover -s unreal/Tests -p test_*.py -v` tests successfully and `python -W error::FutureWarning unreal/Tests/check_aureate_preview_source.py` succeeded without warnings. `check_aureate_request_logic.py --source-only` returned an explicit **SOURCE-ONLY** result; it was not misrepresented as a compiled test. Working tree remained clean (generated `__pycache__` now ignored).
- Actual Windows-generated corrected wing GLB `AureateWake_Wing_Lookdev.glb`: 1,653,804 bytes, SHA-256 `04d7f9461b4cb4475ea98d5e3f7699b68f272f5646362ad7aef0d222ad92ec73`, 280 cm authored span. Root support GLB `AureateWake_RootSupport_Lookdev.glb`: 22,012 bytes, SHA-256 `c350390bf0cc88abe3226511a06deab0427e35df876a979cd35f61ec355178f4`, 100 cm authored length. Both **review-only** models passed their actual Python SHA/material/unit preflights; not imported into UE. Output is isolated outside repo at `C:\TSTSS_Unreal_Windows_ArtReview_PR637`.
- Local machine-only evidence at `unreal/Saved/MigrationEvidence/Windows_QA_Receipt_20261031.json`, with the exact SHA, clean-tree proof and both actual model hashes. `Saved` is intentionally ignored; this is **not** a committed or centrally hosted native acceptance receipt.
- Linux GitHub Actions source checks remain separate and stronger for C++ execution: [integrated source check at earlier branch head `6356197`](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/actions/runs/41194060545) executed the actual shared waterline C++17 predicate's 16 numeric cases and the isolated `RequestForm` C++ logic. Do not conflate Linux C++ proof with a Windows/UE build.

## Exact native readiness blocker

The new **read-only** `unreal/Tools/Check-UnrealHost.ps1` was executed successfully on `neontic` after updating the checkout to **`dc44ef7029dcc78c175f87bde1f21dcce3f4a1be`**. It found:

| Gate | Actual observation |
| --- | --- |
| `ToSailTheStarrySky.uproject` | Present |
| UE 5.8 `Build.bat`, `UnrealEditor.exe`, `UnrealEditor-Cmd.exe` | **Absent** in default engine installation |
| Visual Studio C++ x64 toolset (`vswhere` component query) | **Not installed** |
| Windows 10/11 SDK C++ headers | **Not installed** |
| UE 5.3 directory | Contains `Engine\Plugins` only; no build/editor binaries. **Not** a valid replacement for 5.8 |
| `Check-UnrealHost.ps1 -RequireReady` | Expected **exit 2**, failure closed, clean checkout |

Script output authority: `NATIVE_HOST_PREREQUISITES_ONLY_NOT_A_BUILD_OR_RENDER`. Explicit `-EngineRoot` supports a nonstandard engine path without mutating the machine.

## What must happen before real playable Unreal evidence

1. Install the intended free Unreal Engine **5.8** through Epic Games Launcher (or point `-EngineRoot` to a complete existing installation). Do not substitute UE 5.3 for the project migration target.
2. Install the appropriate free Visual Studio C++ desktop/game toolchain with x64 compiler and Windows SDK. The presence of the Visual Studio *Installer* executable alone did **not** satisfy this.
3. Check the committed C++ project and source branch still match their intended foundations; the Unreal foundation PR continues to evolve separately. Use a clean isolated checkout and run:
   ```powershell
   powershell -NoProfile -File unreal/Tools/Check-UnrealHost.ps1 -RequireReady
   powershell -NoProfile -File unreal/Tools/Verify-Unreal.ps1 -EngineRoot "C:\Program Files\Epic Games\UE_5.8"
   ```
4. Only after native UE compile and automation tests pass: import the **corrected** wing/support GLBs to isolated review folders, run guarded First Wake review art binder, capture actual native frames, verify the single authoritative water-contact path, physics, shaders, artistic acceptance and performance. Keep cinematic/production approval distinct from technical checks.

No automatic engine installation was attempted: the required engine + C++ toolchain are large system-level installations, and this inspection did not establish an unattended installation route or available game-engine credentials. Protected main and Windows installer remain untouched.
