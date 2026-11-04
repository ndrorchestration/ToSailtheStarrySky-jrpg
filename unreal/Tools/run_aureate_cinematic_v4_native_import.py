#!/usr/bin/env python3
"""Resource-gated, finite, single-run native Unreal 5.8 importer.

Launches ONLY a NEW disposable review project; leaves user Editor untouched.
Bounded wall-time and physical-RAM watchdog stop only this launched process.
"""
from pathlib import Path
import ctypes
import json
import os
import shutil
import subprocess
import sys
import time

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"/"AureateCinematicV4Sandbox.uproject"
SCRIPT=Path(__file__).with_name("native_aureate_cinematic_v4_import_entry.py")
EXE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
SOURCE=Path("C:/tmp/TSTSS_AureateCinematicV4_Output_20261103")
LOG=ROOT/"ue584_native_import_host.log"
RECEIPT=ROOT/"native_import_receipt.json"
RUN_RECEIPT=ROOT/"host_run_receipt.json"
LOCK=ROOT/"native_import_active.lock"
MAX_SECONDS=150


class MemoryStatus(ctypes.Structure):
    _fields_=[("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
              ("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),
              ("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),
              ("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),
              ("ullAvailExtendedVirtual",ctypes.c_ulonglong)]


def free_memory_gib():
    m=MemoryStatus()
    m.dwLength=ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise RuntimeError("Cannot read Windows available physical memory")
    return m.ullAvailPhys/(1024**3)


def main():
    assert sys.platform=="win32", "Windows native validation required"
    assert PROJECT.is_file() and EXE.is_file() and SCRIPT.is_file()
    assert SOURCE.is_dir()
    project=json.loads(PROJECT.read_text(encoding="utf-8-sig"))
    assert "AUREATE_CINEMATIC_V4_REVIEW_ONLY" in project.get("Description","")
    assert project.get("EngineAssociation")=="5.8"
    if RECEIPT.exists() or RUN_RECEIPT.exists() or LOG.exists() or LOCK.exists():
        raise FileExistsError("Import already attempted; no retry without new review sandbox")
    if free_memory_gib()<4.0:
        raise RuntimeError("RAM gate: <4 GiB available, refuse competing Unreal Editor")
    if shutil.disk_usage(ROOT).free<14*1024**3:
        raise RuntimeError("Disk gate: <14 GiB free, refuse Unreal Editor import")
    proc_names=subprocess.run(["tasklist","/FI","IMAGENAME eq UnrealEditor-Cmd.exe","/FO","CSV"],
                              capture_output=True,text=True,check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in proc_names:
        raise RuntimeError("Another UE commandlet already active; refuse concurrent import")
    handle=os.open(LOCK,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    os.close(handle)
    command=[str(EXE),str(PROJECT),"-run=pythonscript",
             "-script="+str(SCRIPT),"-NullRHI","-unattended","-nop4",
             "-NoSplash","-NoSound","-stdout","-FullStdOutLogOutput"]
    report={"state":"NOT_LAUNCHED","sandbox":str(PROJECT),
            "engine":"5.8","native_script":str(SCRIPT),
            "resource_gates":{"ram_gib_min":4.0,"disk_gib_min":14.0},
            "max_runtime_sec":MAX_SECONDS,
            "other_user_editor_untouched":True,
            "story_starbourne_gate_changed":False}
    launched=None
    try:
        report["physical_ram_gib_start"]=round(free_memory_gib(),2)
        report["disk_gib_start"]=round(shutil.disk_usage(ROOT).free/1024**3,2)
        with LOG.open("w",encoding="utf-8") as log:
            launched=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,
                                      stdin=subprocess.DEVNULL,creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS,
                                      cwd=str(ROOT))
            report["pid"]=launched.pid
            report["state"]="NATIVE_UNREAL_PROCESS_RUNNING"
            print("V4_NATIVE_PROCESS_STARTED",launched.pid,flush=True)
            start=time.monotonic()
            last_print=start
            while launched.poll() is None:
                elapsed=time.monotonic()-start
                avail=free_memory_gib()
                if elapsed>MAX_SECONDS:
                    report["state"]="NATIVE_RUN_STOPPED_BY_BOUNDED_TIMEOUT"
                    launched.terminate()
                    break
                if avail<0.70:
                    report["state"]="NATIVE_RUN_STOPPED_BY_LOW_MEMORY_WATCHDOG"
                    launched.terminate()
                    break
                if time.monotonic()-last_print>=10:
                    print("V4_NATIVE_PROGRESS",round(elapsed,1),"sec RAM_free",round(avail,2),"GiB",flush=True)
                    last_print=time.monotonic()
                time.sleep(2)
            try:
                exit_code=launched.wait(timeout=10)
            except subprocess.TimeoutExpired:
                launched.kill()
                exit_code=launched.wait(timeout=5)
            report["native_process_exit_code"]=exit_code
        if RECEIPT.exists():
            native=json.loads(RECEIPT.read_text(encoding="utf-8"))
            report["native_state"]=native.get("state")
            report["native_readback"]=native.get("readback")
        else:
            report["native_state"]="NO_NATIVE_RECEIPT"
        if report["state"]=="NATIVE_UNREAL_PROCESS_RUNNING":
            report["state"]=("NATIVE_IMPORT_VERIFIED" if exit_code==0 and
                report["native_state"]=="NATIVE_IMPORT_AND_FIVE_STATICMESH_FOUR_MATERIAL_SLOT_READBACK_PASS"
                else "NATIVE_IMPORT_UNVERIFIED_OR_FAILED")
    finally:
        report["physical_ram_gib_end"]=round(free_memory_gib(),2)
        report["disk_gib_end"]=round(shutil.disk_usage(ROOT).free/1024**3,2)
        RUN_RECEIPT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        LOCK.unlink(missing_ok=True)
        print("V4_NATIVE_RUN_RESULT",json.dumps(report,sort_keys=True),flush=True)
        if LOG.exists():
            print("V4_NATIVE_LOG_TAIL",LOG.read_text(encoding="utf-8",errors="replace")[-4200:],flush=True)
    if report["state"]!="NATIVE_IMPORT_VERIFIED":
        sys.exit(1)


if __name__=="__main__":
    main()
