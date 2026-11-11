#!/usr/bin/env python3
"""Isolated, host-checked UE5.8.4 readback for the native First Wake object World.

Read-only native verifier runs as ONE monitored child, separate from staging.
Success proves saved actor/asset inventory, not real PIE, D3D or production art.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

import run_first_wake_slice_objects_native as guarded
import stage_first_wake_slice_objects as stage

PROJECT=guarded.PROJECT
ROOT=guarded.ROOT
EDITOR=guarded.EDITOR
OUT=guarded.OUTPUT
HOST_STAGE=guarded.HOST
NATIVE_STAGE=guarded.NATIVE
NATIVE_READBACK=OUT/"native_objects_readback.json"
HOST_READBACK=OUT/"host_objects_readback.json"
LOG=OUT/"objects_readback_native.log"
CONSOLE=OUT/"objects_readback_console.log"
VERIFIER=Path(__file__).with_name("verify_first_wake_slice_objects_native.py")
EXPECTED_NATIVE_STATUS="INDEPENDENT_NATIVE_OBJECT_READBACK_PASS_NOT_PIE"

def verify_stage_proof(host,native,new_sha,source_sha,commit):
    if (host.get("status")!="NATIVE_STAGE_SAVED_PENDING_INDEPENDENT_READBACK" or
            native.get("status")!="NATIVE_OBJECT_MAP_SAVED_PENDING_INDEPENDENT_READBACK" or
            host.get("new_map_sha256")!=new_sha or
            native.get("new_map_sha256")!=new_sha or
            native.get("source_map_sha256")!=source_sha or
            host.get("source_commit")!=commit or
            native.get("new_native_actor_count")!=31 or
            native.get("native_static_mesh_assets")!=22 or
            not host.get("config_hashes_preserved") or
            not host.get("source_map_preserved") or
            not host.get("commit_preserved")):
        raise RuntimeError("HOLD: staged native proof is incomplete/drifted")
    return True

def verify_native_receipt(verified,world_sha):
    if (verified.get("status")!=EXPECTED_NATIVE_STATUS or
            verified.get("saved_world_sha256")!=world_sha or
            verified.get("actors")!=115 or
            verified.get("new_visual_actors")!=31 or
            verified.get("distinct_imported_static_meshes")!=22 or
            verified.get("milestones_preserved")!=list(stage.MILESTONES) or
            verified.get("player_starts")!=1 or
            verified.get("physics_verified") is not False or
            verified.get("pie_verified") is not False or
            verified.get("render_verified") is not False or
            verified.get("art_approved") is not False):
        raise RuntimeError("Native readback receipt does not prove bounded saved World")
    return True

def preflight():
    if sys.platform!="win32" or ROOT.name!=stage.ROOT_NAME:
        raise RuntimeError("HOLD: unexpected readback host")
    if (guarded.git("branch","--show-current")!=guarded.BRANCH or
            guarded.git("status","--porcelain","--untracked-files=no")):
        raise RuntimeError("HOLD: dirty/rebased source branch")
    if not EDITOR.is_file() or not VERIFIER.is_file():
        raise RuntimeError("HOLD: native Editor/verifier unavailable")
    version=json.loads((EDITOR.parents[2]/"Build/Build.version").read_text(encoding="utf-8"))
    if tuple(version.get(x) for x in ("MajorVersion","MinorVersion","PatchVersion"))!=(5,8,4):
        raise RuntimeError("HOLD: native Unreal version mismatch")
    for target in (NATIVE_READBACK,HOST_READBACK,LOG,CONSOLE):
        if target.exists(): raise RuntimeError("HOLD: existing readback evidence; refuse overwrite")
    if not all(p.is_file() for p in (HOST_STAGE,NATIVE_STAGE,PROJECT/stage.SOURCE_MAP_REL,
                                    PROJECT/stage.NEW_MAP_REL)):
        raise RuntimeError("HOLD: object stage map and two receipts required")
    host=json.loads(HOST_STAGE.read_text(encoding="utf-8"))
    native=json.loads(NATIVE_STAGE.read_text(encoding="utf-8"))
    mapfile=PROJECT/stage.NEW_MAP_REL
    orig=PROJECT/stage.SOURCE_MAP_REL
    verify_stage_proof(host,native,stage.sha256(mapfile),stage.sha256(orig),
                       guarded.git("rev-parse","HEAD"))
    if list((PROJECT/"Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: user SaveGames exist")
    running=subprocess.run(["tasklist","/FO","CSV"],capture_output=True,text=True,
                           check=True,timeout=20).stdout.lower()
    if any(x in running for x in ("unrealeditor.exe","unrealeditor-cmd.exe",
                                    "livecodingconsole.exe")):
        raise RuntimeError("HOLD: other Unreal Editor/Live Coding session active")
    ram=guarded.free_ram_gib()
    from shutil import disk_usage
    disk=disk_usage(ROOT).free/1024**3
    if ram<guarded.MIN_RAM_GIB or disk<guarded.MIN_DISK_GIB:
        raise RuntimeError(f"HOLD: insufficient RAM/disk ({ram:.2f}/{disk:.2f} GiB)")
    configs=(PROJECT/"Config/DefaultEngine.ini",PROJECT/"Config/DefaultInput.ini")
    config_hashes={p.name:stage.sha256(p) for p in configs}
    return {"status":"OBJECT_READBACK_PRECHECK_PASS_NO_UNREAL_LAUNCH",
            "source_head":guarded.git("rev-parse","HEAD"),
            "staged_map_sha256":stage.sha256(mapfile),
            "parent_map_sha256":stage.sha256(orig),
            "config_hashes":config_hashes,
            "physical_ram_gib":round(ram,3),"disk_gib":round(disk,3),
            "native_gpu_render_verified":False,"pie_verified":False}

def run():
    evidence=preflight()
    configs=(PROJECT/"Config/DefaultEngine.ini",PROJECT/"Config/DefaultInput.ini")
    try:
        for p in configs: os.chmod(p,stat.S_IREAD)
        args=[str(EDITOR),str(PROJECT/"ToSailTheStarrySky.uproject"),
              "-ExecutePythonScript="+str(VERIFIER),"-NullRHI","-unattended",
              "-nop4","-NoSplash","-NoSound","-stdout","-FullStdOutLogOutput",
              "-abslog="+str(LOG)]
        with CONSOLE.open("x",encoding="utf-8") as out:
            child=subprocess.Popen(args,cwd=str(ROOT),stdin=subprocess.DEVNULL,
                                   stdout=out,stderr=subprocess.STDOUT,
                                   creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            evidence["readback_child_pid"]=child.pid
            start=time.monotonic()
            while child.poll() is None:
                if (time.monotonic()-start>guarded.MAX_RUNTIME_SECONDS or
                        guarded.free_ram_gib()<0.85):
                    evidence["safety_termination"]=True
                    child.terminate()
                    break
                time.sleep(2)
            try: status=child.wait(timeout=12)
            except subprocess.TimeoutExpired:
                child.kill()
                status=child.wait(timeout=6)
            evidence["native_exit_code"]=status
        if evidence.get("safety_termination") or status!=0:
            raise RuntimeError("Readback Editor child aborted or failed")
        if not NATIVE_READBACK.is_file() or not LOG.is_file():
            raise RuntimeError("Readback native log/receipt absent")
        verified=json.loads(NATIVE_READBACK.read_text(encoding="utf-8"))
        verify_native_receipt(verified,evidence["staged_map_sha256"])
        if "TSTSS_SLICE_OBJECT_INDEPENDENT_NATIVE_READBACK_PASS_NOT_PIE" not in LOG.read_text(
                encoding="utf-8",errors="replace"):
            raise RuntimeError("Readback log did not attest UE scene inventory")
        evidence["status"]="INDEPENDENT_NATIVE_OBJECT_READBACK_VERIFIED_NOT_PIE"
    except Exception as e:
        evidence["status"]="NATIVE_OBJECT_READBACK_HOLD"
        evidence["error"]=str(e)
    finally:
        for p in configs: os.chmod(p,stat.S_IWRITE|stat.S_IREAD)
        evidence["source_head_preserved"]=guarded.git("rev-parse","HEAD")==evidence["source_head"]
        evidence["original_map_preserved"]=stage.sha256(PROJECT/stage.SOURCE_MAP_REL)==evidence["parent_map_sha256"]
        evidence["stage_map_preserved"]=stage.sha256(PROJECT/stage.NEW_MAP_REL)==evidence["staged_map_sha256"]
        evidence["config_hashes_preserved"]=all(
            stage.sha256(p)==evidence["config_hashes"][p.name] for p in configs)
        if not all(evidence[k] for k in ("source_head_preserved","original_map_preserved",
                                           "stage_map_preserved","config_hashes_preserved")):
            evidence["status"]="NATIVE_OBJECT_READBACK_HOLD"
        with HOST_READBACK.open("x",encoding="utf-8") as out:
            json.dump(evidence,out,indent=2,sort_keys=True)
    return evidence

def main():
    parser=argparse.ArgumentParser()
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--readback",action="store_true")
    a=parser.parse_args()
    try:
        result=preflight() if a.check else run()
        print(json.dumps({k:result.get(k) for k in
            ("status","source_head","native_exit_code","staged_map_sha256","error")},
            sort_keys=True))
        return 0 if result["status"] not in ("NATIVE_OBJECT_READBACK_HOLD",) else 2
    except Exception as e:
        print(json.dumps({"status":"HOLD_NO_EDITOR_LAUNCHED","reason":str(e)}))
        return 2
if __name__=="__main__":
    sys.exit(main())
