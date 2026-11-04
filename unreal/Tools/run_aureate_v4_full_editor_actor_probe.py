#!/usr/bin/env python3
"""Single-run guard for a NEW full-editor UE 5.8.4 actor-creation micro-test.

Never uses the playable game project. Never terminates other Unreal sessions.
"""
from pathlib import Path
import ctypes,json,shutil,subprocess,sys,time,os

ROOT=Path("C:/tmp/TSTSS_AureateV4_ActorPilot_20261103")
PROJ=ROOT/"AureateActorPilot"
UPROJ=PROJ/"AureateActorPilot.uproject"
SOURCE=Path(__file__).with_name("aureate_v4_full_editor_actor_probe.py")
UE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
LOG=ROOT/"full_editor_actor_pilot.log"
RECEIPT=ROOT/"full_editor_actor_probe_receipt.json"
HOST=ROOT/"host_actor_probe_run.json"
MAX_SECONDS=180

class MemoryStatus(ctypes.Structure):
    _fields_=[("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
              ("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),
              ("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),
              ("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),
              ("ullAvailExtendedVirtual",ctypes.c_ulonglong)]
def free_ram():
    s=MemoryStatus();s.dwLength=ctypes.sizeof(s)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s)):
        raise RuntimeError("RAM read failure")
    return s.ullAvailPhys/(1024**3)
def main():
    if sys.platform!="win32" or not UE.is_file() or not SOURCE.is_file():
        raise RuntimeError("Verified Windows UE 5.8.4 and script are required")
    if ROOT.exists():raise FileExistsError("Refuse existing pilot; no repeat")
    if free_ram()<4.2:raise RuntimeError("Need >=4.2 GiB free RAM before full Editor test")
    if shutil.disk_usage(ROOT.parent).free<14*1024**3:
        raise RuntimeError("Need >=14 GiB free disk")
    running=subprocess.run(["tasklist","/FI","IMAGENAME eq UnrealEditor-Cmd.exe","/FO","CSV"],
                           capture_output=True,text=True,check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in running:
        raise RuntimeError("Another commandlet in progress; do not compete")
    ROOT.mkdir()
    PROJ.mkdir()
    (PROJ/"Content").mkdir()
    (PROJ/"Config").mkdir()
    (PROJ/"Config"/"DefaultEngine.ini").write_text(
        "[Core.Log]\nLogPython=Verbose\n",encoding="utf8")
    UPROJ.write_text(json.dumps({
        "FileVersion":3,"EngineAssociation":"5.8","Category":"Games",
        "Description":"AUREATE_ONE_ACTOR_PILOT_ONLY; disposable full Editor test",
        "Plugins":[{"Name":"PythonScriptPlugin","Enabled":True},
                   {"Name":"EditorScriptingUtilities","Enabled":True}]
    },indent=2)+"\n",encoding="utf8")
    report={"state":"NOT_STARTED",
            "project":str(UPROJ),"source_script":str(SOURCE),
            "user_unreal_editor_untouched":True,"starbourne_player_unlock":False,
            "no_production_content":True,"runtime_max_seconds":MAX_SECONDS,
            "started_ram_gib":round(free_ram(),2)}
    command=[str(UE),str(UPROJ),"-ExecutePythonScript="+str(SOURCE),
             "-NullRHI","-NoSplash","-NoSound","-Unattended","-nop4","-stdout",
             "-FullStdOutLogOutput"]
    proc=None
    try:
        with LOG.open("w",encoding="utf8") as o:
            proc=subprocess.Popen(command,stdout=o,stderr=subprocess.STDOUT,
                 stdin=subprocess.DEVNULL,cwd=str(ROOT),
                 creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            report["created_pid"]=proc.pid
            print("V4_FULL_EDITOR_PILOT_LAUNCHED",proc.pid,flush=True)
            started=time.monotonic()
            while proc.poll() is None:
                elapsed=time.monotonic()-started
                memory=free_ram()
                if memory<0.95 or elapsed>MAX_SECONDS:
                    report["state"]="STOPPED_BY_MEMORY_OR_TIME_GUARD"
                    proc.terminate()
                    break
                time.sleep(2)
            try:code=proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill();code=proc.wait(timeout=5)
            report["engine_exit_code"]=code
        if RECEIPT.exists():
            child=json.loads(RECEIPT.read_text(encoding="utf8"))
            report["native_actor_result"]=child
        else:report["native_actor_result"]={"state":"NO_NATIVE_RECEIPT"}
        if report["state"]=="NOT_STARTED":
            report["state"]=("ONE_ACTOR_PILOT_NATIVE_PASS"
             if code==0 and report["native_actor_result"].get("state")==
                    "NATIVE_FULL_EDITOR_ONE_ACTOR_AND_MAP_SAVE_PASS"
             else "ONE_ACTOR_PILOT_NATIVE_FAIL")
    finally:
        report["ending_ram_gib"]=round(free_ram(),2)
        HOST.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("V4_FULL_EDITOR_PILOT_RESULT",json.dumps(report,sort_keys=True),flush=True)
        if LOG.exists():
            data=LOG.read_text(encoding="utf8",errors="replace")
            print("V4_FULL_EDITOR_PILOT_LOG_TAIL",data[-3000:],flush=True)
    if report["state"]!="ONE_ACTOR_PILOT_NATIVE_PASS":sys.exit(1)
if __name__=="__main__":
    main()
