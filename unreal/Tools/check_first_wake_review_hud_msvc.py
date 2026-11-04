#!/usr/bin/env python3
"""Compile the ACTUAL Prelude DrawHUD body with installed Windows MSVC.

Complementary to check_first_wake_review_hud_compiled.py (hosted GCC/Clang).
Do not invoke Unreal Editor, Live Coding, UBT, player SaveGame, any real assets,
or mutate files in a tracked checkout. This checks C++ syntax/behavior against
the very same review API doubles, not actual UE rendering or P01-P13 PIE.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile

import check_first_wake_review_hud_compiled as hud


def find_vcvars64() -> Path:
    roots: list[Path] = []
    if os.getenv("VSINSTALLDIR"):
        roots.append(Path(os.environ["VSINSTALLDIR"]))
    for programs in (os.getenv("ProgramFiles(x86)"), os.getenv("ProgramFiles")):
        if programs:
            for year in ("2022", "2026"):
                for edition in ("BuildTools", "Community", "Professional", "Enterprise"):
                    roots.append(Path(programs) / "Microsoft Visual Studio" / year / edition)
    for root in roots:
        vcvars = root / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"
        if vcvars.is_file():
            return vcvars
    raise RuntimeError("HOLD: authorized machine has no installed vcvars64.bat; no software install")


def run_msvc_case(vcvars: Path, method: str, shipping: int) -> str:
    if shipping not in (0, 1):
        raise ValueError("Only defined shipping or nonshipping test targets are allowed")
    with tempfile.TemporaryDirectory(prefix="tstss-hud-msvc-") as tmp:
        folder = Path(tmp)
        source = folder / "hud_standin.cpp"
        target = folder / "hud_standin.exe"
        source.write_text(hud.API + "\n" + method + "\n" + hud.TEST,
                          encoding="utf-8")
        # Input paths are obtained exclusively from the current temp directory
        # and a locally installed VC environment; no user command injection.
        # cmd /c can misparse a single quoted vcvars64.bat path when
        # subprocess quotes the whole /c argument. A temp batch file
        # eliminates that ambiguity; no machine files/settings are changed.
        batch = folder / "compile_hud_standin.cmd"
        batch.write_text(
            '@echo off\n'
            + f'call "{vcvars}" >nul\n'
            + 'if errorlevel 1 exit /b 1\n'
            + 'cl /nologo /std:c++17 /EHsc /GR /W4 '
            + f'/DUE_BUILD_SHIPPING={shipping} '
            + f'/Fe:"{target}" "{source}"\n'
            + 'exit /b %errorlevel%\n',
            encoding="utf-8",
        )
        build = subprocess.run(
            ["cmd.exe", "/d", "/c", batch.name], cwd=folder,
            capture_output=True, text=True, timeout=90,
            check=False,
        )
        if build.returncode != 0 or not target.is_file():
            raise RuntimeError(
                f"HOLD: MSVC could not compile real review HUD (shipping={shipping}); "
                + (build.stderr + "\n" + build.stdout)[-3200:]
            )
        result = subprocess.run(
            [str(target)], cwd=folder,
            capture_output=True, text=True, timeout=12, check=False,
        )
        if result.returncode != 0 or "portable C++ real DrawHUD behavior checks" not in result.stdout:
            raise RuntimeError(
                f"HOLD: MSVC review HUD behavior failed (shipping={shipping}); "
                + (result.stderr + "\n" + result.stdout)[-3200:]
            )
        return result.stdout.strip()


def main() -> None:
    if os.name != "nt":
        raise RuntimeError("HOLD: Windows/MSVC-only review gate; use hosted GCC harness elsewhere")
    vcvars = find_vcvars64()
    method = hud.extract(hud.SRC.read_text(encoding="utf-8"))
    print("INSTALLED_MSVC_VCVARS=" + str(vcvars))
    for shipping in (0, 1):
        print("MSVC_SHIPPING=" + str(shipping) + ": " +
              run_msvc_case(vcvars, method, shipping))
    print("MSVC_REAL_DrawHUD_BODY_TEST_PASS_NOT_UE_EDITOR_OR_PIE")


if __name__ == "__main__":
    main()
