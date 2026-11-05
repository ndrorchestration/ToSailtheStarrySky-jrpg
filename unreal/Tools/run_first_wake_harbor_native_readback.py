#!/usr/bin/env python3
"""Opt-in independent UE 5.8.4 NullRHI Harbor V1 saved-map readback launcher.

Only run after the OTHER native staging process has completed and produced an
accepted host receipt. Never open another Editor while the user's Editor or
Live Coding is running. Protect both original and newly staged World hashes.
No GPU images, PIE, production changes or art approval from this check.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time

import run_first_wake_harbor_native_stage as stage

ROOT = stage.ROOT
PROJECT = stage.PROJECT
ENGINE = stage.EDITOR
SCRIPT = Path(__file__).with_name("verify_first_wake_harbor_native.py")
STAGE_HOST = stage.HOST
STAGE_NATIVE = stage.NATIVE
READBACK_NATIVE = stage.OUTPUT / "independent_harbor_readback.json"
READBACK_HOST = stage.OUTPUT / "host_harbor_readback.json"
READBACK_LOG = stage.OUTPUT / "harbor_readback_unreal_native.log"
READBACK_CONSOLE = stage.OUTPUT / "harbor_readback_unreal_console.log"
MIN_NATIVE_GIB = stage.MIN_NATIVE_GIB
MIN_DISK_GIB = stage.MIN_FREE_DISK_GIB
MAX_RUNTIME_S = 180


def readback_preflight() -> dict:
    if sys.platform != "win32" or ROOT.name != "TSTSS_EnvironmentHarbor_20261104":
        raise RuntimeError("HOLD: readback requires the authorized isolated Windows worktree")
    if stage.git("branch", "--show-current") != stage.EXPECTED_BRANCH:
        raise RuntimeError("HOLD: wrong review branch")
    if stage.git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("HOLD: uncommitted tracked changes")
    if not SCRIPT.is_file() or not ENGINE.is_file():
        raise RuntimeError("HOLD: readback script or UE binary missing")
    ver = json.loads((ENGINE.parents[2] / "Build/Build.version").read_text(encoding="utf-8"))
    if (ver["MajorVersion"], ver["MinorVersion"], ver["PatchVersion"]) != (5, 8, 4):
        raise RuntimeError("HOLD: installed UE must be 5.8.4")
    if not (PROJECT / "ToSailTheStarrySky.uproject").is_file():
        raise RuntimeError("HOLD: missing isolated Unreal project")
    if any(p.exists() for p in (READBACK_NATIVE, READBACK_HOST, READBACK_LOG, READBACK_CONSOLE)):
        raise RuntimeError("HOLD: prior native readback exists, no overwrite")
    for p in (stage.MAP, stage.OUTPUT_MAP, STAGE_HOST, STAGE_NATIVE):
        if not p.is_file():
            raise RuntimeError("HOLD: native stage map or receipt missing: " + str(p))
    if stage.digest(stage.MAP) != stage.EXPECTED_MAP_SHA:
        raise RuntimeError("HOLD: parent 34-actor World bytes changed")
    host = json.loads(STAGE_HOST.read_text(encoding="utf-8"))
    native = json.loads(STAGE_NATIVE.read_text(encoding="utf-8"))
    if host.get("status") != "NATIVE_MAP_SAVED_PENDING_INDEPENDENT_READBACK":
        raise RuntimeError("HOLD: host stage did not complete successfully")
    if native.get("status") != "NATIVE_HARBOR_MAP_SAVED_PENDING_INDEPENDENT_READBACK":
        raise RuntimeError("HOLD: native stage did not complete successfully")
    map_hash = stage.digest(stage.OUTPUT_MAP)
    if not map_hash or map_hash != host.get("new_map_sha256") or map_hash != native.get("map_sha256"):
        raise RuntimeError("HOLD: staged map hash fails dual receipt custody")
    if host.get("source_head") != stage.git("rev-parse", "HEAD"):
        raise RuntimeError("HOLD: source commit moved after native staging")
    if host.get("config_hashes_preserved") is not True or host.get("parent_map_sha_preserved") is not True:
        raise RuntimeError("HOLD: stage failed to preserve configs or original map")
    if list((PROJECT / "Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: existing SaveGames, do not touch")
    running = subprocess.run(["tasklist", "/FO", "CSV"], timeout=20,
                             capture_output=True, text=True, check=True).stdout.lower()
    if any(name in running for name in
           ("unrealeditor.exe", "unrealeditor-cmd.exe", "livecodingconsole.exe")):
        raise RuntimeError("HOLD: an Editor or Live Coding process is active")
    free = stage.free_gib()
    disk = shutil.disk_usage(ROOT).free / 1024**3
    if free < MIN_NATIVE_GIB or disk < MIN_DISK_GIB:
        raise RuntimeError("HOLD: insufficient physical RAM or free disk for NullRHI readback")
    configs = (PROJECT / "Config/DefaultEngine.ini", PROJECT / "Config/DefaultInput.ini")
    if not all(p.is_file() and p.stat().st_mode & stat.S_IWRITE for p in configs):
        raise RuntimeError("HOLD: tracked config absent or prelocked")
    config_hashes = {p.name: stage.digest(p) for p in configs}
    if config_hashes != host.get("config_hashes"):
        raise RuntimeError("HOLD: protected configs changed since stage")
    return {
        "status": "INDEPENDENT_READBACK_NOT_STARTED",
        "source_head": host["source_head"],
        "parent_map_sha256": stage.EXPECTED_MAP_SHA,
        "new_map_sha256": map_hash,
        "config_hashes": config_hashes,
        "initial_free_gib": round(free, 3),
        "initial_disk_free_gib": round(disk, 3),
        "native_gpu_capture_verified": False,
        "pie_verified": False,
        "creator_art_approved": False,
        "starbourne_unlocked": False,
    }


def main() -> int:
    evidence = readback_preflight()  # No side-effects if safety gate fails.
    configs = (PROJECT / "Config/DefaultEngine.ini", PROJECT / "Config/DefaultInput.ini")
    try:
        for p in configs:
            os.chmod(p, stat.S_IREAD)
        command = [str(ENGINE), str(PROJECT / "ToSailTheStarrySky.uproject"),
                   "-ExecutePythonScript=" + str(SCRIPT),
                   "-NullRHI", "-unattended", "-nop4", "-NoSplash", "-NoSound",
                   "-stdout", "-FullStdOutLogOutput", "-abslog=" + str(READBACK_LOG)]
        with READBACK_CONSOLE.open("x", encoding="utf-8") as out:
            proc = subprocess.Popen(command, cwd=str(ROOT), stdin=subprocess.DEVNULL,
                                    stdout=out, stderr=subprocess.STDOUT,
                                    creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            evidence["readback_child_pid"] = proc.pid
            started = time.monotonic()
            while proc.poll() is None:
                if time.monotonic() - started > MAX_RUNTIME_S or stage.free_gib() < .85:
                    evidence["status"] = "READBACK_CHILD_TERMINATED_BY_SAFETY_GUARD"
                    proc.terminate()
                    break
                time.sleep(2)
            try:
                evidence["editor_exit_code"] = proc.wait(timeout=12)
            except subprocess.TimeoutExpired:
                proc.kill()
                evidence["editor_exit_code"] = proc.wait(timeout=6)
        if evidence["status"] == "READBACK_CHILD_TERMINATED_BY_SAFETY_GUARD":
            raise RuntimeError("Native readback child hit time or memory safety guard")
        if evidence["editor_exit_code"] != 0 or not READBACK_NATIVE.is_file():
            raise RuntimeError("Readback exited nonzero or native readback receipt missing")
        verified = json.loads(READBACK_NATIVE.read_text(encoding="utf-8"))
        if verified.get("status") != "INDEPENDENT_NATIVE_HARBOR_SAVED_WORLD_READBACK_PASS_NOT_PIE":
            raise RuntimeError("Readback script did not report a verified World")
        if verified.get("new_map_sha256") != evidence["new_map_sha256"]:
            raise RuntimeError("Native readback refers to wrong World hash")
        if verified.get("total_actor_count") != 84 or verified.get("new_materials_verified") != 8:
            raise RuntimeError("Native readback actor/material count mismatch")
        if "TSTSS_HARBOR_INDEPENDENT_READBACK_PASS_NOT_PIE" not in READBACK_LOG.read_text(
                encoding="utf-8", errors="replace"):
            raise RuntimeError("UE native log lacks independent readback sentinel")
        evidence["status"] = "INDEPENDENT_NATIVE_HARBOR_READBACK_VERIFIED_NOT_PIE"
        evidence["verified_actor_count"] = verified["total_actor_count"]
        evidence["verified_material_count"] = verified["new_materials_verified"]
    except Exception as err:
        evidence["status"] = "INDEPENDENT_NATIVE_READBACK_HOLD"
        evidence["error"] = str(err)
    finally:
        for p in configs:
            os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
        evidence["config_hashes_preserved"] = all(
            stage.digest(p) == evidence["config_hashes"][p.name] for p in configs)
        evidence["parent_map_sha_preserved"] = stage.digest(stage.MAP) == stage.EXPECTED_MAP_SHA
        evidence["staged_map_sha_preserved"] = stage.digest(stage.OUTPUT_MAP) == evidence["new_map_sha256"]
        evidence["source_head_preserved"] = stage.git("rev-parse", "HEAD") == evidence["source_head"]
        if not all(evidence[key] for key in
                   ("config_hashes_preserved", "parent_map_sha_preserved",
                    "staged_map_sha_preserved", "source_head_preserved")):
            evidence["status"] = "INDEPENDENT_NATIVE_READBACK_HOLD"
        with READBACK_HOST.open("x", encoding="utf-8") as out:
            json.dump(evidence, out, indent=2, sort_keys=True)
    print(json.dumps({k: evidence.get(k) for k in
          ("status", "source_head", "editor_exit_code", "verified_actor_count",
           "verified_material_count", "error")}, sort_keys=True))
    return 0 if evidence["status"] == "INDEPENDENT_NATIVE_HARBOR_READBACK_VERIFIED_NOT_PIE" else 2


if __name__ == "__main__":
    sys.exit(main())
