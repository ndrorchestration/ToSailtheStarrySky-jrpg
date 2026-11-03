"""Resource-gated D3D11 Skybourne screenshot capture in review sandbox.

Each attempt uses unique logs / host receipts. The review map and target image
directory stay immutable/unique; no overwrite or automatic retries. No user
Unreal process is terminated. An engine exit 0 without a positive *native*
receipt is a failure.
"""
import argparse,ctypes,json,re,shutil,subprocess,sys,time
from pathlib import Path

ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"/"AureateCinematicV4Sandbox.uproject"
EXE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
SCRIPT=Path(__file__).with_name("capture_aureate_v4_skybourne_native_gpu.py")
OUT=ROOT/"SkybourneV4NativeGPU_20261103"
RECEIPT=OUT/"native_skybourne_gpu_capture_receipt.json"
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
        raise RuntimeError("Windows RAM status unavailable")
    return m.avail/1024**3

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--attempt",required=True,
                   help="Unique audit token (e.g. attempt02); no overwrite")
    a=p.parse_args(argv)
    if not re.fullmatch(r"[a-z][a-z0-9_-]{2,24}",a.attempt):
        raise ValueError("Invalid attempt label")
    LOG=ROOT/("ue584_skybourne_d3d11_gpu_capture_"+a.attempt+".log")
    HOST=ROOT/("host_skybourne_d3d11_gpu_capture_"+a.attempt+".json")
    if sys.platform!="win32" or not (EXE.is_file() and SCRIPT.is_file() and PROJECT.is_file()):
        raise RuntimeError("Missing Windows UE 5.8.4 or review files")
    project=json.loads(PROJECT.read_text(encoding="utf8"))
    if project.get("EngineAssociation")!="5.8" or "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in project.get("Description",""):
        raise RuntimeError("Refuse non-review project")
    if any(x.exists() for x in (OUT,LOG,HOST)):
        raise FileExistsError("Review capture/attempt exists; preserve and refuse overwrite")
    # D3D11 startup previously consumed all safe memory during the 5.53 GiB
    # headroom run; avoid repeating that risk before 6.5 GiB is available.
    if free_ram()<6.5:
        raise RuntimeError("Free RAM below 6.5 GiB; no GPU capture launched")
    if shutil.disk_usage(ROOT).free<14*1024**3:
        raise RuntimeError("Disk below 14 GiB; no GPU capture launched")
    running=subprocess.run(["tasklist","/FI","IMAGENAME eq UnrealEditor-Cmd.exe","/FO","CSV"],
                           capture_output=True,text=True,check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in running:
        raise RuntimeError("Another UE commandlet running")
    cmd=[str(EXE),str(PROJECT),"-ExecutePythonScript="+str(SCRIPT),
         "-d3d11","-NoSplash","-NoSound","-Unattended","-nop4",
         "-stdout","-FullStdOutLogOutput"]
    info={"state":"NOT_LAUNCHED","gpu_mode":"D3D11",
          "attempt":a.attempt,"user_editor_untouched":True,
          "new_art_approval":False,"player_starbourne_unlocked":False,
          "max_runtime_sec":MAX_SECONDS,"ram_gib_before":round(free_ram(),2)}
    try:
        with LOG.open("x",encoding="utf8") as fd:
            proc=subprocess.Popen(cmd,stdout=fd,stderr=subprocess.STDOUT,
                 stdin=subprocess.DEVNULL,cwd=str(ROOT),
                 creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            info["pid"]=proc.pid
            print("SKYBOURNE_V4_D3D11_STARTED",a.attempt,proc.pid,flush=True)
            start=time.monotonic()
            while proc.poll() is None:
                if time.monotonic()-start>MAX_SECONDS:
                    info["state"]="STOPPED_BY_TIME_WATCHDOG"
                    proc.terminate()
                    break
                if free_ram()<1.5:
                    info["state"]="STOPPED_BY_MEMORY_WATCHDOG"
                    proc.terminate()
                    break
                time.sleep(2)
            try: exit_code=proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill();exit_code=proc.wait(timeout=5)
        info["exit_code"]=exit_code
        native=json.loads(RECEIPT.read_text(encoding="utf8")) if RECEIPT.is_file() else {"state":"NO_NATIVE_RECEIPT"}
        info["native_state"]=native.get("state")
        info["png_sha256"]=native.get("png_sha256")
        info["png_dimensions"]=native.get("actual_dimensions")
        if info["state"]=="NOT_LAUNCHED":
            info["state"]=("NATIVE_GPU_CAPTURE_TASK_PASS_PIXEL_QA_PENDING"
              if exit_code==0 and native.get("state")=="NATIVE_D3D11_CAPTURE_ONE_FRAME_TASK_PASS_PIXEL_QA_PENDING"
              else "NATIVE_GPU_CAPTURE_NOT_VERIFIED")
    finally:
        info["ram_gib_after"]=round(free_ram(),2)
        HOST.write_text(json.dumps(info,indent=2,sort_keys=True)+"\n",encoding="utf8")
        print("SKYBOURNE_V4_D3D11_RESULT",json.dumps(info,sort_keys=True),flush=True)
        if LOG.exists():
            print("SKYBOURNE_V4_D3D11_LOG_TAIL",
                  LOG.read_text(encoding="utf8",errors="replace")[-2800:],flush=True)
    if info["state"]!="NATIVE_GPU_CAPTURE_TASK_PASS_PIXEL_QA_PENDING":
        sys.exit(1)

if __name__=="__main__":main()
