#!/usr/bin/env python3
"""Read-only Windows host admission check for isolated First Wake bokeh staging.

NEVER launches Unreal, cleans disks, kills processes, edits maps, or modifies git.
Run immediately before EACH of the two fresh Unreal Editor stages.
"""
from __future__ import annotations
import argparse
import ctypes
import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unreal"
EXPECTED_WORKTREE = "TSTSS_BokehFocusReview_20261111"
ENGINE_ROOT = Path("C:/Program Files/Epic Games/UE_5.8/Engine")
ENGINE_BIN = ENGINE_ROOT / "Binaries/Win64/UnrealEditor.exe"
ENGINE_VERSION = ENGINE_ROOT / "Build/Build.version"
SOURCE_MAP = PROJECT / "Content/TSTSS/Review/VerticalSlice/VS01_DenithHarbor.umap"
DEST_MAP = PROJECT / "Content/TSTSS/Review/DynamicFocus_V1/M_DenithHarborBokehStudy.umap"
PREPARE_RECEIPT = PROJECT / "Saved/BokehReviewV1/prepare.json"
COMPOSE_RECEIPT = PROJECT / "Saved/BokehReviewV1/compose.json"
MIN_RAM_GIB = 6.5
MIN_DISK_GIB = 14.0
ACTIVE_PROCESSES = {"unrealeditor.exe", "unrealeditor-cmd.exe",
                    "livecodingconsole.exe", "shadercompileworker.exe",
                    "unrealbuildtool.exe"}


class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtended", ctypes.c_ulonglong)
    ]


def free_ram_gib():
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise RuntimeError("cannot read physical memory")
    return status.ullAvailPhys / (1024 ** 3)


def running_engine_processes():
    result = subprocess.run(["tasklist", "/FO", "CSV", "/NH"],
                            capture_output=True, text=True, timeout=20, check=True)
    names = {row[0].lower() for row in csv.reader(result.stdout.splitlines()) if row}
    return sorted(names & ACTIVE_PROCESSES)


def git(*args):
    result = subprocess.run(["git", "-C", str(ROOT), *args],
                            capture_output=True, text=True, timeout=20)
    if result.returncode:
        raise RuntimeError("git status/read failed")
    return result.stdout.strip()


def classify(snapshot, phase):
    failed = []
    if snapshot["platform"] != "win32":
        failed.append("WINDOWS_REQUIRED")
    if snapshot["worktree"] != EXPECTED_WORKTREE:
        failed.append("WORKTREE_MISMATCH")
    if not snapshot["head_matches"]:
        failed.append("HEAD_MISMATCH")
    if not snapshot["engine_correct"]:
        failed.append("ENGINE_VERSION_MISMATCH")
    if not snapshot["source_map_present"]:
        failed.append("SOURCE_MAP_MISSING")
    if snapshot["free_ram_gib"] < MIN_RAM_GIB:
        failed.append("LOW_RAM")
    if snapshot["free_disk_gib"] < MIN_DISK_GIB:
        failed.append("LOW_DISK")
    if snapshot["busy"]:
        failed.append("UNREAL_BUSY")
    if snapshot["source_changes"]:
        failed.append("SOURCE_DIRTY")
    if phase == "prepare":
        if snapshot["review_map_exists"] or snapshot["prepare_receipt_exists"]:
            failed.append("REVIEW_OCCUPIED")
    elif phase == "compose":
        if not snapshot["review_map_exists"] or not snapshot["prepare_receipt_exists"]:
            failed.append("PREPARATION_MISSING")
        if snapshot["compose_receipt_exists"]:
            failed.append("REVIEW_ALREADY_COMPOSED")
    else:
        failed.append("PHASE_INVALID")
    return failed


def inspect(expected_head, phase):
    if sys.platform != "win32":
        return {"status": "HOLD", "reasons": ["WINDOWS_REQUIRED"]}
    if not re.fullmatch(r"[0-9a-f]{40}", expected_head):
        return {"status": "HOLD", "reasons": ["INVALID_EXPECTED_HEAD"]}
    status = git("status", "--porcelain", "-uall").splitlines()
    allowed = "?? unreal/Content/TSTSS/Review/DynamicFocus_V1/"
    dirty = status if phase == "prepare" else [
        line for line in status if not line.startswith(allowed)]
    engine_ok = False
    if ENGINE_VERSION.is_file() and ENGINE_BIN.is_file():
        version = json.loads(ENGINE_VERSION.read_text(encoding="utf-8"))
        engine_ok = [version.get(k) for k in
                     ("MajorVersion", "MinorVersion", "PatchVersion")] == [5, 8, 4]
    snapshot = {
        "platform": sys.platform, "worktree": ROOT.name,
        "head_matches": git("rev-parse", "HEAD").lower() == expected_head,
        "engine_correct": engine_ok, "source_map_present": SOURCE_MAP.is_file(),
        "free_ram_gib": round(free_ram_gib(), 2),
        "free_disk_gib": round(shutil.disk_usage(PROJECT).free / (1024 ** 3), 2),
        "busy": running_engine_processes(),
        "source_changes": dirty,
        "review_map_exists": DEST_MAP.exists(),
        "prepare_receipt_exists": PREPARE_RECEIPT.exists(),
        "compose_receipt_exists": COMPOSE_RECEIPT.exists()
    }
    failures = classify(snapshot, phase)
    return {"schema": "tstss.firstwake.bokeh.host-check.v1",
            "status": "READY_FOR_GUARDED_NATIVE_STAGE" if not failures else "HOLD",
            "phase": phase, "expected_head": expected_head,
            "reasons": failures, "evidence": snapshot,
            "editor_launched": False, "map_written": False}


def self_test():
    good = dict(platform="win32", worktree=EXPECTED_WORKTREE,
                head_matches=True, engine_correct=True, source_map_present=True,
                free_ram_gib=8.0, free_disk_gib=15.0, busy=[], source_changes=[],
                review_map_exists=False, prepare_receipt_exists=False,
                compose_receipt_exists=False)
    assert classify(good, "prepare") == []
    cases = [
        ({"free_disk_gib": 13.26}, "LOW_DISK"),
        ({"free_ram_gib": 6.0}, "LOW_RAM"),
        ({"busy": ["unrealeditor.exe"]}, "UNREAL_BUSY"),
        ({"source_changes": [" M unreal/Config/DefaultEngine.ini"]}, "SOURCE_DIRTY"),
        ({"review_map_exists": True}, "REVIEW_OCCUPIED"),
        ({"head_matches": False}, "HEAD_MISMATCH")
    ]
    for delta, reason in cases:
        changed = {**good, **delta}
        assert reason in classify(changed, "prepare"), reason
    composed = {**good, "review_map_exists": True, "prepare_receipt_exists": True}
    assert classify(composed, "compose") == []
    assert "PREPARATION_MISSING" in classify(good, "compose")
    return {"status": "OFFLINE_HOST_GATES_PASS", "positive_cases": 2,
            "negative_cases": 7, "native_execution": "NOT_RUN"}


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--check", action="store_true")
    parser.add_argument("--expected-head", default="")
    parser.add_argument("--phase", choices=["prepare", "compose"], default="prepare")
    a = parser.parse_args()
    result = self_test() if a.self_test else inspect(a.expected_head.lower(), a.phase)
    print(json.dumps(result, indent=2))
    if result.get("status") == "HOLD":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
