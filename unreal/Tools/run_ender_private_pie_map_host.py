"""Resource-guarded one-shot private Ender PIE map preparation on Neontic.

Does not start PIE, alter shipped assets, close user-owned apps, or publish
private Daz/Unreal material. Only a verified private V5 map and GameMode may be
created. The child process is owned by this invocation and safety monitored.
"""
from __future__ import annotations

import argparse
import ctypes
import csv
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time
import uuid

ROOT = Path(r"C:\TSTSS_CivicIntegration_20261116")
PROJECT = ROOT / "unreal"
EDITOR = Path(r"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe")
UPROJECT = PROJECT / "ToSailTheStarrySky.uproject"
SCRIPT = PROJECT / "Tools/stage_ender_private_pie_map.py"
EVIDENCE = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate"
NATIVE_REPORT = EVIDENCE / "PIE_private_map_prepare_receipt.json"
PRIVATE = PROJECT / "Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
ORIGINAL_MAP = PROJECT / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview.umap"
ORIGINAL_BP = PROJECT / "Content/TSTSS/Review/Characters/EnderSliceVisualV1_NONCANONICAL/BP_EnderSlice_PIEReview.uasset"
PRIVATE_BP = PRIVATE / "BP_EnderLocomotionPreview_NONCANONICAL.uasset"
EXPECTED = {"BP_EnderPIEGameMode_NONCANONICAL.uasset", "FirstWake_PreludeInteraction_V5_VisualReview.umap"}
PROTECTED = (UPROJECT, PROJECT / "Config/DefaultEngine.ini", PROJECT / "Config/DefaultInput.ini",
             ORIGINAL_MAP, ORIGINAL_BP, PRIVATE_BP)
BASE = "c4576432e3025993190d6a126e7198725368c007"
START_RAM = 6.5
START_DISK = 16.5
RUN_RAM = 2.5
RUN_DISK = 14.3
MAX_TIME_S = 300


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def must(ok: bool, token: str) -> None:
    if not ok:
        raise RuntimeError("HOLD_" + token)


def git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                       text=True, timeout=20, check=False)
    must(r.returncode == 0, "GIT_" + args[0].upper())
    return r.stdout.strip()


class Memory(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                ("total", ctypes.c_ulonglong), ("available", ctypes.c_ulonglong),
                ("page_total", ctypes.c_ulonglong), ("page_available", ctypes.c_ulonglong),
                ("virtual_total", ctypes.c_ulonglong), ("virtual_available", ctypes.c_ulonglong),
                ("extended", ctypes.c_ulonglong)]


def memory_gib() -> float:
    m = Memory()
    m.length = ctypes.sizeof(m)
    must(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)) != 0, "RAM_PROBE")
    return m.available / (2 ** 30)


def disk_gib() -> float:
    return shutil.disk_usage("C:\\").free / (2 ** 30)


def active_unreal() -> bool:
    r = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True,
                       text=True, timeout=20, check=False)
    must(r.returncode == 0, "PROCESS_INVENTORY")
    names = {row[0].strip().lower() for row in csv.reader(io.StringIO(r.stdout)) if row}
    return bool(names.intersection({"unrealeditor.exe", "unrealeditor-cmd.exe",
                                    "unrealbuildtool.exe", "livecodingconsole.exe",
                                    "shadercompileworker.exe"}))


def native_38_verified(head: str) -> bool:
    root = PROJECT / "Saved/MigrationEvidence"
    for path in root.glob(head[:12] + "-*/verified-native.json"):
        report_path = path.parent / "AutomationReport/index.json"
        if not report_path.is_file():
            continue
        receipt = json.loads(path.read_text(encoding="utf-8-sig"))
        report = json.loads(report_path.read_text(encoding="utf-8-sig"))
        entries = report.get("tests")
        if (receipt.get("source_sha") == head and
            receipt.get("status") == "WIN64_EDITOR_BUILD_AND_NATIVE_AUTOMATIONS_PASS_CLEAN_SOURCE" and
            receipt.get("required_native_tests") == 38 and
            receipt.get("report_sha256") == sha(report_path) and
            receipt.get("unreal_version") == "5.8.4" and
            (report.get("succeeded"), report.get("failed"), report.get("notRun")) == (38, 0, 0) and
            isinstance(entries, list) and len(entries) == 38 and
            len({row.get("fullTestPath") for row in entries if isinstance(row, dict)}) == 38 and
            all(isinstance(row, dict) and isinstance(row.get("fullTestPath"), str) and
                row["fullTestPath"].startswith("TSTSS.") and row.get("state") == "Success"
                for row in entries)):
            return True
    return False


def preflight() -> str:
    must(sys.platform == "win32", "WINDOWS_REQUIRED")
    must(EDITOR.is_file() and SCRIPT.is_file() and all(p.is_file() for p in PROTECTED),
         "INPUT_MISSING")
    must(git("branch", "--show-current").startswith("review/ender"), "REVIEW_BRANCH_REQUIRED")
    head = git("rev-parse", "HEAD")
    must(len(head) == 40 and not git("status", "--porcelain=v1"), "SOURCE_NOT_CLEAN")
    must(subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", BASE, head],
                        check=False, timeout=20).returncode == 0, "BASE_NATIVE_ANCESTOR")
    must(native_38_verified(head), "EXACT_HEAD_NATIVE_38_REQUIRED")
    must(not active_unreal(), "OTHER_UNREAL_PROCESS")
    must(memory_gib() >= START_RAM and disk_gib() >= START_DISK, "STARTUP_RESERVE")
    must(not NATIVE_REPORT.exists(), "OUTPUT_RECEIPT_COLLISION")
    for name in EXPECTED:
        output = PRIVATE / name
        relative = "unreal/" + str(output.relative_to(PROJECT)).replace("\\", "/")
        must(not output.exists(), "PRIVATE_OUTPUT_COLLISION")
        must(subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", relative],
                            timeout=20).returncode == 0, "PRIVATE_NOT_GIT_IGNORED")
    return head


def execute() -> dict:
    head = preflight()
    folder = EVIDENCE / "HostReceipts" / ("pie-map-" + str(uuid.uuid4()))
    folder.mkdir(parents=True, exist_ok=False)
    receipt_path = folder / "host_receipt.json"
    receipt = {"status": "STARTING", "source_head": head,
               "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "pie_playback_verified": False, "creator_approved": False}
    def save() -> None:
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf8")
    before = {str(p): sha(p) for p in PROTECTED}
    modes = {str(p): p.stat().st_mode for p in PROTECTED}
    env = os.environ.copy()
    env["TSTSS_PRIVATE_ENDER_PIE_MAP"] = "1"
    # This script edits a LevelEditorSubsystem world: use the full-editor
    # Python execution mode, which waits for the startup map/editor context.
    # A startup -ExecCmds=py or lean -run=pythonscript commandlet is unsafe
    # here because the private map clone needs an initialized level editor.
    cmd = [str(EDITOR), str(UPROJECT), "-nullrhi", "-NoSound", "-unattended",
           "-nosplash", "-nop4", "-ExecutePythonScript=" + str(SCRIPT),
           "-abslog=" + str(folder / "engine.log")]
    child = None
    launched_at = None
    flags_set = []
    stop_reason = None
    try:
        for file in PROTECTED:
            os.chmod(file, stat.S_IREAD)
            flags_set.append(file)
        with (folder / "stdout.log").open("w", encoding="utf8") as output:
            launched_at = time.time()
            child = subprocess.Popen(cmd, cwd=str(PROJECT), env=env,
                                     stdin=subprocess.DEVNULL, stdout=output,
                                     stderr=subprocess.STDOUT)
            receipt["owned_child_pid"] = child.pid
            receipt["status"] = "RUNNING"
            save()
            start = time.monotonic()
            while child.poll() is None:
                elapsed = time.monotonic() - start
                receipt["elapsed_s"] = round(elapsed, 1)
                receipt["ram_last_gib"] = round(memory_gib(), 3)
                receipt["disk_last_gib"] = round(disk_gib(), 3)
                save()
                if receipt["ram_last_gib"] < RUN_RAM:
                    stop_reason = "RAM_RESERVE"
                elif receipt["disk_last_gib"] < RUN_DISK:
                    stop_reason = "DISK_RESERVE"
                elif elapsed > MAX_TIME_S:
                    stop_reason = "TIMEOUT"
                if stop_reason:
                    subprocess.run(["taskkill", "/T", "/F", "/PID", str(child.pid)],
                                   capture_output=True, timeout=25, check=False)
                    break
                time.sleep(2)
            child.wait(timeout=30)
            receipt["child_exit_code"] = child.returncode
    finally:
        for file in reversed(flags_set):
            os.chmod(file, modes[str(file)])
        receipt["protected_hashes_unchanged"] = all(sha(p) == before[str(p)] for p in PROTECTED)
        receipt["tracked_source_clean"] = git("rev-parse", "HEAD") == head and not git("status", "--porcelain=v1")
        receipt["report_fresh"] = (launched_at is not None and NATIVE_REPORT.is_file() and
                                   NATIVE_REPORT.stat().st_mtime >= launched_at - 1)
        receipt["native_report"] = (json.loads(NATIVE_REPORT.read_text(encoding="utf8"))
                                    if receipt["report_fresh"] else None)
        report = receipt["native_report"] or {}
        receipt["private_outputs_verified"] = all((PRIVATE / n).is_file() and
                                                  (PRIVATE / n).stat().st_size > 0 for n in EXPECTED)
        receipt["ram_end_gib"] = round(memory_gib(), 3)
        receipt["disk_end_gib"] = round(disk_gib(), 3)
        receipt["status"] = ("HOLD_" + stop_reason if stop_reason else
                             "PRIVATE_PIE_MAP_STAGE_PASS_NOT_PLAYBACK_ACCEPTED"
                             if (receipt.get("child_exit_code") == 0 and
                                 receipt["protected_hashes_unchanged"] and
                                 receipt["tracked_source_clean"] and
                                 receipt["report_fresh"] and
                                 report.get("status") == "PRIVATE_V5_PIE_REVIEW_LEVEL_STAGED_NOT_PLAYED" and
                                 report.get("source_head") == head and
                                 receipt["private_outputs_verified"])
                             else "HOLD_PRIVATE_NATIVE_STAGE_EVIDENCE")
        save()
    return {key: value for key, value in receipt.items() if key != "native_report"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", action="store_true", required=True)
    parser.parse_args()
    try:
        result = execute()
    except BaseException as exc:
        print(json.dumps({"status": "HOLD_GUARDED_PRELAUNCH", "reason": str(exc)[:500]}, indent=2))
        return 4
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PRIVATE_PIE_MAP_STAGE_PASS_NOT_PLAYBACK_ACCEPTED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
