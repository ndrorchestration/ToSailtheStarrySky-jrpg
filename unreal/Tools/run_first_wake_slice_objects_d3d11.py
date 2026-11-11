#!/usr/bin/env python3
"""Fail-closed ONE-CHILD real D3D11 visual QA of saved 115-actor First Wake World.

Host admits exact private native map/asset custody; actual PNGs must pass
both PNG integrity and non-black pixel checks. All screenshots are PREVIEW
evidence, never creator-approved cinematics, gameplay or water physics.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time

import intake_first_wake_slice_gpu_review as intake
import capture_first_wake_slice_objects_d3d11 as capture

ROOT=intake.TARGET
PROJECT=ROOT/"unreal"
UPROJECT=PROJECT/"ToSailTheStarrySky.uproject"
ENGINE=Path("C:/Program Files/Epic Games/UE_5.8")
EXE=ENGINE/"Engine/Binaries/Win64/UnrealEditor-Cmd.exe"
VERSION=ENGINE/"Engine/Build/Build.version"
REG=PROJECT/"Content/Python/test_first_wake_slice_object_gpu_review.py"
RUNSCRIPT=PROJECT/"Tools/capture_first_wake_slice_objects_d3d11.py"
TEST="Editor.Python.ToSailTheStarrySky.test_first_wake_slice_object_gpu_review"
OUTPUT=capture.RESULT_DIR
REPORT=OUTPUT.parent/"D3D11_FirstWakeObjects_AutomationReport_V2"
LOG=OUTPUT.parent/"host_d3d11_unreal_v2.log"
HOST=OUTPUT.parent/"host_d3d11_capture_receipt_v2.json"
MAX_SECONDS=260
MIN_RAM_GIB=6.5
MIN_DISK_GIB=14.0

class Mem(ctypes.Structure):
    _fields_=[("size",ctypes.c_ulong),("load",ctypes.c_ulong),
              ("total",ctypes.c_ulonglong),("avail",ctypes.c_ulonglong),
              ("totalpage",ctypes.c_ulonglong),("availpage",ctypes.c_ulonglong),
              ("totalvirtual",ctypes.c_ulonglong),("availvirtual",ctypes.c_ulonglong),
              ("avail_ext",ctypes.c_ulonglong)]

def ram_gib():
    memory=Mem();memory.size=ctypes.sizeof(memory)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        raise RuntimeError("HOLD: physical RAM status unavailable")
    return memory.avail/1024**3

def gpu_color_quality(pic):
    # No Pillow import at module load: Linux hosted tests need no art packages.
    from PIL import Image,ImageStat
    with Image.open(pic) as image:
        image.load()
        if image.size!=capture.SIZE:
            raise RuntimeError("HOLD: native D3D11 screenshot wrong dimensions")
        sample=image.convert("RGB")
        sample.thumbnail((320,180))
        pixels=list(sample.get_flattened_data() if hasattr(sample,"get_flattened_data") else sample.getdata())
        fractions=sum(1 for color in pixels if max(color)<7)/len(pixels)
        statdata=ImageStat.Stat(sample)
        contrast=sum(statdata.stddev)/3
        if fractions>=.92 or contrast<=4.0:
            raise RuntimeError(f"HOLD: likely black/flat GPU screenshot (black={fractions:.3f}, contrast={contrast:.1f})")
        return {"black_fraction":round(fractions,4),
                "rgb_contrast":round(contrast,2),
                "image_size":list(image.size),
                "approval":"PIXEL_DIVERSITY_ONLY_NOT_CREATOR_VISUAL_APPROVAL"}

def evaluate_native_receipt(native,images,world_sha):
    if (native.get("status")!=capture.STATUS_OK or
            native.get("source_map_sha256")!=world_sha or
            native.get("source_world_unchanged") is not True or
            native.get("temporary_camera_only_not_saved") is not True or
            native.get("art_approved") is not False or
            native.get("pie_verified") is not False or
            native.get("ocean_physics_verified") is not False or
            len(images)!=len(capture.PICS) or
            len(native.get("images",[]))!=len(images)):
        raise RuntimeError("HOLD: native GPU receipt lacks real bounded evidence")
    for expected,real in zip(native["images"],images):
        if expected!=real:
            raise RuntimeError("HOLD: screenshot bytes and source native receipt differ")
    return True

def check():
    if sys.platform!="win32" or ROOT.name!="TSTSS_VSliceVisualRuntime_20261110":
        raise RuntimeError("HOLD: wrong GPU host/worktree")
    if (intake.git(intake.CODE_ROOT,"branch","--show-current")!=intake.DEST_BRANCH or
            intake.git(intake.CODE_ROOT,"status","--porcelain","--untracked-files=no") or
            intake.git(ROOT,"branch","--show-current")!=intake.RUNTIME_BRANCH or
            intake.git(ROOT,"rev-parse","HEAD")!=intake.git(intake.CODE_ROOT,"rev-parse","HEAD")):
        raise RuntimeError("HOLD: GPU source branch/worktree diverged")
    if not all(p.is_file() for p in (UPROJECT,EXE,VERSION,REG,RUNSCRIPT,capture.WORLD_FILE)):
        raise RuntimeError("HOLD: native GPU binary, source map or script missing")
    if tuple(json.loads(VERSION.read_text(encoding="utf-8")).get(k)
             for k in ("MajorVersion","MinorVersion","PatchVersion"))!=(5,8,4):
        raise RuntimeError("HOLD: installed UE 5.8.4 required")
    intake.verify()
    plugins={p.get("Name"):p.get("Enabled") for p in
             json.loads(UPROJECT.read_text(encoding="utf-8")).get("Plugins",[])}
    if not plugins.get("PythonScriptPlugin") or not plugins.get("PythonAutomationTest"):
        raise RuntimeError("HOLD: registered native Python test unavailable")
    if str(RUNSCRIPT).replace("\\","/") not in REG.read_text(encoding="utf-8"):
        raise RuntimeError("HOLD: registered test does not name exact source script")
    for target in (OUTPUT,REPORT,LOG,HOST):
        if target.exists():raise RuntimeError("HOLD: prior GPU output exists; refuse overwrite")
    if list((PROJECT/"Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: user SaveGames present")
    if capture.sha(capture.WORLD_FILE)!=intake.WORLD_SHA:
        raise RuntimeError("HOLD: native source map changed")
    listing=subprocess.run(["tasklist","/FO","CSV"],check=True,capture_output=True,
                           text=True,timeout=15).stdout.lower()
    if any(k in listing for k in ("unrealeditor.exe","unrealeditor-cmd.exe","livecodingconsole.exe")):
        raise RuntimeError("HOLD: another UE Editor or LiveCoding session running")
    ram=ram_gib()
    disk=shutil.disk_usage(ROOT).free/1024**3
    if ram<MIN_RAM_GIB or disk<MIN_DISK_GIB:
        raise RuntimeError(f"HOLD: GPU resources insufficient RAM={ram:.2f}, disk={disk:.2f} GiB")
    return {"status":"NATIVE_GPU_PRECHECK_PASS_NO_EDITOR_LAUNCHED",
            "source_head":intake.git(ROOT,"rev-parse","HEAD"),
            "world_sha256":intake.WORLD_SHA,
            "source_script_sha256":capture.sha(RUNSCRIPT),
            "registration_sha256":capture.sha(REG),
            "initial_ram_gib":round(ram,2),
            "initial_disk_gib":round(disk,2),
            "requested_frame_count":len(capture.PICS),
            "native_gpu_render_verified":False,
            "artist_approved":False,"pie_verified":False}

def run():
    data=check()
    saved=(PROJECT/"Config/DefaultEngine.ini",PROJECT/"Config/DefaultInput.ini")
    protected={f.name:capture.sha(f) for f in saved}
    cmd=[str(EXE),str(UPROJECT),"-d3d11","-Unattended","-NoSplash","-NoSound",
         "-nop4","-stdout","-FullStdOutLogOutput",
         "-ExecCmds=Automation RunTest "+TEST+";Quit",
         "-ReportExportPath="+str(REPORT)]
    state="UNSTARTED"
    native={}
    try:
        for f in saved:f.chmod(stat.S_IREAD)
        LOG.parent.mkdir(parents=True,exist_ok=True)
        with LOG.open("x",encoding="utf-8") as out:
            child=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,
                                   stdout=out,stderr=subprocess.STDOUT,
                                   cwd=str(ROOT),
                                   creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            data["child_pid"]=child.pid
            print("ISOLATED_FIRSTWAKE_D3D11_CHILD_STARTED",child.pid,flush=True)
            t0=time.monotonic()
            while child.poll() is None:
                if time.monotonic()-t0>MAX_SECONDS or ram_gib()<1.1:
                    state="HOLD_WATCHDOG_TIME_OR_RAM"
                    child.terminate()
                    break
                time.sleep(2)
            try: exitcode=child.wait(timeout=12)
            except subprocess.TimeoutExpired:
                child.kill()
                exitcode=child.wait(timeout=5)
        data["native_exit_code"]=exitcode
        if state=="HOLD_WATCHDOG_TIME_OR_RAM" or exitcode!=0:
            raise RuntimeError("HOLD: native GPU process terminated or nonzero exit")
        if not capture.RECEIPT.is_file():
            raise RuntimeError("HOLD: no genuine native screenshot receipt")
        native=json.loads(capture.RECEIPT.read_text(encoding="utf-8"))
        raw=LOG.read_text(encoding="utf-8",errors="replace")
        controller=("Result={Success}" in raw and
                    "Test Completed." in raw and TEST in raw)
        if not controller:
            raise RuntimeError("HOLD: named UE Python automation test not passed")
        actual=[capture.validate_png(p) for p in capture.PICS]
        evaluate_native_receipt(native,actual,intake.WORLD_SHA)
        data["frames"]=[{**frame,**gpu_color_quality(OUTPUT/frame["file"])}
                         for frame in actual]
        data["native_controller_pass"]=True
        data["native_gpu_render_verified"]=True
        data["status"]="REAL_NATIVE_D3D11_FRAMES_PIXEL_QA_PASS_ART_APPROVAL_PENDING"
        state="PASSED"
    except Exception as exc:
        data["status"]="NATIVE_D3D11_GPU_REVIEW_HOLD"
        data["error"]=str(exc)
    finally:
        for f in saved:f.chmod(stat.S_IWRITE|stat.S_IREAD)
        data["map_preserved"]=capture.sha(capture.WORLD_FILE)==intake.WORLD_SHA
        data["source_commit_preserved"]=(intake.git(ROOT,"rev-parse","HEAD")==
                                         data["source_head"]==intake.git(intake.CODE_ROOT,"rev-parse","HEAD"))
        data["config_preserved"]=all(capture.sha(f)==protected[f.name] for f in saved)
        data["art_approved"]=False
        data["pie_verified"]=False
        data["ocean_physics_verified"]=False
        if not all(data[k] for k in ("map_preserved","source_commit_preserved","config_preserved")):
            data["status"]="NATIVE_D3D11_GPU_REVIEW_HOLD"
        with HOST.open("x",encoding="utf-8") as out:
            json.dump(data,out,sort_keys=True,indent=2)
    return data

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--capture",action="store_true")
    a=p.parse_args()
    try:
        result=check() if a.check else run()
        print(json.dumps({k:result.get(k) for k in
            ("status","source_head","world_sha256","native_exit_code",
             "requested_frame_count","frames","error")},sort_keys=True),flush=True)
        return 0 if result["status"] in (
            "NATIVE_GPU_PRECHECK_PASS_NO_EDITOR_LAUNCHED",
            "REAL_NATIVE_D3D11_FRAMES_PIXEL_QA_PASS_ART_APPROVAL_PENDING") else 2
    except Exception as exc:
        print(json.dumps({"status":"HOLD_NO_GPU_EDITOR_LAUNCHED","error":str(exc)}))
        return 2
if __name__=="__main__":
    sys.exit(main())
