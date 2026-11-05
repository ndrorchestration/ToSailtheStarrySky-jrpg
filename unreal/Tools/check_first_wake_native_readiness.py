#!/usr/bin/env python3
"""Read-only Windows admission probe for PR #769's isolated Unreal review.

Does not launch Unreal, create receipts, modify INI/map files, touch SaveGames,
terminate processes, or grant native/art/release approval. HOLD exits nonzero.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

APPROVED_ROOT = "TSTSS_P0CombinedF6Objectives_20261104"
MAP_REPAIR_ROOT = "TSTSS_FirstWakeMapQARepair_20261105"
APPROVED_ROOTS = frozenset((APPROVED_ROOT, MAP_REPAIR_ROOT))
EXPECTED_MAP_SHA = "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80"
MAP_REL = "unreal/Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
VERSION_REL = "Engine/Build/Build.version"
ENGINE_EXES = ("Engine/Binaries/Win64/UnrealEditor.exe",
               "Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
NATIVE_NAMES = "unreal/Tools/Verify-Unreal.ps1"
SHA_RE = re.compile(r"^[a-fA-F0-9]{40}$")
MIN_FREE_DISK_GIB = 14.0
MIN_BUILD_RAM_GIB = 5.0
MIN_PIE_RAM_GIB = 6.5


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def capture(command: list[str], timeout: int = 20) -> str:
    run = subprocess.run(command, check=False, capture_output=True,
                         text=True, timeout=timeout)
    if run.returncode != 0:
        raise RuntimeError("Read-only command failed: " + command[0])
    return run.stdout.strip()


def telemetry() -> dict:
    # Process name and available RAM only: no process command line, no mutation.
    ps = (
        "$names=@(Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd',"
        "'LiveCodingConsole' -ErrorAction SilentlyContinue | "
        "Select-Object -ExpandProperty ProcessName);"
        "$os=Get-CimInstance Win32_OperatingSystem;"
        "[pscustomobject]@{active=@($names);"
        "free_gib=[math]::Round(($os.FreePhysicalMemory / 1048576),4)}"
        " | ConvertTo-Json -Compress"
    )
    raw = json.loads(capture(["powershell.exe", "-NoProfile", "-NonInteractive",
                              "-Command", ps], timeout=30))
    names = raw.get("active") or []
    return {"active": names if isinstance(names, list) else [names],
            "free_ram_gib": float(raw["free_gib"])}


def inspect(repo: Path, engine: Path, expected: str, phase: str) -> dict:
    """Collect evidence read-only. Error states fail closed in evaluate()."""
    found: dict = {"root_name": repo.name, "git_head": None, "git_clean": False,
                   "map_sha": None, "engine_version": None, "engine_exes": False,
                   "native_names": [], "save_files": [], "native_receipts": [],
                   "map_receipts": [], "active": None, "free_ram_gib": None,
                   "free_disk_gib": None, "errors": []}
    try:
        if repo.is_dir():
            actual_top = Path(capture(["git", "-C", str(repo),
                                       "rev-parse", "--show-toplevel"])).resolve()
            found["git_root_matches"] = actual_top == repo.resolve()
            found["git_head"] = capture(["git", "-C", str(repo), "rev-parse", "HEAD"])
            found["git_clean"] = not bool(capture(
                ["git", "-C", str(repo), "status", "--porcelain"]))
            original_map = repo / MAP_REL
            if original_map.is_file():
                found["map_sha"] = sha256(original_map)
            names_path = repo / NATIVE_NAMES
            if names_path.is_file():
                found["native_names"] = re.findall(
                    r"^\s*'(TSTSS\.[^']+)'",
                    names_path.read_text(encoding="utf-8"), re.M)
            save_dir = repo / "unreal/Saved/SaveGames"
            if save_dir.exists():
                found["save_files"] = [
                    f.name for f in save_dir.rglob("*.sav") if f.is_file()]
            evidence = repo / "unreal/Saved/MigrationEvidence"
            if evidence.is_dir():
                for folder in evidence.iterdir():
                    if (folder.is_dir() and folder.name.startswith(expected[:12] + "-") and
                            (folder / "head.txt").is_file() and
                            (folder / "head.txt").read_text(encoding="utf-8").strip() == expected and
                            (folder / "AutomationReport/index.json").is_file()):
                        found["native_receipts"].append(folder.name)
            map_evidence = repo / "unreal/Saved/NativePreludeMapQA"
            if map_evidence.is_dir():
                for file in map_evidence.glob("*.json"):
                    try:
                        record = json.loads(file.read_text(encoding="utf-8-sig"))
                        if record.get("source_sha") == expected:
                            found["map_receipts"].append(file.name)
                    except (ValueError, UnicodeError, OSError):
                        found["errors"].append("Unparseable native map receipt")
    except (OSError, RuntimeError, UnicodeError, subprocess.TimeoutExpired) as err:
        found["errors"].append("Git/source custody inspection failed: " + type(err).__name__)
    try:
        data = json.loads((engine / VERSION_REL).read_text(encoding="utf-8-sig"))
        found["engine_version"] = [
            data.get("MajorVersion"), data.get("MinorVersion"), data.get("PatchVersion")]
        found["engine_exes"] = all((engine / rel).is_file() for rel in ENGINE_EXES)
    except (OSError, ValueError, UnicodeError) as err:
        found["errors"].append("Engine version/paths unreadable: " + type(err).__name__)
    try:
        found.update(telemetry())
        found["free_disk_gib"] = round(shutil.disk_usage(repo).free / (1024**3), 4)
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as err:
        found["errors"].append("Machine resources unavailable: " + type(err).__name__)
    return found


def evaluate(found: dict, expected: str, phase: str) -> dict:
    reasons = list(found.get("errors") or [])
    if not SHA_RE.fullmatch(expected):
        reasons.append("Expected source SHA must contain 40 hex digits")
    if found.get("root_name") not in APPROVED_ROOTS or not found.get("git_root_matches"):
        reasons.append("Not the named, exact-root disposable PR769 worktree")
    if found.get("git_head") != expected or not found.get("git_clean"):
        reasons.append("HEAD or complete Git working tree differs from pinned source")
    if found.get("map_sha") != EXPECTED_MAP_SHA:
        reasons.append("Protected Prelude V2 map SHA-256 differs or is missing")
    if found.get("engine_version") != [5, 8, 4] or not found.get("engine_exes"):
        reasons.append("Installed Unreal Engine 5.8.4 files are not verified")
    names = found.get("native_names") or []
    if len(names) != 29 or len(set(names)) != 29:
        reasons.append("Required native automation inventory must be 29 distinct names")
    if found.get("save_files"):
        reasons.append("Isolated review SaveGame files already exist: never delete/overwrite")
    if found.get("active") is None or found["active"]:
        reasons.append("Unreal Editor/Live Coding process detection unavailable or active")
    needed_ram = MIN_PIE_RAM_GIB if phase == "pie" else MIN_BUILD_RAM_GIB
    if (found.get("free_ram_gib") is None or
            found["free_ram_gib"] < needed_ram):
        reasons.append(f"Available RAM below {needed_ram:g} GiB {phase} threshold")
    if (found.get("free_disk_gib") is None or
            found["free_disk_gib"] < MIN_FREE_DISK_GIB):
        reasons.append("Available C: space below 14 GiB")
    if phase == "pie" and (not found.get("native_receipts") or
                           not found.get("map_receipts")):
        reasons.append("Exact-head native automation and map receipt files missing; "
                       "each must also pass independent schema validation")
    return {
        "status": "HOLD" if reasons else "READ_ONLY_PREFLIGHT_PASS_NOT_NATIVE_EVIDENCE",
        "phase": phase,
        "source_sha": expected,
        "required_native_automations": 29,
        "active_process_names": found.get("active"),
        "available_ram_gib": found.get("free_ram_gib"),
        "available_disk_gib": found.get("free_disk_gib"),
        "protected_map_sha256": found.get("map_sha"),
        "existing_review_save_count": len(found.get("save_files") or []),
        "native_receipt_candidates": len(found.get("native_receipts") or []),
        "map_receipt_candidates": len(found.get("map_receipts") or []),
        "reasons": reasons,
        "unreal_started": False,
        "native_build_or_tests_executed": False,
        "player_save_changed": False,
        "receipt_files_written": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--engine-root", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--phase", choices=["build", "pie"], required=True)
    args = parser.parse_args()
    found = inspect(args.repo.resolve(), args.engine_root.resolve(),
                    args.expected_head, args.phase)
    report = evaluate(found, args.expected_head, args.phase)
    print(json.dumps(report, indent=2))
    return 0 if report["status"].startswith("READ_ONLY_PREFLIGHT_PASS") else 2


if __name__ == "__main__":
    sys.exit(main())
