#!/usr/bin/env python3
"""Fail-closed two-asset review intake for the Aureate Wake hull and bridge.

--check works offline. --import-review requires Unreal Editor Python and must
be explicitly invoked. Does not attach meshes to gameplay, delete existing
assets, change levels, unlock Orbiter or promote any art to canon.

UE import of separate assets is NOT transactional; partial results trigger
a HOLD and remain for manual inspection, never a false atomic success.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct

import author_aureate_body_pair as body

MAX_GLBS = 6_000_000


class BodyPairHold(ValueError):
    pass


def inspect_glb(blob: bytes, expected_name: str):
    if len(blob)<28 or len(blob)>MAX_GLBS or blob[:4]!=b"glTF":
        raise BodyPairHold("Invalid or oversized body candidate GLB")
    version,total=struct.unpack_from("<II",blob,4)
    if version!=2 or total!=len(blob):
        raise BodyPairHold("Invalid GLB length or version")
    jlen,jtype=struct.unpack_from("<I4s",blob,12)
    if jtype!=b"JSON" or jlen%4!=0 or 20+jlen+8>len(blob):
        raise BodyPairHold("Malformed JSON chunk")
    bstart=20+jlen
    blen,btype=struct.unpack_from("<I4s",blob,bstart)
    if btype!=b"BIN\x00" or blen%4!=0 or bstart+8+blen!=len(blob):
        raise BodyPairHold("Malformed BIN chunk")
    try:
        info=json.loads(blob[20:bstart])
    except (UnicodeDecodeError,ValueError) as e:
        raise BodyPairHold("Unreadable JSON section") from e
    meta=info.get("extras",{})
    if (meta.get("authority")!=body.STATUS or
        meta.get("sourceUnits")!="centimeters" or
        meta.get("gltfLinearUnits")!="meters" or
        meta.get("sourceToGltfScale")!=0.01 or
        meta.get("orbiter")!="locked" or
        meta.get("noGameplayOrCollision") is not True):
        raise BodyPairHold("Unapproved source scale, usage or Orbiter provenance")
    if len(info.get("meshes",[]))!=1 or len(info["meshes"][0].get("primitives",[]))!=3:
        raise BodyPairHold("Expected one three-section review mesh")
    if len(info.get("materials",[]))!=3:
        raise BodyPairHold("Expected three review material sections")
    for primitive in info["meshes"][0]["primitives"]:
        if set(primitive.get("attributes",{}))!={"POSITION","NORMAL","TEXCOORD_0"}:
            raise BodyPairHold("Incomplete mesh channels")
        if primitive.get("mode")!=4:
            raise BodyPairHold("Wrong mesh primitive mode")
    if expected_name==body.HULL:
        a=info["accessors"][info["meshes"][0]["primitives"][0]["attributes"]["POSITION"]]
        if abs(a["min"][0]+4.8)>.001 or abs(a["max"][0]-5.6)>.001:
            raise BodyPairHold("Hull x-axis or scale mismatch")
    elif expected_name==body.BRIDGE:
        a=info["accessors"][info["meshes"][0]["primitives"][0]["attributes"]["POSITION"]]
        if not 1.46<a["max"][1]<1.49 or info["materials"][0].get("alphaMode")!="BLEND":
            raise BodyPairHold("Bridge dome height or glass material mismatch")
    else:
        raise BodyPairHold("Unexpected body part name")
    return info


def preflight(folder: Path) -> dict:
    folder=folder.resolve(strict=True)
    if not folder.is_dir():raise BodyPairHold("Expected a body-pair folder")
    try:
        manifest=json.loads((folder/body.MANIFEST).read_text(encoding="utf-8"))
    except (OSError,ValueError) as e:
        raise BodyPairHold("Missing or malformed body manifest") from e
    if (manifest.get("status")!=body.STATUS or
        manifest.get("source_to_gltf_scale")!=0.01 or
        manifest.get("source_units")!="centimeters" or
        manifest.get("gltf_linear_units")!="meters" or
        manifest.get("destinations")!=body.DESTINATIONS or
        set(manifest.get("parts",[]))!={body.HULL,body.BRIDGE}):
        raise BodyPairHold("Manifest does not describe the approved review-only intake contract")
    receipts={}
    for name in (body.HULL,body.BRIDGE):
        path=(folder/name).resolve(strict=True)
        if path.parent!=folder or path.name!=name:
            raise BodyPairHold("Unexpected external or redirected source file")
        blob=path.read_bytes()
        digest=hashlib.sha256(blob).hexdigest()
        if manifest.get("sha256",{}).get(name)!=digest:
            raise BodyPairHold("Source hash differs from generated receipt: "+name)
        inspect_glb(blob,name)
        receipts[name]={"sha256":digest,"bytes":len(blob),
                        "destination":body.DESTINATIONS[name]}
    return {"authority":"NONCANONICAL_REVIEW_NOT_GAMEPLAY",
            "parts":receipts, "checked":True}


def import_review(folder: Path, receipt: dict) -> dict:
    try:
        import unreal
    except ImportError as e:
        raise BodyPairHold("Unreal Editor Python is required for --import-review") from e
    required=("EditorAssetLibrary","AssetImportTask","AssetToolsHelpers",
              "StaticMesh","load_asset")
    if not all(hasattr(unreal,name) for name in required):
        raise BodyPairHold("Missing Unreal Editor import APIs")
    lib=unreal.EditorAssetLibrary
    # Both destination preflights occur BEFORE creating either task.
    for name in (body.HULL,body.BRIDGE):
        dest=body.DESTINATIONS[name]
        if lib.does_directory_exist(dest) and lib.list_assets(
            dest,recursive=True,include_folder=False):
            raise BodyPairHold("An intake destination is occupied; no overwrite: "+dest)
    tasks=[]
    for name in (body.HULL,body.BRIDGE):
        task=unreal.AssetImportTask()
        task.set_editor_property("filename",str((folder/name).resolve(strict=True)))
        task.set_editor_property("destination_path",body.DESTINATIONS[name])
        task.set_editor_property("automated",False) # human inspects Interchange pipeline
        task.set_editor_property("replace_existing",False)
        task.set_editor_property("save",True)
        tasks.append(task)
    # Import is not atomic in UE. A partial result cannot count as success.
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    imported={}
    for name,task in zip((body.HULL,body.BRIDGE),tasks):
        paths=list(task.get_editor_property("imported_object_paths"))
        good=[p for p in paths if p.startswith(body.DESTINATIONS[name]+"/")
              and isinstance(unreal.load_asset(p),unreal.StaticMesh)]
        imported[name]={"assets":paths,"static_meshes":good}
    if not all(imported[n]["static_meshes"] for n in (body.HULL,body.BRIDGE)):
        raise BodyPairHold(
            "PARTIAL IMPORT HOLD: one or both StaticMesh assets missing. "
            "Inspect candidate folders manually; no gameplay bindings were made.")
    return {"status":"TWO_REVIEW_MESHES_IMPORTED_NOT_APPROVED",
            "source_checksums":{n:v["sha256"] for n,v in receipt["parts"].items()},
            "candidate_assets":imported}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir",type=Path,required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--import-review",action="store_true")
    args=parser.parse_args(argv)
    try:
        receipt=preflight(args.source_dir)
        if args.import_review:
            receipt["import_review"]=import_review(args.source_dir.resolve(),receipt)
        print(json.dumps(receipt,indent=2))
    except (BodyPairHold,OSError,KeyError,IndexError,TypeError,struct.error) as e:
        parser.exit(1,"BODY PAIR INTAKE HOLD: "+str(e)+"\n")


if __name__=="__main__":
    main()
