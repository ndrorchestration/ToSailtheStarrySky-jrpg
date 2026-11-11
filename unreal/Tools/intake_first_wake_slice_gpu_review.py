#!/usr/bin/env python3
"""Copy verified, private native UE5.8.4 level/assets into isolated GPU review.

Only specific first-wake packages; never user SaveGames, developer caches,
restricted Starbourne art, source files, or production assets.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

SOURCE=Path("C:/TSTSS_VSliceObjectsNativeV2_20261110")
TARGET=Path("C:/TSTSS_VSliceVisualRuntime_20261110")
CODE_ROOT=Path("C:/TSTSS_VSliceVisualQA_20261110")
SOURCE_HEAD="f47656774d5bb0f163cef550eba09577e2ab8aef"
DEST_BRANCH="review/ue58-vslice-object-gpuqa-20261110"
RUNTIME_BRANCH="review/ue58-vslice-object-gpu-runtime-20261110"
WORLD_REL="unreal/Content/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1.umap"
WORLD_SHA="837e537ab91339f56af006782c8e7dba9ac981d36eb800eb3b2a10c97661bbbc"
OBJECT_DIR="unreal/Content/TSTSS/Review/Objects/FirstWakeSliceV1"
SOURCE_MANIFEST="unreal/Saved/FirstWakeSliceObjectsV1/harbor_private_intake_manifest.json"
LOCAL_RECEIPT="unreal/Saved/FirstWakeSliceVisualQA/private_gpu_intake_receipt.json"
EXTRA=(
    WORLD_REL,
    "unreal/Saved/FirstWakeSliceObjectsV1/native_objects_stage.json",
    "unreal/Saved/FirstWakeSliceObjectsV1/host_objects_stage.json",
    "unreal/Saved/FirstWakeSliceObjectsV1/native_objects_readback.json",
    "unreal/Saved/FirstWakeSliceObjectsV1/host_objects_readback.json",
    "unreal/Saved/FirstWakeSliceObjectsV1/editor_module_custody.json",
)
RESTRICTED=("starbourne","submersible")
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def git(root,*args):
    return subprocess.run(["git","-C",str(root),*args],check=True,capture_output=True,
                          text=True,timeout=30).stdout.rstrip("\r\n")

def safe(relative):
    rel=Path(str(relative).replace("\\","/"))
    if (rel.is_absolute() or not rel.parts or rel.parts[0]!="unreal" or
            ".." in rel.parts or ":" in rel.as_posix() or
            any(k in rel.as_posix().lower() for k in RESTRICTED)):
        raise RuntimeError("HOLD: disallowed review binary path: "+str(relative))
    return rel

def collect():
    private=json.loads((SOURCE/SOURCE_MANIFEST).read_text(encoding="utf-8"))
    if (private.get("status")!="VERIFIED_PRIVATE_HARBOR_ASSETS_COPIED_NOT_UNREAL_LOADED" or
            private.get("source_files")!=92 or len(private.get("file_hashes",{}))!=92):
        raise RuntimeError("HOLD: source private native Harbor custody absent")
    source_native=json.loads((SOURCE/EXTRA[1]).read_text(encoding="utf-8"))
    host_stage=json.loads((SOURCE/EXTRA[2]).read_text(encoding="utf-8"))
    readback=json.loads((SOURCE/EXTRA[3]).read_text(encoding="utf-8"))
    host_rb=json.loads((SOURCE/EXTRA[4]).read_text(encoding="utf-8"))
    module=json.loads((SOURCE/EXTRA[5]).read_text(encoding="utf-8"))
    if (digest(SOURCE/WORLD_REL)!=WORLD_SHA or
            source_native.get("status")!="NATIVE_OBJECT_MAP_SAVED_PENDING_INDEPENDENT_READBACK" or
            source_native.get("new_map_sha256")!=WORLD_SHA or
            source_native.get("native_static_mesh_assets")!=22 or
            source_native.get("new_native_actor_count")!=31 or
            host_stage.get("status")!="NATIVE_STAGE_SAVED_PENDING_INDEPENDENT_READBACK" or
            host_stage.get("new_map_sha256")!=WORLD_SHA or
            host_stage.get("source_commit")!=SOURCE_HEAD or
            host_stage.get("native_exit_code")!=0 or
            readback.get("status")!="INDEPENDENT_NATIVE_OBJECT_READBACK_PASS_NOT_PIE" or
            readback.get("saved_world_sha256")!=WORLD_SHA or
            readback.get("actors")!=115 or
            readback.get("distinct_imported_static_meshes")!=22 or
            readback.get("new_visual_actors")!=31 or
            host_rb.get("status")!="INDEPENDENT_NATIVE_OBJECT_READBACK_VERIFIED_NOT_PIE" or
            host_rb.get("native_exit_code")!=0 or
            not all(host_rb.get(k) for k in
                    ("stage_map_preserved","original_map_preserved",
                     "source_head_preserved","config_hashes_preserved")) or
            module.get("status")!="EVIDENCE_BOUND_EDITOR_MODULE_COPIED_NATIVE_LOAD_NOT_YET_RUN"):
        raise RuntimeError("HOLD: V2 separate real UE native readback evidence diverged")
    files={}
    for name,hash_value in private["file_hashes"].items():
        path=safe(name)
        if digest(SOURCE/path)!=hash_value:
            raise RuntimeError("HOLD: previously proven parent Harbor package changed "+name)
        files[path.as_posix()]=hash_value
    mesh_files=[p for p in (SOURCE/OBJECT_DIR).rglob("*") if p.is_file()]
    if len(mesh_files)!=220:
        raise RuntimeError("HOLD: expected 220 real UE mesh/material package files")
    for full in mesh_files:
        rel=safe(full.relative_to(SOURCE))
        if rel.suffix.lower() not in (".uasset",".uexp",".ubulk"):
            raise RuntimeError("HOLD: unexpected imported package format")
        files[rel.as_posix()]=digest(full)
    for name in EXTRA:
        path=safe(name)
        files[path.as_posix()]=digest(SOURCE/path)
    for record in module.get("files",[]):
        path=safe(record["relative_path"])
        if digest(SOURCE/path)!=record["sha256"]:
            raise RuntimeError("HOLD: native UE game module custody drifted")
        files[path.as_posix()]=record["sha256"]
    if len(files)<315:
        raise RuntimeError("HOLD: incomplete imported object dependency chain")
    return files

def plugin_only_review_change():
    old=json.loads((SOURCE/"unreal/ToSailTheStarrySky.uproject").read_text(encoding="utf-8"))
    new=json.loads((TARGET/"unreal/ToSailTheStarrySky.uproject").read_text(encoding="utf-8"))
    plugins={p["Name"]:p["Enabled"] for p in old.get("Plugins",[])}
    modified={p["Name"]:p["Enabled"] for p in new.get("Plugins",[])}
    expected={**plugins,"PythonAutomationTest":True}
    if plugins.get("PythonScriptPlugin") is not True or modified!=expected:
        raise RuntimeError("HOLD: GPU test plugin change is not limited to PythonAutomationTest")
    old.pop("Plugins");new.pop("Plugins")
    if old!=new:
        raise RuntimeError("HOLD: review .uproject changed beyond opt-in Python GPU testing")
    for name in ("unreal/Config/DefaultEngine.ini","unreal/Config/DefaultInput.ini"):
        if digest(SOURCE/name)!=digest(TARGET/name):
            raise RuntimeError("HOLD: protected engine/input config drifted")
    if git(CODE_ROOT,"diff","--name-only",SOURCE_HEAD,git(CODE_ROOT,"rev-parse","HEAD"),
           "--","unreal/Source","unreal/Config",
           "unreal/ToSailTheStarrySkyEditor.Target.cs",
           "unreal/ToSailTheStarrySky.Target.cs"):
        raise RuntimeError("HOLD: current native C++ source no longer matches V2")

def preflight():
    if (SOURCE.name!="TSTSS_VSliceObjectsNativeV2_20261110" or
            TARGET.name!="TSTSS_VSliceVisualRuntime_20261110" or
            CODE_ROOT.name!="TSTSS_VSliceVisualQA_20261110"):
        raise RuntimeError("HOLD: wrong isolated GPU review worktree")
    if git(SOURCE,"rev-parse","HEAD")!=SOURCE_HEAD or git(SOURCE,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: native proven V2 source mutated")
    if (git(CODE_ROOT,"branch","--show-current")!=DEST_BRANCH or
            git(CODE_ROOT,"status","--porcelain","--untracked-files=no") or
            git(TARGET,"branch","--show-current")!=RUNTIME_BRANCH or
            git(TARGET,"rev-parse","HEAD")!=git(CODE_ROOT,"rev-parse","HEAD")):
        raise RuntimeError("HOLD: GPU review source/isolated runtime branch diverged")
    dirty=git(TARGET,"status","--porcelain","--untracked-files=no").splitlines()
    if dirty!=[" M unreal/ToSailTheStarrySky.uproject"]:
        raise RuntimeError("HOLD: runtime must differ ONLY by PythonAutomationTest plugin")
    plugin_only_review_change()
    if (TARGET/LOCAL_RECEIPT).exists():
        raise RuntimeError("HOLD: private review receipt already present")
    if list((TARGET/"unreal/Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: existing user save state")
    files=collect()
    for name in files:
        if (TARGET/safe(name)).exists():
            raise RuntimeError("HOLD: cannot overwrite preexisting private asset "+name)
    return files

def copy():
    files=preflight()
    for name,expected in files.items():
        source=SOURCE/safe(name);dest=TARGET/safe(name)
        dest.parent.mkdir(parents=True,exist_ok=True)
        with source.open("rb") as stream,dest.open("xb") as out:
            shutil.copyfileobj(stream,out,1024*1024)
        if digest(dest)!=expected:
            raise RuntimeError("HOLD: imported dependency transfer hash mismatch "+name)
    report={"status":"VERIFIED_PRIVATE_115_ACTOR_GPU_REVIEW_ASSETS_COPIED_NOT_RENDERED",
            "source_native_head":SOURCE_HEAD,"source_saved_world_sha256":WORLD_SHA,
            "private_files":len(files),"file_hashes":files,
            "native_readback_previously_verified":True,"gpu_render_verified":False,
            "pie_verified":False,"art_approved":False}
    dst=TARGET/LOCAL_RECEIPT
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open("x",encoding="utf-8") as out:
        json.dump(report,out,indent=2,sort_keys=True)
    return {"status":report["status"],"file_count":len(files),
            "map_sha256":WORLD_SHA,"native_render_verified":False}

def verify():
    path=TARGET/LOCAL_RECEIPT
    if not path.is_file():raise RuntimeError("HOLD: private intake receipt missing")
    receipt=json.loads(path.read_text(encoding="utf-8"))
    if (receipt.get("status")!="VERIFIED_PRIVATE_115_ACTOR_GPU_REVIEW_ASSETS_COPIED_NOT_RENDERED" or
            receipt.get("source_native_head")!=SOURCE_HEAD or
            receipt.get("source_saved_world_sha256")!=WORLD_SHA or
            receipt.get("native_readback_previously_verified") is not True or
            receipt.get("gpu_render_verified") is not False or
            receipt.get("pie_verified") is not False or receipt.get("art_approved") is not False):
        raise RuntimeError("HOLD: private intake status inconsistent")
    copied=receipt.get("file_hashes",{})
    if len(copied)!=receipt.get("private_files",0) or len(copied)<315:
        raise RuntimeError("HOLD: incomplete native visual review custody")
    for name,expected in copied.items():
        path=TARGET/safe(name)
        if not path.is_file() or digest(path)!=expected:
            raise RuntimeError("HOLD: native visual review file modified "+name)
    plugin_only_review_change()
    return {"status":"VERIFIED_GPU_REVIEW_SOURCE_FILES_ONLY_NOT_RENDERED",
            "private_files":len(copied),"map_sha256":WORLD_SHA}

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--audit",action="store_true")
    g.add_argument("--copy",action="store_true")
    g.add_argument("--verify",action="store_true")
    a=p.parse_args()
    result=({"status":"GPU_NATIVE_ASSET_INTAKE_PREFLIGHT_PASS_NO_FILES_COPIED",
             "count":len(preflight()),"world_sha256":WORLD_SHA}
            if a.audit else copy() if a.copy else verify())
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=="__main__":
    main()
