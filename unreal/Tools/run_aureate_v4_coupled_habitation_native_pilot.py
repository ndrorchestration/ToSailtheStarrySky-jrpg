"""Resource-gated one-time UE5.8 NullRHI bridge+quarters pivot test."""
import ctypes,json,shutil,subprocess,sys,time
from pathlib import Path

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"/"AureateCinematicV4Sandbox.uproject"
EXE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
SCRIPT=Path(__file__).with_name("stage_aureate_v4_coupled_habitation_native_pilot.py")
OUTPUT=ROOT/"coupled_habitation_native_pilot_receipt_20261103.json"
LOG=ROOT/"coupled_habitation_native_pilot_host_20261103.log"
HOST=ROOT/"coupled_habitation_native_host_receipt_20261103.json"
MAPFILE=PROJECT.parent/"Content"/"TSTSS"/"Review"/"Scenes"/"AureateV4_HabitationCoupledPivot_20261103_PILOT.umap"
MAX_SECONDS=160
class Mem(ctypes.Structure):
    _fields_=[("size",ctypes.c_ulong),("load",ctypes.c_ulong),
              ("total",ctypes.c_ulonglong),("avail",ctypes.c_ulonglong),
              ("totalpage",ctypes.c_ulonglong),("availpage",ctypes.c_ulonglong),
              ("totalvirtual",ctypes.c_ulonglong),("availvirtual",ctypes.c_ulonglong),
              ("avail_ext",ctypes.c_ulonglong)]
def ram_gib():
    m=Mem();m.size=ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise RuntimeError("Physical memory data unavailable")
    return m.avail/1024**3
def main():
    if sys.platform!="win32" or not all(x.is_file() for x in (PROJECT,EXE,SCRIPT)):
        raise RuntimeError("Wrong host or missing Unreal review files")
    conf=json.loads(PROJECT.read_text(encoding="utf8"))
    if conf.get("EngineAssociation")!="5.8" or "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in conf.get("Description",""):
        raise RuntimeError("Non-review Unreal project")
    if any(x.exists() for x in (OUTPUT,LOG,HOST,MAPFILE)):
        raise FileExistsError("Pivot pilot already attempted, refuse replacement")
    if ram_gib()<4.2:raise RuntimeError("Free RAM below 4.2 GiB, no native pilot")
    if shutil.disk_usage(ROOT).free<14*1024**3:raise RuntimeError("Disk below 14 GiB")
    active=subprocess.run(["tasklist","/FI","IMAGENAME eq UnrealEditor-Cmd.exe","/FO","CSV"],
                          capture_output=True,text=True,check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in active:raise RuntimeError("Other UE commandlet active")
    command=[str(EXE),str(PROJECT),"-ExecutePythonScript="+str(SCRIPT),
             "-NullRHI","-Unattended","-NoSplash","-NoSound","-nop4",
             "-stdout","-FullStdOutLogOutput"]
    host={"state":"NOT_STARTED","user_editor_untouched":True,
          "source_skybourne_scene_unchanged":True,"starbourne_unlocked":False,
          "ram_gib_start":round(ram_gib(),2),"runtime_cap_sec":MAX_SECONDS}
    try:
        with LOG.open("x",encoding="utf8") as out:
            proc=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT,
                   stdin=subprocess.DEVNULL,cwd=str(ROOT),
                   creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            host["pid"]=proc.pid
            print("COUPLED_BRIDGE_QUARTERS_NATIVE_PILOT_STARTED",proc.pid,flush=True)
            start=time.monotonic()
            while proc.poll() is None:
                if time.monotonic()-start>MAX_SECONDS or ram_gib()<0.95:
                    host["state"]="STOPPED_BY_RESOURCE_WATCHDOG"
                    proc.terminate();break
                time.sleep(2)
            try:code=proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill();code=proc.wait(timeout=5)
        host["exit_code"]=code
        data=json.loads(OUTPUT.read_text(encoding="utf8")) if OUTPUT.is_file() else {}
        host["native_state"]=data.get("state","MISSING_NATIVE_RECEIPT")
        host["map_sha256"]=data.get("saved_map_sha256")
        if host["state"]=="NOT_STARTED":
            host["state"]=("NATIVE_COUPLED_PIVOT_PASS" if code==0 and
                data.get("state")=="NATIVE_COUPLED_HABITATION_REVIEW_PIVOT_PASS"
                and data.get("review_angle_restored") is True
                else "NATIVE_COUPLED_PIVOT_HOLD")
    finally:
        host["ram_gib_end"]=round(ram_gib(),2)
        HOST.write_text(json.dumps(host,sort_keys=True,indent=2)+"\n",encoding="utf8")
        print("COUPLED_PIVOT_HOST_RESULT",json.dumps(host,sort_keys=True),flush=True)
        if LOG.is_file():
            print("COUPLED_PIVOT_HOST_LOG_TAIL",LOG.read_text(encoding="utf8",errors="replace")[-2500:],flush=True)
    if host["state"]!="NATIVE_COUPLED_PIVOT_PASS":sys.exit(1)
if __name__=="__main__":main()
