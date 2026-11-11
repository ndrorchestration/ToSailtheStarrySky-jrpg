#!/usr/bin/env python3
"""Guarded one-child UE5.8.4 true D3D11 GPU source-art review of saved PBR V3.

Runs only when 200-actor World privately copied/rehashed, exact source C++
unchanged, local runtime project plugin strictly isolated. Native controller,
4 actual PNG SHA/CRC/size, pixel diversity and unchanged source maps required.
"""
from __future__ import annotations
import argparse
import ctypes
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time

import intake_first_wake_pbr_gpu_v3 as intake
import capture_first_wake_pbr_gpu_v3 as capture

ROOT=intake.DEST
PROJECT=ROOT/"unreal"
UPROJECT=PROJECT/"ToSailTheStarrySky.uproject"
ENGINE=Path("C:/Program Files/Epic Games/UE_5.8")
EDITOR=ENGINE/"Engine/Binaries/Win64/UnrealEditor-Cmd.exe"
VERSION=ENGINE/"Engine/Build/Build.version"
REG=PROJECT/"Content/Python/test_first_wake_pbr_gpu_v3.py"
SCRIPT=PROJECT/"Tools/capture_first_wake_pbr_gpu_v3.py"
TEST="Editor.Python.ToSailTheStarrySky.test_first_wake_pbr_gpu_v3"
OUTPUT=capture.OUTPUT
REPORT=OUTPUT.parent/"PBR_V3_GPU_AutomationReport_20261111_R1"
LOG=OUTPUT.parent/"PBR_V3_GPU_UE584_D3D11_HostLog_20261111_R1.log"
HOST=OUTPUT.parent/"PBR_V3_GPU_UE584_D3D11_HostReceipt_20261111_R1.json"
MAX_SECONDS=300
MIN_RAM_GIB=6.5
MIN_DISK_GIB=14.0
PASS="REAL_NATIVE_PBR_V3_D3D11_FRAMES_QA_PASS_ART_REVIEW_PENDING"

class Mem(ctypes.Structure):
    _fields_=[("length",ctypes.c_ulong),("load",ctypes.c_ulong),
              ("total",ctypes.c_ulonglong),("available",ctypes.c_ulonglong),
              ("page",ctypes.c_ulonglong),("pagefree",ctypes.c_ulonglong),
              ("virtual",ctypes.c_ulonglong),("virtualfree",ctypes.c_ulonglong),
              ("extended",ctypes.c_ulonglong)]

def ram():
    state=Mem()
    state.length=ctypes.sizeof(state)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
        raise RuntimeError("HOLD: available physical memory unknown")
    return state.available/1024**3

def quality(frame):
    from PIL import Image,ImageStat
    with Image.open(frame) as im:
        im.load()
        if im.size!=capture.SIZE:
            raise RuntimeError("HOLD: real native frame unexpected image dimensions")
        img=im.convert("RGB")
        img.thumbnail((320,180))
        pixels=list(img.get_flattened_data() if hasattr(img,"get_flattened_data") else img.getdata())
        black=sum(max(c)<7 for c in pixels)/len(pixels)
        contrast=sum(ImageStat.Stat(img).stddev)/3
        if black>=.92 or contrast<=4:
            raise RuntimeError("HOLD: almost black or featureless native frame")
        return {"black_fraction":round(black,4),
                "rgb_contrast":round(contrast,2),
                "approval":"GPU_PIXEL_EVIDENCE_ONLY_NO_CREATOR_ART_APPROVAL"}

def match_receipt(native,images):
    if (native.get("status")!=capture.STATUS or
            native.get("world_sha256")!=intake.WORLD_SHA or
            native.get("source_world_preserved") is not True or
            native.get("no_source_level_save") is not True or
            native.get("native_level_actors")!=200 or
            native.get("transient_hidden_developer_text_signs")!=7 or
            native.get("hidden_gameplay_milestones")!=0 or
            native.get("transient_sign_policy_status")!="ONLY_SEVEN_DEV_SIGNS_HIDDEN_TRANSIENT_FOR_CAPTURE" or
            native.get("gpu_visual_approved") is not False or
            native.get("pie_verified") is not False or
            native.get("ocean_splashdown_verified") is not False or
            native.get("starbourne_unlocked") is not False or
            native.get("frames_expected")!=len(capture.FRAMES) or
            len(images)!=len(capture.FRAMES) or
            native.get("images")!=images):
        raise RuntimeError("HOLD: actual 200-actor native GPU and sign policy receipt inconsistent")
    return True

def check():
    if sys.platform!="win32" or ROOT.name!="TSTSS_VSliceLookdev_20261111" or (
            ROOT.parent.name!="TSTSS_V3_GPU_20261111"):
        raise RuntimeError("HOLD: wrong Windows native 200-actor GPU workspace")
    if (intake.git(ROOT,"branch","--show-current")!=intake.BRANCH or
            intake.git(intake.SRC,"rev-parse","HEAD")!=intake.SOURCE_HEAD):
        raise RuntimeError("HOLD: wrong GPU branch or original native R1 source")
    tracked=intake.git(ROOT,"status","--porcelain","--untracked-files=no").splitlines()
    if tracked!=[" M unreal/ToSailTheStarrySky.uproject"]:
        raise RuntimeError("HOLD: GPU runtime requires exact one-file uncommitted PythonAutomationTest delta")
    if not all(p.is_file() for p in (UPROJECT,EDITOR,VERSION,REG,SCRIPT,capture.WORLD_FILE)):
        raise RuntimeError("HOLD: actual engine/project/registered review/level missing")
    version=json.loads(VERSION.read_text(encoding="utf-8"))
    if [version.get(k) for k in ("MajorVersion","MinorVersion","PatchVersion")]!=[5,8,4]:
        raise RuntimeError("HOLD: exact installed UE 5.8.4 needed")
    intake.verify()
    if str(SCRIPT).replace("\\","/") not in REG.read_text(encoding="utf-8"):
        raise RuntimeError("HOLD: registered Python automation test not bound to script")
    if not all(json.loads(UPROJECT.read_text(encoding="utf-8")).get("Plugins")):
        raise RuntimeError("HOLD: project plugins invalid")
    for item in (OUTPUT,HOST,LOG,REPORT):
        if item.exists():
            raise RuntimeError("HOLD: previous GPU output already exists; no overwrites")
    if list((PROJECT/"Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: user SaveGame present")
    listing=subprocess.run(["tasklist","/FO","CSV"],check=True,capture_output=True,
                           text=True,timeout=20).stdout.lower()
    if any(x in listing for x in ("unrealeditor.exe","unrealeditor-cmd.exe","livecodingconsole.exe")):
        raise RuntimeError("HOLD: another user Unreal Editor/LiveCoding process is active")
    available=ram()
    space=shutil.disk_usage(ROOT).free/1024**3
    if available<MIN_RAM_GIB or space<MIN_DISK_GIB:
        raise RuntimeError(f"HOLD: D3D11 requires RAM={available:.2f} (min 6.5), disk={space:.2f} (min 14) GiB")
    return {"status":"PBR_V3_GPU_HOST_PREFLIGHT_PASS_NO_EDITOR_LAUNCHED",
            "source_head":intake.git(ROOT,"rev-parse","HEAD"),
            "native_map_sha256":intake.WORLD_SHA,
            "source_script_sha256":intake.sha(SCRIPT),
            "registered_script_sha256":intake.sha(REG),
            "initial_free_ram_gib":round(available,2),
            "initial_free_disk_gib":round(space,2),
            "frame_count":len(capture.FRAMES),
            "native_gpu_verified":False,"pie_verified":False,"art_approved":False}

def run():
    data=check()
    configs=[PROJECT/"Config/DefaultEngine.ini",PROJECT/"Config/DefaultInput.ini"]
    protected={p.name:intake.sha(p) for p in configs}
    cmd=[str(EDITOR),str(UPROJECT),"-d3d11","-Unattended","-NoSplash",
         "-NoSound","-nop4","-stdout","-FullStdOutLogOutput",
         "-ExecCmds=Automation RunTest "+TEST+";Quit",
         "-ReportExportPath="+str(REPORT)]
    try:
        for p in configs:p.chmod(stat.S_IREAD)
        LOG.parent.mkdir(parents=True,exist_ok=True)
        with LOG.open("x",encoding="utf-8") as out:
            child=subprocess.Popen(cmd,cwd=str(ROOT),stdin=subprocess.DEVNULL,
                                   stdout=out,stderr=subprocess.STDOUT,
                                   creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            data["owned_editor_pid"]=child.pid
            print("PBR_V3_ISOLATED_D3D11_CHILD_STARTED",child.pid,flush=True)
            started=time.monotonic()
            while child.poll() is None:
                if time.monotonic()-started>MAX_SECONDS or ram()<1.1:
                    data["watchdog_terminated"]=True
                    child.terminate()
                    break
                time.sleep(2)
            try:code=child.wait(timeout=12)
            except subprocess.TimeoutExpired:
                child.kill()
                code=child.wait(timeout=5)
        data["editor_exit_code"]=code
        if code!=0 or data.get("watchdog_terminated"):
            raise RuntimeError("HOLD: native D3D11 child terminated/failed")
        if not capture.NATIVE_RECEIPT.is_file():
            raise RuntimeError("HOLD: native UE 200-actor screenshot receipt absent")
        native=json.loads(capture.NATIVE_RECEIPT.read_text(encoding="utf-8"))
        log=LOG.read_text(encoding="utf-8",errors="replace")
        if not all(text in log for text in ("Result={Success}","Test Completed.",TEST)):
            raise RuntimeError("HOLD: named UE native Python automation controller failed/not found")
        actual=[capture.validate_png(p) for p in capture.FRAMES]
        match_receipt(native,actual)
        data["frames"]=[{**row,**quality(OUTPUT/row["file"])} for row in actual]
        data["controller_pass"]=True
        data["native_gpu_verified"]=True
        data["status"]=PASS
    except Exception as exc:
        data["status"]="PBR_V3_GPU_HOST_HOLD"
        data["error"]=str(exc)
    finally:
        for p in configs:p.chmod(stat.S_IWRITE|stat.S_IREAD)
        data["native_map_preserved"]=intake.sha(capture.WORLD_FILE)==intake.WORLD_SHA
        data["source_head_preserved"]=intake.git(ROOT,"rev-parse","HEAD")==data["source_head"]
        data["config_hashes_preserved"]=all(intake.sha(p)==protected[p.name] for p in configs)
        data["art_approved"]=False
        data["pie_verified"]=False
        data["water_physics_verified"]=False
        if not all(data[x] for x in (
                "native_map_preserved","source_head_preserved","config_hashes_preserved")):
            data["status"]="PBR_V3_GPU_HOST_HOLD"
        with HOST.open("x",encoding="utf-8") as out:
            json.dump(data,out,sort_keys=True,indent=2)
    return data

def main():
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check",action="store_true")
    group.add_argument("--capture",action="store_true")
    a=p.parse_args()
    try:
        result=check() if a.check else run()
        print(json.dumps({k:result.get(k) for k in (
            "status","source_head","native_map_sha256","editor_exit_code",
            "frame_count","frames","error")},sort_keys=True),flush=True)
        return 0 if result["status"] in (
            "PBR_V3_GPU_HOST_PREFLIGHT_PASS_NO_EDITOR_LAUNCHED",PASS) else 2
    except Exception as exc:
        print(json.dumps({"status":"HOLD_NO_D3D11_EDITOR_LAUNCHED","error":str(exc)}))
        return 2
if __name__=="__main__":
    sys.exit(main())
