#!/usr/bin/env python3
"""Read-only admission for feature-branch native VS02 atmosphere authoring.

Never launches UE, cleans caches, edits game/source/configs, or creates maps.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import check_first_wake_bokeh_host as native_host
import stage_first_wake_playable_engine_atmosphere as stage

MIN_DISK_GIB = 14.0
MIN_RAM_GIB = 6.5
DLL = stage.PROJECT / "Binaries/Win64/UnrealEditor-ToSailTheStarrySky.dll"


def classify(s: dict) -> list[str]:
    reasons = []
    checks = (
        ("WINDOWS_REQUIRED", s.get("platform") == "win32"),
        ("WRONG_WORKTREE", s.get("worktree") == stage.WORKTREE),
        ("EXACT_HEAD_MISMATCH", s.get("head_matches") is True),
        ("SOURCE_DIRTY", not s.get("source_changes")),
        ("ENGINE_VERSION_MISMATCH", s.get("engine_correct") is True),
        ("SOURCE_MAP_MISSING_OR_DRIFTED", s.get("map_sha_matches") is True),
        ("NATIVE_EDITOR_MODULE_UNBUILT", s.get("compiled_dll_exists") is True),
        ("RECEIPT_OCCUPIED", s.get("receipt_exists") is False),
        ("UNREAL_BUSY", not s.get("unreal_processes")),
        ("LOW_RAM", s.get("free_ram_gib", 0) >= MIN_RAM_GIB),
        ("LOW_DISK", s.get("free_disk_gib", 0) >= MIN_DISK_GIB),
    )
    for code, acceptable in checks:
        if not acceptable:
            reasons.append(code)
    return reasons


def command(*args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", "-C", str(stage.ROOT), *args],
        capture_output=True, text=True, check=False, timeout=25,
    )
    return proc.returncode, proc.stdout.strip()


def inspect(expected_head: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", expected_head.lower()):
        return {"status": "HOLD", "reasons": ["INVALID_EXPECTED_HEAD"],
                "editor_launched": False, "map_written": False}
    if sys.platform != "win32":
        return {"status": "HOLD", "reasons": ["WINDOWS_REQUIRED"],
                "editor_launched": False, "map_written": False}
    rc, head = command("rev-parse", "HEAD")
    src, changes = command("status", "--porcelain", "-uall")
    engine_ok = False
    if native_host.ENGINE_VERSION.is_file() and native_host.ENGINE_BIN.is_file():
        try:
            v = json.loads(native_host.ENGINE_VERSION.read_text(encoding="utf-8"))
            engine_ok = [v.get("MajorVersion"), v.get("MinorVersion"),
                         v.get("PatchVersion")] == [5, 8, 4]
        except (OSError, ValueError):
            pass
    native_map_hash = (
        stage.digest(stage.MAP_FILE)
        if stage.MAP_FILE.is_file() else ""
    )
    snapshot = {
        "platform": sys.platform,
        "worktree": stage.ROOT.name,
        "head_matches": rc == 0 and head.lower() == expected_head.lower(),
        "source_changes": changes.splitlines() if src == 0 else ["GIT_STATUS_ERROR"],
        "engine_correct": engine_ok,
        "map_sha_matches": native_map_hash == stage.EXPECTED_ORIGINAL_SHA,
        "compiled_dll_exists": DLL.is_file(),
        "receipt_exists": stage.RECEIPT.is_file(),
        "unreal_processes": native_host.running_engine_processes(),
        "free_ram_gib": round(native_host.free_ram_gib(), 3),
        "free_disk_gib": round(
            shutil.disk_usage(stage.PROJECT).free / (1024.0 ** 3), 3),
    }
    reasons = classify(snapshot)
    return {
        "schema": "tstss.firstwake.playable_engine_map.host_admission.v1",
        "status": "READY_FOR_ISOLATED_NATIVE_VS02_STAGE" if not reasons else "HOLD",
        "reasons": reasons,
        "exact_head": expected_head.lower(),
        "gates": {"ram_gib": MIN_RAM_GIB, "disk_gib": MIN_DISK_GIB},
        "evidence": snapshot,
        "editor_launched": False, "map_written": False,
        "native_pie": "NOT_RUN",
    }


def self_test() -> dict:
    good = {
        "platform": "win32", "worktree": stage.WORKTREE,
        "head_matches": True, "source_changes": [],
        "engine_correct": True, "map_sha_matches": True,
        "compiled_dll_exists": True, "receipt_exists": False,
        "unreal_processes": [], "free_ram_gib": 7.0,
        "free_disk_gib": 16.0,
    }
    assert classify(good) == []
    cases = [
        ({"free_ram_gib": 4.3}, "LOW_RAM"),
        ({"free_disk_gib": 13.9}, "LOW_DISK"),
        ({"compiled_dll_exists": False}, "NATIVE_EDITOR_MODULE_UNBUILT"),
        ({"head_matches": False}, "EXACT_HEAD_MISMATCH"),
        ({"source_changes": [" M unreal/Config/DefaultInput.ini"]}, "SOURCE_DIRTY"),
        ({"unreal_processes": ["unrealeditor.exe"]}, "UNREAL_BUSY"),
        ({"map_sha_matches": False}, "SOURCE_MAP_MISSING_OR_DRIFTED"),
        ({"receipt_exists": True}, "RECEIPT_OCCUPIED"),
        ({"worktree": "TSTSS_BokehFocusReview_20261111"}, "WRONG_WORKTREE"),
    ]
    for change, wanted in cases:
        assert wanted in classify({**good, **change}), wanted
    return {
        "status": "PLAYABLE_ENGINE_HOST_OFFLINE_FIXTURES_PASS",
        "cases": 10, "editor_launched": False, "map_written": False,
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    one = p.add_mutually_exclusive_group(required=True)
    one.add_argument("--check", action="store_true")
    one.add_argument("--self-test", action="store_true")
    p.add_argument("--expected-head", default="")
    args = p.parse_args()
    value = self_test() if args.self_test else inspect(args.expected_head)
    print(json.dumps(value, indent=2))
    if value.get("status") == "HOLD":
        raise SystemExit(2)
