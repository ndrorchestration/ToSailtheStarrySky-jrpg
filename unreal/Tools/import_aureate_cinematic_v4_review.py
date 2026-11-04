#!/usr/bin/env python3
"""Fail-closed preflight; optionally import V4 detail GLBs to a disposable UE sandbox.

--check is pure Python and performs NO Unreal calls. --import-review may ONLY
run in a newly created project named AureateCinematicV4Sandbox with explicit
REVIEW_ONLY project description. No maps, actors, game code or form gates change.
Native asset writes are not transactional: discard the sandbox on failure.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

try:
    from build_aureate_cinematic_v4 import (
        FILES, MANIFEST, REVIEW_ROOT, PROVENANCE, APPROVED_ART_SHA,
        FORM_NAMES, ATTACHMENTS, STATUS)
except ImportError:
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"ArtSource"/"ShipReview"))
    from build_aureate_cinematic_v4 import (
        FILES, MANIFEST, REVIEW_ROOT, PROVENANCE, APPROVED_ART_SHA,
        FORM_NAMES, ATTACHMENTS, STATUS)


class CinematicV4Hold(ValueError):
    pass


def preflight(folder:Path):
    folder=folder.resolve(strict=True)
    if not folder.is_dir(): raise CinematicV4Hold("Source must be a directory")
    if {p.name for p in folder.iterdir()} != set(FILES)|{MANIFEST}:
        raise CinematicV4Hold("Unexpected or missing review files")
    manifest=json.loads((folder/MANIFEST).read_text(encoding="utf-8"))
    expected={"stage":PROVENANCE,"status":STATUS,
              "original_approved_image_sha256":APPROVED_ART_SHA,
              "canonical_form_names":list(FORM_NAMES),
              "candidate_import_folder":REVIEW_ROOT,
              "attachment_plan_review_only":ATTACHMENTS,
              "material_sections_each":4,
              "native_unreal_import":"NOT_VERIFIED",
              "native_unreal_render":"NOT_VERIFIED",
              "starbourne_gameplay_unlocked":False,
              "form_enum_or_save_schema_changed":False,
              "production_content_changed":False}
    for key,correct in expected.items():
        if manifest.get(key)!=correct:
            raise CinematicV4Hold("Manifest safety/provenance mismatch: "+key)
    found={}
    for name in FILES:
        p=folder/name
        if p.is_symlink() or not p.is_file() or p.stat().st_size>25_000_000:
            raise CinematicV4Hold("Unsafe GLB candidate: "+name)
        blob=p.read_bytes()
        if hashlib.sha256(blob).hexdigest()!=manifest.get("sha256",{}).get(name):
            raise CinematicV4Hold("SHA-256 mismatch: "+name)
        if len(blob)<28 or blob[:4]!=b"glTF":
            raise CinematicV4Hold("Invalid GLB header: "+name)
        version,total=struct.unpack_from("<II",blob,4)
        jlen,jtype=struct.unpack_from("<I4s",blob,12)
        if version!=2 or total!=len(blob) or jtype!=b"JSON" or jlen%4 or 20+jlen+8>len(blob):
            raise CinematicV4Hold("Invalid GLB framing: "+name)
        binlen,bintype=struct.unpack_from("<I4s",blob,20+jlen)
        if bintype!=b"BIN\0" or binlen%4 or 20+jlen+8+binlen!=len(blob):
            raise CinematicV4Hold("Invalid GLB binary chunk: "+name)
        doc=json.loads(blob[20:20+jlen])
        if doc.get("extras",{}).get("authority")!=STATUS or doc["extras"].get("sourceToGltfScale")!=.01:
            raise CinematicV4Hold("GLB not a meter-scaled review candidate: "+name)
        meshes=doc.get("meshes",[])
        if len(meshes)!=1 or len(meshes[0].get("primitives",[]))!=4 or len(doc.get("materials",[]))!=4:
            raise CinematicV4Hold("Missing material/mesh sections: "+name)
        found[name]=hashlib.sha256(blob).hexdigest()
    return {"status":"SAFE_FOR_DISPOSABLE_UNREAL_IMPORT_REVIEW_ONLY",
            "candidate_folder":REVIEW_ROOT,"sha256":found,
            "asset_count":len(found),"starbourne_locked":True}


def native_import(folder:Path,receipt:dict):
    try: import unreal
    except ImportError as exc:
        raise CinematicV4Hold("Native import requires Unreal Editor Python") from exc
    project_dir=Path(unreal.Paths.project_dir()).resolve()
    if project_dir.name!="AureateCinematicV4Sandbox":
        raise CinematicV4Hold("Refusing active/game project: use AureateCinematicV4Sandbox")
    project_file=project_dir/"AureateCinematicV4Sandbox.uproject"
    conf=json.loads(project_file.read_text(encoding="utf-8-sig"))
    if conf.get("EngineAssociation") not in ("5.8","5.8.4") or \
            "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in conf.get("Description",""):
        raise CinematicV4Hold("Sandbox engine / review designation mismatch")
    if not unreal.SystemLibrary.get_engine_version().startswith("5.8."):
        raise CinematicV4Hold("Native engine version is not 5.8.x")
    lib=unreal.EditorAssetLibrary
    if lib.does_directory_exist(REVIEW_ROOT) and \
            lib.list_assets(REVIEW_ROOT,recursive=True,include_folder=False):
        raise CinematicV4Hold("Destination occupied; refuse overwrite")
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    imported={}
    for name in FILES:
        job=unreal.AssetImportTask()
        job.set_editor_property("filename",str((folder/name).resolve(strict=True)))
        job.set_editor_property("destination_path",REVIEW_ROOT)
        job.set_editor_property("automated",True)
        job.set_editor_property("replace_existing",False)
        job.set_editor_property("save",True)
        tools.import_asset_tasks([job])
        paths=list(job.get_editor_property("imported_object_paths"))
        meshes=[unreal.load_asset(path) for path in paths]
        static=[asset for asset in meshes if isinstance(asset,unreal.StaticMesh)]
        if len(static)!=1:
            raise CinematicV4Hold("Import returned wrong StaticMesh count: "+name)
        imported[name]=paths
    return {"status":"IMPORTED_IN_DISPOSABLE_REVIEW_SANDBOX_NOT_ART_APPROVED",
            "candidate_assets":imported,"source_sha256":receipt["sha256"],
            "scene_saved":False,"actor_changed":False,"starbourne_unlocked":False}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-dir",required=True,type=Path)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--import-review",action="store_true")
    args=p.parse_args(argv)
    try:
        receipt=preflight(args.source_dir)
        if args.import_review:
            receipt["native_result"]=native_import(args.source_dir,receipt)
        print(json.dumps(receipt,indent=2,sort_keys=True))
    except (CinematicV4Hold,OSError,ValueError,KeyError,TypeError) as exc:
        p.exit(1,"AUREATE CINEMATIC V4 HOLD: "+str(exc)+"\n")


if __name__=="__main__":
    main()
