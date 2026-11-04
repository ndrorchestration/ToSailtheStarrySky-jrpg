"""One-time resource-gated UE5.8 NullRHI leaf-wing source review intake."""
from pathlib import Path
import ctypes,json,shutil,subprocess,sys,time

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"/"AureateCinematicV4Sandbox.uproject"
EXE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
SCRIPT=Path(__file__).with_name("intake_aureate_v4_coupled_habitation_native.py")
NATIVE=ROOT/"coupled_habitation_native_import_20261104.json"
HOST=ROOT/"coupled_habitation_native_host_20261104.json"
LOG=ROOT/"coupled_habitation_native_host_20261104.log"
MAX_SECONDS=150
class Mem(ctypes.Structure):
    _fields_=[("size",ctypes.c_ulong),("load",ctypes.c_ulong),
              ("total",ctypes.c_ulonglong),("avail",ctypes.c_ulonglong),
              ("totalpage",ctypes.c_ulonglong),("availpage",ctypes.c_ulonglong),
              ("totalvirtual",ctypes.c_ulonglong),("availvirtual",ctypes.c_ulonglong),
              ("avail_ext",ctypes.c_ulonglong)]
def free_ram():
    m=Mem();m.size=ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise RuntimeError("Cannot measure available RAM")
    return m.avail/1024**3
def main():
    if sys.platform!="win32" or not all(p.is_file() for p in (PROJECT,EXE,SCRIPT)):
        raise RuntimeError("Review host/project/engine/script unavailable")
    conf=json.loads(PROJECT.read_text(encoding="utf8"))
    if conf.get("EngineAssociation")!="5.8" or "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in conf.get("Description",""):
        raise RuntimeError("Refuse nonreview Unreal project")
    if any(p.exists() for p in (NATIVE,HOST,LOG)):
        raise FileExistsError("One-time wing-native test already attempted")
    if free_ram()<4.2:raise RuntimeError("Free RAM below 4.2GiB")
    if shutil.disk_usage(ROOT).free<14*1024**3:
        raise RuntimeError("Free disk below 14GiB")
    running=subprocess.run(["tasklist","/FI","IMAGENAME eq UnrealEditor-Cmd.exe","/FO","CSV"],
                           capture_output=True,text=True,check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in running:
        raise RuntimeError("Concurrent Unreal commandlet refused")
    command=[str(EXE),str(PROJECT),"-ExecutePythonScript="+str(SCRIPT),
             "-NullRHI","-NoSplash","-NoSound","-Unattended","-nop4",
             "-stdout","-FullStdOutLogOutput"]
    report={"state":"NOT_STARTED","user_editor_untouched":True,
            "gameplay_changed":False,"starbourne_player_unlocked":False,
            "max_runtime_sec":MAX_SECONDS,"start_free_ram_gib":round(free_ram(),2)}
    try:
        with LOG.open("x",encoding="utf8") as log:
            proc=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,
                                  stdin=subprocess.DEVNULL,cwd=str(ROOT),
                                  creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            report["pid"]=proc.pid
            print("NATIVE_HABITATION_INTAKE_STARTED",proc.pid,flush=True)
            started=time.monotonic()
            while proc.poll() is None:
                if time.monotonic()-started>MAX_SECONDS or free_ram()<1.0:
                    report["state"]="STOPPED_BY_RAM_OR_TIMEOUT_WATCHDOG"
                    proc.terminate()
                    break
                time.sleep(2)
            try:code=proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill();code=proc.wait(timeout=5)
        report["engine_exit_code"]=code
        native=json.loads(NATIVE.read_text(encoding="utf8")) if NATIVE.exists() else {}
        report["native_state"]=native.get("state","MISSING_NATIVE_RECEIPT")
        report["imported_meshes"]=native.get("imported",{})
        if report["state"]=="NOT_STARTED":
            report["state"]=("NATIVE_HABITATION_IMPORT_PASS" if
                code==0 and native.get("state")=="TWO_NATIVE_NONCANONICAL_HABITATION_MESHES_IMPORT_PASS"
                else "NATIVE_HABITATION_IMPORT_HOLD")
    finally:
        report["end_free_ram_gib"]=round(free_ram(),2)
        HOST.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("NATIVE_HABITATION_IMPORT_RESULT",json.dumps(report,sort_keys=True),flush=True)
        if LOG.is_file():
            data=LOG.read_text(encoding="utf8",errors="replace").splitlines()
            errs=[line for line in data if ("LogPython: Error:" in line or
                 "COUPLED_HABITATION_V4_NATIVE_INTAKE" in line or "Error:" in line)]
            print("NATIVE_HABITATION_IMPORT_LOG_EVENTS",errs[-12:],flush=True)
    if report["state"]!="NATIVE_HABITATION_IMPORT_PASS":sys.exit(1)
if __name__=="__main__":main()
