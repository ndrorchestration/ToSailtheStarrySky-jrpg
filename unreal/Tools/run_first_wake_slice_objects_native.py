#!/usr/bin/env python3
"""Safety-gated, opt-in one-child UE5.8.4 NullRHI object import/map staging.

Never runs from CI. --check is strictly read-only; --stage only when all gates pass.
No user Unreal sessions killed; no source art, saves or existing levels overwritten.
"""
from __future__ import annotations
import argparse
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

import stage_first_wake_slice_objects as stage
import prepare_first_wake_editor_module as native_module

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/"unreal"
EDITOR=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe")
OUTPUT=PROJECT/"Saved/FirstWakeSliceObjectsV1"
NATIVE=PROJECT/stage.DEST_RECEIPT_REL
HOST=OUTPUT/"host_objects_stage.json"
LOG=OUTPUT/"objects_native.log"
CONSOLE=OUTPUT/"objects_console.log"
BRANCH="review/ue58-vslice-objects-native-v2-20261110"
MIN_RAM_GIB=5.0
MIN_DISK_GIB=14.0
MAX_RUNTIME_SECONDS=300

class MemStatus(ctypes.Structure):
    _fields_=[("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
              ("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),
              ("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),
              ("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),
              ("ullAvailExtendedVirtual",ctypes.c_ulonglong)]
def free_ram_gib():
    ms=MemStatus();ms.dwLength=ctypes.sizeof(ms)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms)):
        raise RuntimeError("Cannot verify available physical memory")
    return ms.ullAvailPhys/1024**3
def git(*args):
    return subprocess.run(["git","-C",str(ROOT),*args],capture_output=True,
                          text=True,check=True,timeout=30).stdout.strip()
def prerequisites():
    if sys.platform!="win32" or ROOT.name!=stage.ROOT_NAME:
        raise RuntimeError("HOLD: only the isolated Windows worktree may stage")
    if git("branch","--show-current")!=BRANCH or git("status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: branch wrong or tracked source not clean")
    if not EDITOR.is_file() or not (PROJECT/"ToSailTheStarrySky.uproject").is_file():
        raise RuntimeError("HOLD: installed native Unreal project/Editor missing")
    build=json.loads((EDITOR.parents[2]/"Build/Build.version").read_text(encoding="utf-8"))
    if [build[k] for k in ("MajorVersion","MinorVersion","PatchVersion")] != [5,8,4]:
        raise RuntimeError("HOLD: expected installed Unreal Engine 5.8.4")
    source=PROJECT/stage.SOURCE_MAP_REL
    parent=PROJECT/stage.SOURCE_RECEIPT_REL
    if not source.is_file() or not parent.is_file():
        raise RuntimeError("HOLD: native harbor map+receipt not staged/copied")
    parent_json=json.loads(parent.read_text(encoding="utf-8"))
    if (parent_json.get("status")!="NATIVE_HARBOR_MAP_SAVED_PENDING_INDEPENDENT_READBACK"
          or parent_json.get("map_sha256")!=stage.sha256(source)):
        raise RuntimeError("HOLD: parent map/hash/receipt mismatch")
    for p in (PROJECT/stage.NEW_MAP_REL,NATIVE,HOST,LOG,CONSOLE):
        if p.exists(): raise RuntimeError("HOLD: previous objects output exists: "+p.name)
    if list((PROJECT/"Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: user/review save exists, will not touch")
    stages=stage.validate_source()
    # The isolated worktree must possess a source-parity-checked UE Editor DLL
    # from an independently read-back native source revision. Never pretend
    # that a bare .uproject can load a missing C++ game module.
    native_module.verify_module()
    process_listing=subprocess.run(["tasklist","/FO","CSV"],capture_output=True,
                                   text=True,check=True,timeout=20).stdout.lower()
    if any(p in process_listing for p in
           ("unrealeditor.exe","unrealeditor-cmd.exe","livecodingconsole.exe")):
        raise RuntimeError("HOLD: another UE/LiveCoding session running")
    ram=free_ram_gib(); disk=shutil.disk_usage(ROOT).free/1024**3
    if ram<MIN_RAM_GIB or disk<MIN_DISK_GIB:
        raise RuntimeError(f"HOLD: insufficient resources: physicalRAM={ram:.2f} GiB disk={disk:.2f} GiB")
    configs=[PROJECT/"Config/DefaultEngine.ini",PROJECT/"Config/DefaultInput.ini"]
    for p in configs:
        if not p.is_file(): raise RuntimeError("HOLD: missing original Unreal config "+p.name)
    return dict(stages,source_commit=git("rev-parse","HEAD"),
                source_map_sha256=stage.sha256(source),
                starting_physical_ram_gib=round(ram,3),
                starting_disk_gib=round(disk,3),
                config_hashes={p.name:stage.sha256(p) for p in configs},
                status="SOURCE_AND_HOST_PREFLIGHT_PASS_NO_UNREAL_LAUNCH")

def stage_native():
    record=prerequisites()
    configs=[PROJECT/"Config/DefaultEngine.ini",PROJECT/"Config/DefaultInput.ini"]
    OUTPUT.mkdir(parents=True,exist_ok=True)
    code=None
    try:
        for p in configs: os.chmod(p,stat.S_IREAD)
        cmd=[str(EDITOR),str(PROJECT/"ToSailTheStarrySky.uproject"),
             "-ExecutePythonScript="+str(Path(stage.__file__).resolve()),
             "-NullRHI","-unattended","-nop4","-NoSplash","-NoSound",
             "-stdout","-FullStdOutLogOutput","-abslog="+str(LOG)]
        env=os.environ.copy()
        env["TSTSS_SLICE_OBJECT_STAGE_EXPLICIT"]="1"
        with CONSOLE.open("x",encoding="utf-8") as log:
            child=subprocess.Popen(cmd,cwd=str(ROOT),env=env,stdin=subprocess.DEVNULL,
                                   stdout=log,stderr=subprocess.STDOUT,
                                   creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            record["child_pid"]=child.pid
            start=time.monotonic()
            while child.poll() is None:
                if time.monotonic()-start>MAX_RUNTIME_SECONDS or free_ram_gib()<0.85:
                    child.terminate()
                    record["safety_termination"]=True
                    break
                time.sleep(2)
            try: code=child.wait(timeout=12)
            except subprocess.TimeoutExpired:
                child.kill();code=child.wait(timeout=6)
        record["native_exit_code"]=code
        if record.get("safety_termination") or code!=0:
            raise RuntimeError("Unreal child terminated or exited nonzero")
        if not NATIVE.is_file(): raise RuntimeError("Missing native receipt")
        receipt=json.loads(NATIVE.read_text(encoding="utf-8"))
        dst=PROJECT/stage.NEW_MAP_REL
        if (receipt.get("status")!="NATIVE_OBJECT_MAP_SAVED_PENDING_INDEPENDENT_READBACK"
                or not dst.is_file() or stage.sha256(dst)!=receipt.get("new_map_sha256")
                or receipt.get("new_native_actor_count")!=31):
            raise RuntimeError("Invalid saved native map/receipt")
        if not LOG.is_file() or "TSTSS_SLICE_OBJECT_NATIVE_STAGE_SAVED_NOT_PIE" not in LOG.read_text(encoding="utf-8",errors="replace"):
            raise RuntimeError("UE log missing actual native stage sentinel")
        record["status"]="NATIVE_STAGE_SAVED_PENDING_INDEPENDENT_READBACK"
        record["new_map_sha256"]=receipt["new_map_sha256"]
    except Exception as e:
        record["status"]="NATIVE_STAGE_HOLD"
        record["error"]=str(e)
    finally:
        for p in configs:
            os.chmod(p,stat.S_IWRITE|stat.S_IREAD)
        record["config_hashes_preserved"]=all(stage.sha256(p)==record["config_hashes"][p.name] for p in configs)
        record["source_map_preserved"]=stage.sha256(PROJECT/stage.SOURCE_MAP_REL)==record["source_map_sha256"]
        record["commit_preserved"]=git("rev-parse","HEAD")==record["source_commit"]
        if not all(record[k] for k in ("config_hashes_preserved","source_map_preserved","commit_preserved")):
            record["status"]="NATIVE_STAGE_HOLD"
        with HOST.open("x",encoding="utf-8") as f:
            json.dump(record,f,indent=2,sort_keys=True)
    return record

def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--stage",action="store_true")
    args=parser.parse_args()
    try:
        out=prerequisites() if args.check else stage_native()
        print(json.dumps({k:out.get(k) for k in
            ("status","source_commit","starting_physical_ram_gib","starting_disk_gib",
             "native_exit_code","new_map_sha256","error")},sort_keys=True))
        return 0 if out["status"]!="NATIVE_STAGE_HOLD" else 2
    except Exception as e:
        print(json.dumps({"status":"HOLD_NO_EDITOR_LAUNCHED","reason":str(e)}))
        return 2
if __name__=="__main__": sys.exit(main())
