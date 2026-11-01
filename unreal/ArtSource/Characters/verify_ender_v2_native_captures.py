"""Validate real UE D3D11 Ender sculpt study screenshots on GPU host.

Requires Pillow; deliberately separate from source-only CI and artist approval.
"""
import hashlib,json
from pathlib import Path
from PIL import Image
from verify_render_pngs import inspect_png

PREFIX="C__TSTSS_CastAllSandbox_20261101_Saved_CharacterLookdev_EnderFidelityV2Native_"
REQUIRED=("Ender_v2_front","Ender_v2_three_quarter")
def verify(root):
    root=Path(root)
    images={}
    for name in REQUIRED:
        target=root/(PREFIX+name+".png")/"Windows"/"D3D11_SM5"/"Incoming.png"
        if not target.exists():raise RuntimeError("No real native screenshot "+name)
        info=inspect_png(target,(1280,720))
        with Image.open(target) as img:
            img.load()
            color=img.convert("RGB")
            # Pixel brightness >20: non-black scene content. This checks
            # visibility only, not anatomy, textures or artistic fidelity.
            count=sum(1 for r,g,b in color.get_flattened_data() if max(r,g,b)>20)
            coverage=count/(color.width*color.height)
        if not 0.04 <= coverage <= 0.85:
            raise RuntimeError("Screenshot blank, obstructed or overexposed: "+name)
        info.update({"visible_fraction":round(coverage,4)})
        images[name]=info
    hashes=[v["sha256"] for v in images.values()]
    if len(set(hashes))!=len(hashes):
        raise RuntimeError("Duplicate camera screenshots")
    return {"status":"NATIVE_TWO_VIEW_IMAGE_PASS_ART_UNAPPROVED",
            "images":images,"art_approved":False,
            "renderer":"UE 5.8.4 D3D11 SM5","exact_camera_script":"capture_ender_fidelity_v2.py"}
if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("report_dir",type=Path)
    args=ap.parse_args()
    print(json.dumps(verify(args.report_dir),indent=2))
