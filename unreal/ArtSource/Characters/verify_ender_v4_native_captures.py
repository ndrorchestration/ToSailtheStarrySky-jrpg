"""Verify real Ender V4 D3D11 native head turnarounds, not task filenames."""
import hashlib
import json
from pathlib import Path
from verify_render_pngs import resolve_capture,inspect_png
from verify_ender_comparison_pixels import decode_png_rgb
from build_ender_fidelity_v4 import PREDECESSOR_HASHES

SHA="ac36e1d23044ca79d5a954dc8cb85cff8461117c026674ed77fe2e482acaca0b"
MAP="/Game/ArtLookdev/ReviewMaps/TSTSS_EnderFidelityV2_Review"
MAP_SHA="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
VIEWS=("v4_head_front","v4_head_three_quarter","v4_head_profile")

def visible_head(p):
    (w,h),channels,rows=decode_png_rgb(p)
    if (w,h)!=(1280,720):raise ValueError("Unreal frame dimensions wrong")
    foreground=bright=total=0
    for y in range(int(h*.14),int(h*.85),3):
        for x in range(int(w*.28),int(w*.72),3):
            rgb=rows[y][x*channels:x*channels+3]
            total+=1
            if max(rgb)>38:
                foreground+=1
            if all(c>247 for c in rgb):
                bright+=1
    coverage=foreground/total
    if coverage<.015:raise ValueError("Head subject absent/black/clipped")
    if bright/total>.18:raise ValueError("Blown-out head preview")
    return {"central_foreground_fraction":round(coverage,4),
            "central_white_fraction":round(bright/total,4)}

def verify(report_dir,receipt_file):
    receipt=json.loads(Path(receipt_file).read_text(encoding="utf-8"))
    if receipt.get("status")!="V4_NATIVE_SCREENSHOT_TASKS_COMPLETE_PIXEL_QA_PENDING":
        raise ValueError("Missing native V4 task receipt")
    if not str(receipt.get("engine","")).startswith("5.8."):
        raise ValueError("Wrong Unreal version")
    if receipt.get("source_sha256")!=SHA or receipt.get("map")!=MAP:
        raise ValueError("Wrong asset/map source")
    if not str(receipt.get("asset","")).startswith("/Game/ArtLookdev/Characters/EnderAnatomyV4/"):
        raise ValueError("Non-review asset in report")
    if receipt.get("saved_map_sha256_before")!=MAP_SHA or receipt.get("saved_map_sha256_after")!=MAP_SHA:
        raise ValueError("Original V2 map altered or missing")
    if (receipt.get("creator_likeness_approved") is not False or
        receipt.get("production_map_modified") is not False or
        receipt.get("source_modified") is not False or
        receipt.get("unrigged") is not True):
        raise ValueError("Unauthorized V4 production/approval status")
    if tuple(receipt.get("views",()))!=VIEWS:
        raise ValueError("Native camera views changed")
    tasks=receipt.get("capture_tasks",[])
    if [t.get("name") for t in tasks]!=list(VIEWS):
        raise ValueError("Missing/reordered native screenshot tasks")
    for item in tasks:
        if not isinstance(item.get("ticks"),int) or item["ticks"]<0:
            raise ValueError("Missing task completion ticks")
        if not str(item.get("requested","")).replace("\\","/").endswith("/"+item["name"]+".png"):
            raise ValueError("Screenshot request provenance mismatch")
    result={}
    for name in VIEWS:
        p=resolve_capture(Path(report_dir),name)
        result[name]={**inspect_png(p,(1280,720)),**visible_head(p),"actual_png":str(p)}
    if len({v["sha256"] for v in result.values()})!=3:
        raise ValueError("Three views duplicated")
    return {"status":"V4_NATIVE_SCREENSHOT_INTEGRITY_PASS_ART_HOLD",
            "creator_approved":False,"rigged":False,"images":result}

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("report_folder",type=Path)
    parser.add_argument("task_receipt",type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(args.report_folder,args.task_receipt),indent=2))
