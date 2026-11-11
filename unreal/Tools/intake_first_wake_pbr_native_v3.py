#!/usr/bin/env python3
"""Import exact independently native-readback private dependencies into V3.

All binary packages remain on NEONTIC, untracked. The 115-actor World is
copied, never moved/overwritten. Derivative stage must prove its own UE receipt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import intake_first_wake_slice_gpu_review as prior
import stage_first_wake_pbr_native_v3 as stage

SRC=prior.SOURCE
DEST=Path(__file__).resolve().parents[2]
BRANCH="review/ue58-vslice-lookdev-native-r1-20261111"
INPUT_HEAD="f47656774d5bb0f163cef550eba09577e2ab8aef"
RECEIPT=Path("unreal/Saved/FirstWakeMaterialLookdevV3/private_native_intake_receipt.json")
EXPECTED_COUNT=321

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda:f.read(1024*1024),b""):h.update(data)
    return h.hexdigest()

def git(root,*args):
    return subprocess.run(["git","-C",str(root),*args],check=True,
                          capture_output=True,text=True,timeout=30).stdout.rstrip("\r\n")

def safe(text):
    return prior.safe(text)

def preflight():
    if SRC.name!="TSTSS_VSliceObjectsNativeV2_20261110" or DEST.name!="TSTSS_VSliceLookdev_20261111":
        raise RuntimeError("HOLD: private native custody wrong worktrees")
    if git(SRC,"rev-parse","HEAD")!=INPUT_HEAD or git(SRC,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: original native-readback V2 source dirty/drifted")
    if git(DEST,"branch","--show-current")!=BRANCH or git(DEST,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: target review source dirty/drifted")
    changes=git(DEST,"diff","--name-only",INPUT_HEAD,git(DEST,"rev-parse","HEAD"),
                "--","unreal/Source","unreal/Config","unreal/Plugins",
                "unreal/ToSailTheStarrySky.uproject",
                "unreal/ToSailTheStarrySkyEditor.Target.cs","unreal/ToSailTheStarrySky.Target.cs")
    if changes:
        raise RuntimeError("HOLD: C++/Config/uproject not source-equivalent to original native World")
    files=prior.collect()
    if len(files)!=EXPECTED_COUNT or files.get(prior.WORLD_REL)!=prior.WORLD_SHA:
        raise RuntimeError("HOLD: incomplete 321-file First Wake World custody")
    if (DEST/RECEIPT).exists() or (DEST/"unreal"/stage.DEST_REL).exists():
        raise RuntimeError("HOLD: native intake/derived output already exists")
    if list((DEST/"unreal/Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: existing review SaveGames")
    for name in files:
        if (DEST/safe(name)).exists():
            raise RuntimeError("HOLD: destination already contains private asset "+name)
    return files

def copy():
    items=preflight()
    for name,expected in items.items():
        source=SRC/safe(name)
        destination=DEST/safe(name)
        destination.parent.mkdir(parents=True,exist_ok=True)
        with source.open("rb") as inp,destination.open("xb") as out:
            shutil.copyfileobj(inp,out,1024*1024)
        if digest(destination)!=expected:
            raise RuntimeError("HOLD: copied private native asset hash drift: "+name)
    evidence={"status":"VERIFIED_321_PRIVATE_NATIVE_FILES_COPIED_LOOKDEV_NOT_RENDERED",
              "source_commit":INPUT_HEAD,
              "source_world_sha256":prior.WORLD_SHA,
              "files":items,"file_count":len(items),
              "native_lookdev_staged":False,
              "gpu_render_verified":False,"pie_verified":False,
              "art_approved":False}
    target=DEST/RECEIPT
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("x",encoding="utf-8") as out:
        json.dump(evidence,out,sort_keys=True,indent=2)
    return {"status":evidence["status"],"file_count":len(items)}

def verify():
    path=DEST/RECEIPT
    if not path.is_file():
        raise RuntimeError("HOLD: private V3 lookdev intake receipt absent")
    data=json.loads(path.read_text(encoding="utf-8"))
    if (data.get("status")!="VERIFIED_321_PRIVATE_NATIVE_FILES_COPIED_LOOKDEV_NOT_RENDERED" or
            data.get("source_commit")!=INPUT_HEAD or
            data.get("source_world_sha256")!=prior.WORLD_SHA or
            data.get("file_count")!=EXPECTED_COUNT or
            data.get("native_lookdev_staged") is not False or
            data.get("gpu_render_verified") is not False or
            data.get("pie_verified") is not False or
            data.get("art_approved") is not False):
        raise RuntimeError("HOLD: invalid original native intake provenance")
    files=data.get("files",{})
    if len(files)!=EXPECTED_COUNT:
        raise RuntimeError("HOLD: private native asset inventory incomplete")
    for name,expected in files.items():
        dest=DEST/safe(name)
        if not dest.is_file() or digest(dest)!=expected:
            raise RuntimeError("HOLD: local native asset no longer SHA matched "+name)
    if (DEST/"unreal"/stage.PARENT_REL).is_file() and digest(DEST/"unreal"/stage.PARENT_REL)!=stage.plan.BASE_SHA:
        raise RuntimeError("HOLD: inherited scene World hash drift")
    return {"status":"PBR_V3_PRIVATE_BINARY_SHA_CUSTODY_PASS_NOT_NATIVE",
            "files":len(files),"source_world_sha256":stage.plan.BASE_SHA}

def main():
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--audit",action="store_true")
    group.add_argument("--copy",action="store_true")
    group.add_argument("--verify",action="store_true")
    a=p.parse_args()
    res=({"status":"PRIVATE_BINARY_INTAKE_PREFLIGHT_PASS",
          "count":len(preflight())} if a.audit
         else copy() if a.copy else verify())
    print(json.dumps(res,indent=2,sort_keys=True))
if __name__=="__main__":
    main()
