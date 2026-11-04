#!/usr/bin/env python3
"""Windows MSVC proof of actual E-focus hint C++ against bounded API doubles.

Never starts Unreal, UBT or Live Coding; does not touch installed tools,
player saves, production assets, or tracked source. Not native UE/PIE proof.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile

import check_first_wake_focus_hint_compiled as focus
from check_first_wake_review_hud_msvc import find_vcvars64


def run_case(vcvars: Path, method: str, shipping: int) -> str:
    if os.name != "nt" or shipping not in (0, 1):
        raise RuntimeError("HOLD: only the installed Windows MSVC compiler may run these cases")
    with tempfile.TemporaryDirectory(prefix="tstss-focus-msvc-") as temp:
        folder = Path(temp)
        cpp = folder / "focus_standin.cpp"
        exe = folder / "focus_standin.exe"
        cpp.write_text(focus.API + "\n" + method + "\n" + focus.TEST,
                       encoding="utf-8")
        batch = folder / "compile_focus_standin.cmd"
        batch.write_text(
            '@echo off\n'
            + f'call "{vcvars}" >nul\n'
            + 'if errorlevel 1 exit /b 1\n'
            + 'cl /nologo /std:c++17 /EHsc /GR /W4 '
            + f'/DUE_BUILD_SHIPPING={shipping} '
            + f'/Fe:"{exe}" "{cpp}"\n'
            + 'exit /b %errorlevel%\n',
            encoding="utf-8",
        )
        build = subprocess.run(["cmd.exe", "/d", "/c", batch.name],
                               cwd=folder, capture_output=True,
                               text=True, timeout=90, check=False)
        if build.returncode or not exe.is_file():
            raise RuntimeError("HOLD: real focus hint MSVC source compile failed: " +
                               (build.stderr + build.stdout)[-3400:])
        run = subprocess.run([str(exe)], cwd=folder, capture_output=True,
                             text=True, timeout=12, check=False)
        if run.returncode or "actual C++ focus hint checks" not in run.stdout:
            raise RuntimeError("HOLD: focus hint MSVC behavior rejected: " +
                               (run.stderr + run.stdout)[-3400:])
        return run.stdout.strip()


def main() -> None:
    if os.name != "nt":
        raise RuntimeError("HOLD: Windows-only; hosted Linux runs portable C++ harness")
    vcvars = find_vcvars64()
    actual = focus.extract(focus.SRC.read_text(encoding="utf-8"))
    print("INSTALLED_MSVC_VCVARS=" + str(vcvars))
    for shipping in (0, 1):
        print(f"FOCUS_MSVC_SHIPPING={shipping}: " + run_case(vcvars, actual, shipping))
    print("MSVC_REAL_FOCUS_HINT_BODY_PASS_NOT_UNREAL_EDITOR_OR_PIE")


if __name__ == "__main__":
    main()
