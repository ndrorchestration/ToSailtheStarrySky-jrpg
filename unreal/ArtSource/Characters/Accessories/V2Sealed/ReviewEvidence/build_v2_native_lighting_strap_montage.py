"""Create review-only triptych from three verified native V2 Unreal PNGs.

Never edits the source image; only scales and labels native frames. Does not
confer artistic approval or prove physical head/strap contact.
"""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
base=Path(r"C:\MH5\CastAllSandbox\Saved\CharacterLookdev\GogglesFitV2")
spec=[
 ("Old lighting","RenderTargetV2LowerForehead02","ender_v5_sealed_aviator_goggles_v2_lower_front.png"),
 ("Low lighting","RenderTargetV2LowerForehead04_LightsTenth","ender_v5_sealed_aviator_goggles_v2_lower_front.png"),
 ("Rear-side","RenderTargetV2RearSide05_LightsTenth","ender_v5_sealed_goggles_v2_rearside.png"),
]
output=base/"Ender_V2_Native_Light_And_Strap_Review_20261104.webp"
receipt=base/"Ender_V2_Native_Light_And_Strap_Review_20261104.json"
if output.exists() or receipt.exists(): raise RuntimeError("FAIL_CLOSED output exists")
panel=(400,267)
canvas=Image.new("RGB",(3*400+40,330),(21,26,31))
d=ImageDraw.Draw(canvas)
try:ft=ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf",20)
except Exception: ft=ImageFont.load_default()
sources=[]
for i,(label,folder,name) in enumerate(spec):
    directory=base/folder
    path=directory/name
    r=json.loads((directory/"capture_receipt.json").read_text(encoding="utf8"))
    if r["status"] not in ("NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED","NATIVE_V2_TENTH_LIGHT_PNG_CORE_PASS_VISUAL_UNREVIEWED"):
        raise RuntimeError("Native capture unverified "+folder)
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=r["captures"][0]["sha256_raw"]:
        raise RuntimeError("Native image SHA drift "+folder)
    with Image.open(path) as im:
        if im.size!=(480,320):raise RuntimeError("Unexpected image size")
        img=im.convert("RGB").resize(panel,Image.Resampling.LANCZOS)
    left=20+400*i
    canvas.paste(img,(left,40))
    d.text((left+8,12),label,fill=(235,240,244),font=ft)
    sources.append({"folder":folder,"filename":name,
                    "native_raw_sha256":r["captures"][0]["sha256_raw"],
                    "native_core_sha256":r["captures"][0]["sha256_png_core"]})
d.text((22,310),"Ender V2 / Unreal 5.8.4 / REVIEW ONLY / NO FIT APPROVAL",fill=(239,197,129),font=ft)
canvas.save(output,"WEBP",quality=58,method=6)
result={"status":"NATIVE_3_IMAGE_MONTAGE_VERIFIED_NONCANONICAL",
        "sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
        "output_bytes":output.stat().st_size,
        "original_pixel_data_modified":False,
        "review_images_resized":True,
        "materials_approved":False,"fit_verified":False,
        "game_assets_modified":False,"sources":sources}
receipt.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
print("MONTAGE",output,"BYTES",output.stat().st_size,"SHA",result["sha256"])
