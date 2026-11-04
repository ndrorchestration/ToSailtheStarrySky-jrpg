"""Independently verify native Ender V5 manual-exposure and lower-light renders.

Only private native image pixels/receipts are opened; the public report includes
hashes and statistics, never the screenshots or approved face references.
"""
import hashlib
import io
import json
import struct
import zlib
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

HERE = Path(__file__).resolve().parent
RUNS = Path("C:/MH5/CastAllSandbox/Saved/CharacterLookdev/GogglesFitV1")
OUT = HERE / "Evidence/ender_v5_native_capture_matrix_20261104.json"
EXPECTED = {
    "source_meta_sha256": "2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d",
    "source_map_sha256": "025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a",
    "source_goggles_sha256": "76eb9696e2abf719bcfd3d467313e46136f5d92cc36cd6b3845ae447a272c1ae",
}
CAPTURES = [
    ("baseline_final", "RenderTargetCombined02",
     "NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED",
     "212041ad0b39fc7eefc5f479bd3dae4427aa04ffcf4e497ec95283123407f808"),
    ("manual_minus2_ev", "RenderTargetCombined05_ManualExposure",
     "NATIVE_V5_GOGGLES_MANUAL_EXPOSURE_PNG_CORE_PASS_VISUAL_UNREVIEWED",
     "212041ad0b39fc7eefc5f479bd3dae4427aa04ffcf4e497ec95283123407f808"),
    ("tenth_temporary_light", "RenderTargetCombined06_LightTenth",
     "NATIVE_V5_GOGGLES_TENTH_LIGHT_PNG_CORE_PASS_VISUAL_UNREVIEWED",
     "90de28a3d58b37f100c0c8066369c7e18aee49696cbbb5530f2dbc8776c5e58f"),
]


def require(valid, message):
    if not valid:
        raise AssertionError("FAIL_CLOSED " + message)


def validated_core(path):
    blob = path.read_bytes()
    require(blob[:8] == b"\x89PNG\r\n\x1a\n", "PNG signature")
    pos, saw_idat, dims, saw_end = 8, False, None, False
    while pos + 12 <= len(blob):
        count = struct.unpack_from(">I", blob, pos)[0]
        tag = blob[pos + 4:pos + 8]
        require(count <= 10_000_000 and pos + count + 12 <= len(blob), "chunk bounds")
        payload = blob[pos + 8:pos + 8 + count]
        crc = struct.unpack_from(">I", blob, pos + 8 + count)[0]
        require((zlib.crc32(tag + payload) & 0xFFFFFFFF) == crc, "chunk CRC")
        if tag == b"IHDR":
            dims = struct.unpack_from(">II", payload)
        if tag == b"IDAT":
            saw_idat = True
        pos += count + 12
        if tag == b"IEND":
            saw_end = True
            break
    require(saw_end and saw_idat and dims == (480, 320), "complete 480x320 PNG")
    return blob[:pos], len(blob) - pos


def check_capture(name, directory, status, pinned_hash):
    folder = RUNS / directory
    receipt = json.loads((folder / "capture_receipt.json").read_text(encoding="utf-8"))
    require(receipt.get("status") == status, name + " genuine native success receipt")
    for field, target in EXPECTED.items():
        require(receipt.get(field) == target, name + " pinned source " + field)
        after_field = field.replace("source_", "") + "_after"
        require(receipt.get(after_field) == target, name + " unchanged " + after_field)
    for guard in ("canonical", "production_game_modified", "source_assets_saved",
                  "review_map_saved", "face_likeness_approved",
                  "materials_artist_approved", "goggles_fit_approved",
                  "rigging_verified"):
        require(receipt.get(guard) is False, name + " no false acceptance " + guard)
    require(len(receipt.get("captures", [])) == 1, name + " one native screenshot")
    core, trailing = validated_core(folder / "ender_v5_goggles_rt_front.png")
    digest = hashlib.sha256(core).hexdigest()
    native = receipt["captures"][0]
    require(native.get("sha256_png_core") == pinned_hash == digest,
            name + " image core hash")
    require(native.get("crc_pass") is True and native.get("trailing_bytes_after_iend") == trailing,
            name + " original chunk evidence")
    img = Image.open(io.BytesIO(core))
    img.load()
    return digest, img.convert("RGB"), trailing


def metrics(img):
    crop = img.crop((140, 42, 340, 320))
    px = list(crop.get_flattened_data())
    return {
        "mean_rgb_full": [round(v, 3) for v in ImageStat.Stat(img).mean],
        "crop_nearwhite_fraction": round(sum(min(v) >= 245 for v in px) / len(px), 6),
        "crop_nearblack_fraction": round(sum(max(v) <= 12 for v in px) / len(px), 6),
    }


def assert_source_light_only():
    baseline = (HERE / "native_rt_ender_v5_goggles01.py").read_text(encoding="utf-8")
    variant = (HERE / "native_rt_ender_v5_goggles_light_tenth_20261104.py").read_text(
        encoding="utf-8")
    changes = (
        ("RenderTargetCombined06_LightTenth", "RenderTargetCombined02"),
        ("NATIVE_V5_GOGGLES_TENTH_LIGHT_PNG_CORE_PASS_VISUAL_UNREVIEWED",
         "NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED"),
        ('comp.set_editor_property("intensity",power*0.1)',
         'comp.set_editor_property("intensity",power)'),
    )
    for new, old in changes:
        require(variant.count(new) == 1, "exactly one changed light-script token")
        variant = variant.replace(new, old)
    require(variant == baseline, "low-light variant unexpectedly modified camera/assets")


def run():
    assert_source_light_only()
    records, imgs = {}, {}
    for key, directory, status, hash_value in CAPTURES:
        digest, im, trailing = check_capture(key, directory, status, hash_value)
        records[key] = {"png_core_sha256": digest, "trailing_bytes": trailing, **metrics(im)}
        imgs[key] = im
    require(ImageChops.difference(imgs["baseline_final"], imgs["manual_minus2_ev"]).getbbox()
            is None, "manual result unexpectedly differs")
    require(ImageChops.difference(imgs["baseline_final"], imgs["tenth_temporary_light"]).getbbox()
            is not None, "lower light made no pixel difference")
    clipped_before = records["baseline_final"]["crop_nearwhite_fraction"]
    clipped_after = records["tenth_temporary_light"]["crop_nearwhite_fraction"]
    require(clipped_after < clipped_before, "no clipping improvement")
    report = {
        "status": "ACTUAL_UE584_TENTH_LIGHT_REDUCES_FINALCOLOR_CLIPPING_ART_HOLD",
        "actual_native_renderer": "Unreal 5.8.4 D3D11 SM5, SceneCapture2D RenderTarget",
        "crop_region_xyxy": [140, 42, 340, 320],
        "white_clip_definition": "min(R,G,B)>=245",
        "native_captures": records,
        "manual_exposure_is_pixel_identical": True,
        "lower_light_is_pixel_distinct": True,
        "clipping_reduction_fraction_points": round(clipped_before - clipped_after, 6),
        "identical_meta_map_and_v1_goggles_hashes": EXPECTED,
        "goggles_v1_creator_rejected_as_glasses": True,
        "goggles_v2_fit_approved": False,
        "face_approved": False,
        "production_materials_changed": False,
        "lighting_changed_only_transiently": True,
        "production_actors_changed": False,
        "rig_or_animation_approved": False,
        "no_canon_promotion": True,
        "private_pngs_in_git": False,
    }
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        require(OUT.read_text(encoding="utf-8") == serialized,
                "existing report collision or altered evidence")
    else:
        OUT.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    run()
