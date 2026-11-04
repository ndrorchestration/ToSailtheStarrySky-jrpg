"""Produce a labelled comparison of THREE existing UE screenshots; no image invention."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib

ROOT=Path(r"C:\MH4\CastAllSandbox\Saved\CharacterLookdev\V5NativeScreens")
SOURCES=[
    ("PROFILE  /  +X", "ender_v5_green_faceclose01","face_front_close.png"),
    ("FRONT  /  +Y", "ender_v5_green_truefront02","face_truefront_plus_y.png"),
    ("THREE-QUARTER  /  +X +Y", "ender_v5_green_threequarter03","face_threequarter_front.png"),
]
OUT=ROOT/"Ender_V5_Three_Angles_Native_20261103.png"
MANIFEST=ROOT/"Ender_V5_Three_Angles_Native_20261103.json"
if OUT.exists() or MANIFEST.exists():
    raise RuntimeError("FAIL_CLOSED: output already exists")
W,H=800,450
margin,pad=24,14
panel_w,panel_h=640,360
canvas_w=margin*2+3*panel_w+2*pad
canvas_h=514
canvas=Image.new("RGB",(canvas_w,canvas_h),(18,23,29))
draw=ImageDraw.Draw(canvas)
try:
    font=ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf",22)
    small=ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf",15)
except Exception:
    font=ImageFont.load_default()
    small=ImageFont.load_default()
manifest={"status":"THREE_NATIVE_RENDER_FILES_VERIFIED_VISUAL_LIKENESS_NOT_APPROVED",
    "provenance":"Original Unreal 5.8.4 D3D11 PNGs; only labels and resizing added",
    "game":"To Sail the Starry Sky", "character":"Ender V5",
    "cropped_or_invented_face":False,"canonical":False,
    "source_original_asset_sha256":"2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d",
    "source_original_map_sha256":"025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a",
    "views":[]}
for i,(label,folder,name) in enumerate(SOURCES):
    dir=ROOT/folder
    png=dir/name
    receipt=dir/"capture_receipt.json"
    if not png.is_file() or not receipt.is_file():
        raise RuntimeError("FAIL_CLOSED: original screenshot absent: "+name)
    data=json.loads(receipt.read_text(encoding="utf-8"))
    if data["status"]!="NATIVE_PNG_CAPTURED_VISUAL_UNREVIEWED":
        raise RuntimeError("FAIL_CLOSED: screenshot receipt not successful")
    if data["asset_sha256_after"]!=manifest["source_original_asset_sha256"] or data["map_sha256_after"]!=manifest["source_original_map_sha256"]:
        raise RuntimeError("FAIL_CLOSED: source assets changed during rendering")
    blob=png.read_bytes()
    sha=hashlib.sha256(blob).hexdigest()
    if data["captures"][0]["sha256"]!=sha:
        raise RuntimeError("FAIL_CLOSED: screenshot SHA mismatch")
    with Image.open(png) as image:
        if image.size!=(W,H):raise RuntimeError("Unexpected native PNG resolution")
        frame=image.convert("RGB").resize((panel_w,panel_h),Image.Resampling.LANCZOS)
    x=margin+i*(panel_w+pad)
    canvas.paste(frame,(x,69))
    draw.rectangle((x,69,x+panel_w-1,69+panel_h-1),outline=(74,88,103),width=2)
    draw.text((x,29),label,fill=(230,234,239),font=font)
    manifest["views"].append({"label":label,"native_source":str(png),"native_sha256":sha,"native_size":[W,H],"resized_size":[panel_w,panel_h],"verified":True})
draw.line((margin,445,canvas_w-margin,445),fill=(68,80,90),width=2)
draw.text((margin,459),"ENDER V5  /  UNREAL 5.8.4  /  NONCANONICAL MODEL & MATERIAL REVIEW",fill=(255,200,115),font=small)
draw.text((margin,483),"Real native GPU captures  •  No sculpt, rig, or cinematic likeness approval implied",fill=(177,187,196),font=small)
canvas.save(OUT,format="PNG",optimize=True)
manifest["contact_sheet_sha256"]=hashlib.sha256(OUT.read_bytes()).hexdigest()
manifest["contact_sheet_path"]=str(OUT)
MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
print("NATIVE_V5_THREE_VIEW_CONTACT_SHEET_PASS",str(OUT))
for v in manifest["views"]:print(v["label"],v["native_sha256"],"VERIFIED")
print("SHEET_SHA256",manifest["contact_sheet_sha256"])
