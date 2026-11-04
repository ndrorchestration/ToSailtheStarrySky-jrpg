#!/usr/bin/env python3
"""Resource-gated native UE 5.8.4 *review map staging* for V4 horizon scene.

Does not render a GPU image, modify a current user Unreal Editor, import
packages, touch production levels or approve art. One attempt, one new map.
Call only on the authorized Windows sandbox after inspecting current work.
"""
import argparse
import ctypes
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox/AureateCinematicV4Sandbox.uproject"
EDITOR=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
STAGE=Path(__file__).with_name("stage_aureate_v4_horizon_atmosphere_review.py")
MAPDIR=ROOT/"AureateCinematicV4Sandbox/Content/TSTSS/Review/Scenes"
TARGET=MAPDIR/"AureateV4_Skybourne_HorizonAtmosphere_ReviewV1.umap"
MATERIALDIR=ROOT/"AureateCinematicV4Sandbox/Content/TSTSS/Review/Environment/V4HorizonReviewV1"
HASHES={
 "AureateCinematicV4_Skybourne_Hero_20261103_FullEditor.umap":
     "16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40",
 "AureateCinematicV4_Seabourne_20261103_FullEditor.umap":
     "b0b0587783197b2eff4a3e820fb49a52ac70edbbc9519a8cdbceee470edc955a",
 "AureateCinematicV4_Submersible_20261103_FullEditor.umap":
     "815e235aae6abef0e9a816bd8c9d01a13b4441bd81538763d2424e799e925f35",
 "AureateCinematicV4_Starbourne_20261103_FullEditor.umap":
     "953bb2aaca0db194bdd871229cdb13245c59ceab19cf0f8cbc44a802c01e0e00",
}
MAX_SECONDS=180
class Mem(ctypes.Structure):
    _fields_=[("size",ctypes.c_ulong),("load",ctypes.c_ulong),
              ("total",ctypes.c_ulonglong),("avail",ctypes.c_ulonglong),
              ("totalpage",ctypes.c_ulonglong),("availpage",ctypes.c_ulonglong),
              ("totalvirtual",ctypes.c_ulonglong),("availvirtual",ctypes.c_ulonglong),
              ("avail_ext",ctypes.c_ulonglong)]

def ram_gib():
    m=Mem()
    m.size=ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise RuntimeError("RAM status API unavailable")
    return m.avail/1024**3

def checksum(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def four_maps_unchanged():
    return {name: (MAPDIR/name).is_file() and checksum(MAPDIR/name)==expected
            for name,expected in HASHES.items()}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--attempt",required=True,help="Unused lowercase tag, 3-19 characters")
    args=p.parse_args(argv)
    attempt=args.attempt
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,18}",attempt):
        raise ValueError("Invalid unique attempt tag")
    if sys.platform!="win32":
        raise RuntimeError("Native review staging requires authorized Windows host")
    if not all(path.is_file() for path in (PROJECT,EDITOR,STAGE)):
        raise RuntimeError("Missing disposable UE5.8 project, editor or stage source")
    project=json.loads(PROJECT.read_text(encoding="utf8"))
    if (project.get("EngineAssociation")!="5.8" or
       "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in project.get("Description","")):
        raise RuntimeError("Refusing to stage a non-review project")
    before=four_maps_unchanged()
    if not all(before.values()):
        raise RuntimeError("One or more of the four original native V4 map SHAs changed")
    if TARGET.exists() or MATERIALDIR.exists():
        raise FileExistsError("Horizon destination already exists: no overwrite or retry")
    if ram_gib()<4.2:
        raise RuntimeError("RAM < 4.2 GiB: native Editor staging prohibited")
    if shutil.disk_usage(ROOT).free < 14*1024**3:
        raise RuntimeError("Disk < 14 GiB: native Editor staging prohibited")
    tasklist=subprocess.run(["tasklist","/FO","CSV"],capture_output=True,text=True,check=True).stdout
    for name in ("UnrealEditor.exe","UnrealEditor-Cmd.exe"):
        if '"'+name+'"' in tasklist:
            raise RuntimeError("Unreal Editor already running; refuse competing native job")
    receipt=ROOT/("native_v4_horizon_stage_"+attempt+".json")
    log=ROOT/("ue584_horizon_stage_"+attempt+".log")
    host=ROOT/("host_v4_horizon_stage_"+attempt+".json")
    if any(path.exists() for path in (receipt,log,host)):
        raise FileExistsError("Prior attempt evidence exists: no overwrite")
    env=dict(__import__('os').environ)
    env["TSTSS_V4_HORIZON_RECEIPT"]=str(receipt)
    cmd=[str(EDITOR),str(PROJECT),"-ExecutePythonScript="+str(STAGE),
         "-NullRHI","-NoSplash","-NoSound","-Unattended","-nop4",
         "-stdout","-FullStdOutLogOutput"]
    outcome={"status":"NOT_LAUNCHED","attempt":attempt,
             "user_editor_untouched":True,"real_gpu_rendered":False,
             "production_or_save_changed":False,"starbourne_player_unlocked":False,
             "preflight_map_shas":before,"ram_gib_before":round(ram_gib(),2)}
    try:
        with log.open("x",encoding="utf8") as sink:
            child=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=sink,
                      stderr=subprocess.STDOUT,env=env,cwd=str(ROOT),
                      creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            outcome["own_pid"]=child.pid
            started=time.monotonic()
            while child.poll() is None:
                if time.monotonic()-started>MAX_SECONDS:
                    outcome["status"]="OWN_CHILD_STOPPED_TIME_WATCHDOG"
                    child.terminate()
                    break
                if ram_gib()<0.95:
                    outcome["status"]="OWN_CHILD_STOPPED_LOW_MEMORY"
                    child.terminate()
                    break
                time.sleep(2)
            try:
                outcome["exit_code"]=child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                outcome["exit_code"]=child.wait(timeout=5)
        native=json.loads(receipt.read_text(encoding="utf8")) if receipt.is_file() else {}
        outcome["native_stage_state"]=native.get("state","MISSING_NATIVE_RECEIPT")
        outcome["native_new_map_sha256"]=native.get("new_map_sha256")
        if outcome["status"]=="NOT_LAUNCHED":
            if (outcome["exit_code"]==0 and
                native.get("state")=="NATIVE_HORIZON_STAGE_REVIEW_MAP_ONLY_PASS" and
                TARGET.is_file() and checksum(TARGET)==native.get("new_map_sha256")):
                outcome["status"]="NEW_REVIEW_LEVEL_NATIVE_NULLRHI_STAGE_PASS_GPU_NOT_TESTED"
            else:
                outcome["status"]="NATIVE_HORIZON_STAGE_NOT_VERIFIED"
    except Exception as exc:
        outcome["error"]=str(exc)
        if outcome["status"]=="NOT_LAUNCHED":
            outcome["status"]="NATIVE_HORIZON_STAGE_NOT_VERIFIED"
    finally:
        after=four_maps_unchanged()
        outcome["postflight_map_shas"]=after
        if not all(after.values()):
            outcome["status"]="ORIGINAL_FOUR_FORM_MAP_DRIFT_BLOCK"
        outcome["ram_gib_after"]=round(ram_gib(),2)
        host.write_text(json.dumps(outcome,sort_keys=True,indent=2)+"\n",encoding="utf8")
        print("V4_HORIZON_STAGE_HOST "+json.dumps(outcome,sort_keys=True),flush=True)
    if outcome["status"]!="NEW_REVIEW_LEVEL_NATIVE_NULLRHI_STAGE_PASS_GPU_NOT_TESTED":
        raise SystemExit(1)

if __name__=="__main__":
    main()
