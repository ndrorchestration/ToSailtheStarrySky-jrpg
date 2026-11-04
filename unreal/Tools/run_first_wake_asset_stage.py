"""Finite, resource-guarded native level staging in one disposable UE 5.8.4 Editor.

No production checkout, player SaveGame, or existing Editor process is touched.
The named full Editor is launched with NullRHI: no gameplay or GPU verification.
"""
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
UPROJECT = PROJECT / "ToSailTheStarrySky.uproject"
EDITOR = Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe")
SCRIPT = Path(__file__).with_name("stage_first_wake_asset_scene.py")
OUTPUT = PROJECT / "Saved/AssetAssemblyEvidence"
NATIVE = OUTPUT / "first_wake_asset_scene_native_20261104.json"
HOST = OUTPUT / "host_asset_stage_20261104.json"
LOG = OUTPUT / "first_wake_asset_stage_20261104.log"
BASE = PROJECT / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
EXPECTED_SHA = "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80"

ASSETS = (
    ("ship", "TSTSS/Review/ShipArt/CinematicV4/AureateWake_SharedExteriorTrim_V4_REVIEW/StaticMeshes/AureateWake_SharedExteriorTrim_V4_REVIEW.uasset"),
    ("ship", "TSTSS/Review/ShipArt/WingCinematicCandidate_20261103/AureateWake_Wing_Lookdev/StaticMeshes/AureateWake_Wing_Lookdev.uasset"),
    ("ship", "TSTSS/Review/ShipArt/CoupledHabitation_20261104/AureateWake_CoupledBridge_Geodesic_REVIEW/StaticMeshes/AureateWake_CoupledBridge_Geodesic_REVIEW.uasset"),
    ("ship", "TSTSS/Review/ShipArt/CoupledHabitation_20261104/AureateWake_CurvedLivingQuarters_REVIEW/StaticMeshes/AureateWake_CurvedLivingQuarters_REVIEW.uasset"),
    ("cast", "ArtLookdev/Characters/Ionia/Ionia/StaticMeshes/Ionia.uasset"),
    ("cast", "ArtLookdev/Characters/EnderFidelityV2/Ender_ender_fidelity_v2/StaticMeshes/Ender_ender_fidelity_v2.uasset"),
)
SHIP = Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103/AureateCinematicV4Sandbox/Content")
CAST = Path("C:/TSTSS_CastAllSandbox_20261101/Content")


class MemoryStatus(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def free_gib():
    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("Windows RAM status inaccessible")
    return status.ullAvailPhys / (1024 ** 3)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if sys.platform != "win32" or ROOT.name != "TSTSS_AssetAssembly_20261104":
        raise RuntimeError("Only the isolated Windows asset worktree is authorized")
    if not UPROJECT.is_file() or not EDITOR.is_file() or not SCRIPT.is_file():
        raise FileNotFoundError("UE project, installed 5.8 Editor or stage source absent")
    version = json.loads((EDITOR.parents[2] / "Build/Build.version").read_text())
    if (version["MajorVersion"], version["MinorVersion"], version["PatchVersion"]) != (5, 8, 4):
        raise RuntimeError("Exact installed Unreal 5.8.4 required")
    if any(p.exists() for p in (NATIVE, HOST, LOG)):
        raise FileExistsError("Earlier native attempt exists; no silent retry or overwrite")
    if not BASE.is_file() or sha(BASE) != EXPECTED_SHA:
        raise RuntimeError("Original V2 map digest mismatch")
    if list((PROJECT / "Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("Protected player SaveGame exists in isolated project")
    if free_gib() < 5.0 or shutil.disk_usage(ROOT).free < 14 * 1024**3:
        raise RuntimeError("Native map stage requires >=5 GiB available RAM and >=14 GiB free disk")
    running = subprocess.run(
        ["tasklist", "/FO", "CSV"], capture_output=True, text=True, check=True).stdout.lower()
    if any(name in running for name in ("unrealeditor.exe", "unrealeditor-cmd.exe", "livecodingconsole.exe")):
        raise RuntimeError("Another Unreal Editor is active; no concurrent stage")
    fingerprints = {}
    for group, relative in ASSETS:
        source = (SHIP if group == "ship" else CAST) / relative
        target = PROJECT / "Content" / relative
        if not source.is_file() or not target.is_file() or sha(source) != sha(target):
            raise RuntimeError("Missing/drifted imported native asset: " + relative)
        fingerprints[relative] = sha(target)
    before_sha = sha(BASE)
    configs = [PROJECT / "Config/DefaultEngine.ini", PROJECT / "Config/DefaultInput.ini"]
    if any(not f.is_file() or not os.access(f, os.W_OK) or not f.stat().st_mode & stat.S_IWRITE for f in configs):
        raise RuntimeError("Config files are already write-protected; refuse to adopt state")
    cfg_shas = {p.name: sha(p) for p in configs}
    source_head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    if subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"], text=True).strip():
        raise RuntimeError("Tracked source is dirty before native staging")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    state = {"status": "NATIVE_NOT_STARTED", "source_head": source_head,
             "native_asset_sha256": fingerprints, "base_map_sha256": before_sha,
             "nullrhi": True, "pie_verified": False, "gpu_rendered": False,
             "production_art_approved": False, "starbourne_unlocked": False}
    proc = None
    try:
        for f in configs:
            os.chmod(f, stat.S_IREAD)
        args = [str(EDITOR), str(UPROJECT), "-ExecutePythonScript=" + str(SCRIPT),
                "-NullRHI", "-unattended", "-nop4", "-NoSplash", "-NoSound",
                "-stdout", "-FullStdOutLogOutput"]
        with LOG.open("x", encoding="utf-8") as log:
            proc = subprocess.Popen(
                args, stdout=log, stderr=subprocess.STDOUT,
                cwd=str(ROOT), stdin=subprocess.DEVNULL,
                creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            state["pid"] = proc.pid
            print("ASSET_NATIVE_EDITOR_STARTED", proc.pid, "RAM", round(free_gib(), 2), flush=True)
            start = time.monotonic()
            while proc.poll() is None:
                elapsed = time.monotonic() - start
                available = free_gib()
                if elapsed > 210 or available < 0.85:
                    state["status"] = "NATIVE_CHILD_TERMINATED_RESOURCE_GUARD"
                    proc.terminate()
                    break
                if int(elapsed) % 20 == 0:
                    print("ASSET_NATIVE_PROGRESS", round(elapsed), "RAM", round(available, 2), flush=True)
                time.sleep(2)
            try:
                result = proc.wait(timeout=12)
            except subprocess.TimeoutExpired:
                proc.kill()
                result = proc.wait(timeout=5)
            state["editor_exit_code"] = result
        if state["status"] == "NATIVE_CHILD_TERMINATED_RESOURCE_GUARD":
            raise RuntimeError("Launched Editor stopped by independent resource watchdog")
        if state["editor_exit_code"] != 0:
            raise RuntimeError("Full Unreal Editor failed: exit " + str(state["editor_exit_code"]))
        native = json.loads(NATIVE.read_text(encoding="utf-8"))
        if native.get("status") != "NATIVE_ASSET_WORLD_SAVED_AND_RELOADED_NOT_PIE":
            raise RuntimeError("Native scene receipt absent or failed validation")
        log_text = LOG.read_text(encoding="utf-8", errors="replace")
        if "TSTSS_FIRST_WAKE_ASSET_ASSEMBLY_NATIVE_SAVE_RELOAD_PASS" not in log_text:
            raise RuntimeError("Actual full Editor PASS sentinel absent")
        state.update({"status": "NATIVE_ASSET_WORLD_SAVED_RELOADED_NOT_PIE",
                      "native_receipt_sha256": sha(NATIVE),
                      "new_map_sha256": native["new_map_sha256"],
                      "new_map_package": native["new_map_package"]})
    except Exception as exc:
        state["status"] = "NATIVE_ASSET_STAGE_HOLD"
        state["error"] = str(exc)
        print("ASSET_NATIVE_HOLD", exc, flush=True)
    finally:
        for f in configs:
            os.chmod(f, stat.S_IWRITE | stat.S_IREAD)
        state["config_shas_preserved"] = all(sha(p) == cfg_shas[p.name] for p in configs)
        state["base_map_sha_preserved"] = sha(BASE) == before_sha
        state["source_head_preserved"] = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip() == source_head
        if not all((state["config_shas_preserved"], state["base_map_sha_preserved"],
                    state["source_head_preserved"])):
            state["status"] = "NATIVE_ASSET_STAGE_HOLD"
        HOST.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
        print("ASSET_NATIVE_RESULT", json.dumps({
            "status": state["status"], "head": state["source_head"],
            "exit": state.get("editor_exit_code"), "map": state.get("new_map_package")}), flush=True)
    if state["status"] != "NATIVE_ASSET_WORLD_SAVED_RELOADED_NOT_PIE":
        raise RuntimeError("Native stage incomplete; see saved local evidence")


if __name__ == "__main__":
    main()
