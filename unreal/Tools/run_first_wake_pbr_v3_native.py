#!/usr/bin/env python3
"""Source-lock, safeguard and launch ONE opt-in UE5.8.4 NullRHI PBR stage.

--check never launches Unreal. Existing .umap, user editor, SaveGame, prior
stage output or inadequate resources produce an explicit HOLD, no cleanup.
"""
from __future__ import annotations
import argparse
import ctypes
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time

import intake_first_wake_pbr_native_v3 as private
import stage_first_wake_pbr_native_v3 as stage

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/"unreal"
ENGINE=Path("C:/Program Files/Epic Games/UE_5.8")
EDITOR=ENGINE/"Engine/Binaries/Win64/UnrealEditor.exe"
VERSION=ENGINE/"Engine/Build/Build.version"
BRANCH="review/ue58-vslice-lookdev-native-r1-20261111"
SOURCE_SHA="b7b741e0259c1fe0fefe3d078b7b6e7b2dfbc423"
OUTPUT=PROJECT/"Saved/FirstWakeMaterialLookdevV3"
NATIVE=PROJECT/stage.RECEIPT_REL
HOST=OUTPUT/"host_native_stage.json"
LOG=OUTPUT/"native_stage_editor.log"
CONSOLE=OUTPUT/"native_stage_console.log"
MIN_RAM_GIB=5.0
MIN_DISK_GIB=14.0
MAX_SECONDS=360

class Memory(ctypes.Structure):
    _fields_=[("size",ctypes.c_ulong),("load",ctypes.c_ulong),
              ("physical",ctypes.c_ulonglong),("available",ctypes.c_ulonglong),
              ("page",ctypes.c_ulonglong),("free_page",ctypes.c_ulonglong),
              ("virtual",ctypes.c_ulonglong),("free_virtual",ctypes.c_ulonglong),
              ("extended",ctypes.c_ulonglong)]

def ram():
    state=Memory()
    state.size=ctypes.sizeof(state)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
        raise RuntimeError("HOLD: physical memory API unavailable")
    return state.available/1024**3

def preflight():
    if sys.platform!="win32" or ROOT.name!=stage.plan.ROOT_NAME:
        raise RuntimeError("HOLD: incorrect Windows isolated PBR worktree")
    if private.git(ROOT,"branch","--show-current")!=BRANCH:
        raise RuntimeError("HOLD: source branch mismatch")
    if private.git(ROOT,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: tracked review source dirty")
    current=private.git(ROOT,"rev-parse","HEAD")
    if not private.git(ROOT,"merge-base","--is-ancestor",SOURCE_SHA,current)=="":
        raise RuntimeError("HOLD: expected source ancestor lost")
    if not all(x.is_file() for x in (EDITOR,VERSION,PROJECT/"ToSailTheStarrySky.uproject")):
        raise RuntimeError("HOLD: native UE Editor or project missing")
    version=json.loads(VERSION.read_text(encoding="utf-8"))
    if [version.get(k) for k in ("MajorVersion","MinorVersion","PatchVersion")]!=[5,8,4]:
        raise RuntimeError("HOLD: UE5.8.4 native requirement")
    summary=private.verify()
    source=PROJECT/stage.PARENT_REL
    source_sha=stage.plan.BASE_SHA
    if not source.is_file() or stage.sha(source)!=source_sha:
        raise RuntimeError("HOLD: source native World SHA mismatch")
    if not (PROJECT/stage.plan.ORIGINAL_PATH).is_file():
        raise RuntimeError("HOLD: original asset assembly receipt missing")
    for x in (PROJECT/stage.DEST_REL,NATIVE,HOST,LOG,CONSOLE):
        if x.exists():
            raise RuntimeError("HOLD: no native result or previous receipt may be overwritten "+x.name)
    if (PROJECT/"Saved/SaveGames").exists() and list((PROJECT/"Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: existing user SaveGame")
    plan=stage.validate_source()
    running=subprocess.run(["tasklist","/FO","CSV"],check=True,capture_output=True,
                           text=True,timeout=20).stdout.lower()
    if any(name in running for name in (
            "unrealeditor.exe","unrealeditor-cmd.exe","livecodingconsole.exe")):
        raise RuntimeError("HOLD: existing user Unreal Editor or LiveCoding")
    r=ram()
    d=shutil.disk_usage(ROOT).free/1024**3
    if r<MIN_RAM_GIB or d<MIN_DISK_GIB:
        raise RuntimeError(f"HOLD: native PBR stage resources RAM={r:.2f}, DISK={d:.2f} GiB")
    config=[PROJECT/"Config/DefaultEngine.ini",PROJECT/"Config/DefaultInput.ini"]
    if not all(p.is_file() for p in config):
        raise RuntimeError("HOLD: missing protected Engine/Input config")
    return {**plan,
            "status":"PBR_V3_NATIVE_STAGE_PREFLIGHT_PASS_NO_UNREAL_LAUNCHED",
            "source_head":current,
            "source_map_sha256":source_sha,
            "original_assembly_sha256":stage.sha(PROJECT/stage.plan.ORIGINAL_PATH),
            "source_config_sha256":{p.name:stage.sha(p) for p in config},
            "start_free_ram_gib":round(r,2),"start_free_disk_gib":round(d,2),
            "copied_private_native_files":summary["files"],
            "native_editor_started":False}

def stage_native():
    report=preflight()
    protected=[PROJECT/"Config/DefaultEngine.ini",PROJECT/"Config/DefaultInput.ini"]
    cmd=[str(EDITOR),str(PROJECT/"ToSailTheStarrySky.uproject"),
         "-ExecutePythonScript="+str(Path(stage.__file__).resolve()),
         "-NullRHI","-unattended","-nop4","-NoSplash","-NoSound",
         "-stdout","-FullStdOutLogOutput","-abslog="+str(LOG)]
    env=os.environ.copy()
    env[stage.OPT_IN]="1"
    OUTPUT.mkdir(parents=True,exist_ok=True)
    try:
        for p in protected:os.chmod(p,stat.S_IREAD)
        with CONSOLE.open("x",encoding="utf-8") as out:
            child=subprocess.Popen(cmd,cwd=str(ROOT),env=env,
                                   stdout=out,stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL,
                                   creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            report["native_editor_started"]=True
            report["child_pid"]=child.pid
            started=time.monotonic()
            while child.poll() is None:
                if time.monotonic()-started>MAX_SECONDS or ram()<0.85:
                    report["watchdog_terminated"]=True
                    child.terminate()
                    break
                time.sleep(2)
            try:code=child.wait(timeout=12)
            except subprocess.TimeoutExpired:
                child.kill();code=child.wait(timeout=6)
        report["native_exit_code"]=code
        if code!=0 or report.get("watchdog_terminated"):
            raise RuntimeError("HOLD: UE native child exited nonzero or was terminated by safety watchdog")
        if not NATIVE.is_file() or not LOG.is_file():
            raise RuntimeError("HOLD: native material stage receipt/editor log absent")
        native=json.loads(NATIVE.read_text(encoding="utf-8"))
        built=PROJECT/stage.DEST_REL
        if (native.get("status")!="NATIVE_PBR_V3_MAP_SAVED_PENDING_INDEPENDENT_READBACK" or
                native.get("parent_map_sha256")!=stage.plan.BASE_SHA or
                native.get("native_texture_assets")!=30 or
                native.get("native_material_assets")!=10 or
                native.get("new_actors")!=len(stage.plan.DETAILS)+1 or
                native.get("saved_actor_count")!=115+len(stage.plan.DETAILS)+1 or
                native.get("original_floor_collision_preserved") is not True or
                native.get("original_interaction_markers_preserved") is not True or
                not built.is_file() or stage.sha(built)!=native.get("new_map_sha256")):
            raise RuntimeError("HOLD: native stage receipt does not prove actual new World")
        if "FIRSTWAKE_PBR_V3_NATIVE_SAVED_NOT_PIE" not in LOG.read_text(encoding="utf-8",errors="replace"):
            raise RuntimeError("HOLD: native Unreal stage log does not corroborate receipt")
        report["status"]="NATIVE_PBR_V3_MAP_SAVED_PENDING_INDEPENDENT_READBACK"
        report["new_map_sha256"]=native["new_map_sha256"]
    except Exception as e:
        report["status"]="NATIVE_PBR_V3_STAGE_HOLD"
        report["error"]=str(e)
    finally:
        for p in protected:os.chmod(p,stat.S_IREAD|stat.S_IWRITE)
        report["source_head_preserved"]=private.git(ROOT,"rev-parse","HEAD")==report["source_head"]
        report["parent_map_preserved"]=stage.sha(PROJECT/stage.PARENT_REL)==report["source_map_sha256"]
        report["original_assembly_preserved"]=stage.sha(PROJECT/stage.plan.ORIGINAL_PATH)==report["original_assembly_sha256"]
        report["protected_configs_preserved"]=all(stage.sha(p)==report["source_config_sha256"][p.name] for p in protected)
        if not all(report[k] for k in (
                "source_head_preserved","parent_map_preserved",
                "original_assembly_preserved","protected_configs_preserved")):
            report["status"]="NATIVE_PBR_V3_STAGE_HOLD"
        with HOST.open("x",encoding="utf-8") as out:
            json.dump(report,out,indent=2,sort_keys=True)
    return report

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--stage",action="store_true")
    a=p.parse_args()
    try:
        out=preflight() if a.check else stage_native()
        print(json.dumps({k:out.get(k) for k in
                          ("status","source_head","start_free_ram_gib","start_free_disk_gib",
                           "native_exit_code","new_map_sha256","error")},sort_keys=True))
        return 0 if out["status"] not in ("NATIVE_PBR_V3_STAGE_HOLD",) else 2
    except Exception as e:
        print(json.dumps({"status":"HOLD_NO_EDITOR_LAUNCHED","reason":str(e)}))
        return 2
if __name__=="__main__":
    sys.exit(main())
