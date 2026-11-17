"""Host-side, reversible admission + execution for PRIVATE Ender IK review.

Usage (Neontic only):
  python unreal/Tools/run_ender_private_retarget_native.py --audit
  TSTSS_PRIVATE_IK_CREATE=1 python ... --create-rigs
The second command is opt-in and is only eligible after a successful native
--audit on the exact current head. Nothing runs in the background.

Only the process spawned by this script can be stopped by its watchdog.
Unrelated Unreal/editor/user processes block admission; never kill them.
"""
import argparse
import ctypes
import datetime
import hashlib
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
UPROJECT = PROJECT / "ToSailTheStarrySky.uproject"
EDITOR = Path(
    r"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
)
TOOLS = PROJECT / "Tools"
LOCAL_BRANCH = "review/ender853-local-native-review-20261117"
VALIDATED_ANCESTOR = "cc7548ba53705f5f6d0fd331cf89d32d138a8e0f"
EVIDENCE = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate"
STARTUP_GATE = EVIDENCE / "startup_gate.json"
PROTECTED = (
    UPROJECT,
    PROJECT / "Config/DefaultEngine.ini",
    PROJECT / "Config/DefaultInput.ini",
)
STARTUP_RAM_GIB = 6.5
STARTUP_DISK_GIB = 16.5
RUNTIME_RAM_FLOOR_GIB = 2.5
RUNTIME_DISK_FLOOR_GIB = 14.3

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def require(ok, code):
    if not ok:
        raise RuntimeError("HOLD_" + code)

def git(*args):
    run = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, timeout=20, check=False,
    )
    require(run.returncode == 0, "GIT_" + "_".join(args[:2]).upper())
    return run.stdout.strip()

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def ram_gib():
    class Memory(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
            ("total", ctypes.c_ulonglong), ("available", ctypes.c_ulonglong),
            ("page_total", ctypes.c_ulonglong),
            ("page_available", ctypes.c_ulonglong),
            ("virtual_total", ctypes.c_ulonglong),
            ("virtual_available", ctypes.c_ulonglong),
            ("extended", ctypes.c_ulonglong),
        ]
    m = Memory()
    m.length = ctypes.sizeof(m)
    require(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)),
            "RAM_PROBE_FAILED")
    return m.available / 2**30

def disk_gib():
    return shutil.disk_usage("C:\\").free / 2**30

def ue_processes():
    import csv
    import io
    result = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"],
        capture_output=True, text=True, timeout=15, check=True,
    )
    names = {row[0].strip().lower() for row in
             csv.reader(io.StringIO(result.stdout)) if row}
    return names.intersection({
        "unrealeditor.exe", "unrealeditor-cmd.exe", "unrealbuildtool.exe",
        "livecodingconsole.exe", "shadercompileworker.exe",
    })

def signed_native_evidence(mode):
    return EVIDENCE / ("prerequisite_report.json" if mode == "audit"
                       else "rig_build_receipt.json")

def preflight(mode):
    require(sys.platform == "win32", "WINDOWS_REQUIRED")
    require(UPROJECT.is_file() and EDITOR.is_file(), "UNREAL_NOT_INSTALLED")
    require(git("branch", "--show-current") == LOCAL_BRANCH,
            "WRONG_WORKTREE_BRANCH")
    head = git("rev-parse", "HEAD")
    require(len(head) == 40, "INVALID_HEAD")
    ancestor = subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor",
         VALIDATED_ANCESTOR, head], timeout=20, check=False
    )
    require(ancestor.returncode == 0, "NATIVE_ANCESTOR_MISSING")
    require(not git("status", "--porcelain=v1", "--untracked-files=no"),
            "TRACKED_WORKTREE_DIRTY")
    require(not ue_processes(), "OTHER_UNREAL_PROCESS_ACTIVE")
    require(ram_gib() >= STARTUP_RAM_GIB, "STARTUP_RAM_RESERVE")
    require(disk_gib() >= STARTUP_DISK_GIB, "STARTUP_DISK_RESERVE")
    for file_path in PROTECTED:
        require(file_path.is_file(), "PROTECTED_FILE_MISSING")
    for script in (
        TOOLS / "inspect_ender_manny_retarget_prereqs.py",
        TOOLS / "build_private_ender_ik_retargeter.py",
    ):
        require(script.is_file(), "TOOLS_MISSING")
    if mode == "create-rigs":
        require(os.environ.get("TSTSS_PRIVATE_IK_CREATE") == "1",
                "NO_EXPLICIT_CREATE_OPT_IN")
        prior = signed_native_evidence("audit")
        require(prior.is_file(), "MISSING_PREVIOUS_AUDIT")
        data = json.loads(prior.read_text(encoding="utf8"))
        require(data.get("source_head") == head and
                data.get("status") ==
                "NATIVE_RETARGET_INPUTS_VALIDATED_NOT_RETARGETED",
                "PRIOR_NATIVE_AUDIT_NOT_ACCEPTED")
        created = datetime.datetime.fromisoformat(data["created_utc"])
        require(created.tzinfo is not None and
                abs((datetime.datetime.now(datetime.timezone.utc) -
                     created).total_seconds()) < 6 * 3600,
                "PRIOR_AUDIT_STALE")
        output = "unreal/Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/"
        for asset in (
            "IK_Manny_EnderReview_NONCANONICAL.uasset",
            "IK_Genesis9_EnderReview_NONCANONICAL.uasset",
            "RTG_MannyToEnder_NONCANONICAL.uasset",
        ):
            check = subprocess.run(
                ["git", "-C", str(ROOT), "check-ignore", "-q", output + asset],
                timeout=15, check=False,
            )
            require(check.returncode == 0, "PRIVATE_OUTPUT_NOT_IGNORED")
            require(not (PROJECT / "Content/TSTSS/Review/Characters/"
                         "EnderRetarget_NONCANONICAL" / asset).exists(),
                    "REVIEW_RIG_ALREADY_PRESENT")
    return head

def run_native(mode):
    head = preflight(mode)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    run_id = str(uuid.uuid4())
    record_dir = EVIDENCE / "HostReceipts" / run_id
    record_dir.mkdir(parents=True, exist_ok=False)
    gate = {
        "status": "HOST_ADMITTED", "run_id": run_id, "mode": mode,
        "source_head": head, "utc": utc_now(),
        "ram_start_gib": round(ram_gib(), 3),
        "disk_start_gib": round(disk_gib(), 3),
    }
    require(gate["ram_start_gib"] >= STARTUP_RAM_GIB and
            gate["disk_start_gib"] >= STARTUP_DISK_GIB,
            "SECOND_STARTUP_RESOURCE_CHECK")
    STARTUP_GATE.write_text(json.dumps(gate, indent=2), encoding="utf8")
    script = TOOLS / (
        "inspect_ender_manny_retarget_prereqs.py" if mode == "audit"
        else "build_private_ender_ik_retargeter.py"
    )
    before = {str(path): sha(path) for path in PROTECTED}
    modes = {path: path.stat().st_mode for path in PROTECTED}
    # Guard against Unreal's observed automatic DefaultEngine/Input.ini rewrites.
    # Always restore original permission flags, never overwrite changed CONTENT.
    prepared_readonly = []
    cmd = [
        str(EDITOR), str(UPROJECT), "-nullrhi", "-NoSound", "-unattended",
        "-nosplash", "-nop4", "-ExecCmds=py " + str(script),
        "-abslog=" + str(record_dir / "engine.log"),
    ]
    env = os.environ.copy()
    env["TSTSS_PRIVATE_IK_RUN_ID"] = run_id
    if mode != "create-rigs":
        env.pop("TSTSS_PRIVATE_IK_CREATE", None)
    receipt = {
        "status": "STARTING", "mode": mode, "run_id": run_id,
        "source_head": head, "admission": gate,
        "protected_hashes_before": before,
        "project_data_mutation_authorized": False,
        "art_approved": False, "native_animation_verified": False,
        "stdout": str(record_dir / "stdout.log"),
    }
    receipt_path = record_dir / "host_receipt.json"
    def save():
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf8")
    owned_child = None
    stop_reason = None
    launched_at = None
    try:
        # Keep permission changes inside the try/finally. Even if a single
        # os.chmod or Popen fails, restore every file already touched.
        for path in PROTECTED:
            os.chmod(path, stat.S_IREAD)
            prepared_readonly.append(path)
        with (record_dir / "stdout.log").open("w", encoding="utf8") as log:
            launched_at = time.time()
            owned_child = subprocess.Popen(
                cmd, cwd=str(PROJECT), stdin=subprocess.DEVNULL,
                stdout=log, stderr=subprocess.STDOUT, env=env,
            )
            receipt["owned_pid"] = owned_child.pid
            receipt["status"] = "RUNNING"
            save()
            start = time.monotonic()
            while owned_child.poll() is None:
                elapsed = time.monotonic() - start
                receipt.update(
                    elapsed_s=round(elapsed, 1),
                    disk_last_gib=round(disk_gib(), 3),
                    ram_last_gib=round(ram_gib(), 3),
                )
                save()
                if receipt["disk_last_gib"] < RUNTIME_DISK_FLOOR_GIB:
                    stop_reason = "DISK_SAFETY_STOP"
                elif receipt["ram_last_gib"] < RUNTIME_RAM_FLOOR_GIB:
                    stop_reason = "RAM_SAFETY_STOP"
                elif elapsed > (240 if mode == "create-rigs" else 180):
                    stop_reason = "NATIVE_TIMEOUT"
                if stop_reason:
                    if owned_child.poll() is None:
                        # This PID is exclusively the subprocess we created.
                        subprocess.run(
                            ["taskkill", "/F", "/T", "/PID",
                             str(owned_child.pid)],
                            capture_output=True, timeout=25, check=False,
                        )
                    owned_child.wait(timeout=25)
                    break
                time.sleep(2)
        receipt["exit_code"] = owned_child.returncode
    finally:
        for path in reversed(prepared_readonly):
            os.chmod(path, modes[path])
        receipt["protected_unchanged"] = all(
            Path(path).is_file() and sha(Path(path)) == old
            for path, old in before.items()
        )
        receipt["tracked_clean"] = not bool(
            git("status", "--porcelain=v1", "--untracked-files=no")
        )
        receipt["head_unchanged"] = git("rev-parse", "HEAD") == head
        receipt["disk_end_gib"] = round(disk_gib(), 3)
        receipt["ram_end_gib"] = round(ram_gib(), 3)
        artifact = signed_native_evidence(mode)
        receipt["native_report_fresh"] = bool(
            launched_at is not None and artifact.is_file() and
            artifact.stat().st_mtime >= launched_at - 1.0
        )
        receipt["native_report"] = (
            json.loads(artifact.read_text(encoding="utf8"))
            if receipt["native_report_fresh"] else None
        )
        wanted_status = (
            "NATIVE_RETARGET_INPUTS_VALIDATED_NOT_RETARGETED"
            if mode == "audit" else
            "PRIVATE_IK_RIGS_CREATED_REVIEW_ONLY_NO_ANIMATION"
        )
        report = receipt["native_report"] or {}
        saved = report.get("saved_assets", [])
        names = (
            "IK_Manny_EnderReview_NONCANONICAL",
            "IK_Genesis9_EnderReview_NONCANONICAL",
            "RTG_MannyToEnder_NONCANONICAL",
        )
        review_folder = PROJECT / (
            "Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
        )
        rig_files_valid = (
            mode == "audit" or (
                isinstance(saved, list) and len(saved) == len(names) and
                sorted(saved) == sorted([
                    "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/"
                    + name + "." + name for name in names
                ]) and
                all(
                    (review_folder / (name + ".uasset")).is_file() and
                    (review_folder / (name + ".uasset")).stat().st_size > 0
                    for name in names
                )
            )
        )
        receipt["rig_files_verified"] = rig_files_valid
        proof_ok = all((
            receipt.get("exit_code") == 0,
            receipt["protected_unchanged"],
            receipt["tracked_clean"],
            receipt["head_unchanged"],
            receipt["native_report_fresh"],
            report.get("status") == wanted_status,
            report.get("source_head") == head,
            rig_files_valid,
        ))
        receipt["status"] = (
            "HOLD_" + stop_reason if stop_reason else
            "NATIVE_" + mode.upper().replace("-", "_") + "_PASS"
            if proof_ok else "HOLD_NARROW_NATIVE_EVIDENCE"
        )
        save()
    print(json.dumps({
        "status": receipt["status"], "source_head": head,
        "run_id": run_id, "log": str(receipt_path),
        "disk_end_gib": receipt["disk_end_gib"],
        "ram_end_gib": receipt["ram_end_gib"],
        "protected_unchanged": receipt["protected_unchanged"],
        "tracked_clean": receipt["tracked_clean"],
        "native_status": (receipt["native_report"] or {}).get("status"),
    }, indent=2), flush=True)
    return receipt["status"].endswith("_PASS")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--audit", action="store_true")
    choice.add_argument("--create-rigs", action="store_true")
    args = parser.parse_args()
    try:
        sys.exit(0 if run_native(
            "audit" if args.audit else "create-rigs") else 3)
    except Exception as exc:
        print("HOLD_GUARDED_NATIVE_HOST: " + str(exc), file=sys.stderr)
        sys.exit(4)
