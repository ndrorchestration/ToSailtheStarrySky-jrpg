#!/usr/bin/env python3
"""Runs Skybourne-only full Editor preview stage, safely and once.

Writes to the already imported, isolated V4 review sandbox and a NEW map path.
Preserves user Editor and all previous successful/failed receipts.
"""
import ctypes,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"/"AureateCinematicV4Sandbox.uproject"
UE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
SCRIPT=Path(__file__).with_name("aureate_v4_full_editor_skybourne_stage.py")
RECEIPT=ROOT/"full_editor_skybourne_stage_receipt.json"
LOG=ROOT/"ue584_full_editor_skybourne_stage.log"
HOST=ROOT/"host_full_editor_skybourne_stage_receipt.json"
MAPFILE=PROJECT.parent/"Content"/"TSTSS"/"Review"/"Scenes"/"AureateCinematicV4_Skybourne_Hero_20261103_FullEditor.umap"
MAX_SECONDS=160

class Mem(ctypes.Structure):
    _fields_=[("size",ctypes.c_ulong),("load",ctypes.c_ulong),
              ("total",ctypes.c_ulonglong),("avail",ctypes.c_ulonglong),
              ("totalpage",ctypes.c_ulonglong),("availpage",ctypes.c_ulonglong),
              ("totalvirtual",ctypes.c_ulonglong),("availvirtual",ctypes.c_ulonglong),
              ("avail_ext",ctypes.c_ulonglong)]
def free_ram():
    m=Mem();m.size=ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise RuntimeError("Windows available-RAM query failed")
    return m.avail/1024**3

def main():
    if sys.platform!="win32":raise RuntimeError("Native UE Windows only")
    if not (UE.is_file() and SCRIPT.is_file() and PROJECT.is_file()):
        raise RuntimeError("Missing UE or V4 sandbox/script")
    data=json.loads(PROJECT.read_text(encoding="utf8"))
    if data.get("EngineAssociation")!="5.8" or "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in data.get("Description",""):
        raise RuntimeError("Not a review-only UE5.8 sandbox")
    if any(x.exists() for x in (RECEIPT,LOG,HOST,MAPFILE)):
        raise FileExistsError("Skybourne staging already attempted; refuse overwrite")
    if free_ram()<4.2:raise RuntimeError("RAM gate below 4.2 GiB: do not launch")
    if shutil.disk_usage(ROOT).free<14*1024**3:
        raise RuntimeError("Disk gate below 14 GiB: do not launch")
    tasks=subprocess.run(["tasklist","/FI","IMAGENAME eq UnrealEditor-Cmd.exe","/FO","CSV"],
                         capture_output=True,text=True,check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in tasks:
        raise RuntimeError("Another UE commandlet exists: refuse concurrency")
    cmd=[str(UE),str(PROJECT),"-ExecutePythonScript="+str(SCRIPT),
         "-NullRHI","-NoSplash","-NoSound","-Unattended","-nop4",
         "-stdout","-FullStdOutLogOutput"]
    report={"state":"NOT_STARTED","new_map_only":True,"user_editor_untouched":True,
            "starbourne_player_lock_unchanged":True,"max_seconds":MAX_SECONDS,
            "ram_gib_start":round(free_ram(),2)}
    proc=None
    try:
        with LOG.open("w",encoding="utf8") as output:
            proc=subprocess.Popen(cmd,stdout=output,stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL,cwd=str(ROOT),
                                  creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            report["pid"]=proc.pid
            print("V4_SKYBOURNE_FULL_EDITOR_STARTED",proc.pid,flush=True)
            t0=time.monotonic()
            while proc.poll() is None:
                if free_ram()<0.95 or time.monotonic()-t0>MAX_SECONDS:
                    report["state"]="STOPPED_BY_RAM_OR_TIME_WATCHDOG"
                    proc.terminate()
                    break
                time.sleep(2)
            try: code=proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill();code=proc.wait(timeout=5)
        report["exit_code"]=code
        native=json.loads(RECEIPT.read_text(encoding="utf8")) if RECEIPT.exists() else {"state":"MISSING_NATIVE_RECEIPT"}
        report["native_state"]=native.get("state")
        report["native_map_sha256"]=native.get("map_sha256")
        report["native_actor_count"]=native.get("actor_count")
        if report["state"]=="NOT_STARTED":
            report["state"]=("SKYBOURNE_STAGE_NATIVE_PASS"
              if code==0 and native.get("state")=="SKYBOURNE_ONE_FORM_NATIVE_FULL_EDITOR_ACTOR_STAGE_PASS"
              else "SKYBOURNE_STAGE_NATIVE_FAIL")
    finally:
        report["ram_gib_end"]=round(free_ram(),2)
        HOST.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("V4_SKYBOURNE_STAGE_RESULT",json.dumps(report,sort_keys=True),flush=True)
        if LOG.exists():
            print("V4_SKYBOURNE_STAGE_LOG_TAIL",
                  LOG.read_text(encoding="utf8",errors="replace")[-3200:],flush=True)
    if report["state"]!="SKYBOURNE_STAGE_NATIVE_PASS":sys.exit(1)

if __name__=="__main__":main()
