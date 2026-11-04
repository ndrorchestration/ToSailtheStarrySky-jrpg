"""Verify and normalize UE native V5+goggles render-target PNG.

The untouched original remains in the private MH5 Saved directory. Removes
only non-PNG bytes after IEND. The visual review WebP is recompressed for
sharing but never represented as an unmodified native source image.
"""
from pathlib import Path
import hashlib,struct,zlib,json
from PIL import Image,ImageStat

DIR=Path(r"C:\MH5\CastAllSandbox\Saved\CharacterLookdev\GogglesFitV1\RenderTargetCombined02")
RAW=DIR/"ender_v5_goggles_rt_front.png"
CLEAN=DIR/"ender_v5_goggles_rt_front_clean.png"
WEBP=DIR/"ender_v5_goggles_rt_front_review.webp"
OUT=DIR/"png_postprocessing_receipt.json"
NATIVE=DIR/"capture_receipt.json"
if any(p.exists() for p in [CLEAN,WEBP,OUT]):
    raise RuntimeError("FAIL_CLOSED refuse overwrite")
data=RAW.read_bytes()
native=json.loads(NATIVE.read_text(encoding="utf-8"))
if native["status"]!="NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED":
    raise RuntimeError("No native capture proof")
if data[:8]!=b"\x89PNG\r\n\x1a\n":raise RuntimeError("Not PNG")
pos=8;chunks=[];wh=None;end=False
while pos+12<=len(data):
    n=struct.unpack_from(">I",data,pos)[0];tag=data[pos+4:pos+8]
    finish=pos+12+n
    if finish>len(data):raise RuntimeError("Incomplete PNG")
    payload=data[pos+8:pos+8+n]
    crc=struct.unpack_from(">I",data,pos+8+n)[0]
    if zlib.crc32(tag+payload)&0xffffffff!=crc:raise RuntimeError("CRC invalid")
    if tag==b"IHDR":wh=struct.unpack_from(">II",payload)
    chunks.append(tag.decode("ascii"))
    pos=finish
    if tag==b"IEND":end=True;break
if not end or "IDAT" not in chunks or wh!=(480,320):
    raise RuntimeError("Incorrect source PNG")
core=data[:pos]
if native["captures"][0]["sha256_raw"]!=hashlib.sha256(data).hexdigest():raise RuntimeError("Raw receipt drift")
if native["captures"][0]["sha256_png_core"]!=hashlib.sha256(core).hexdigest():raise RuntimeError("Core receipt drift")
CLEAN.write_bytes(core)
with Image.open(CLEAN) as im:im.verify()
im=Image.open(CLEAN).convert("RGB")
s=ImageStat.Stat(im)
if sum(mx-mn for mn,mx in s.extrema)<25:
    raise RuntimeError("Suspiciously flat image")
im.save(WEBP,"WEBP",quality=89,method=6)
with Image.open(WEBP) as view:view.verify()
rec={"status":"NATIVE_V5_GOGGLES_PNG_CORE_VERIFIED_SAFE_COPY",
     "original_file":str(RAW),"validated_copy":str(CLEAN),
     "review_webp":str(WEBP),"original_raw_sha256":hashlib.sha256(data).hexdigest(),
     "validated_png_sha256":hashlib.sha256(core).hexdigest(),
     "review_webp_sha256":hashlib.sha256(WEBP.read_bytes()).hexdigest(),
     "raw_bytes":len(data),"validated_png_bytes":len(core),
     "review_webp_bytes":WEBP.stat().st_size,"trailing_bytes_removed":len(data)-pos,
     "png_width_height":list(wh),"pillow_verified":True,"png_chunk_crc_verified":True,
     "rgb_extrema":s.extrema,"rgb_mean":[round(v,2) for v in s.mean],
     "pixel_data_modified_in_png":False,"review_webp_lossy_recompression":True,
     "source_character_or_map_modified":False,"artist_accepted":False,
     "wearable_head_fit_verified":False,"material_fidelity_verified":False,
     "production_game_asset":False,"canonical":False}
OUT.write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("TSTSS_V5_GOGGLES_PNG_VERIFIED",str(CLEAN),"WEBP_BYTES",rec["review_webp_bytes"],
      "SHA",rec["validated_png_sha256"])
