"""Bounded native NullRHI audit of four existing V4 maps; no edits."""
from pathlib import Path
import ctypes,json,shutil,subprocess,sys,time

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"/"AureateCinematicV4Sandbox.uproject"
EXE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
SCRIPT=Path(__file__).with_name("audit_aureate_v4_four_native_maps_readonly.py")
NATIVE=ROOT/"four_map_native_readonly_audit_v2_20261103.json"
HOST=ROOT/"host_four_map_native_readonly_audit_v2_20261103.json"
LOG=ROOT/"four_map_native_readonly_audit_v2_20261103.log"
MAX_SECONDS=130

class Mem(ctypes.Structure):
    _fields_=[("size",ctypes.c_ulong),("load",ctypes.c_ulong),
              ("total",ctypes.c_ulonglong),("avail",ctypes.c_ulonglong),
              ("totalpage",ctypes.c_ulonglong),("availpage",ctypes.c_ulonglong),
              ("totalvirtual",ctypes.c_ulonglong),("availvirtual",ctypes.c_ulonglong),
              ("avail_ext",ctypes.c_ulonglong)]
def ram_gib():
    m=Mem();m.size=ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise RuntimeError("No physical RAM telemetry")
    return m.avail/1024**3

def main():
    if sys.platform!="win32" or not (PROJECT.is_file() and EXE.is_file() and SCRIPT.is_file()):
        raise RuntimeError("Missing sandbox, Windows engine or audit")
    config=json.loads(PROJECT.read_text(encoding="utf8"))
    if config.get("EngineAssociation")!="5.8" or "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in config.get("Description",""):
        raise RuntimeError("Refuse nonreview project")
    if any(p.exists() for p in (NATIVE,HOST,LOG)):
        raise FileExistsError("Refuse prior audit evidence")
    if ram_gib()<4.2:raise RuntimeError("Insufficient free RAM for NullRHI audit")
    if shutil.disk_usage(ROOT).free<14*1024**3:raise RuntimeError("Insufficient disk space")
    active=subprocess.run(["tasklist","/FI","IMAGENAME eq UnrealEditor-Cmd.exe","/FO","CSV"],
        capture_output=True,text=True,check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in active:raise RuntimeError("Other Unreal commandlet active")
    cmd=[str(EXE),str(PROJECT),"-ExecutePythonScript="+str(SCRIPT),
         "-NullRHI","-Unattended","-NoSplash","-NoSound","-nop4",
         "-stdout","-FullStdOutLogOutput"]
    host={"state":"NOT_STARTED","user_editor_untouched":True,
          "starbourne_unlocked":False,"max_seconds":MAX_SECONDS,
          "starting_free_ram_gib":round(ram_gib(),2)}
    try:
        with LOG.open("x",encoding="utf8") as out:
            process=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,
                 stdin=subprocess.DEVNULL,cwd=str(ROOT),
                 creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            host["pid"]=process.pid
            print("V4_FOUR_MAP_READONLY_AUDIT_STARTED",process.pid,flush=True)
            start=time.monotonic()
            while process.poll() is None:
                if time.monotonic()-start>MAX_SECONDS or ram_gib()<0.95:
                    host["state"]="STOPPED_BY_TIME_OR_LOW_MEMORY"
                    process.terminate()
                    break
                time.sleep(2)
            try:exit_code=process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill();exit_code=process.wait(timeout=5)
        host["exit_code"]=exit_code
        receipt=json.loads(NATIVE.read_text(encoding="utf8")) if NATIVE.exists() else {}
        host["native_state"]=receipt.get("state","NO_NATIVE_RECEIPT")
        host["four_review_maps"]=len(receipt.get("forms",[]))
        if host["state"]=="NOT_STARTED":
            host["state"]=("NATIVE_FOUR_MAP_READONLY_PASS" if exit_code==0 and
               receipt.get("state")=="FOUR_MAP_READONLY_NATIVE_AUDIT_PASS" and
               len(receipt.get("forms",[]))==4 else "NATIVE_FOUR_MAP_READONLY_HOLD")
    finally:
        host["ending_free_ram_gib"]=round(ram_gib(),2)
        HOST.write_text(json.dumps(host,sort_keys=True,indent=2)+"\n",encoding="utf8")
        print("V4_FOUR_MAP_AUDIT_RESULT",json.dumps(host,sort_keys=True),flush=True)
        if LOG.exists():
            data=LOG.read_text(encoding="utf8",errors="replace")
            print("V4_FOUR_MAP_AUDIT_LOG_TAIL",data[-2500:],flush=True)
    if host["state"]!="NATIVE_FOUR_MAP_READONLY_PASS":sys.exit(1)
if __name__=="__main__":main()
