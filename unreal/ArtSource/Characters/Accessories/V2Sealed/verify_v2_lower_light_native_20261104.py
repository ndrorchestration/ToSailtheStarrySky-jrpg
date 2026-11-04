"""Verify genuine Unreal 5.8.4 V2 sealed-aviator lower-light native captures.

The original private images remain on the authorized workstation. Public
receipt contains only hashes and measurements, never private screenshot pixels.
"""
import hashlib
import io
import json
import struct
import zlib
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

HERE = Path(__file__).resolve().parent
ROOT = Path("C:/MH5/CastAllSandbox/Saved/CharacterLookdev/GogglesFitV2")
BASE = ROOT / "RenderTargetV2LowerForehead02"
LOW = ROOT / "RenderTargetV2LowerForehead04_LightsTenth"
IMAGE_NAME = "ender_v5_sealed_aviator_goggles_v2_lower_front.png"
OUT = HERE / "Evidence/native_v2_lower_light_review_20261104.json"
EXPECTED = {
    "meta": "2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d",
    "map": "025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a",
    "goggles": "5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb",
}
BASE_SHA = "dc9116e68a5404ebb4b377b78f443a902a5a4521734ad5533e94793e104fc709"
LOW_SHA = "6ef2842848c21207cd17859341b015169e91d8929ea5c9f96a10f3f9aa5efbb2"
STATUS_BASE = "NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED"
STATUS_LOW = "NATIVE_V2_TENTH_LIGHT_PNG_CORE_PASS_VISUAL_UNREVIEWED"


def require(valid, label):
    if not valid:
        raise AssertionError("FAIL_CLOSED: " + label)


def verify_png(path, expected):
    data = path.read_bytes()
    require(data[:8] == b"\x89PNG\r\n\x1a\n", "PNG signature")
    off, dims, idat, ended = 8, None, False, False
    while off + 12 <= len(data):
        n = struct.unpack_from(">I", data, off)[0]
        name = data[off + 4:off + 8]
        require(n < 20_000_000 and off + 12 + n <= len(data), "PNG chunk bounds")
        content = data[off + 8:off + 8 + n]
        stored = struct.unpack_from(">I", data, off + 8 + n)[0]
        require((zlib.crc32(name + content) & 0xffffffff) == stored, "PNG chunk CRC")
        if name == b"IHDR":
            dims = struct.unpack_from(">II", content)
        idat |= name == b"IDAT"
        off += n + 12
        if name == b"IEND":
            ended = True
            break
    require(ended and idat and dims == (480, 320), "480x320 image core")
    core = data[:off]
    digest = hashlib.sha256(core).hexdigest()
    require(digest == expected, "pinned native PNG core")
    img = Image.open(io.BytesIO(core))
    img.load()
    return img.convert("RGB"), len(data) - off, digest


def verify_native_run(folder, status, expected):
    r = json.loads((folder / "capture_receipt.json").read_text(encoding="utf-8"))
    require(r.get("status") == status, "exact native status")
    require(r.get("engine", "").startswith("5.8.4-"), "native UE version")
    require(r.get("goggles_world_xyz_extent_cm") == [19.2, 19.17101, 8.02],
            "same imported V2 geometry dimensions")
    require(r.get("goggles_position_relative_to_v5_cm") == [0, 9.5, 168.5],
            "same lower-forehead transform")
    for key, sha in EXPECTED.items():
        require(r.get("source_" + key + "_sha256") == sha, key + " before")
        require(r.get(key + "_sha256_after") == sha, key + " after")
    for guard in ("canonical", "production_game_modified", "source_assets_saved",
                  "review_map_saved", "real_head_collision_verified",
                  "goggles_fit_approved", "face_likeness_approved",
                  "materials_artist_approved", "rigging_verified"):
        require(r.get(guard) is False, "no false approval " + guard)
    require(len(r.get("captures", [])) == 1, "one actual capture")
    image, trailing, digest = verify_png(folder / IMAGE_NAME, expected)
    require(r["captures"][0].get("sha256_png_core") == digest,
            "native receipt/image hash parity")
    require(r["captures"][0].get("crc_pass") is True,
            "native PNG CRC positive")
    require(r["captures"][0].get("trailing_bytes_after_iend") == trailing,
            "PNG exporter trailing-byte evidence")
    return image, trailing


def summary(img):
    crop = img.crop((110, 38, 370, 319))
    pixels = list(crop.get_flattened_data())
    return {
        "mean_rgb_full": [round(v, 3) for v in ImageStat.Stat(img).mean],
        "crop_nearwhite_fraction": round(sum(min(x) >= 245 for x in pixels) / len(pixels), 6),
        "crop_nearblack_fraction": round(sum(max(x) <= 12 for x in pixels) / len(pixels), 6),
    }


def validate_single_variable_code():
    source = (HERE / "native_rt_v2_lower_forehead_front.py").read_text(encoding="utf-8")
    trial = (HERE / "native_rt_v2_lower_forehead_light_tenth_review_20261104.py").read_text(
        encoding="utf-8")
    replacements = [
        ("RenderTargetV2LowerForehead04_LightsTenth", "RenderTargetV2LowerForehead02"),
        ("NATIVE_V2_TENTH_LIGHT_PNG_CORE_PASS_VISUAL_UNREVIEWED", STATUS_BASE),
        ('comp.set_editor_property("intensity",power*0.1)',
         'comp.set_editor_property("intensity",power)'),
    ]
    for changed, unchanged in replacements:
        require(trial.count(changed) == 1, "unique source parameter " + changed)
        trial = trial.replace(changed, unchanged)
    require(trial == source, "no unintended lighting/camera/geometry changes")


def main():
    validate_single_variable_code()
    baseline, before_extra = verify_native_run(BASE, STATUS_BASE, BASE_SHA)
    lower, after_extra = verify_native_run(LOW, STATUS_LOW, LOW_SHA)
    require(ImageChops.difference(baseline, lower).getbbox() is not None,
            "tenth-light pixels must change")
    b, a = summary(baseline), summary(lower)
    require(a["crop_nearwhite_fraction"] < b["crop_nearwhite_fraction"],
            "no clipping reduction")
    result = {
        "status": "NATIVE_V2_SEALED_GOGGLES_LOW_LIGHT_IMPROVES_READABILITY_ART_HOLD",
        "native_ue": "5.8.4 D3D11",
        "comparison_crop_xyxy": [110, 38, 370, 319],
        "white_clip_test": "min(R,G,B)>=245",
        "old_lighting": {"sha256_png_core": BASE_SHA, "trailing_exporter_bytes": before_extra,
                         **b},
        "temporary_pointlight_x0p1": {"sha256_png_core": LOW_SHA,
                                      "trailing_exporter_bytes": after_extra, **a},
        "white_clip_fraction_point_reduction": round(
            b["crop_nearwhite_fraction"] - a["crop_nearwhite_fraction"], 6),
        "same_source_sha256_before_after": EXPECTED,
        "original_V2_binary_byte_parity_claim": False,
        "review_only_noncanonical": True,
        "goggles_physically_fitted": False,
        "visual_material_approval": False,
        "facial_likeness_approved": False,
        "production_model_changed": False,
        "real_rig_approved": False,
        "private_source_images_in_repository": False,
    }
    body = json.dumps(result, sort_keys=True, indent=2) + "\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        require(OUT.read_text(encoding="utf-8") == body,
                "existing evidence collision")
    else:
        OUT.write_text(body, encoding="utf-8")
    print(body)


if __name__ == "__main__":
    main()
