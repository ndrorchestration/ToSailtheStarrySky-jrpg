"""Compare independently captured native UE V5+goggles baseline and -2 EV variants.

This verifies whether the transient post-process exposure setting affected any
PNG pixel. It does not approve character materials or face likeness.
"""
from pathlib import Path
import hashlib,struct,zlib,json
from PIL import Image,ImageChops

ROOT=Path(r"C:\MH5\CastAllSandbox\Saved\CharacterLookdev\GogglesFitV1")
BASE=ROOT/"RenderTargetCombined02"
TEST=ROOT/"RenderTargetCombined03_ExposureBiasMinus2"
OUT=TEST/"exposure_minus2_comparison.json"
if OUT.exists():raise RuntimeError("FAIL_CLOSED output already exists")
def file_core(path):
    b=path.read_bytes()
    if b[:8]!=b"\x89PNG\r\n\x1a\n":raise RuntimeError("Not PNG")
    p=8;end=False
    while p+12<=len(b):
        n=struct.unpack_from(">I",b,p)[0];typ=b[p+4:p+8];endpos=p+12+n
        if endpos>len(b):raise RuntimeError("Incomplete chunk")
        if zlib.crc32(typ+b[p+8:p+8+n])&0xffffffff!=struct.unpack_from(">I",b,p+8+n)[0]:
            raise RuntimeError("CRC error")
        p=endpos
        if typ==b"IEND":end=True;break
    if not end:raise RuntimeError("No PNG IEND")
    return b[:p],len(b)-p
b0,trail0=file_core(BASE/"ender_v5_goggles_rt_front.png")
b1,trail1=file_core(TEST/"ender_v5_goggles_rt_front.png")
r0=json.loads((BASE/"capture_receipt.json").read_text(encoding="utf-8"))
r1=json.loads((TEST/"capture_receipt.json").read_text(encoding="utf-8"))
if not r1.get("exposure_bias_ev")==-2.0:raise RuntimeError("Incorrect variant")
if r0.get("exposure_bias_ev") is not None:raise RuntimeError("Incorrect baseline")
if r0["status"]!=r1["status"] or r1["status"]!="NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED":
    raise RuntimeError("One native run not passed")
if any(r0[k]!=r1[k] for k in ("source_meta_sha256","source_map_sha256","source_goggles_sha256")):
    raise RuntimeError("Source asset drift")
from io import BytesIO
with Image.open(BytesIO(b0)) as image: im0=image.convert("RGB")
with Image.open(BytesIO(b1)) as image: im1=image.convert("RGB")
if im0.size!=(480,320) or im1.size!=(480,320):raise RuntimeError("Image size drift")
difference=ImageChops.difference(im0,im1)
changed_box=difference.getbbox()
report={
"status":"EXPOSURE_MINUS2_RENDER_IDENTICAL_PIXELS_TO_BASELINE" if changed_box is None else "EXPOSURE_MINUS2_RENDER_PIXELS_DIFFER",
"baseline_core_sha256":hashlib.sha256(b0).hexdigest(),
"minus2_core_sha256":hashlib.sha256(b1).hexdigest(),
"baseline_png_trailing_bytes":trail0,"minus2_png_trailing_bytes":trail1,
"same_png_core_bytes":b0==b1,"same_rgb_pixels":changed_box is None,
"exposure_bias_ev_proposed":-2.0,"sampled_image_size":[480,320],
"source_originals_unchanged":True,
"visual_quality_approved":False,"any_sculpt_or_material_asset_changed":False,
"rig_verified":False,"goggles_fit_verified":False,"canonical":False
}
OUT.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
print("TSTSS_NATIVE_EXPOSURE_DELTA",report["status"],report["baseline_core_sha256"],report["minus2_core_sha256"])
