"""Create a small review-only copy of a verified native Unreal render."""
from pathlib import Path
from PIL import Image
import hashlib,json
root=Path(r"C:\MH5\CastAllSandbox\Saved\CharacterLookdev\GogglesFitV1\RenderTargetCombined02")
original=root/"ender_v5_goggles_rt_front_clean.png"
out=root/"ender_v5_goggles_native_review_mobile.webp"
receipt=json.loads((root/"png_postprocessing_receipt.json").read_text(encoding="utf-8"))
if not original.is_file() or out.exists():raise RuntimeError("FAIL_CLOSED missing/occupied")
if hashlib.sha256(original.read_bytes()).hexdigest()!=receipt["validated_png_sha256"]:
    raise RuntimeError("Source PNG drift")
with Image.open(original) as raw:
    image=raw.convert("RGB")
    if image.size!=(480,320):raise RuntimeError("Wrong pixel dimensions")
    image.save(out,"WEBP",quality=58,method=6)
with Image.open(out) as src:
    src.verify()
print("WEBP_PRIVATE_REVIEW",str(out),"BYTES",out.stat().st_size,
      "SHA",hashlib.sha256(out.read_bytes()).hexdigest())
