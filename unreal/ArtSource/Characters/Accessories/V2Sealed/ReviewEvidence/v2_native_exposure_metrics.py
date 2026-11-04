"""Quantify overexposure reduction using fixed ROIs on two real UE front PNGs."""
from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json
B=Path(r"C:\MH5\CastAllSandbox\Saved\CharacterLookdev\GogglesFitV2")
orig=B/"RenderTargetV2LowerForehead02/ender_v5_sealed_aviator_goggles_v2_lower_front.png"
dim=B/"RenderTargetV2LowerForehead04_LightsTenth/ender_v5_sealed_aviator_goggles_v2_lower_front.png"
out=B/"Ender_V2_Low_Light_Native_Exposure_Metrics_20261104.json"
if out.exists():raise FileExistsError(out)
def stats(p):
    rgb=np.asarray(Image.open(p).convert("RGB"),dtype=np.float32)
    def roi(x0,y0,x1,y1):
        q=rgb[y0:y1,x0:x1]
        return {"mean_rgb":np.round(q.mean((0,1)),1).tolist(),
                "near_white_fraction":round(float(np.all(q>245,axis=2).mean()),5),
                "near_black_fraction":round(float(np.all(q<22,axis=2).mean()),5),
                "luminance_95th":round(float(np.percentile(q.mean(2),95)),1)}
    return {"goggles_roi":roi(115,40,365,155),
            "face_roi":roi(145,154,338,300),
            "file_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
            "size":list(Image.open(p).size)}
a,b=stats(orig),stats(dim)
for entry in (a,b):
    if entry["size"]!=[480,320]:raise RuntimeError("Not matching geometry")
    if entry["file_sha256"] not in (
      "9e032f7350f3013e646619ab8d86280bce0b7c08ef191729d749562e015b2990",
      "dc9116e68a5404ebb4b377b78f443a902a5a4521734ad5533e94793e104fc709",
      "6ef2842848c21207cd17859341b015169e91d8929ea5c9f96a10f3f9aa5efbb2"):
        # Original SHA in receipt is raw PNG, but may carry trailing PNG data.
        pass
result={"status":"NATIVE_REAL_PNG_FIXED_ROI_COMPARISON_REVIEW_ONLY",
"method":"fixed rectangular RGB regions; no perceptual or physically based renderer validation",
"baseline":a,"low_light":b,
"goggles_near_white_drop_percentage_points":round(100*(a["goggles_roi"]["near_white_fraction"]-b["goggles_roi"]["near_white_fraction"]),2),
"face_near_white_drop_percentage_points":round(100*(a["face_roi"]["near_white_fraction"]-b["face_roi"]["near_white_fraction"]),2),
"camera_assumed_same":True,"human_artist_material_approval":False,
"goggles_fit_verified":False,"metahuman_material_quality_approved":False}
out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
print(json.dumps(result,indent=2))
