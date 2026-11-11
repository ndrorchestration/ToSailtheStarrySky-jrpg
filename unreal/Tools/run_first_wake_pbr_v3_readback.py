#!/usr/bin/env python3
"""Resource and custody-gated independent UE5.8 native PBR V3 saved map readback.

One separately launched Editor NullRHI process, original map/Configs unchanged.
Not a GPU, aesthetic, user-interaction, physics or release acceptance gate.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time

import intake_first_wake_pbr_native_v3 as private
import run_first_wake_pbr_v3_native as stagehost
import stage_first_wake_pbr_native_v3 as stage
import verify_first_wake_pbr_v3_native as verifier

ROOT=stagehost.ROOT
PROJECT=stagehost.PROJECT
EDITOR=stagehost.EDITOR
OUTPUT=stagehost.OUTPUT
SOURCE=PROJECT/stage.PARENT_REL
DEST=PROJECT/stage.DEST_REL
NATIVE_STAGE=PROJECT/stage.RECEIPT_REL
HOST_STAGE=stagehost.HOST
NATIVE_READBACK=PROJECT/verifier.RECEIPT
HOST=OUTPUT/"host_independent_readback.json"
LOG=OUTPUT/"native_independent_readback.log"
CONSOLE=OUTPUT/"native_independent_readback_console.log"
EXPECTED_STATUS=verifier.STATUS

def proof_check(host,native,head,derived_sha):
    if (host.get("status")!="NATIVE_PBR_V3_MAP_SAVED_PENDING_INDEPENDENT_READBACK" or
            host.get("new_map_sha256")!=derived_sha or
            host.get("source_head")!=head or
            host.get("native_exit_code")!=0 or
            native.get("status")!="NATIVE_PBR_V3_MAP_SAVED_PENDING_INDEPENDENT_READBACK" or
            native.get("new_map_sha256")!=derived_sha or
            native.get("parent_map_sha256")!=stage.plan.BASE_SHA or
            native.get("saved_actor_count")!=200 or
            native.get("new_actors")!=85 or
            native.get("native_material_assets")!=10 or
            native.get("native_texture_assets")!=30 or
            native.get("original_floor_collision_preserved") is not True or
            native.get("original_interaction_markers_preserved") is not True or
            not all(host.get(x) for x in ("source_head_preserved","parent_map_preserved",
                                         "original_assembly_preserved","protected_configs_preserved"))):
        raise RuntimeError("HOLD: genuine native stage map/host source proof is incomplete")
    return True

def receipt_check(native,derived_sha):
    if (native.get("status")!=EXPECTED_STATUS or
            native.get("derived_world_sha256")!=derived_sha or
            native.get("actors")!=200 or
            native.get("original_actors_inherited")!=115 or
            native.get("new_visual_only_mesh_actors")!=84 or
            native.get("new_camera_count")!=1 or
            native.get("materials_replaced_on_inherited_actors")!=18 or
            native.get("native_material_assets_reloaded")!=10 or
            native.get("native_texture_assets_reloaded")!=30 or
            native.get("preserved_interactions")!=list(stage.plan.MILESTONES) or
            len(native.get("preserved_signs",[]))!=7 or
            native.get("original_floor_collision_verified") is not True or
            native.get("original_floor_geometry_verified") is not True or
            native.get("new_detail_collision_disabled") is not True or
            native.get("gpu_render_verified") is not False or
            native.get("pie_verified") is not False or
            native.get("art_approved") is not False or
            native.get("physics_splashdown_verified") is not False):
        raise RuntimeError("HOLD: independent native PBR readback receipt invalid")
    return True

def preflight():
    if sys.platform!="win32" or ROOT.name!=stage.plan.ROOT_NAME:
        raise RuntimeError("HOLD: wrong independent native readback host")
    if private.git(ROOT,"branch","--show-current")!=stagehost.BRANCH or private.git(
            ROOT,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: dirty or wrong current review source")
    current=private.git(ROOT,"rev-parse","HEAD")
    if not all(p.is_file() for p in (EDITOR,stagehost.VERSION,DEST,SOURCE,
                                     NATIVE_STAGE,HOST_STAGE)):
        raise RuntimeError("HOLD: authentic previously saved native V3 map+receipts missing")
    version=json.loads(stagehost.VERSION.read_text(encoding="utf-8"))
    if [version.get(k) for k in ("MajorVersion","MinorVersion","PatchVersion")]!=[5,8,4]:
        raise RuntimeError("HOLD: wrong installed UE5.8.4")
    private.verify()
    if stage.sha(SOURCE)!=stage.plan.BASE_SHA:
        raise RuntimeError("HOLD: original 115-actor source SHA drift")
    host=json.loads(HOST_STAGE.read_text(encoding="utf-8"))
    native=json.loads(NATIVE_STAGE.read_text(encoding="utf-8"))
    derived=stage.sha(DEST)
    proof_check(host,native,current,derived)
    for p in (NATIVE_READBACK,HOST,LOG,CONSOLE):
        if p.exists():
            raise RuntimeError("HOLD: previous readback output cannot be overwritten")
    if list((PROJECT/"Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: user SaveGame present")
    processes=subprocess.run(["tasklist","/FO","CSV"],capture_output=True,
                             text=True,check=True,timeout=20).stdout.lower()
    if any(x in processes for x in ("unrealeditor.exe","unrealeditor-cmd.exe",
                                    "livecodingconsole.exe")):
        raise RuntimeError("HOLD: another Unreal Editor or LiveCoding process active")
    ram=stagehost.ram()
    disk=shutil.disk_usage(ROOT).free/1024**3
    if ram<stagehost.MIN_RAM_GIB or disk<stagehost.MIN_DISK_GIB:
        raise RuntimeError(f"HOLD: resources RAM={ram:.2f}, disk={disk:.2f} GiB")
    configs=[PROJECT/"Config/DefaultEngine.ini",PROJECT/"Config/DefaultInput.ini"]
    return {"status":"PBR_V3_INDEPENDENT_READBACK_PREFLIGHT_PASS_NO_UNREAL_LAUNCHED",
            "source_head":current,"derived_sha256":derived,
            "parent_sha256":stage.plan.BASE_SHA,
            "config_sha256":{p.name:stage.sha(p) for p in configs},
            "ram_gib":round(ram,2),"disk_gib":round(disk,2)}

def readback():
    evidence=preflight()
    protected=[PROJECT/"Config/DefaultEngine.ini",PROJECT/"Config/DefaultInput.ini"]
    try:
        for file in protected:os.chmod(file,stat.S_IREAD)
        args=[str(EDITOR),str(PROJECT/"ToSailTheStarrySky.uproject"),
              "-ExecutePythonScript="+str(Path(verifier.__file__).resolve()),
              "-NullRHI","-unattended","-nop4","-NoSplash","-NoSound",
              "-stdout","-FullStdOutLogOutput","-abslog="+str(LOG)]
        with CONSOLE.open("x",encoding="utf-8") as out:
            child=subprocess.Popen(args,stdout=out,stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL,cwd=str(ROOT),
                                   creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            evidence["pid"]=child.pid
            started=time.monotonic()
            while child.poll() is None:
                if (time.monotonic()-started>stagehost.MAX_SECONDS or
                        stagehost.ram()<0.85):
                    child.terminate()
                    evidence["safety_termination"]=True
                    break
                time.sleep(2)
            try:exit_code=child.wait(timeout=12)
            except subprocess.TimeoutExpired:
                child.kill()
                exit_code=child.wait(timeout=6)
        evidence["native_exit_code"]=exit_code
        if exit_code!=0 or evidence.get("safety_termination"):
            raise RuntimeError("HOLD: native independent readback child exited nonzero")
        if not NATIVE_READBACK.is_file() or not LOG.is_file():
            raise RuntimeError("HOLD: native independent readback receipt/log missing")
        report=json.loads(NATIVE_READBACK.read_text(encoding="utf-8"))
        receipt_check(report,evidence["derived_sha256"])
        if "FIRSTWAKE_PBR_V3_INDEPENDENT_READBACK_PASS_NOT_PIE" not in LOG.read_text(
                encoding="utf-8",errors="replace"):
            raise RuntimeError("HOLD: native UE readback sentinel missing")
        evidence["status"]="INDEPENDENT_NATIVE_PBR_V3_READBACK_VERIFIED_NOT_PIE"
    except Exception as exc:
        evidence["status"]="INDEPENDENT_NATIVE_PBR_V3_READBACK_HOLD"
        evidence["error"]=str(exc)
    finally:
        for file in protected:os.chmod(file,stat.S_IWRITE|stat.S_IREAD)
        evidence["source_head_preserved"]=private.git(ROOT,"rev-parse","HEAD")==evidence["source_head"]
        evidence["derived_map_preserved"]=stage.sha(DEST)==evidence["derived_sha256"]
        evidence["parent_map_preserved"]=stage.sha(SOURCE)==evidence["parent_sha256"]
        evidence["protected_configs_preserved"]=all(
            stage.sha(p)==evidence["config_sha256"][p.name] for p in protected)
        if not all(evidence[x] for x in (
                "source_head_preserved","derived_map_preserved","parent_map_preserved",
                "protected_configs_preserved")):
            evidence["status"]="INDEPENDENT_NATIVE_PBR_V3_READBACK_HOLD"
        with HOST.open("x",encoding="utf-8") as out:
            json.dump(evidence,out,indent=2,sort_keys=True)
    return evidence

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--readback",action="store_true")
    a=p.parse_args()
    try:
        value=preflight() if a.check else readback()
        print(json.dumps({k:value.get(k) for k in
                          ("status","source_head","derived_sha256","native_exit_code","error")},
                         sort_keys=True))
        return 0 if value["status"]!="INDEPENDENT_NATIVE_PBR_V3_READBACK_HOLD" else 2
    except Exception as e:
        print(json.dumps({"status":"HOLD_NO_EDITOR_LAUNCHED","reason":str(e)}))
        return 2
if __name__=="__main__":
    sys.exit(main())
