"""Safe NullRHI native stage of one fresh four-leaf V4 lookdev map."""
import ctypes,json,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"/"AureateCinematicV4Sandbox.uproject"
EXE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
SCRIPT=Path(__file__).with_name("stage_aureate_v4_coupled_habitation_native.py")
NATIVE=ROOT/"native_coupled_habitation_stage_20261104.json"
HOST=ROOT/"native_coupled_habitation_stage_host_20261104.json"
LOG=ROOT/"native_coupled_habitation_stage_host_20261104.log"
MAP=PROJECT.parent/"Content"/"TSTSS"/"Review"/"Scenes"/"AureateV4_Skybourne_CoupledHabitation_20261104.umap"
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
        raise RuntimeError("Physical RAM telemetry unavailable")
    return m.avail/1024**3
def main():
    if sys.platform!="win32" or not all(p.is_file() for p in (PROJECT,EXE,SCRIPT)):
        raise RuntimeError("Wrong Windows host or missing review files")
    conf=json.loads(PROJECT.read_text(encoding="utf8"))
    if conf.get("EngineAssociation")!="5.8" or "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in conf.get("Description",""):
        raise RuntimeError("Refuse production/other Unreal project")
    if any(p.exists() for p in (NATIVE,HOST,LOG,MAP)):
        raise FileExistsError("One-time fresh lookdev already attempted")
    if ram_gib()<4.2:raise RuntimeError("Below 4.2GiB free RAM")
    if shutil.disk_usage(ROOT).free<14*1024**3:
        raise RuntimeError("Below 14GiB free disk")
    active=subprocess.run(["tasklist","/FI","IMAGENAME eq UnrealEditor-Cmd.exe","/FO","CSV"],
                          capture_output=True,text=True,check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in active:raise RuntimeError("Other UE commandlet active")
    cmd=[str(EXE),str(PROJECT),"-ExecutePythonScript="+str(SCRIPT),
         "-NullRHI","-Unattended","-NoSplash","-NoSound","-nop4",
         "-stdout","-FullStdOutLogOutput"]
    report={"state":"NOT_STARTED","user_editor_untouched":True,
            "gameplay_modified":False,"original_four_form_maps_unchanged":True,
            "starbourne_player_unlocked":False,"starting_ram_gib":round(ram_gib(),2)}
    try:
        with LOG.open("x",encoding="utf8") as out:
            process=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,
                  stdin=subprocess.DEVNULL,cwd=str(ROOT),
                  creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            report["pid"]=process.pid
            print("COUPLED_HABITATION_STAGE_STARTED",process.pid,flush=True)
            start=time.monotonic()
            while process.poll() is None:
                if time.monotonic()-start>MAX_SECONDS or ram_gib()<.95:
                    report["state"]="STOPPED_BY_RAM_OR_TIME_WATCHDOG"
                    process.terminate();break
                time.sleep(2)
            try:code=process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill();code=process.wait(timeout=5)
        report["engine_exit_code"]=code
        native=json.loads(NATIVE.read_text(encoding="utf8")) if NATIVE.is_file() else {}
        report["native_state"]=native.get("state","MISSING_NATIVE_RECEIPT")
        report["new_map_sha256"]=native.get("map_sha256")
        if report["state"]=="NOT_STARTED":
            report["state"]=("NATIVE_COUPLED_HABITATION_STAGE_PASS" if
              code==0 and native.get("state")=="NATIVE_FRESH_COUPLED_HABITATION_REVIEW_STAGE_PASS"
              and native.get("leaf_wing_count")==4 and native.get("native_actor_count")==15
              else "NATIVE_COUPLED_HABITATION_STAGE_HOLD")
    finally:
        report["ending_ram_gib"]=round(ram_gib(),2)
        HOST.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf8")
        print("COUPLED_HABITATION_STAGE_RESULT",json.dumps(report,sort_keys=True),flush=True)
        if LOG.is_file():
            logs=LOG.read_text(encoding="utf8",errors="replace").splitlines()
            print("COUPLED_HABITATION_STAGE_LOG_ERRORS",
                  [x for x in logs if "LogPython: Error:" in x or
                   "Fatal error" in x or "V4_COUPLED_HABITATION_NATIVE_STAGE" in x][-8:],flush=True)
    if report["state"]!="NATIVE_COUPLED_HABITATION_STAGE_PASS":sys.exit(1)
if __name__=="__main__":main()
