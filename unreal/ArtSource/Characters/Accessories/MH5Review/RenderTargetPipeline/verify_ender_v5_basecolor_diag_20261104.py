"""Verify actual native Ender V5 final-vs-base-color render diagnostics.

Review evidence only. Does not save meshes, scenes or approve likeness.
Usage: python verify_ender_v5_basecolor_diag_20261104.py
"""
import hashlib
import io
import json
import struct
import zlib
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

HERE = Path(__file__).resolve().parent
ROOT = Path("C:/MH5/CastAllSandbox/Saved/CharacterLookdev/GogglesFitV1")
FINAL = ROOT / "RenderTargetCombined02"
BASE = ROOT / "RenderTargetCombined04_BaseColor"
OUT = HERE / "Evidence/ender_v5_basecolor_comparison_20261104.json"
EXPECTED = {
    "meta": "2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d",
    "map": "025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a",
    "goggles": "76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae",
}
STATUS_FINAL = "NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED"
STATUS_BASE = "NATIVE_V5_GOGGLES_BASECOLOR_PNG_CORE_PASS_VISUAL_UNREVIEWED"


def require(ok, label):
    if not ok:
        raise AssertionError("FAIL_CLOSED " + label)


def png_core(path):
    b = path.read_bytes()
    require(b.startswith(b"\x89PNG\r\n\x1a\n"), "png header")
    pos, chunks, dims = 8, [], None
    while pos + 12 <= len(b):
        n = struct.unpack_from(">I", b, pos)[0]
        typ = b[pos + 4:pos + 8]
        require(n <= 16_000_000 and pos + n + 12 <= len(b), "png chunk bounds")
        payload = b[pos + 8:pos + 8 + n]
        crc = struct.unpack_from(">I", b, pos + 8 + n)[0]
        require(crc == (zlib.crc32(typ + payload) & 0xFFFFFFFF), "png crc")
        if typ == b"IHDR":
            dims = struct.unpack_from(">II", payload)
        chunks.append(typ)
        pos += n + 12
        if typ == b"IEND":
            break
    require(chunks[-1] == b"IEND" and b"IDAT" in chunks, "png complete")
    require(dims == (480, 320), "png dimensions")
    core = b[:pos]
    return hashlib.sha256(core).hexdigest(), core, len(b) - pos


def validate_receipt(directory, expected_status):
    j = json.loads((directory / "capture_receipt.json").read_text(encoding="utf-8"))
    require(j["status"] == expected_status, "native status")
    require(j.get("canonical") is False and j.get("production_game_modified") is False,
            "no promotion")
    require(j.get("source_assets_saved") is False and j.get("review_map_saved") is False,
            "no save")
    require(j.get("meta_sha256_after") == EXPECTED["meta"] == j.get("source_meta_sha256"),
            "MetaHuman unchanged")
    require(j.get("map_sha256_after") == EXPECTED["map"] == j.get("source_map_sha256"),
            "map unchanged")
    require(j.get("goggles_sha256_after") == EXPECTED["goggles"] == j.get("source_goggles_sha256"),
            "goggles unchanged")
    require(len(j.get("captures", [])) == 1 and j["captures"][0]["crc_pass"] is True,
            "exactly one verified capture")
    sha, raw, trailing = png_core(directory / "ender_v5_goggles_rt_front.png")
    require(j["captures"][0]["sha256_png_core"] == sha, "capture hash")
    require(j["captures"][0]["trailing_bytes_after_iend"] == trailing, "png trailing bytes")
    im = Image.open(io.BytesIO(raw))
    im.load()
    return sha, im.convert("RGB"), trailing


def verify_source_single_variable():
    original = (HERE / "native_rt_ender_v5_goggles01.py").read_text(encoding="utf-8")
    trial = (HERE / "native_rt_ender_v5_goggles_basecolor_diag_20261104.py").read_text(encoding="utf-8")
    substitutions = [
        ("RenderTargetCombined04_BaseColor", "RenderTargetCombined02"),
        ("NATIVE_V5_GOGGLES_BASECOLOR_PNG_CORE_PASS_VISUAL_UNREVIEWED",
         "NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED"),
        ("SceneCapture2D SCS_BASE_COLOR diagnostic -> RenderingLibrary.export_render_target",
         "SceneCapture2D -> RenderingLibrary.export_render_target"),
        ("SCS_BASE_COLOR", "SCS_FINAL_COLOR_LDR"),
    ]
    for before, after in substitutions:
        require(trial.count(before) == 1, "single parameter substitution: " + before)
        trial = trial.replace(before, after)
    require(trial == original, "unexpected source drift")


def summary(im):
    crop = im.crop((140, 42, 340, 320))
    vals = list(crop.get_flattened_data())
    return {
        "mean_rgb_full": [round(x, 2) for x in ImageStat.Stat(im).mean],
        "face_goggles_crop_white_clip_fraction": round(
            sum(min(rgb) >= 245 for rgb in vals) / len(vals), 5),
        "face_goggles_crop_near_black_fraction": round(
            sum(max(rgb) <= 12 for rgb in vals) / len(vals), 5),
    }


def run():
    # Allow verified, identical re-reads; never rewrite or replace a conflicting receipt.
    verify_source_single_variable()
    final_sha, final_img, final_trailing = validate_receipt(FINAL, STATUS_FINAL)
    base_sha, base_img, base_trailing = validate_receipt(BASE, STATUS_BASE)
    require(final_sha != base_sha, "no diagnostic change")
    diff = ImageChops.difference(final_img, base_img)
    require(diff.getbbox() is not None, "no pixel difference")
    result = {
        "status": "NATIVE_BASECOLOR_DIAGNOSTIC_PASS_ART_HOLD",
        "native_engine": "UE5.8.4 D3D11",
        "size": [480, 320],
        "changed_capture_source_only": "SCS_FINAL_COLOR_LDR to SCS_BASE_COLOR",
        "final_color_png_core_sha256": final_sha,
        "base_color_png_core_sha256": base_sha,
        "final_color_png_trailing_bytes": final_trailing,
        "base_color_png_trailing_bytes": base_trailing,
        "final_color": summary(final_img),
        "base_color": summary(base_img),
        "pixel_differences_exist": True,
        "same_source_meta_map_goggles_sha256": EXPECTED,
        "metahuman_likeness_approved": False,
        "goggles_v1_approved": False,
        "goggles_v2_native_verified": False,
        "gameplay_rig_verified": False,
        "canon_promotion": False,
        "private_screenshots_committed": False,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if OUT.exists():
        require(OUT.read_text(encoding="utf-8") == serialized,
                "existing receipt differs; refuse overwrite")
    else:
        OUT.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    run()
