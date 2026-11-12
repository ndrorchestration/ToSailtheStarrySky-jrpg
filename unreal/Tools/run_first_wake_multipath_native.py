#!/usr/bin/env python3
"""Host-side guarded UE 5.8.4 one-process importer for First Wake shore review.

--check never launches Unreal. --stage requires exact 40-char HEAD, zero
pre-existing Editor/LiveCoding, >=6.5 GiB free RAM, >=14 GiB disk and a clean
isolated source worktree. Only this launcher's child may be terminated.
"""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import time

import stage_first_wake_multipath_shore as stage

ROOT = stage.ROOT
PROJECT = stage.PROJECT
EDITOR = Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe")
LOG_DIR = PROJECT / "Saved/MultipathV1"
LOG = LOG_DIR / "shore_unreal.log"
STDOUT = LOG_DIR / "shore_stdout.log"
PREPARE_LOG = LOG_DIR / "shore_prepare_unreal.log"
PREPARE_STDOUT = LOG_DIR / "shore_prepare_stdout.log"
HOST_RECEIPT = LOG_DIR / "shore_host_receipt.json"
MIN_FREE_RAM_GIB = 6.5
MIN_FREE_DISK_GIB = 14.0
MAX_BUILD_SECONDS = 480
ACTIVE_NAMES = ("unrealeditor.exe", "unrealeditor-cmd.exe", "livecodingconsole.exe")

class MemoryStatus(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

def free_ram_gib() -> float:
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise RuntimeError("HOLD: cannot read physical RAM")
    return status.ullAvailPhys / (1024 ** 3)

def current_editor_processes() -> list[str]:
    output = subprocess.run(["tasklist", "/FO", "CSV"], check=True,
                            capture_output=True, text=True, timeout=20).stdout.lower()
    return [name for name in ACTIVE_NAMES if name in output]

def current_ubt_build_running() -> bool:
    """Refuse another agent's UBT before spawning our review Editor child.

    Returns only busy/idle; does not log other agents' command lines.
    """
    query = (
        "$p=@(Get-CimInstance Win32_Process "
        "-Filter \"Name='cmd.exe' OR Name='dotnet.exe' OR Name='UnrealBuildTool.exe'\" "
        "-ErrorAction Stop | Where-Object { $_.CommandLine -match "
        "'(?i)(?:UnrealBuildTool(?:\\.dll|\\.exe)?|[\\\\/]Build\\.bat)' });"
        "if($p.Count -gt 0){'BUSY'}else{'IDLE'}"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", query],
        capture_output=True, text=True, timeout=20, check=False,
    )
    status = result.stdout.strip()
    if result.returncode != 0 or status not in ("BUSY", "IDLE"):
        raise RuntimeError("HOLD: unable to reliably inspect concurrent Unreal native builds")
    return status == "BUSY"


def required_engine_version() -> None:
    version_file = Path("C:/Program Files/Epic Games/UE_5.8/Engine/Build/Build.version")
    if not EDITOR.is_file() or not version_file.is_file():
        raise RuntimeError("HOLD: native UE5.8.4 installation absent")
    data = json.loads(version_file.read_text(encoding="utf-8"))
    if [data.get(k) for k in ("MajorVersion", "MinorVersion", "PatchVersion")] != [5, 8, 4]:
        raise RuntimeError("HOLD: wrong installed Unreal Engine version")

def verified_native_receipt(expected_head: str) -> dict:
    """Accept only a full same-head 36-test real native report + generated gate."""
    evidence = PROJECT / "Saved/MigrationEvidence"
    required_source = (PROJECT / "Tools/Verify-Unreal.ps1").read_text(encoding="utf-8")
    required = re.findall(r"^\s*'(TSTSS\.[^']+)'", required_source, re.M)
    if len(required) != 36 or len(set(required)) != 36:
        raise RuntimeError("HOLD: full native test inventory drift")
    if not evidence.is_dir():
        raise RuntimeError("HOLD: no native UHT/Win64/36-test receipt at this head")
    for folder in sorted(evidence.iterdir(), reverse=True):
        receipt_file = folder / "verified-native.json"
        report_file = folder / "AutomationReport/index.json"
        head_file = folder / "head.txt"
        if not (receipt_file.is_file() and report_file.is_file() and head_file.is_file()):
            continue
        try:
            receipt = json.loads(receipt_file.read_text(encoding="utf-8-sig"))
            report = json.loads(report_file.read_text(encoding="utf-8-sig"))
            if (receipt.get("status") != "WIN64_EDITOR_BUILD_AND_NATIVE_AUTOMATIONS_PASS_CLEAN_SOURCE"
                    or receipt.get("source_sha") != expected_head.lower()
                    or head_file.read_text(encoding="utf-8-sig").strip().lower() != expected_head.lower()
                    or receipt.get("unreal_version") != "5.8.4"
                    or type(receipt.get("required_native_tests")) is not int
                    or receipt["required_native_tests"] != 36
                    or receipt.get("pie_player_input") != "NOT_TESTED"
                    or receipt.get("visual_approval") != "NOT_TESTED"
                    or receipt.get("report_sha256") != checksum(report_file)):
                continue
            if not all(type(report.get(field)) is int for field in ("succeeded", "failed", "notRun")):
                continue
            if report["failed"] != 0 or report["notRun"] != 0 or report["succeeded"] < 36:
                continue
            tests = report.get("tests")
            if not isinstance(tests, list) or len(tests) < 36:
                continue
            # Keep this secondary consumer equivalent to the authoritative
            # PowerShell validator: EVERY per-test row must be a successful,
            # named, unique result and the total must match exactly.
            if not all(isinstance(entry, dict)
                       and isinstance(entry.get("fullTestPath"), str)
                       and bool(entry["fullTestPath"].strip())
                       and entry.get("state") == "Success"
                       for entry in tests):
                continue
            names = [entry["fullTestPath"] for entry in tests]
            if len(names) != len(set(names)) or report["succeeded"] != len(tests):
                continue
            if not set(required).issubset(set(names)):
                continue
            if not ((folder / "build.log").is_file() and (folder / "automation.log").is_file()):
                continue
            return {"receipt": str(receipt_file), "automation_report_sha256": checksum(report_file)}
        except (ValueError, KeyError, TypeError, OSError):
            continue
    raise RuntimeError("HOLD: no accepted exact-head native 36-test evidence; do not stage UE visual actors")

def prerequisites(expected_head: str) -> dict:
    if sys.platform != "win32":
        raise RuntimeError("HOLD: this guarded native runner is Windows-only")
    if not re.fullmatch(r"[a-fA-F0-9]{40}", expected_head):
        raise RuntimeError("HOLD: explicit exact 40-hex integration HEAD is mandatory")
    if ROOT.name != stage.WORKTREE or stage.git("branch", "--show-current") != stage.BRANCH:
        raise RuntimeError("HOLD: unrelated source checkout or branch")
    if (stage.git("rev-parse", "HEAD").lower() != expected_head.lower()
            or stage.git("status", "--porcelain")):
        raise RuntimeError("HOLD: stale exact-head or dirty source")
    required_engine_version()
    if not (PROJECT / "ToSailTheStarrySky.uproject").is_file():
        raise RuntimeError("HOLD: UE project file missing")
    for file in (stage.SAVED_RECEIPT, stage.PREPARE_RECEIPT, HOST_RECEIPT,
                 PREPARE_LOG, PREPARE_STDOUT, LOG, STDOUT,
                 PROJECT / "Content/TSTSS/Review/MultipathV1"):
        if file.exists():
            raise RuntimeError("HOLD: previously created output must not be overwritten: " + file.name)
    if (PROJECT / "Saved/SaveGames").is_dir() and list((PROJECT / "Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: preexisting saves cannot be altered")
    processes = current_editor_processes()
    if processes:
        raise RuntimeError("HOLD: concurrent UE/LiveCoding activity: " + ", ".join(processes))
    if current_ubt_build_running():
        raise RuntimeError("HOLD: another agent's UnrealBuildTool/Build.bat is active")
    ram = free_ram_gib()
    disk = shutil.disk_usage(ROOT).free / (1024 ** 3)
    if ram < MIN_FREE_RAM_GIB or disk < MIN_FREE_DISK_GIB:
        raise RuntimeError("HOLD: RAM/disk below graphical stage threshold: %.2f / %.2f GiB" % (ram, disk))
    plan = stage.evidence_plan()
    if plan["native_staged"] or plan["PIE_verified"] or plan["visual_approved"]:
        raise RuntimeError("HOLD: source plan already claims unsupported authority")
    native_proof = verified_native_receipt(expected_head)
    return {"status": "HOST_PREFLIGHT_PASS_NO_UNREAL_LAUNCH",
            "native_proof": native_proof,
            "exact_head": expected_head.lower(), "free_ram_gib": round(ram, 3),
            "free_disk_gib": round(disk, 3), "source_sha256": plan["source_sha256"],
            "engine": plan["engine"], "review_map": plan["new_map"]}

def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stage_native(expected_head: str) -> dict:
    """Two separate UE child processes: prepare the map, THEN compose actors.

    UE 5.8.4 can fatally leak a newly duplicated standalone UWorld when
    duplicate_asset and load_map run in the same Python/Editor process.
    Each phase must have a separate child process and independent log sentinel.
    """
    report = prerequisites(expected_head)
    config_paths = [PROJECT / "Config/DefaultEngine.ini", PROJECT / "Config/DefaultInput.ini"]
    config_hashes = {p.name: checksum(p) for p in config_paths}
    config_modes = {p.name: p.stat().st_mode for p in config_paths}
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        for p in config_paths:
            os.chmod(p, stat.S_IREAD)
        for phase in ("prepare", "compose"):
            if phase == "compose":
                # Phase one must have exited cleanly and fully materialized a
                # unique map package. No previous UWorld reference survives.
                if not stage.PREPARE_RECEIPT.is_file():
                    raise RuntimeError("HOLD: no native first-process preparation receipt")
                if not (PROJECT / "Content/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review.umap").is_file():
                    raise RuntimeError("HOLD: no saved review map from preparation")
                if current_editor_processes() or current_ubt_build_running():
                    raise RuntimeError("HOLD: other Unreal process appeared before composition")
                ram = free_ram_gib()
                disk = shutil.disk_usage(ROOT).free / (1024 ** 3)
                if ram < MIN_FREE_RAM_GIB or disk < MIN_FREE_DISK_GIB:
                    raise RuntimeError("HOLD: insufficient post-preparation RAM/disk %.2f / %.2f GiB" % (ram, disk))
                if stage.git("rev-parse", "HEAD").lower() != expected_head.lower():
                    raise RuntimeError("HOLD: source HEAD moved before composition")
                prepared = json.loads(stage.PREPARE_RECEIPT.read_text(encoding="utf-8"))
                map_file = PROJECT / "Content/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review.umap"
                if (prepared.get("status") != "REVIEW_ASSETS_AND_BASE_MAP_PREPARED_NOT_PIE"
                        or prepared.get("source_head") != expected_head.lower()
                        or prepared.get("base_map_sha256") != checksum(map_file)
                        or prepared.get("prepared_object_meshes") != 22
                        or prepared.get("PIE_verified") is not False):
                    raise RuntimeError("HOLD: first-process receipt does not authorize composition")
            env = os.environ.copy()
            env["TSTSS_MP_EXPECTED_HEAD"] = expected_head.lower()
            env["TSTSS_MP_STAGE_EXPLICIT"] = "1"
            env["TSTSS_MP_PHASE"] = phase
            current_log = PREPARE_LOG if phase == "prepare" else LOG
            current_stdout = PREPARE_STDOUT if phase == "prepare" else STDOUT
            command = [
                str(EDITOR), str(PROJECT / "ToSailTheStarrySky.uproject"),
                "-ExecutePythonScript=" + str(Path(stage.__file__).resolve()),
                "-NullRHI", "-unattended", "-nop4", "-NoSplash", "-NoSound",
                "-stdout", "-FullStdOutLogOutput", "-abslog=" + str(current_log),
            ]
            with current_stdout.open("x", encoding="utf-8") as stream:
                child = subprocess.Popen(command, cwd=str(ROOT), env=env,
                                         stdin=subprocess.DEVNULL, stdout=stream,
                                         stderr=subprocess.STDOUT,
                                         creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
                report[phase + "_child_pid"] = child.pid
                stop_reason = None
                started = time.monotonic()
                while child.poll() is None:
                    if time.monotonic() - started > MAX_BUILD_SECONDS:
                        stop_reason = "Own Unreal " + phase + " process exceeded time cap"
                        break
                    if free_ram_gib() < 0.85:
                        stop_reason = "Own Unreal " + phase + " process exceeded free-RAM floor"
                        break
                    time.sleep(2)
                if stop_reason:
                    child.terminate()
                try:
                    child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=10)
            report[phase + "_native_exit_code"] = child.returncode
            if stop_reason or child.returncode != 0:
                raise RuntimeError(stop_reason or "Native Unreal " + phase + " process returned failure")
            sentinel = ("TSTSS_MULTIPATH_SHORE_PREPARED_NOT_PIE"
                        if phase == "prepare" else "TSTSS_MULTIPATH_SHORE_NATIVE_SAVED_NOT_PIE")
            if (not current_log.is_file() or
                    sentinel not in current_log.read_text(encoding="utf-8", errors="replace")):
                raise RuntimeError("HOLD: " + phase + " native sentinel missing")
        if not stage.SAVED_RECEIPT.is_file():
            raise RuntimeError("HOLD: separate composition process produced no native stage receipt")
        receipt = json.loads(stage.SAVED_RECEIPT.read_text(encoding="utf-8"))
        if (receipt.get("status") != "NATIVE_REVIEW_MAP_SAVED_NOT_PIE_OR_VISUAL_APPROVED"
                or receipt.get("source_head") != expected_head.lower()
                or receipt.get("native_staged") is not True
                or receipt.get("PIE_verified") is not False
                or receipt.get("visual_approved") is not False):
            raise RuntimeError("HOLD: native final receipt has unsafe status")
        file = PROJECT / "Content/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review.umap"
        if not file.is_file() or checksum(file) != receipt.get("new_map_sha256"):
            raise RuntimeError("HOLD: independently readable map/hash missing")
        if checksum(stage.MAP_FILE) != report["source_sha256"]:
            raise RuntimeError("HOLD: original source map changed")
        report["status"] = "NATIVE_SAVED_PENDING_INDEPENDENT_EDITOR_AND_PIE_READBACK"
        report["new_map_sha256"] = checksum(file)
    except Exception as exc:
        report["status"] = "NATIVE_STAGE_HOLD"
        report["error"] = str(exc)
    finally:
        for p in config_paths:
            os.chmod(p, config_modes[p.name])
        report["configs_unchanged"] = all(checksum(p) == config_hashes[p.name] for p in config_paths)
        report["source_head_unchanged"] = stage.git("rev-parse", "HEAD").lower() == expected_head.lower()
        report["original_shore_map_unchanged"] = checksum(stage.MAP_FILE) == report["source_sha256"]
        with HOST_RECEIPT.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    return report

def main() -> int:
    parser = argparse.ArgumentParser()
    gate = parser.add_mutually_exclusive_group(required=True)
    gate.add_argument("--check", action="store_true")
    gate.add_argument("--stage", action="store_true")
    parser.add_argument("--expected-head", required=True)
    args = parser.parse_args()
    try:
        report = stage_native(args.expected_head) if args.stage else prerequisites(args.expected_head)
    except Exception as exc:
        report = {"status": "HOST_PREFLIGHT_HOLD_NO_UNREAL_LAUNCH", "reason": str(exc)}
    print(json.dumps(report, indent=2))
    return 0 if report["status"] in (
        "HOST_PREFLIGHT_PASS_NO_UNREAL_LAUNCH",
        "NATIVE_SAVED_PENDING_INDEPENDENT_EDITOR_AND_PIE_READBACK",
    ) else 2

if __name__ == "__main__":
    raise SystemExit(main())
