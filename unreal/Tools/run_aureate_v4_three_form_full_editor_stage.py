"""Run native Seabourne / Submersible / private Starbourne stage once, safely.

Lightweight full Editor NullRHI branch; does not use GPU graphics hardware,
does not affect user Editor, approved art, gameplay, story gate or SaveGame.
"""
import ctypes,json,shutil,subprocess,sys,time
from pathlib import Path

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"/"AureateCinematicV4Sandbox.uproject"
EXE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
SCRIPT=Path(__file__).with_name("aureate_v4_full_editor_three_form_stage.py")
RECEIPT=ROOT/"full_editor_three_form_stage_receipt.json"
LOG=ROOT/"ue584_three_form_full_editor_staging.log"
HOST=ROOT/"host_three_form_full_editor_staging_receipt.json"
MAX_SECONDS=170

class Mem(ctypes.Structure):
    _fields_=[("size",ctypes.c_ulong),("load",ctypes.c_ulong),
              ("total",ctypes.c_ulonglong),("avail",ctypes.c_ulonglong),
              ("totalpage",ctypes.c_ulonglong),("availpage",ctypes.c_ulonglong),
              ("totalvirtual",ctypes.c_ulonglong),("availvirtual",ctypes.c_ulonglong),
              ("avail_ext",ctypes.c_ulonglong)]
def free_ram():
    m=Mem();m.size=ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise RuntimeError("No physical memory status")
    return m.avail/1024**3

def main():
    if sys.platform!="win32" or not (PROJECT.is_file() and EXE.is_file() and SCRIPT.is_file()):
        raise RuntimeError("Wrong host or missing source/project")
    proj=json.loads(PROJECT.read_text(encoding="utf8"))
    if proj.get("EngineAssociation")!="5.8" or "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in proj.get("Description",""):
        raise RuntimeError("Not disposable UE 5.8 art sandbox")
    if any(x.exists() for x in (RECEIPT,LOG,HOST)):
        raise FileExistsError("Three-form native stage already attempted")
    for name in ("Seabourne","Submersible","Starbourne"):
        mapfile=PROJECT.parent/"Content"/"TSTSS"/"Review"/"Scenes"/(
           "AureateCinematicV4_"+name+"_20261103_FullEditor.umap")
        if mapfile.exists():
            raise FileExistsError("Refuse existing review map: "+str(mapfile))
    if free_ram()<4.2:
        raise RuntimeError("RAM gate below 4.2 GiB; no NullRHI Editor stage launched")
    if shutil.disk_usage(ROOT).free<14*1024**3:
        raise RuntimeError("Disk gate below 14 GiB")
    processes=subprocess.run(["tasklist","/FI","IMAGENAME eq UnrealEditor-Cmd.exe","/FO","CSV"],
                             capture_output=True,text=True,check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in processes:
        raise RuntimeError("Other UE commandlet active")
    cmd=[str(EXE),str(PROJECT),"-ExecutePythonScript="+str(SCRIPT),
         "-NullRHI","-NoSplash","-NoSound","-Unattended","-nop4",
         "-stdout","-FullStdOutLogOutput"]
    report={"state":"NOT_STARTED","user_editor_untouched":True,
            "gpu_capture_claim":False,"starbourne_story_gate":False,
            "max_runtime_seconds":MAX_SECONDS,"ram_gib_start":round(free_ram(),2)}
    try:
        with LOG.open("x",encoding="utf8") as out:
            proc=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,
                  stdin=subprocess.DEVNULL,cwd=str(ROOT),
                  creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            report["pid"]=proc.pid
            print("V4_THREE_FORM_EDITOR_STARTED",proc.pid,flush=True)
            started=time.monotonic()
            while proc.poll() is None:
                if time.monotonic()-started>MAX_SECONDS:
                    report["state"]="STOPPED_BY_TIMEOUT"
                    proc.terminate();break
                if free_ram()<0.95:
                    report["state"]="STOPPED_BY_LOW_RAM"
                    proc.terminate();break
                time.sleep(2)
            try:code=proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill();code=proc.wait(timeout=5)
        report["exit_code"]=code
        native=json.loads(RECEIPT.read_text(encoding="utf8")) if RECEIPT.is_file() else {"state":"MISSING_NATIVE_RECEIPT"}
        report["native_state"]=native.get("state")
        report["completed_maps"]=native.get("completed_maps",[])
        if report["state"]=="NOT_STARTED":
            report["state"]=("NATIVE_THREE_FORM_STAGE_PASS"
              if code==0 and native.get("state")=="THREE_NATIVE_FULL_EDITOR_REVIEW_MAPS_STAGED_PASS"
              and len(native.get("completed_maps",[]))==3 else "NATIVE_THREE_FORM_STAGE_FAIL")
    finally:
        report["ram_gib_end"]=round(free_ram(),2)
        HOST.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("V4_THREE_FORM_STAGE_RESULT",json.dumps(report,sort_keys=True),flush=True)
        if LOG.exists():
            print("V4_THREE_FORM_NATIVE_LOG_TAIL",
                  LOG.read_text(encoding="utf8",errors="replace")[-2900:],flush=True)
    if report["state"]!="NATIVE_THREE_FORM_STAGE_PASS":sys.exit(1)

if __name__=="__main__": main()
