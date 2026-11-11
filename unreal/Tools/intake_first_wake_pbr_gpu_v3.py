#!/usr/bin/env python3
"""Custody-only intake: verified 200-actor PBR map to clean GPU review worktree.

No changes to original native level/actor/physics/save, no private source
binary upload. Expected sole GPU runtime tracked delta: local PythonAutomationTest.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from intake_first_wake_pbr_native_v3 import safe

SRC=Path("C:/TSTSS_V3_Retry_20261111/TSTSS_VSliceLookdev_20261111")
DEST=Path(__file__).resolve().parents[2]
SOURCE_HEAD="2c22f9ad1c043a97fbbd8cebbf1adae1ab1e3ffd"
BRANCH="review/ue58-vslice-lookdev-gpu-20261111"
WORLD_SHA="3e3d65e1e30b7620b6ddc4d47cf7b94e447d930a7f290818068ac50a51641815"
WORLD_REL="unreal/Content/TSTSS/Review/Scenes/FirstWake_MaterialLookdev_20261111_REVIEW_V3.umap"
ROOT_ASSETS="unreal/Content/TSTSS/Review/Environment/FirstWakeMaterialLookdevV3"
INPUT_RECEIPT="unreal/Saved/FirstWakeMaterialLookdevV3/private_native_intake_receipt.json"
NEW_RECEIPTS=(
    "unreal/Saved/FirstWakeMaterialLookdevV3/native_stage.json",
    "unreal/Saved/FirstWakeMaterialLookdevV3/host_native_stage.json",
    "unreal/Saved/FirstWakeMaterialLookdevV3/native_independent_readback.json",
    "unreal/Saved/FirstWakeMaterialLookdevV3/host_independent_readback.json",
    INPUT_RECEIPT,
)
OUT="unreal/Saved/FirstWakeMaterialLookdevV3/verified_gpu_input_manifest.json"
MIN_FILES=321+40+1+len(NEW_RECEIPTS)

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for buf in iter(lambda:f.read(1024*1024),b""):h.update(buf)
    return h.hexdigest()

def git(path,*args):
    return subprocess.run(["git","-C",str(path),*args],check=True,capture_output=True,
                          text=True,timeout=20).stdout.rstrip("\r\n")

def runtime_project_only():
    import json
    parent=json.loads((SRC/"unreal/ToSailTheStarrySky.uproject").read_text("utf-8"))
    child=json.loads((DEST/"unreal/ToSailTheStarrySky.uproject").read_text("utf-8"))
    original={p["Name"]:p["Enabled"] for p in parent["Plugins"]}
    runtime={p["Name"]:p["Enabled"] for p in child["Plugins"]}
    if original.get("PythonScriptPlugin") is not True or runtime!={
            **original,"PythonAutomationTest":True}:
        raise RuntimeError("HOLD: GPU plugin delta not exactly PythonAutomationTest")
    if {k:v for k,v in parent.items() if k!="Plugins"}!={
            k:v for k,v in child.items() if k!="Plugins"}:
        raise RuntimeError("HOLD: runtime project descriptor changed beyond plugin")
    for rel in ("unreal/Config/DefaultEngine.ini","unreal/Config/DefaultInput.ini"):
        if sha(SRC/rel)!=sha(DEST/rel):
            raise RuntimeError("HOLD: protected UE config altered")
    return True

def inventory():
    if (SRC.name!="TSTSS_VSliceLookdev_20261111" or
            DEST.name!="TSTSS_VSliceLookdev_20261111" or
            SRC.parent.name!="TSTSS_V3_Retry_20261111" or
            DEST.parent.name!="TSTSS_V3_GPU_20261111"):
        raise RuntimeError("HOLD: wrong source/destination GPU worktree")
    if git(SRC,"rev-parse","HEAD")!=SOURCE_HEAD or git(
            SRC,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: exact independently native-readback source drifted")
    if git(DEST,"branch","--show-current")!=BRANCH:
        raise RuntimeError("HOLD: target review branch mismatch")
    if git(DEST,"diff","--name-only",SOURCE_HEAD,git(DEST,"rev-parse","HEAD"),"--",
           "unreal/Source","unreal/Config","unreal/ToSailTheStarrySky.uproject"):
        raise RuntimeError("HOLD: GPU branch modified verified C++/Config or project")
    runtime_project_only()
    source_receipt=json.loads((SRC/INPUT_RECEIPT).read_text(encoding="utf-8"))
    files=source_receipt.get("files",{})
    if (source_receipt.get("status")!="VERIFIED_321_PRIVATE_NATIVE_FILES_COPIED_LOOKDEV_NOT_RENDERED" or
            source_receipt.get("file_count")!=321 or len(files)!=321):
        raise RuntimeError("HOLD: expected original 321 source native packages not proven")
    native=json.loads((SRC/NEW_RECEIPTS[0]).read_text(encoding="utf-8"))
    host_stage=json.loads((SRC/NEW_RECEIPTS[1]).read_text(encoding="utf-8"))
    reread=json.loads((SRC/NEW_RECEIPTS[2]).read_text(encoding="utf-8"))
    host_readback=json.loads((SRC/NEW_RECEIPTS[3]).read_text(encoding="utf-8"))
    if (native.get("status")!="NATIVE_PBR_V3_MAP_SAVED_PENDING_INDEPENDENT_READBACK" or
            native.get("new_map_sha256")!=WORLD_SHA or
            native.get("saved_actor_count")!=200 or
            native.get("new_actors")!=85 or
            native.get("native_material_assets")!=10 or
            native.get("native_texture_assets")!=30 or
            host_stage.get("native_exit_code")!=0 or
            host_stage.get("new_map_sha256")!=WORLD_SHA or
            host_stage.get("status")!="NATIVE_PBR_V3_MAP_SAVED_PENDING_INDEPENDENT_READBACK" or
            reread.get("status")!="INDEPENDENT_NATIVE_PBR_V3_READBACK_PASS_NOT_PIE" or
            reread.get("derived_world_sha256")!=WORLD_SHA or
            reread.get("actors")!=200 or
            reread.get("native_material_assets_reloaded")!=10 or
            reread.get("native_texture_assets_reloaded")!=30 or
            reread.get("original_floor_collision_verified") is not True or
            reread.get("new_detail_collision_disabled") is not True or
            host_readback.get("status")!="INDEPENDENT_NATIVE_PBR_V3_READBACK_VERIFIED_NOT_PIE" or
            host_readback.get("native_exit_code")!=0 or
            not all(host_readback.get(k) for k in
                    ("source_head_preserved","derived_map_preserved","parent_map_preserved",
                     "protected_configs_preserved")) or
            sha(SRC/WORLD_REL)!=WORLD_SHA):
        raise RuntimeError("HOLD: distinct native stage/readback evidence not established")
    files={safe(k).as_posix():v for k,v in files.items()}
    new_assets=[p for p in (SRC/ROOT_ASSETS).rglob("*.uasset") if p.is_file()]
    if len(new_assets)!=40:
        raise RuntimeError("HOLD: precisely 30 imported native textures and 10 PBR materials required")
    for p in new_assets:
        rel=safe(p.relative_to(SRC))
        files[rel.as_posix()]=sha(p)
    files[WORLD_REL]=WORLD_SHA
    for rel in NEW_RECEIPTS:
        files[rel]=sha(SRC/rel)
    if len(files)!=MIN_FILES:
        raise RuntimeError("HOLD: native GPU private asset custody count diverged")
    for relative,digest in files.items():
        if sha(SRC/safe(relative))!=digest:
            raise RuntimeError("HOLD: original native asset SHA changed: "+relative)
    return files

def preflight():
    if (DEST/OUT).exists():
        raise RuntimeError("HOLD: native GPU intake manifest already exists")
    files=inventory()
    for path in files:
        if (DEST/safe(path)).exists():
            raise RuntimeError("HOLD: cannot overwrite existing private GPU asset "+path)
    if list((DEST/"unreal/Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: user SaveGame present")
    return files

def copy():
    files=preflight()
    for path,expected in files.items():
        src=SRC/safe(path)
        dest=DEST/safe(path)
        dest.parent.mkdir(parents=True,exist_ok=True)
        with src.open("rb") as inp,dest.open("xb") as out:
            shutil.copyfileobj(inp,out,1024*1024)
        if sha(dest)!=expected:
            raise RuntimeError("HOLD: native GPU destination SHA mismatch "+path)
    receipt={"status":"VERIFIED_NATIVE_200_ACTOR_GPU_PRIVATE_CUSTODY_NOT_RENDERED",
             "files":files,"file_count":len(files),
             "native_world_sha256":WORLD_SHA,"native_gpu_render_verified":False,
             "pie_verified":False,"art_approved":False}
    dest=DEST/OUT
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf-8") as out:
        json.dump(receipt,out,indent=2,sort_keys=True)
    return {"status":receipt["status"],"file_count":len(files)}

def verify():
    p=DEST/OUT
    if not p.is_file():raise RuntimeError("HOLD: private GPU dependency intake receipt missing")
    manifest=json.loads(p.read_text(encoding="utf-8"))
    if (manifest.get("status")!="VERIFIED_NATIVE_200_ACTOR_GPU_PRIVATE_CUSTODY_NOT_RENDERED" or
            manifest.get("file_count")!=MIN_FILES or
            manifest.get("native_world_sha256")!=WORLD_SHA or
            manifest.get("native_gpu_render_verified") is not False or
            manifest.get("pie_verified") is not False or
            manifest.get("art_approved") is not False or
            len(manifest.get("files",{}))!=MIN_FILES):
        raise RuntimeError("HOLD: invalid native GPU custody manifest status")
    for path,expected in manifest["files"].items():
        if not (DEST/safe(path)).is_file() or sha(DEST/safe(path))!=expected:
            raise RuntimeError("HOLD: GPU private asset missing or modified "+path)
    runtime_project_only()
    return {"status":"PRIVATE_200_ACTOR_GPU_BINARY_SHA_CUSTODY_VERIFIED_NOT_RENDERED",
            "files":MIN_FILES,"map_sha256":WORLD_SHA}

def main():
    parser=argparse.ArgumentParser()
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--audit",action="store_true")
    g.add_argument("--copy",action="store_true")
    g.add_argument("--verify",action="store_true")
    args=parser.parse_args()
    result=({"status":"GPU_NATIVE_INTAKE_PREFLIGHT_PASS_NO_FILES_COPIED",
             "count":len(preflight())} if args.audit else
            copy() if args.copy else verify())
    print(json.dumps(result,sort_keys=True))
if __name__=="__main__":
    main()
