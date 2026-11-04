"""Single isolated V4 Skybourne D3D11 screenshot via *registered* UE PythonAutomationTest.

Corrects the prior bare ExecutePythonScript case in which the latent callback
never ticked. Does not alter active user Editor or existing four review maps.
"""
from pathlib import Path
import ctypes,hashlib,json,shutil,subprocess,sys,time
ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT=ROOT/"AureateCinematicV4Sandbox"/"AureateCinematicV4Sandbox.uproject"
EXE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
SCRIPT=Path(__file__).with_name("capture_aureate_v4_habitation_gpu_automation13.py")
REG=PROJECT.parent/"Content"/"Python"/"test_aureate_v4_habitation_automation13.py"
TEST="Editor.Python.AureateCinematicV4Sandbox.test_aureate_v4_habitation_automation13"
OUTPUT=ROOT/"SkybourneV4HabitationGPU_20261104_Automation13"
RECEIPT=OUTPUT/"native_skybourne_gpu_capture_receipt.json"
PNG=OUTPUT/"Skybourne_V4_UE584_D3D11_ThreeQuarter_REVIEW.png"
REPORT=ROOT/"SkybourneV4Habitation_D3D11_Automation13_Report"
LOG=ROOT/"skybourne_v4_habitation_d3d11_automation13_native.log"
HOST=ROOT/"skybourne_v4_habitation_d3d11_automation13_host_receipt.json"
MAX_SECONDS=190
class Mem(ctypes.Structure):
    _fields_=[("size",ctypes.c_ulong),("load",ctypes.c_ulong),
              ("total",ctypes.c_ulonglong),("avail",ctypes.c_ulonglong),
              ("totalpage",ctypes.c_ulonglong),("availpage",ctypes.c_ulonglong),
              ("totalvirtual",ctypes.c_ulonglong),("availvirtual",ctypes.c_ulonglong),
              ("avail_ext",ctypes.c_ulonglong)]
def free_ram():
    m=Mem();m.size=ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise RuntimeError("Physical RAM status unavailable")
    return m.avail/1024**3
def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()

def main():
    if sys.platform!="win32" or not all(x.is_file() for x in (PROJECT,EXE,SCRIPT,REG)):
        raise RuntimeError("Missing Windows, engine or registered private review scripts")
    conf=json.loads(PROJECT.read_text(encoding="utf8"))
    plugins={x["Name"] for x in conf.get("Plugins",[]) if x.get("Enabled")}
    if conf.get("EngineAssociation")!="5.8" or \
       "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in conf.get("Description","") or \
       not {"PythonScriptPlugin","PythonAutomationTest"}<=plugins:
        raise RuntimeError("Expected strictly disposable Python-test-enabled UE 5.8 review project")
    if any(x.exists() for x in (OUTPUT,REPORT,LOG,HOST)):
        raise FileExistsError("Previous automation capture attempt: refuse overwrite")
    if "capture_aureate_v4_habitation_gpu_automation13.py" not in REG.read_text(encoding="utf8"):
        raise RuntimeError("Unexpected Python automation registration")
    if free_ram()<6.5:raise RuntimeError("D3D11 preflight below 6.5 GiB free RAM")
    if shutil.disk_usage(ROOT).free<14*1024**3:raise RuntimeError("D3D11 disk preflight below 14 GiB")
    running=subprocess.run(["tasklist","/FI","IMAGENAME eq UnrealEditor-Cmd.exe","/FO","CSV"],
        capture_output=True,text=True,check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in running:raise RuntimeError("Concurrent UE commandlet refused")
    args=[str(EXE),str(PROJECT),"-d3d11","-Unattended","-NoSplash","-NoSound",
          "-nop4","-stdout","-FullStdOutLogOutput",
          "-ExecCmds=Automation RunTest "+TEST+";Quit",
          "-ReportExportPath="+str(REPORT)]
    result={"state":"NOT_STARTED","expected_named_test":TEST,
            "source_sha256":sha(SCRIPT),"registration_sha256":sha(REG),
            "gameplay_modified":False,"user_editor_touched":False,
            "starbourne_player_unlocked":False,
            "start_free_ram_gib":round(free_ram(),2)}
    try:
        with LOG.open("x",encoding="utf8") as log:
            proc=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,
                 stdin=subprocess.DEVNULL,cwd=str(ROOT),
                 creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            result["pid"]=proc.pid
            print("REGISTERED_SKYBOURNE_V4_D3D11_AUTOMATION_STARTED",proc.pid,flush=True)
            t0=time.monotonic()
            while proc.poll() is None:
                if time.monotonic()-t0>MAX_SECONDS or free_ram()<1.5:
                    result["state"]="STOPPED_BY_RAM_OR_TIMEOUT_WATCHDOG"
                    proc.terminate()
                    break
                time.sleep(2)
            try:code=proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill();code=proc.wait(timeout=5)
        result["engine_exit_code"]=code
        data=json.loads(RECEIPT.read_text(encoding="utf8")) if RECEIPT.is_file() else {}
        result["native_receipt_state"]=data.get("state","NO_NATIVE_RECEIPT")
        result["native_png_sha256"]=data.get("png_sha256")
        result["native_png_dimensions"]=data.get("actual_dimensions")
        logtext=LOG.read_text(encoding="utf8",errors="replace")
        controller=("Result={Success}" in logtext and TEST in logtext
                    and "Test Completed." in logtext)
        result["named_automation_controller_success"]=bool(controller)
        result["png_file_exists"]=PNG.is_file()
        result["actual_png_sha256"]=sha(PNG) if PNG.is_file() else None
        if result["state"]=="NOT_STARTED":
            result["state"]=("SKYBOURNE_V4_REGISTERED_GPU_CAPTURE_PASS_PIXEL_QA_PENDING"
                if code==0 and controller and PNG.is_file() and
                   data.get("state")=="NATIVE_D3D11_CAPTURE_ONE_FRAME_TASK_PASS_PIXEL_QA_PENDING" and
                   data.get("png_sha256")==sha(PNG) else
                   "SKYBOURNE_V4_REGISTERED_GPU_CAPTURE_HOLD")
    finally:
        result["end_free_ram_gib"]=round(free_ram(),2)
        HOST.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
        print("REGISTERED_SKYBOURNE_GPU_RESULT",json.dumps(result,sort_keys=True),flush=True)
        if LOG.is_file():
            lines=LOG.read_text(encoding="utf8",errors="replace").splitlines()
            matches=[x for x in lines if ("AutomationController" in x or "AutomationCommandLine" in x or
                        "V4_SKY" in x or "Error:" in x)]
            print("REGISTERED_SKYBOURNE_GPU_NATIVE_LOG_MATCHES",matches[-16:],flush=True)
    if result["state"]!="SKYBOURNE_V4_REGISTERED_GPU_CAPTURE_PASS_PIXEL_QA_PENDING":
        sys.exit(1)
if __name__=="__main__":main()
