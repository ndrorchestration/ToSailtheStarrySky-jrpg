"""Independent validation of native Ender V5 MetaHuman landmark-index census.

This check CERTIFIES only API-provided coordinates and read-only source custody.
Do not infer landmark semantics, 2D-reference correspondence or sculpt approval.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ASSET_SHA="7d648da499e5756d845faeed221ac4584e51516d1274b766db41d908e1fb17bd"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
STATUS="NATIVE_METAHUMAN_79_INDEX_ATLAS_PASS_NO_SCULPT"
OBJECT="/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase"
NOT_DONE=("source_asset_changed","face_landmarks_edited","semantic_point_names_known",
          "source_image_landmark_correspondences_approved","likeness_approved",
          "face_assembled","skin_editing_available","rigged","render_verified",
          "image_space_coordinates_measured")

def check_payload(d):
    if d.get("status")!=STATUS or not str(d.get("engine","")).startswith("5.8."):
        raise ValueError("Wrong native status or Unreal engine")
    if d.get("source_asset")!=OBJECT:
        raise ValueError("Unrecognized MetaHuman base")
    if d.get("source_uasset_sha256_before_after")!=ASSET_SHA or d.get("saved_reference_map_sha256_before_after")!=MAP_SHA:
        raise ValueError("Source/map SHA not verified")
    for k in NOT_DONE:
        if d.get(k) is not False:
            raise ValueError("False promotion or missing explicit hold: "+k)
    if d.get("point_count")!=79:
        raise ValueError("Exactly 79 native points required")
    pts=d.get("points",[])
    if not isinstance(pts,list) or len(pts)!=79:
        raise ValueError("Missing points")
    if [v.get("index") for v in pts]!=list(range(79)):
        raise ValueError("Index range/order or uniqueness wrong")
    for entry in pts:
        xyz=entry.get("xyz_cm")
        if not isinstance(xyz,list) or len(xyz)!=3:
            raise ValueError("Coordinate missing")
        if any(not isinstance(x,(int,float)) or isinstance(x,bool) or not math.isfinite(x) or abs(x)>1000 for x in xyz):
            raise ValueError("Nonfinite/implausible coordinate")
    for j,ax in enumerate("xyz"):
        vals=[r["xyz_cm"][j] for r in pts]
        bound=d.get("bounds_cm",{}).get(ax,{})
        if abs(bound.get("min_cm",1e6)-min(vals))>1e-4 or abs(bound.get("max_cm",-1e6)-max(vals))>1e-4:
            raise ValueError("Tampered "+ax+" bounds")
        if max(vals)-min(vals)<0.1:
            raise ValueError("Collapsed "+ax+" native axis")
    if "no semantic names" not in d.get("coordinate_system","").lower():
        raise ValueError("No coordinate/semantic disclaimer")
    return {"status":"V5_NATIVE_INDEX_COORDINATES_VERIFIED_NOT_REFERENCE_MATCHED",
            "points":79,
            "x_span_cm":round(d["bounds_cm"]["x"]["max_cm"]-d["bounds_cm"]["x"]["min_cm"],3),
            "y_span_cm":round(d["bounds_cm"]["y"]["max_cm"]-d["bounds_cm"]["y"]["min_cm"],3),
            "z_span_cm":round(d["bounds_cm"]["z"]["max_cm"]-d["bounds_cm"]["z"]["min_cm"],3),
            "approved_likeness":False}

def check_real(data_file,source_asset,mapfile,logfile):
    d=json.loads(Path(data_file).read_text(encoding="utf-8"))
    report=check_payload(d)
    asset=Path(source_asset).read_bytes()
    if not asset.startswith(bytes.fromhex("c1832a9e")) or hashlib.sha256(asset).hexdigest()!=ASSET_SHA:
        raise ValueError("Native MetaHuman binary source integrity failed")
    if hashlib.sha256(Path(mapfile).read_bytes()).hexdigest()!=MAP_SHA:
        raise ValueError("Native reference map integrity failed")
    log=Path(logfile).read_text(encoding="utf-8",errors="replace")
    for marker in ("TSTSS_ENDER_V5_LANDMARK_ATLAS_NATIVE_PASS",
                   "Test Completed. Result={Success} Name={test_ender_v5_landmark_atlas_native}",
                   "TEST COMPLETE. EXIT CODE: 0"):
        if marker not in log:
            raise ValueError("Missing actual native automation success proof: "+marker)
    report["native_automation_log_verified"]=True
    report["source_binary_sha256"]=ASSET_SHA
    report["reference_map_sha256"]=MAP_SHA
    report["native_landmark_snapshot_sha256"]=hashlib.sha256(Path(data_file).read_bytes()).hexdigest()
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for n in ("json_receipt","native_source_asset","native_review_map","native_log"):
        p.add_argument(n,type=Path)
    args=p.parse_args()
    print(json.dumps(check_real(args.json_receipt,args.native_source_asset,args.native_review_map,args.native_log),indent=2))
