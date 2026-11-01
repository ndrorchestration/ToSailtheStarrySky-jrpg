#!/usr/bin/env python3
"""Fail-closed check and opt-in UE Editor import for the 100-cm support GLB.

--check works in ordinary Python, and verifies exact bytes and linear units.
--import-review requires Unreal Editor Python and never touches gameplay maps,
ships or the existing reviewed wing import destination.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct

FILENAME="AureateWake_RootSupport_Lookdev.glb"
STATUS="NONCANONICAL_REVIEW_NOT_ART_ACCEPTED"
REVIEW_FOLDER="/Game/TSTSS/Review/ShipArt/RootSupportCandidateV1"


class SupportReviewHold(ValueError):
    pass


def preflight(asset: Path, manifest_path: Path) -> dict:
    asset=asset.resolve(strict=True)
    manifest_path=manifest_path.resolve(strict=True)
    if asset.name != FILENAME or asset.stat().st_size > 20_000_000:
        raise SupportReviewHold("Expected one named, bounded root support candidate")
    doc_manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    if doc_manifest.get("status")!=STATUS:
        raise SupportReviewHold("Missing noncanonical review provenance")
    if (doc_manifest.get("source_to_gltf_scale"),doc_manifest.get("nominal_length_cm"))!=(.01,100.):
        raise SupportReviewHold("Unsupported unit scale or strut length")
    binary=asset.read_bytes()
    sha=hashlib.sha256(binary).hexdigest()
    if sha!=doc_manifest.get("sha256",{}).get(FILENAME):
        raise SupportReviewHold("SHA-256 mismatch: refused altered support GLB")
    if len(binary)<28 or binary[:4]!=b"glTF":
        raise SupportReviewHold("Missing binary GLB header")
    version,total=struct.unpack_from("<II",binary,4)
    jlen,jtype=struct.unpack_from("<I4s",binary,12)
    if version!=2 or total!=len(binary) or jtype!=b"JSON" or jlen%4 or 20+jlen+8>len(binary):
        raise SupportReviewHold("Invalid glTF 2.0 JSON container")
    bin_len,bin_type=struct.unpack_from("<I4s",binary,20+jlen)
    if bin_type!=b"BIN\0" or bin_len%4 or 20+jlen+8+bin_len!=len(binary):
        raise SupportReviewHold("Invalid binary GLB chunk")
    scene=json.loads(binary[20:20+jlen])
    extras=scene.get("extras",{})
    if (extras.get("authority"),extras.get("gltfLinearUnits"),extras.get("sourceToGltfScale"),
        extras.get("strutLengthCm"))!=(STATUS,"meters",.01,100.):
        raise SupportReviewHold("Missing authored meter-scale/authority proof")
    meshes=scene.get("meshes",[])
    if len(meshes)!=1 or len(meshes[0].get("primitives",[]))!=3 or len(scene.get("materials",[]))!=3:
        raise SupportReviewHold("Expected exactly 3 material-section root support")
    for section in meshes[0]["primitives"]:
        attr=section.get("attributes",{})
        if not {"POSITION","NORMAL","TEXCOORD_0"}.issubset(attr):
            raise SupportReviewHold("Incomplete PBR vertex attributes")
        if section.get("mode") != 4:
            raise SupportReviewHold("Expected triangles")
    accessor=scene["accessors"][meshes[0]["primitives"][0]["attributes"]["POSITION"]]
    if abs(accessor["min"][0])>1e-5 or abs(accessor["max"][0]-1)>1e-5:
        raise SupportReviewHold("Expected GLB strut to span 1 meter on local +X")
    materials=scene["materials"]
    if "emissiveFactor" not in materials[2]:
        raise SupportReviewHold("Missing luminous detail section")
    return {"authority":"REVIEW_ONLY_NOT_GAMEPLAY","sha256":sha,
            "strut_length_cm":100.,"material_sections":3,"destination":REVIEW_FOLDER}


def import_review(asset: Path, receipt: dict) -> dict:
    try:
        import unreal
    except ImportError as exc:
        raise SupportReviewHold("Unreal Editor Python required for --import-review") from exc
    required=("EditorAssetLibrary","AssetImportTask","AssetToolsHelpers","StaticMesh","load_asset")
    if not all(hasattr(unreal,name) for name in required):
        raise SupportReviewHold("Unreal Editor import APIs not available")
    lib=unreal.EditorAssetLibrary
    if lib.does_directory_exist(REVIEW_FOLDER) and lib.list_assets(REVIEW_FOLDER, recursive=True, include_folder=False):
        raise SupportReviewHold("Refusing to overwrite any existing reviewed support asset")
    task=unreal.AssetImportTask()
    task.set_editor_property("filename",str(asset.resolve(strict=True)))
    task.set_editor_property("destination_path",REVIEW_FOLDER)
    task.set_editor_property("automated",False)
    task.set_editor_property("replace_existing",False)
    task.set_editor_property("save",True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    paths=list(task.get_editor_property("imported_object_paths"))
    imported=[unreal.load_asset(p) for p in paths]
    if not any(isinstance(item,unreal.StaticMesh) for item in imported if item is not None):
        raise SupportReviewHold("No StaticMesh was imported; inspect editor dialog/candidate folder")
    return {"status":"IMPORTED_AS_REVIEW_CANDIDATE_ONLY","candidate_assets":paths,
            "source_sha256":receipt["sha256"]}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--glb",required=True,type=Path)
    parser.add_argument("--manifest",required=True,type=Path)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--import-review",action="store_true")
    args=parser.parse_args(argv)
    try:
        result=preflight(args.glb,args.manifest)
        if args.import_review:
            result["import_result"]=import_review(args.glb,result)
        print(json.dumps(result,indent=2))
    except (SupportReviewHold,OSError,KeyError,IndexError,TypeError,ValueError,struct.error) as exc:
        parser.exit(1,"ROOT SUPPORT IMPORT HOLD: "+str(exc)+"\n")


if __name__=="__main__":
    main()
