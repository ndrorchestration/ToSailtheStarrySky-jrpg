"""Create audited upright *display derivatives* of raw Unreal review screenshots.

Do not mutate source PNGs; do not treat these as corrected Unreal meshes.
A deliberate 180-degree raster rotation is an observed presentation repair
for the currently inverted PR #647 native D3D11 review frames.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageStat


def derive(raw_path, output_path):
    raw_path, output_path = Path(raw_path), Path(output_path)
    if not raw_path.is_file() or raw_path.resolve() == output_path.resolve():
        raise ValueError("Must read existing raw screenshot and write a separate derivative")
    if output_path.exists():
        raise FileExistsError("Refuse to overwrite existing screenshot")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    before = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    with Image.open(raw_path) as inp:
        inp.load()
        if inp.format != "PNG" or inp.width < 500 or inp.height < 400:
            raise ValueError("Expected real native screenshot PNG")
        corrected = inp.convert("RGBA").transpose(Image.Transpose.ROTATE_180)
        original = inp.convert("RGBA")
        w, h = original.size
        probes = ((5, 7), (w // 2, h // 3), (w // 3, h // 2))
        for x, y in probes:
            if corrected.getpixel((x, y)) != original.getpixel((w - x - 1, h - y - 1)):
                raise AssertionError("Pixel mapping does not match 180-degree rotation")
        corrected.save(output_path, format="PNG", optimize=True)
        metrics = ImageStat.Stat(corrected.convert("RGB"))
        result = {
            "status": "DERIVED_DISPLAY_ROTATED_180_NOT_ENGINE_CAPTURE",
            "source_path": str(raw_path),
            "source_sha256": before,
            "derived_path": str(output_path),
            "derived_sha256": hashlib.sha256(output_path.read_bytes()).hexdigest(),
            "transform": "rotate_pixels_180_degrees",
            "pixel_size": [w, h],
            "mean_rgb": [round(x, 3) for x in metrics.mean],
            "original_unmodified": hashlib.sha256(raw_path.read_bytes()).hexdigest() == before,
            "visual_quality_approved": False,
            "model_orientation_changed": False,
            "provenance": "Unreal 5.8.4 D3D11 review PNG; external presentation-only transformation",
        }
    receipt = output_path.with_suffix(".orientation.json")
    receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_png")
    parser.add_argument("output_png")
    a = parser.parse_args()
    print(json.dumps(derive(a.raw_png, a.output_png), indent=2))
