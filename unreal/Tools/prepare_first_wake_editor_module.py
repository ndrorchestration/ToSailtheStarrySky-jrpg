#!/usr/bin/env python3
"""Copy a source-equivalent, natively loaded UE5.8.4 Editor module.

This is NOT a new compile. Provenance ties the DLL to the prior successful
separate-process Harbor native saved-world readback and exact C++/config parity.
Only the small module/target metadata are copied, NOT an old PDB or user saves.
The new isolated project must still genuinely load the module on its own.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import transfer_first_wake_harbor_review as intake

SOURCE=intake.SOURCE_ROOT
DEST=intake.DEST_ROOT
SOURCE_HEAD=intake.SOURCE_HEAD
DEST_BRANCH=intake.DEST_BRANCH
MANIFEST=Path("unreal/Saved/FirstWakeSliceObjectsV1/editor_module_custody.json")
BINARY_FILES=(
    "unreal/Binaries/Win64/UnrealEditor-ToSailTheStarrySky.dll",
    "unreal/Binaries/Win64/UnrealEditor.modules",
    "unreal/Binaries/Win64/ToSailTheStarrySkyEditor.target",
)
# Modules and direct project dependencies must match byte-for-byte in Git.
# Python stage tools, source-art files and docs may differ by design.
SOURCE_PATHS=(
    "unreal/Source","unreal/Config","unreal/Plugins",
    "unreal/ToSailTheStarrySky.uproject",
    "unreal/ToSailTheStarrySkyEditor.Target.cs",
    "unreal/ToSailTheStarrySky.Target.cs",
)

def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def diff_paths(source_head,dest_head):
    x=subprocess.run(["git","-C",str(DEST),"diff","--name-only",source_head,
                      dest_head,"--",*SOURCE_PATHS],
                     capture_output=True,text=True,check=True,timeout=30)
    return [s for s in x.stdout.strip().splitlines() if s]

def preflight():
    if SOURCE.name!="TSTSS_EnvironmentHarborRecovery_20261105" or DEST.name!="TSTSS_VSliceObjectsNativeV2_20261110":
        raise RuntimeError("HOLD: wrong native module source/target")
    if intake.git(SOURCE,"rev-parse","HEAD")!=SOURCE_HEAD:
        raise RuntimeError("HOLD: original compiled source head changed")
    if intake.git(SOURCE,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: compiled Harbor tracked source dirty")
    if intake.git(DEST,"branch","--show-current")!=DEST_BRANCH:
        raise RuntimeError("HOLD: wrong isolated recovery branch")
    if intake.git(DEST,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: target tracked source dirty")
    dest_head=intake.git(DEST,"rev-parse","HEAD")
    differences=diff_paths(SOURCE_HEAD,dest_head)
    if differences:
        raise RuntimeError("HOLD: native C++/config/uproject differs: "+repr(differences))
    if not intake.receipt_check(SOURCE)["native_readback_verified"]:
        raise RuntimeError("HOLD: original UE5.8 native load evidence missing")
    engine=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Build/Build.version")
    if not engine.is_file():
        raise RuntimeError("HOLD: installed UE engine version cannot be proven")
    build=json.loads(engine.read_text(encoding="utf-8"))
    if tuple(build[k] for k in ("MajorVersion","MinorVersion","PatchVersion"))!=(5,8,4):
        raise RuntimeError("HOLD: source compiled module UE version unsupported")
    source_mod=json.loads((SOURCE/BINARY_FILES[1]).read_text(encoding="utf-8"))
    if (not source_mod.get("BuildId") or
        source_mod.get("Modules",{}).get("ToSailTheStarrySky")!="UnrealEditor-ToSailTheStarrySky.dll"):
        raise RuntimeError("HOLD: original native module metadata invalid")
    if (DEST/MANIFEST).exists():
        raise RuntimeError("HOLD: module transfer receipt already exists")
    for rel in BINARY_FILES:
        p=SOURCE/rel
        target=DEST/rel
        if not p.is_file() or p.is_symlink() or target.exists():
            raise RuntimeError("HOLD: original module missing or output already exists "+rel)
    return {"status":"VERIFIED_NATIVE_SOURCE_EQUIVALENCE_NO_MODULE_COPIED",
            "source_native_head":SOURCE_HEAD,"target_source_head":dest_head,
            "git_cpp_config_diff_count":0,"engine_version":"5.8.4",
            "module_build_id":source_mod["BuildId"],
            "files":[{"relative_path":r,"sha256":digest(SOURCE/r),"bytes":(SOURCE/r).stat().st_size}
                     for r in BINARY_FILES],
            "native_readback_verified_historical":True,
            "new_worktree_native_module_load_verified":False}

def copy_module():
    report=preflight()
    for rec in report["files"]:
        rel=rec["relative_path"]
        source=SOURCE/rel
        target=DEST/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        with source.open("rb") as reader,target.open("xb") as writer:
            shutil.copyfileobj(reader,writer,1024*1024)
        if digest(target)!=rec["sha256"]:
            raise RuntimeError("HOLD: copied module differs from source "+rel)
    report["status"]="EVIDENCE_BOUND_EDITOR_MODULE_COPIED_NATIVE_LOAD_NOT_YET_RUN"
    receipt=DEST/MANIFEST
    receipt.parent.mkdir(parents=True,exist_ok=True)
    with receipt.open("x",encoding="utf-8") as out:
        json.dump(report,out,indent=2,sort_keys=True)
    return report

def verify_module():
    receipt=DEST/MANIFEST
    if not receipt.is_file():
        raise RuntimeError("HOLD: copied-module custody receipt missing")
    report=json.loads(receipt.read_text(encoding="utf-8"))
    if (report.get("status")!="EVIDENCE_BOUND_EDITOR_MODULE_COPIED_NATIVE_LOAD_NOT_YET_RUN" or
        report.get("source_native_head")!=SOURCE_HEAD or
        report.get("git_cpp_config_diff_count")!=0 or
        report.get("engine_version")!="5.8.4" or
        not report.get("native_readback_verified_historical") or
        report.get("new_worktree_native_module_load_verified") is not False):
        raise RuntimeError("HOLD: compiled module custody claims invalid")
    if len(report.get("files",[]))!=len(BINARY_FILES):
        raise RuntimeError("HOLD: missing required module file receipts")
    if {x["relative_path"] for x in report["files"]}!=set(BINARY_FILES):
        raise RuntimeError("HOLD: unexpected transferred binary paths")
    for x in report["files"]:
        src=SOURCE/x["relative_path"]
        dst=DEST/x["relative_path"]
        if (not src.is_file() or not dst.is_file() or
            digest(src)!=x["sha256"] or digest(dst)!=x["sha256"] or
            dst.stat().st_size!=x["bytes"]):
            raise RuntimeError("HOLD: copied module file/source drift: "+x["relative_path"])
    if diff_paths(SOURCE_HEAD,intake.git(DEST,"rev-parse","HEAD")):
        raise RuntimeError("HOLD: C++/config source parity lost")
    return {"status":"EVIDENCE_BOUND_EDITOR_MODULE_FILES_VERIFIED_NOT_LOADED",
            "module_count":len(report["files"]),
            "source_cpp_config_identical":True,"native_module_load_verified":False}

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--audit",action="store_true")
    g.add_argument("--copy",action="store_true")
    g.add_argument("--verify",action="store_true")
    a=p.parse_args()
    x=preflight() if a.audit else (copy_module() if a.copy else verify_module())
    if a.audit: x={k:v for k,v in x.items() if k!="files"}
    print(json.dumps(x,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
