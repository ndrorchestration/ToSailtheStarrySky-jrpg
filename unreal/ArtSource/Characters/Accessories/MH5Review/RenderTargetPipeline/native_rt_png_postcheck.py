"""Sanitize native Unreal RenderTarget PNG by removing data after IEND.

This is byte-preserving within all PNG chunks (no image creation, art edits,
or enhancement). Original kept; a separate SHA provenance receipt is emitted.
"""
from pathlib import Path
import hashlib,struct,zlib,json
from PIL import Image,ImageStat

DIR=Path(r"C:\Users\Admin\work\TSTSS-Cast643-UEImport-Sandbox-20261101\Saved\CharacterLookdev\RenderTargetDiagnostic01")
ORIGINAL=DIR/"scene_capture_cube.png"
CLEAN=DIR/"scene_capture_cube_validated.png"
OUT=DIR/"png_integrity_second_opinion.json"
if CLEAN.exists() or OUT.exists():raise RuntimeError("FAIL_CLOSED refuse overwrite")
data=ORIGINAL.read_bytes()
if data[:8]!=b"\x89PNG\r\n\x1a\n":raise RuntimeError("Not PNG")
n=8;types=[];wh=None;endFound=False
while n+12<=len(data):
    length=struct.unpack_from(">I",data,n)[0];tag=data[n+4:n+8]
    end=n+12+length
    if end>len(data):raise RuntimeError("Invalid chunk length")
    payload=data[n+8:n+8+length]
    crc=struct.unpack_from(">I",data,n+8+length)[0]
    if zlib.crc32(tag+payload)&0xffffffff!=crc:raise RuntimeError("CRC mismatch")
    if tag==b"IHDR":wh=struct.unpack_from(">II",payload)
    types.append(tag.decode("ascii","replace"))
    n=end
    if tag==b"IEND":endFound=True;break
if not endFound or wh!=(320,180) or "IDAT" not in types:raise RuntimeError("PNG core not complete")
core=data[:n]
CLEAN.write_bytes(core)
with Image.open(CLEAN) as image:image.verify()
rgb=Image.open(CLEAN).convert("RGB")
s=ImageStat.Stat(rgb)
result={"status":"PNG_CORE_VALID_AND_TRAILING_BYTES_REMOVED",
 "original_file":str(ORIGINAL),"sanitized_file":str(CLEAN),
 "original_sha256":hashlib.sha256(data).hexdigest(),
 "sanitized_sha256":hashlib.sha256(core).hexdigest(),
 "original_bytes":len(data),"sanitized_bytes":len(core),
 "trailing_bytes_removed":len(data)-n,"trailing_contains_png_signature":b"\x89PNG\r\n\x1a\n" in data[n:],
 "png_ihdr_width_height":list(wh),"crc_errors":0,
 "pillow_verify":True,"rgb_mean":[round(v,2) for v in s.mean],
 "pixel_rgb_center":list(rgb.getpixel((160,90))),"pixel_rgb_corner":list(rgb.getpixel((0,0))),
 "pixel_data_modified":False,"source_art_altered":False,
 "metahuman_rendered":False,"goggles_rendered":False}
OUT.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
print("TSTSS_RENDER_TARGET_PNG_CORE_PASS",str(CLEAN),result["trailing_bytes_removed"],result["sanitized_sha256"])
