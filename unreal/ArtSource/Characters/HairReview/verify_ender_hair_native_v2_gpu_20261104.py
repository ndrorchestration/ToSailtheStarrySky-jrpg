"""Independent NEONTIC-only Ender hair native import/render custody verification.

Only runs with actual on-host PNG pixels and Unreal receipts. Hosted CI must NOT
infer native GPU validity from source tests or this script's mere existence.
"""
import hashlib
import io
import json
import struct
import zlib
from pathlib import Path
from PIL import Image, ImageStat

HERE=Path(__file__).resolve().parent
ROOT=Path(r"C:\MH5\CastAllSandbox\Saved\CharacterLookdev\EnderHairReviewV1")
OUT=HERE / "Evidence/ender_hair_native_provenance_v2_20261104.json"
META="2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d"
MAP="025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a"
GOGGLES="5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb"
HAIR_V1="01bb9f400454d633c5e887cd47a12fd1af34e5bbf6b7c05ab6a5929b0a6db562"
HAIR_V2="0da20d3b34e3fdf6171476db1736d2e2607987c71403272207e428f18c8ca9cd"
IMG_V1="fc3e70b005c9c6f4af419de9a91a1d6d077811969f0b816ec8fe72467f68bdcc"
V2_FOLDER=ROOT/"NativeHairV2AndV2Goggles02"
V2_IMAGE="ender_v5_copper_hair_v2_plus_sealed_goggles_v2_front.png"

def need(ok,label):
    if not ok:raise AssertionError("FAIL_CLOSED "+label)

def read_json(p):return json.loads(p.read_text(encoding="utf-8"))

def png_core(p):
    data=p.read_bytes()
    need(data[:8]==b"\x89PNG\r\n\x1a\n","PNG signature")
    end=8;chunks=[];dims=None
    while end+12 <= len(data):
        size=struct.unpack_from(">I",data,end)[0]
        kind=data[end+4:end+8]
        need(size<20_000_000 and end+size+12<=len(data),"PNG bounds")
        payload=data[end+8:end+8+size]
        crc=struct.unpack_from(">I",data,end+8+size)[0]
        need((zlib.crc32(kind+payload)&0xffffffff)==crc,"PNG CRC")
        if kind==b"IHDR":dims=struct.unpack_from(">II",payload)
        chunks.append(kind)
        end += size+12
        if kind==b"IEND":break
    need(chunks[-1]==b"IEND" and b"IDAT" in chunks and dims==(480,320),
         "480x320 PNG complete")
    core=data[:end]
    img=Image.open(io.BytesIO(core)).convert("RGB")
    img.load()
    stat=ImageStat.Stat(img)
    need(sum(stat.stddev)>15,"actual nonflat image pixels")
    return {"sha256_png_core":hashlib.sha256(core).hexdigest(),
            "sha256_raw":hashlib.sha256(data).hexdigest(),
            "crc_valid":True,"trailing_exporter_bytes":len(data)-end,
            "image_size":[480,320],
            "mean_rgb":[round(x,2) for x in stat.mean]}

def guarded_import(name,expected_hash,expected_status,expected_dims):
    x=read_json(ROOT/name)
    need(x["status"]==expected_status,"native import exact status")
    need(x["source_glb_sha256"]==expected_hash==x["glb_sha256_after"],
         "hair source integrity")
    need(x["meta_sha256_after"]==META and x["map_sha256_after"]==MAP,
         "MetaHuman/map unchanged")
    need(x["native_material_slots"]==5 and
         all(abs(a-b)<.01 for a,b in zip(x["native_bounds_xyz_cm"],expected_dims)),
         "actual native static geometry/material axes")
    for flag in ("approved_facial_likeness","actual_hair_fit_verified",
                 "creator_approved","skeletal_mesh","live_hair_groom","gameplay_changed",
                 "original_meta_modified","review_map_modified","canon_promoted"):
        need(x.get(flag) is False,"false acceptance: "+flag)
    return {"status":x["status"],"hair_source_sha256":expected_hash,
            "material_slots":5,"native_bounds_xyz_cm":x["native_bounds_xyz_cm"],
            "is_static_review_mesh":True,"creator_approved":False}

def guarded_capture(dir,filename,expected_status,expected_hair_sha,expected_image_sha=None):
    r=read_json(dir/"capture_receipt.json")
    need(r["status"]==expected_status and len(r["captures"])==1,"real GPU receipt")
    need(r["native_3d_render"] is True and r["canonical"] is False,
         "not a promoted render")
    need(r["source_meta_sha256_after"]==META==r["source_meta_sha256"],
         "original MH integrity")
    need(r["source_map_sha256_after"]==MAP==r["source_map_sha256"],
         "original map integrity")
    need(r["source_goggles_sha256_after"]==GOGGLES==r["source_goggles_v2_glb_sha256"],
         "sealed goggles V2 source integrity")
    need(r["source_hair_sha256_after"]==expected_hair_sha==r["source_hair_glb_sha256"],
         "source hair identity")
    for flag in ("actual_scalp_intersection_verified","goggles_wearable_fit",
                 "approved_face_likeness","hair_visual_approval",
                 "hair_color_lock_approved","rigging_verified",
                 "source_assets_saved","map_saved","production_game_changed"):
        need(r.get(flag) is False,"no false approval: "+flag)
    stats=png_core(dir/filename)
    need(r["captures"][0]["png_core_sha256"]==stats["sha256_png_core"],
         "true image/receipt hash parity")
    if expected_image_sha:
        need(stats["sha256_png_core"]==expected_image_sha,"pinned V1 screenshot SHA")
    return stats

def run():
    head=read_json(ROOT/"NativeHeadBounds01/head_bounds.json")
    need(head["status"]=="NATIVE_V5_SKELETAL_COMPONENT_BOUNDS_READBACK_PASS_ART_HOLD",
         "native head bone readback")
    need(head["meta_sha256_after"]==META and head["map_sha256_after"]==MAP,
         "head probe integrity")
    need(all("bounds_unavailable" in comp for comp in head["components"]),
         "do not claim actual scalp bounds when API returned no bounds")
    first=guarded_import("native_import01.json",HAIR_V1,
           "NATIVE_ENDER_HAIR_STATIC_IMPORT_PASS_FIT_AND_ART_HOLD",
           [23.0297,18.7177,24.3367])
    second=guarded_import("native_import02.json",HAIR_V2,
           "NATIVE_ENDER_HAIR_V2_STATIC_IMPORT_PASS_FIT_AND_ART_HOLD",
           [23.0270,18.4382,24.9912])
    v1=guarded_capture(ROOT/"NativeHairAndV2Goggles01",
           "ender_v5_copper_hair_v1_plus_sealed_goggles_v2_front.png",
           "NATIVE_ENDER_COPPER_HAIR_V1_AND_GOGGLES_V2_GPU_PASS_ART_HOLD",
           HAIR_V1,IMG_V1)
    v2_status="NOT_CAPTURED_NATIVE"
    v2=None
    if (V2_FOLDER/"capture_receipt.json").is_file():
        v2=guarded_capture(V2_FOLDER,V2_IMAGE,
             "NATIVE_ENDER_COPPER_HAIR_V2_AND_GOGGLES_V2_GPU_PASS_ART_HOLD",HAIR_V2)
        v2_status="NATIVE_GPU_CAPTURED_REQUIRES_VISUAL_ARTIST_QA"
    result={
        "status":"NATIVE_V1_RENDER_VERIFIED_VISUAL_FAIL_V2_IMPORT_VERIFIED"
                 if v2 is None else "NATIVE_V1_V2_RENDER_TECH_VERIFIED_ART_HOLD",
        "first_approved_character_art_not_in_git":True,
        "v1_static_import":first,
        "v2_static_import":second,
        "v1_actual_native_gpu_png":v1,
        "v1_visual_qa":"FAIL_PALE_ROPELIKE_STRANDS_CROP_AND_HAIRLINE",
        "v2_capture_status":v2_status,
        "v2_actual_native_gpu_png":v2,
        "scalp_bounds_native_api_unavailable":True,
        "hair_groom_rigging_approved":False,
        "rejected_v1_goggles_promoted":False,
        "creator_approval":False,"gameplay_integration":False,
        "source_sha256":{"meta":META,"map":MAP,"sealed_v2_goggles":GOGGLES}
    }
    text=json.dumps(result,sort_keys=True,indent=2)+"\n"
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if OUT.exists():
        need(OUT.read_text(encoding="utf-8")==text,"already-recorded receipt mismatch")
    else:OUT.write_text(text,encoding="utf-8")
    print(text)

if __name__=="__main__":
    run()
