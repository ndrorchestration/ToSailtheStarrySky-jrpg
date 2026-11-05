#!/usr/bin/env python3
"""Optional, guarded NullRHI UE5.8.4 First Wake Harbor V1 staging runner.

This runner cannot claim a native PASS unless Unreal Editor exits 0, the new
map/receipt exist, and native project log evidence matches. It refuses active
Editors and low RAM instead of closing user processes. No GPU or PIE.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unreal"
SOURCE = Path(__file__).with_name("build_first_wake_harbor_environment.py")
MAP = PROJECT / "Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap"
OUTPUT_MAP = PROJECT / "Content/TSTSS/Review/Scenes/FirstWake_HarborEnvironment_20261104_REVIEW_V1.umap"
EXPECTED_MAP_SHA = "54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5"
EDITOR = Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe")
OUTPUT = PROJECT / "Saved/FirstWakeEnvironmentV1"
NATIVE = OUTPUT / "native_harbor_stage.json"
HOST = OUTPUT / "host_harbor_stage.json"
LOG = OUTPUT / "harbor_unreal_native.log"
CONSOLE = OUTPUT / "harbor_unreal_console.log"
EXPECTED_BRANCH = "review/ue58-firstwake-environments-20261104"
MIN_NATIVE_GIB = 5.0
MIN_FREE_DISK_GIB = 14.0
MAX_RUNTIME_S = 240


class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def free_gib():
    info = MemoryStatus()
    info.dwLength = ctypes.sizeof(info)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(info)):
        raise OSError("Cannot verify physical RAM on this workstation")
    return info.ullAvailPhys / 1024**3


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(["git", "-C", str(ROOT), *args], timeout=25,
                            capture_output=True, text=True, check=True)
    return result.stdout.strip()


def native_preflight() -> dict:
    if sys.platform != "win32" or ROOT.name != "TSTSS_EnvironmentHarbor_20261104":
        raise RuntimeError("HOLD: unsupported or non-isolated workstation")
    if git("branch", "--show-current") != EXPECTED_BRANCH:
        raise RuntimeError("HOLD: unexpected current branch")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("HOLD: tracked source differs from committed HEAD")
    if not SOURCE.is_file() or not EDITOR.is_file() or not (PROJECT / "ToSailTheStarrySky.uproject").is_file():
        raise RuntimeError("HOLD: Unreal project, script, or installed Editor missing")
    engine = json.loads((EDITOR.parents[2] / "Build/Build.version").read_text(encoding="utf-8"))
    if (engine["MajorVersion"], engine["MinorVersion"], engine["PatchVersion"]) != (5, 8, 4):
        raise RuntimeError("HOLD: exact installed UE 5.8.4 required")
    if not MAP.is_file() or digest(MAP) != EXPECTED_MAP_SHA:
        raise RuntimeError("HOLD: copied original V3 map absent or drifted")
    if any(p.exists() for p in (OUTPUT_MAP, NATIVE, HOST, LOG, CONSOLE)):
        raise RuntimeError("HOLD: prior environment stage artifact already exists")
    if list((PROJECT / "Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: existing SaveGame files must remain untouched")
    running = subprocess.run(["tasklist", "/FO", "CSV"], timeout=20,
                             capture_output=True, text=True, check=True).stdout.lower()
    if any(tag in running for tag in
           ("unrealeditor.exe", "unrealeditor-cmd.exe", "livecodingconsole.exe")):
        raise RuntimeError("HOLD: user Unreal Editor or Live Coding currently active")
    available = free_gib()
    disk_gib = shutil.disk_usage(ROOT).free / 1024**3
    if available < MIN_NATIVE_GIB or disk_gib < MIN_FREE_DISK_GIB:
        raise RuntimeError("HOLD: insufficient free RAM/disk for isolated NullRHI stage")
    configs = (PROJECT / "Config/DefaultEngine.ini", PROJECT / "Config/DefaultInput.ini")
    if not all(p.is_file() and p.stat().st_mode & stat.S_IWRITE for p in configs):
        raise RuntimeError("HOLD: missing or pre-locked tracked configs")
    return {
        "source_head": git("rev-parse", "HEAD"),
        "parent_map_sha256": EXPECTED_MAP_SHA,
        "initial_free_gib": round(available, 3),
        "initial_disk_free_gib": round(disk_gib, 3),
        "config_hashes": {p.name: digest(p) for p in configs},
        "native_render_verified": False,
        "pie_verified": False,
        "production_art_approved": False,
        "starbourne_unlocked": False,
        "status": "NATIVE_STAGE_NOT_STARTED",
    }


def main() -> int:
    evidence = native_preflight()  # Fail before making new files.
    config_paths = (PROJECT / "Config/DefaultEngine.ini", PROJECT / "Config/DefaultInput.ini")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    try:
        for path in config_paths:
            os.chmod(path, stat.S_IREAD)
        args = [str(EDITOR), str(PROJECT / "ToSailTheStarrySky.uproject"),
                "-ExecutePythonScript=" + str(SOURCE),
                "-NullRHI", "-unattended", "-nop4", "-NoSplash", "-NoSound",
                "-stdout", "-FullStdOutLogOutput", "-abslog=" + str(LOG)]
        # Default script needs '--build' to do real native authoring. Unreal
        # ExecutePythonScript calls this file without args; set a sentinel env.
        env = os.environ.copy()
        env["TSTSS_HARBOR_BUILD_EXPLICIT"] = "1"
        with CONSOLE.open("x", encoding="utf-8") as stream:
            proc = subprocess.Popen(args, cwd=str(ROOT), env=env, stdin=subprocess.DEVNULL,
                                    stdout=stream, stderr=subprocess.STDOUT,
                                    creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            evidence["child_pid"] = proc.pid
            started = time.monotonic()
            while proc.poll() is None:
                if time.monotonic() - started > MAX_RUNTIME_S or free_gib() < .85:
                    evidence["status"] = "NATIVE_CHILD_TERMINATED_BY_SAFETY_GUARD"
                    proc.terminate()
                    break
                time.sleep(2)
            try:
                evidence["editor_exit_code"] = proc.wait(timeout=12)
            except subprocess.TimeoutExpired:
                proc.kill()
                evidence["editor_exit_code"] = proc.wait(timeout=6)
        if evidence["status"] == "NATIVE_CHILD_TERMINATED_BY_SAFETY_GUARD":
            raise RuntimeError("Native Editor stopped by resource/runtime guard")
        if evidence["editor_exit_code"] != 0 or not NATIVE.is_file():
            raise RuntimeError("Missing native receipt or nonzero Editor exit")
        native = json.loads(NATIVE.read_text(encoding="utf-8"))
        if native.get("status") != "NATIVE_HARBOR_MAP_SAVED_PENDING_INDEPENDENT_READBACK":
            raise RuntimeError("Native receipt does not assert a saved map")
        if not OUTPUT_MAP.is_file() or digest(OUTPUT_MAP) != native.get("map_sha256"):
            raise RuntimeError("Saved map byte hash differs from native receipt")
        if "TSTSS_HARBOR_NATIVE_STAGE_SAVED_NOT_PIE" not in LOG.read_text(
                encoding="utf-8", errors="replace"):
            raise RuntimeError("Full native log lacks Harbor stage success sentinel")
        evidence["status"] = "NATIVE_MAP_SAVED_PENDING_INDEPENDENT_READBACK"
        evidence["new_map_sha256"] = native["map_sha256"]
    except Exception as e:
        evidence["status"] = "NATIVE_STAGE_HOLD"
        evidence["error"] = str(e)
    finally:
        for path in config_paths:
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        evidence["config_hashes_preserved"] = all(
            digest(p) == evidence["config_hashes"][p.name] for p in config_paths)
        evidence["parent_map_sha_preserved"] = digest(MAP) == EXPECTED_MAP_SHA
        evidence["source_head_preserved"] = git("rev-parse", "HEAD") == evidence["source_head"]
        if not all((evidence["config_hashes_preserved"],
                    evidence["parent_map_sha_preserved"],
                    evidence["source_head_preserved"])):
            evidence["status"] = "NATIVE_STAGE_HOLD"
        HOST.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({k: evidence.get(k) for k in
          ("status", "source_head", "editor_exit_code", "new_map_sha256", "error")},
          sort_keys=True))
    return 0 if evidence["status"] == "NATIVE_MAP_SAVED_PENDING_INDEPENDENT_READBACK" else 2


if __name__ == "__main__":
    sys.exit(main())
