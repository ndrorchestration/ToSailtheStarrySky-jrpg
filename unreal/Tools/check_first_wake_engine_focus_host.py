#!/usr/bin/env python3
"""Read-only host admission for the isolated First Wake ENGINE optical review.

Always run BEFORE launching either guarded UE Editor process. No staging,
disk cleanup, networking, source mutations, or implicit permission to compile.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

import check_first_wake_bokeh_host as host
import stage_first_wake_engine_focus_review as engine


def inspect(expected_head: str, phase: str) -> dict:
    if sys.platform != "win32":
        return {"status": "HOLD", "reasons": ["WINDOWS_REQUIRED"],
                "engine_editor_launched": False}
    if not re.fullmatch(r"[0-9a-f]{40}", expected_head.lower()):
        return {"status": "HOLD", "reasons": ["INVALID_EXPECTED_HEAD"],
                "engine_editor_launched": False}
    if phase not in ("prepare", "compose"):
        return {"status": "HOLD", "reasons": ["PHASE_INVALID"],
                "engine_editor_launched": False}
    result = subprocess.run(
        ["git", "-C", str(engine.ROOT), "status", "--porcelain", "-uall"],
        capture_output=True, text=True, check=False, timeout=20)
    if result.returncode:
        return {"status": "HOLD", "reasons": ["GIT_STATUS_UNAVAILABLE"],
                "engine_editor_launched": False}
    changes = result.stdout.splitlines()
    if phase == "compose":
        changes = [s for s in changes if not s.startswith(
            "?? unreal/Content/TSTSS/Review/EngineFocus_V1/")]
    head = subprocess.run(
        ["git", "-C", str(engine.ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False, timeout=20)
    actual_head = head.stdout.strip().lower() if head.returncode == 0 else ""

    engine_correct = False
    if host.ENGINE_VERSION.is_file() and host.ENGINE_BIN.is_file():
        try:
            version = json.loads(host.ENGINE_VERSION.read_text(encoding="utf-8"))
            engine_correct = [version.get(k) for k in
                              ("MajorVersion", "MinorVersion", "PatchVersion")] == [5, 8, 4]
        except (OSError, ValueError, KeyError):
            pass

    snapshot = {
        "platform": sys.platform,
        "worktree": engine.ROOT.name,
        "head_matches": actual_head == expected_head.lower(),
        "engine_correct": engine_correct,
        "source_map_present": engine.SOURCE_FILE.is_file(),
        "free_ram_gib": round(host.free_ram_gib(), 2),
        "free_disk_gib": round(
            shutil.disk_usage(engine.PROJECT).free / (1024 ** 3), 2),
        "busy": host.running_engine_processes(),
        "source_changes": changes,
        "review_map_exists": engine.DEST_FILE.exists(),
        "prepare_receipt_exists": engine.PREPARE_RECEIPT.exists(),
        "compose_receipt_exists": engine.COMPOSE_RECEIPT.exists(),
    }
    reasons = host.classify(snapshot, phase)
    saved = engine.PROJECT / "Saved/SaveGames"
    if saved.exists() and list(saved.glob("*.sav")):
        reasons.append("SAVEGAMES_PRESENT")
    if phase == "prepare" and engine.DEST_FILE.parent.exists():
        reasons.append("REVIEW_NAMESPACE_OCCUPIED")
    return {
        "schema": "tstss.firstwake.engine_focus.host_admission.v1",
        "status": "READY_FOR_ENGINE_REVIEW_STAGE" if not reasons else "HOLD",
        "reasons": reasons, "phase": phase, "exact_head": expected_head,
        "resource_gates": {"min_ram_gib": host.MIN_RAM_GIB,
                           "min_disk_gib": host.MIN_DISK_GIB},
        "evidence": snapshot, "engine_editor_launched": False,
        "map_written": False, "native_compile_executed": False,
    }


def self_test() -> dict:
    base = dict(
        platform="win32", worktree=engine.WORKTREE,
        head_matches=True, engine_correct=True, source_map_present=True,
        free_ram_gib=8.0, free_disk_gib=15.0,
        busy=[], source_changes=[], review_map_exists=False,
        prepare_receipt_exists=False, compose_receipt_exists=False
    )
    assert host.classify(base, "prepare") == []
    assert "LOW_DISK" in host.classify({**base, "free_disk_gib": 13.28}, "prepare")
    assert "LOW_RAM" in host.classify({**base, "free_ram_gib": 3.0}, "prepare")
    assert "UNREAL_BUSY" in host.classify(
        {**base, "busy": ["unrealeditor.exe"]}, "prepare")
    assert "SOURCE_DIRTY" in host.classify(
        {**base, "source_changes": [" M unreal/Config/DefaultEngine.ini"]}, "prepare")
    composed = {**base, "review_map_exists": True,
                "prepare_receipt_exists": True}
    assert host.classify(composed, "compose") == []
    assert "PREPARATION_MISSING" in host.classify(base, "compose")
    return {"status": "ENGINE_HOST_GATES_OFFLINE_PASS",
            "checks": 7, "native_launch": "NOT_RUN"}


def main():
    p = argparse.ArgumentParser()
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--self-test", action="store_true")
    modes.add_argument("--check", action="store_true")
    p.add_argument("--expected-head", default="")
    p.add_argument("--phase", choices=["prepare", "compose"], default="prepare")
    args = p.parse_args()
    result = self_test() if args.self_test else inspect(
        args.expected_head.lower(), args.phase)
    print(json.dumps(result, indent=2))
    if result.get("status") == "HOLD":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
