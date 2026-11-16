#!/usr/bin/env python3
"""Native snapshot runner and source-only conservative verifier adapter."""
import argparse, ctypes, hashlib, importlib.util, json, os, re, shutil, stat, subprocess, sys, uuid
from pathlib import Path
import aureate_envelope_records as records
ROOT=Path(__file__).resolve().parents[2]
PROJECT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103/AureateCinematicV4Sandbox").resolve()
UE=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
REC=Path(__file__).with_name("export_aureate_envelopes_native.py")
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def output_path(p):
    p=p.resolve()
    if p.exists() or not p.parent.is_dir() or p.is_relative_to(ROOT.resolve()) or p.is_relative_to(PROJECT):
        raise ValueError("HOLD output must be new and outside checkout and project")
    return p
def combine(a):
    out=output_path(a.output)
    raw=[p.read_bytes() for p in (a.start,a.end,a.labels)]
    start,end,mapping=[json.loads(v) for v in raw]
    if set(mapping)!={"start","end"}: raise ValueError("HOLD mappings need start and end")
    config=records.build_config(start,end,mapping["start"],mapping["end"],a.clearance)
    path=ROOT/"unreal/ArtSource/ShipReview/aureate_swept_clearance.py"
    spec=importlib.util.spec_from_file_location("swept",path); verifier=importlib.util.module_from_spec(spec); spec.loader.exec_module(verifier)
    result=verifier.verify(config)
    payload={"status":"SOURCE_SIDE_BOX_SCREEN_NOT_NATIVE_COLLISION_PROOF","config":config,"verifier":result,
      "snapshot_sha256":{"start":hashlib.sha256(raw[0]).hexdigest(),"end":hashlib.sha256(raw[1]).hexdigest()},
      "label_mapping_sha256":hashlib.sha256(raw[2]).hexdigest(),
      "source_maps":{"start":start["map_sha256"],"end":end["map_sha256"]},
      "shared_frame":"OPERATOR_ASSERTED_NOT_VERIFIED","actual_animation_path_verified":False,
      "native_collision_verified":False,"creator_approved":False,"gameplay_authorized":False,
      "mesh_package_bytes_verified":False}
    encoded=json.dumps(payload,indent=2,allow_nan=False)
    with out.open("x",encoding="utf-8") as f: f.write(encoded)
    print("SOURCE_ONLY_VERDICT",result["verdict"],"output",out)
    return 0 if result["verdict"]==verifier.V_CLEAR else 1
class MEMORY(ctypes.Structure):
    _fields_=[("size",ctypes.c_ulong),("load",ctypes.c_ulong),("total",ctypes.c_ulonglong),("available",ctypes.c_ulonglong),("page",ctypes.c_ulonglong),("pagefree",ctypes.c_ulonglong),("virt",ctypes.c_ulonglong),("virtfree",ctypes.c_ulonglong),("extended",ctypes.c_ulonglong)]
def free_ram():
    m=MEMORY(); m.size=ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)): raise RuntimeError("HOLD memory unavailable")
    return m.available
def inventory(p):
    return {str(x.relative_to(p)):sha(x) for x in p.rglob("*") if x.is_file()} if p.exists() else {}
def native_export(a):
    if sys.platform!="win32": raise RuntimeError("HOLD native export requires Windows")
    out=output_path(a.output)
    if not re.fullmatch(r"/Game/TSTSS/Review/Scenes/[A-Za-z0-9_]+",a.map): raise ValueError("HOLD invalid review map")
    if not re.fullmatch(r"[0-9a-f]{64}",a.map_sha256) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}",a.frame): raise ValueError("HOLD map hash or frame")
    mapfile=PROJECT/"Content"/Path(a.map.removeprefix("/Game/")+".umap")
    project=PROJECT/"AureateCinematicV4Sandbox.uproject"
    if not UE.is_file() or not project.is_file() or not mapfile.is_file() or sha(mapfile)!=a.map_sha256: raise RuntimeError("HOLD missing or changed review input")
    version=json.loads((UE.parents[2]/"Build"/"Build.version").read_text(encoding="utf-8"))
    if [version.get(k) for k in ("MajorVersion","MinorVersion","PatchVersion")]!=[5,8,4]: raise RuntimeError("HOLD wrong Unreal version")
    desc=json.loads(project.read_text(encoding="utf-8"))
    if "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in desc.get("Description",""): raise RuntimeError("HOLD wrong project")
    head=subprocess.run(["git","-C",str(ROOT),"rev-parse","HEAD"],capture_output=True,text=True,check=True).stdout.strip()
    dirty=subprocess.run(["git","-C",str(ROOT),"status","--porcelain","-uall"],capture_output=True,text=True,check=True).stdout
    if not re.fullmatch(r"[0-9a-f]{40}",a.expected_head) or head!=a.expected_head or dirty: raise RuntimeError("HOLD exact clean source required")
    running=subprocess.run(["tasklist","/FO","CSV","/NH"],capture_output=True,text=True,check=True).stdout.lower()
    if any(('"'+x+'"') in running for x in ("unrealeditor.exe","unrealeditor-cmd.exe","livecodingconsole.exe","unrealbuildtool.exe","shadercompileworker.exe","cl.exe","dotnet.exe")):
        raise RuntimeError("HOLD another native session or build")
    if free_ram()<6.5*1024**3 or shutil.disk_usage(PROJECT).free<14*1024**3: raise RuntimeError("HOLD insufficient RAM or disk")
    protected=[project,mapfile]+[p for p in (PROJECT/"Config").glob("Default*.ini") if p.is_file()]
    before={str(p):sha(p) for p in protected}; saves=inventory(PROJECT/"Saved/SaveGames")
    token=uuid.uuid4().hex
    candidate=out.parent/(out.name+"."+token+".candidate")
    logfile=out.parent/(out.name+"."+token+".log")
    env=os.environ.copy(); env.update({"TSTSS_ENVELOPE_EXPORT_EXPLICIT":"1","TSTSS_ENVELOPE_MAP":a.map,
       "TSTSS_ENVELOPE_MAP_SHA":a.map_sha256,"TSTSS_ENVELOPE_OUTPUT":str(candidate),"TSTSS_ENVELOPE_FRAME":a.frame})
    cmd=[str(UE),str(project),"-ExecutePythonScript="+str(REC),"-NullRHI","-NoSplash","-NoSound","-Unattended","-nop4","-stdout","-FullStdOutLogOutput"]
    modes={p:p.stat().st_mode for p in protected}
    try:
        for p,mode in modes.items(): os.chmod(p,mode & ~stat.S_IWRITE)
        with logfile.open("x",encoding="utf-8") as stream:
            proc=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,env=env)
            try: rc=proc.wait(timeout=180)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try: proc.wait(timeout=10)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait()
                raise RuntimeError("HOLD owned commandlet timed out; log retained")
    finally:
        for p,mode in modes.items(): os.chmod(p,mode)
    if rc!=0 or not candidate.is_file(): raise RuntimeError("HOLD commandlet failed; log retained")
    if any(sha(p)!=old for p,old in ((Path(k),v) for k,v in before.items())) or inventory(PROJECT/"Saved/SaveGames")!=saves:
        raise RuntimeError("HOLD input/config/save drift; candidate retained, not published")
    snap=json.loads(candidate.read_text(encoding="utf-8"))
    if snap.get("map_sha256")!=a.map_sha256 or snap.get("map_package")!=a.map or snap.get("frame")!=a.frame:
        raise RuntimeError("HOLD snapshot metadata mismatch")
    encoded=json.dumps(snap,indent=2,allow_nan=False)
    with out.open("x",encoding="utf-8") as f: f.write(encoded)
    print("NATIVE_SNAPSHOT_SAVED_NOT_COLLISION_PROOF",out,"sha256",sha(out),"log",logfile)
    return 0
def main():
    p=argparse.ArgumentParser(description=__doc__); subs=p.add_subparsers(dest="mode",required=True)
    c=subs.add_parser("combine"); c.add_argument("--start",type=Path,required=True); c.add_argument("--end",type=Path,required=True); c.add_argument("--labels",type=Path,required=True); c.add_argument("--clearance",type=float,required=True); c.add_argument("--output",type=Path,required=True)
    e=subs.add_parser("export"); e.add_argument("--map",required=True); e.add_argument("--map-sha256",required=True); e.add_argument("--frame",required=True); e.add_argument("--expected-head",required=True); e.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    try: return combine(a) if a.mode=="combine" else native_export(a)
    except (ValueError,RuntimeError,OSError,KeyError,subprocess.SubprocessError) as exc:
        print("HOLD:",exc,file=sys.stderr); return 2
if __name__=="__main__": sys.exit(main())
