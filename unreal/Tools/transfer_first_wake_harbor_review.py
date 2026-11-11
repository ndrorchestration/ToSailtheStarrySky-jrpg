#!/usr/bin/env python3
"""Content-only, no-overwrite intake of independently verified First Wake Harbor.

The imported private .uasset/.umap packages remain local and untracked.
No restricted Starbourne/Submersible art, running Editor, gameplay state,
source checkout or protected main is changed by the transfer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

SOURCE_ROOT = Path("C:/TSTSS_EnvironmentHarborRecovery_20261105")
DEST_ROOT = Path(__file__).resolve().parents[2]
SOURCE_HEAD = "7c3293babc8d4b39c4d99696ff302211f27028c5"
DEST_BRANCH = "review/ue58-vslice-objects-20261110"
HARBOR_SHA = "073edd19e7ebdcee48b65fb3428fb19d8c8b8c6ca1b95cc4c6f04ed6ea4dd621"
ASSET_WORLD_SHA = "54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5"
MANIFEST = Path("unreal/Saved/FirstWakeSliceObjectsV1/harbor_private_intake_manifest.json")

# Exact known-dependent directories from the verified 34-actor map's six
# existing meshes and their imported materials/textures. Neither unreferenced
# Starbourne nor Submersible candidate directories are included.
FOLDERS = (
    "unreal/Content/ArtLookdev/Characters/EnderFidelityV2",
    "unreal/Content/ArtLookdev/Characters/Ionia",
    "unreal/Content/TSTSS/Review/ShipArt/CinematicV4/AureateWake_SharedExteriorTrim_V4_REVIEW",
    "unreal/Content/TSTSS/Review/ShipArt/CoupledHabitation_20261104/AureateWake_CoupledBridge_Geodesic_REVIEW",
    "unreal/Content/TSTSS/Review/ShipArt/CoupledHabitation_20261104/AureateWake_CurvedLivingQuarters_REVIEW",
    "unreal/Content/TSTSS/Review/ShipArt/WingCinematicCandidate_20261103/AureateWake_Wing_Lookdev",
    "unreal/Content/TSTSS/Review/Environment/FirstWakeHarborV1",
)
FILES = (
    "unreal/Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap",
    "unreal/Content/TSTSS/Review/Scenes/FirstWake_HarborEnvironment_20261104_REVIEW_V1.umap",
    "unreal/Saved/FirstWakeEnvironmentV1/native_harbor_stage.json",
    "unreal/Saved/FirstWakeEnvironmentV1/host_harbor_stage.json",
    "unreal/Saved/FirstWakeEnvironmentV1/independent_harbor_readback.json",
    "unreal/Saved/FirstWakeEnvironmentV1/host_harbor_readback.json",
)

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def git(root,*parts):
    return subprocess.run(["git","-C",str(root),*parts],capture_output=True,
                          text=True,check=True,timeout=30).stdout.strip()

def safe_rel(p):
    path=Path(str(p).replace("\\","/"))
    if (path.is_absolute() or ":" in str(path) or ".." in path.parts or
            not path.parts or path.parts[0].lower()!="unreal"):
        raise RuntimeError("HOLD: unsafe relative asset path")
    if any(x.lower() in str(path).lower() for x in ("starbourne","submersible")):
        raise RuntimeError("HOLD: restricted ship configuration not part of the vertical slice")
    return path

def selected_files(source=SOURCE_ROOT):
    records=set()
    for folder in FOLDERS:
        rel=safe_rel(folder)
        src=source/rel
        if not src.is_dir(): raise RuntimeError("HOLD: missing source package folder "+folder)
        files=list(src.rglob("*.uasset"))
        if not files: raise RuntimeError("HOLD: empty original package folder "+folder)
        for f in files:
            if f.is_symlink() or not f.is_file():
                raise RuntimeError("HOLD: unsafe source package")
            records.add(f.relative_to(source))
    for name in FILES:
        p=safe_rel(name)
        if not (source/p).is_file() or (source/p).is_symlink():
            raise RuntimeError("HOLD: missing source World or receipt "+name)
        records.add(p)
    return sorted(records,key=lambda p:str(p).lower())

def receipt_check(source=SOURCE_ROOT):
    project=source/"unreal"
    saved=project/"Saved/FirstWakeEnvironmentV1"
    native=json.loads((saved/"native_harbor_stage.json").read_text(encoding="utf-8"))
    host=json.loads((saved/"host_harbor_stage.json").read_text(encoding="utf-8"))
    readback=json.loads((saved/"independent_harbor_readback.json").read_text(encoding="utf-8"))
    host_rb=json.loads((saved/"host_harbor_readback.json").read_text(encoding="utf-8"))
    harbor=project/"Content/TSTSS/Review/Scenes/FirstWake_HarborEnvironment_20261104_REVIEW_V1.umap"
    base=project/"Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap"
    if (digest(harbor)!=HARBOR_SHA or digest(base)!=ASSET_WORLD_SHA or
        native.get("status")!="NATIVE_HARBOR_MAP_SAVED_PENDING_INDEPENDENT_READBACK" or
        native.get("map_sha256")!=HARBOR_SHA or
        native.get("parent_map_sha256")!=ASSET_WORLD_SHA or
        native.get("previous_actor_count")!=34 or
        native.get("new_actor_count")!=50 or
        host.get("status")!="NATIVE_MAP_SAVED_PENDING_INDEPENDENT_READBACK" or
        host.get("new_map_sha256")!=HARBOR_SHA or
        host.get("source_head")!=SOURCE_HEAD or
        host.get("editor_exit_code")!=0 or
        readback.get("status")!="INDEPENDENT_NATIVE_HARBOR_SAVED_WORLD_READBACK_PASS_NOT_PIE" or
        readback.get("new_map_sha256")!=HARBOR_SHA or
        readback.get("inherited_actor_count")!=34 or
        readback.get("milestones_verified")!=7 or
        host_rb.get("status")!="INDEPENDENT_NATIVE_HARBOR_READBACK_VERIFIED_NOT_PIE" or
        host_rb.get("new_map_sha256")!=HARBOR_SHA or
        host_rb.get("verified_actor_count")!=84 or
        host_rb.get("verified_material_count")!=8 or
        host_rb.get("editor_exit_code")!=0):
        raise RuntimeError("HOLD: source native Harbor proof incomplete or divergent")
    for record in (host,host_rb):
        for prop in ("config_hashes_preserved","parent_map_sha_preserved","source_head_preserved"):
            if prop in record and not record[prop]:
                raise RuntimeError("HOLD: source native Harbor custody FAILED: "+prop)
    return {"source_native_head":SOURCE_HEAD,"harbor_sha256":HARBOR_SHA,
            "native_actor_count":84,"native_material_count":8,
            "native_readback_verified":True,"native_render_verified":False,
            "pie_verified":False}

def preflight(source=SOURCE_ROOT,dest=DEST_ROOT):
    if source.name!="TSTSS_EnvironmentHarborRecovery_20261105" or dest.name!="TSTSS_VSliceObjects_20261110":
        raise RuntimeError("HOLD: wrong named source/target worktree")
    if source.resolve()==dest.resolve():
        raise RuntimeError("HOLD: source and target same")
    if git(source,"rev-parse","HEAD")!=SOURCE_HEAD:
        raise RuntimeError("HOLD: source native custody SHA changed")
    if git(source,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: source tracked files modified")
    if git(dest,"branch","--show-current")!=DEST_BRANCH:
        raise RuntimeError("HOLD: target branch incorrect")
    if git(dest,"status","--porcelain","--untracked-files=no"):
        raise RuntimeError("HOLD: target tracked files modified")
    if (dest/"unreal/Saved/SaveGames").exists() and list((dest/"unreal/Saved/SaveGames").glob("*.sav")):
        raise RuntimeError("HOLD: existing target SaveGames")
    if (dest/MANIFEST).exists():
        raise RuntimeError("HOLD: transfer manifest already exists; never overwrite")
    if (dest/"unreal/Content/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1.umap").exists():
        raise RuntimeError("HOLD: object scene already saved")
    proof=receipt_check(source)
    selected=selected_files(source)
    if len(selected)<80:
        raise RuntimeError("HOLD: too few native asset dependencies")
    if any((dest/p).exists() for p in selected):
        raise RuntimeError("HOLD: destination contains a native dependency; never overwrite")
    sizes=sum((source/p).stat().st_size for p in selected)
    return {**proof,"source_files":len(selected),"bytes":sizes,
            "selected":[p.as_posix() for p in selected],
            "status":"PRIVATE_SOURCE_DEPENDENCIES_ADMITTED_NOT_COPIED"}

def copy_private_files(report, source=SOURCE_ROOT, dest=DEST_ROOT):
    # Every destination path is new; failed partial copy remains visible for
    # forensics and must not be silently cleaned/retried in this workspace.
    for rel in report["selected"]:
        src=source/safe_rel(rel)
        target=dest/safe_rel(rel)
        target.parent.mkdir(parents=True,exist_ok=True)
        with src.open("rb") as reader,target.open("xb") as writer:
            shutil.copyfileobj(reader,writer,1024*1024)
        if digest(src)!=digest(target):
            raise RuntimeError("HOLD: native dependency transfer hash mismatch "+rel)
    report["status"]="VERIFIED_PRIVATE_HARBOR_ASSETS_COPIED_NOT_UNREAL_LOADED"
    report["file_hashes"]={p:digest(dest/safe_rel(p)) for p in report["selected"]}
    target=dest/MANIFEST
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("x",encoding="utf-8") as stream:
        json.dump(report,stream,indent=2,sort_keys=True)
    return {k:v for k,v in report.items() if k not in ("selected","file_hashes")}

def copy_native():
    return copy_private_files(preflight())

def main():
    parser=argparse.ArgumentParser()
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--audit",action="store_true")
    g.add_argument("--copy",action="store_true")
    args=parser.parse_args()
    result=preflight() if args.audit else copy_native()
    if args.audit: result={k:v for k,v in result.items() if k!="selected"}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
