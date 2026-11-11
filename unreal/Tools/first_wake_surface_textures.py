#!/usr/bin/env python3
"""Deterministic source textures and opt-in native surface pass for six First Wake maps.

SOURCE generator is engine-free. STAGE only in the exact dedicated review worktree,
and duplicates maps into a distinct destination. Never edits original levels, saves,
story authority, or original flat preview materials. Art is REVIEW ONLY.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unreal"
SOURCE = PROJECT / "DataSource/Textures/FirstWakeSurfaceV1"
DEST = "/Game/TSTSS/Review/SurfacePassV1"
BASE = "/Game/TSTSS/Review/VerticalSlice"
WORKTREE = "TSTSS_SurfacePass_20261111"
SIZE = 512
SCENES = ("VS01_DenithHarbor", "VS02_AureateInteriors",
          "VS03_FirstWakeSky", "VS04_SplashdownSea",
          "VS05_DenithFuelShanty", "VS06_SplashdownShore")
# Name -> albedo sRGB, base roughness, metallic, geometric pattern, UV repeat.
SURFACES = {
    "sand": ((187, 145, 95), .82, .0, "grain", 5.0),
    "stone": ((99, 112, 116), .83, .0, "masonry", 3.0),
    "dark_stone": ((43, 58, 68), .89, .0, "strata", 3.5),
    "timber": ((116, 78, 51), .77, .0, "wood", 4.0),
    "brass": ((162, 120, 53), .31, 1.0, "brushed", 2.0),
    "ocean": ((16, 66, 85), .19, .0, "waves", 1.4),
    "aether": ((49, 135, 148), .30, .12, "weave", 3.0),
    "cloud": ((188, 198, 207), .94, .0, "cloud", 1.5),
    "warm": ((221, 153, 87), .52, .0, "glass", 2.0),
    "green": ((70, 105, 75), .91, .0, "moss", 5.0),
}
PREFIX = "TSTSS_VS_REVIEW_"

def stable_hash(x: int, y: int, seed: int) -> float:
    q = ((x * 374761393 + y * 668265263 + seed * 1442695041) & 0xffffffff)
    q ^= (q >> 13)
    q = (q * 1274126177) & 0xffffffff
    q ^= (q >> 16)
    return (q & 65535) / 65535.0

def height(name: str, x: int, y: int) -> float:
    u = x / SIZE
    v = y / SIZE
    noise = stable_hash(x, y, len(name) * 71)
    coarse = .5 + .25 * math.sin(u * 27 + math.sin(v * 19) * 1.8)
    if name == "sand":
        h = .45 * coarse + .32 * noise + .23 * math.sin((u + v) * 220)
    elif name in ("stone", "dark_stone"):
        mortar = .13 if ((x % 118) < 3 or (y % 93) < 4) else 0
        h = .42 * coarse + .45 * noise - mortar + .12 * math.sin(v * 37)
    elif name == "timber":
        h = .46 + .24 * math.sin(u * 115 + 4 * math.sin(v * 9)) + .16 * noise
    elif name == "brass":
        h = .58 + .10 * math.sin(v * 400) + .09 * noise
    elif name == "ocean":
        h = .48 + .27 * math.sin(u * 55 + v * 24) + .15 * math.sin(u * 103 - v * 67) + .05 * noise
    elif name == "aether":
        h = .41 + .30 * abs(math.sin(u * 40) * math.cos(v * 38)) + .08 * noise
    elif name == "cloud":
        h = .46 + .25 * math.sin(u * 12 + math.cos(v * 15)) + .12 * math.sin(v * 24) + .08 * noise
    elif name == "warm":
        h = .54 + .07 * math.sin(u * 44) + .07 * noise
    else:
        h = .25 + .35 * coarse + .35 * noise
    return max(0.0, min(1.0, h))

def byte(x: float) -> int:
    return max(0, min(255, int(round(x))))

def png_rgb(rows: list[bytes], width: int, length: int) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    raw = b"".join(b"\0" + row for row in rows)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, length, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 8)) + chunk(b"IEND", b""))

def render(name: str, size: int = SIZE) -> dict[str, bytes]:
    if name not in SURFACES or size != SIZE:
        raise ValueError("unknown surface or unapproved texture dimensions")
    color, rough, metallic, _, _ = SURFACES[name]
    rows = {"BaseColor": [], "Normal": [], "ORM": []}
    for y in range(size):
        scan = {k: bytearray() for k in rows}
        for x in range(size):
            h = height(name, x, y)
            bump = (h - .5)
            grit = stable_hash(x, y, len(name) * 19) - .5
            # Restrained luminance variation; readable even under storm lighting.
            factor = max(.64, min(1.22, .87 + bump * .39 + grit * .13))
            c = [byte(v * factor) for v in color]
            if name == "ocean":
                c = [byte(color[i] * (.83 + .29 * h)) for i in range(3)]
            if name == "brass" and h < .42:  # subtle oxidized marks
                c = [byte(c[i] * (.76 if i == 0 else .90 if i == 1 else 1.05)) for i in range(3)]
            dx = height(name, (x + 1) % size, y) - height(name, (x - 1) % size, y)
            dy = height(name, x, (y + 1) % size) - height(name, x, (y - 1) % size)
            strength = .42 if name in ("ocean", "aether", "warm") else 1.10
            nx, ny = -dx * strength, -dy * strength
            inv = 1.0 / math.sqrt(nx * nx + ny * ny + 1.0)
            scan["BaseColor"].extend(c)
            scan["Normal"].extend((byte(127.5 + 127.5 * nx * inv),
                                   byte(127.5 + 127.5 * ny * inv),
                                   byte(127.5 + 127.5 * inv)))
            scan["ORM"].extend((byte(240 - 28 * (1.0 - h)),
                                byte(255 * max(.07, min(.98, rough + bump * .10))),
                                byte(255 * metallic)))
        for channel in rows:
            rows[channel].append(bytes(scan[channel]))
    return {channel: png_rgb(v, size, size) for channel, v in rows.items()}

def manifest() -> dict:
    return {"schema": "tstss.firstwake.surfacepass.v1",
            "authority": "REVIEW_ONLY_NOT_CANON_ART_OR_NATIVE_VISUAL_APPROVAL",
            "source_maps": [BASE + "/" + n for n in SCENES],
            "review_maps": [DEST + "/" + n + "_SurfaceReview" for n in SCENES],
            "textures": {n: {"channels": ["BaseColor", "Normal", "ORM"],
                             "size": SIZE, "uv_tiling": spec[4]}
                         for n, spec in SURFACES.items()},
            "physical_workflow": "albedo_srgb_normal_linear_ORM_linear",
            "production_maps_changed": False, "PIE_verified": False,
            "weather_assurance": "separate_unverified_integration",
            "visual_approval": False}

def generate() -> dict:
    SOURCE.mkdir(parents=True, exist_ok=True)
    receipt = manifest()
    hashes = {}
    for name in SURFACES:
        for channel, data in render(name).items():
            path = SOURCE / ("T_FW_" + name + "_" + channel + ".png")
            if path.exists() and path.read_bytes() != data:
                raise RuntimeError("Refusing overwrite of divergent texture: " + str(path))
            path.write_bytes(data)
            hashes[path.name] = hashlib.sha256(data).hexdigest()
    receipt["sha256"] = hashes
    dest = SOURCE / "surface_manifest.review.json"
    if dest.exists() and json.loads(dest.read_text(encoding="utf-8")) != receipt:
        raise RuntimeError("Refusing divergent receipt overwrite")
    dest.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt

def git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(ROOT), *args], check=True,
                       capture_output=True, text=True, timeout=30)
    return r.stdout.strip()

def native_preflight(u):
    if ROOT.name != WORKTREE or Path(u.Paths.project_dir()).resolve() != PROJECT.resolve():
        raise RuntimeError("HOLD: wrong native authoring project/worktree")
    sha = os.environ.get("TSTSS_SURFACE_EXPECTED_HEAD", "")
    if not re.fullmatch("[0-9a-fA-F]{40}", sha) or sha.lower() != git("rev-parse", "HEAD").lower():
        raise RuntimeError("HOLD: exact HEAD not pinned")
    if git("status", "--porcelain"):
        raise RuntimeError("HOLD: dirty source worktree")
    if u.EditorAssetLibrary.does_directory_exist(DEST):
        raise RuntimeError("HOLD: destination already exists")
    if u.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: dirty map")
    if u.EditorLoadingAndSavingUtils.get_dirty_content_packages():
        raise RuntimeError("HOLD: dirty content")
    manifest_file = SOURCE / "surface_manifest.review.json"
    if not manifest_file.is_file():
        raise RuntimeError("HOLD: source texture manifest absent")
    report = json.loads(manifest_file.read_text(encoding="utf-8"))
    if report["schema"] != manifest()["schema"] or sorted(report["textures"]) != sorted(SURFACES):
        raise RuntimeError("HOLD: texture inventory drift")
    for fn, expected in report["sha256"].items():
        f = SOURCE / fn
        if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest() != expected:
            raise RuntimeError("HOLD: texture sha mismatch: " + fn)
    for n in SCENES:
        if not u.EditorAssetLibrary.does_asset_exist(BASE + "/" + n):
            raise RuntimeError("HOLD: native source map missing: " + n)
    return sha.lower(), report

def native_stage():
    import unreal as u
    sha, report = native_preflight(u)
    asset_tools = u.AssetToolsHelpers.get_asset_tools()
    if not u.EditorAssetLibrary.make_directory(DEST):
        raise RuntimeError("HOLD: cannot create new review destination")
    texture_assets = {}
    for name in SURFACES:
        for channel in ("BaseColor", "Normal", "ORM"):
            task = u.AssetImportTask()
            task.set_editor_property("filename", str(SOURCE / ("T_FW_" + name + "_" + channel + ".png")))
            task.set_editor_property("destination_path", DEST)
            task.set_editor_property("destination_name", "T_FW_" + name + "_" + channel)
            task.set_editor_property("automated", True)
            task.set_editor_property("replace_existing", False)
            task.set_editor_property("save", True)
            asset_tools.import_asset_tasks([task])
            paths = list(task.get_editor_property("imported_object_paths"))
            if len(paths) != 1:
                raise RuntimeError("HOLD: texture import failed: " + name + "/" + channel)
            tex = u.load_asset(str(paths[0]))
            if tex is None:
                raise RuntimeError("HOLD: imported texture missing")
            if channel != "BaseColor":
                tex.set_editor_property("srgb", False)
                tex.set_editor_property("compression_settings",
                                        u.TextureCompressionSettings.TC_NORMALMAP if channel == "Normal"
                                        else u.TextureCompressionSettings.TC_MASKS)
            if not u.EditorAssetLibrary.save_loaded_asset(tex):
                raise RuntimeError("HOLD: imported texture save failed")
            texture_assets[(name, channel)] = tex

    materials = {}
    editor = u.MaterialEditingLibrary
    for name in SURFACES:
        m = asset_tools.create_asset("M_FW_" + name, DEST, u.Material, u.MaterialFactoryNew())
        if m is None:
            raise RuntimeError("HOLD: material create failed: " + name)
        # Material UV tiling matches the source material family.
        coord = editor.create_material_expression(m, u.MaterialExpressionTextureCoordinate, -900, 0)
        coord.set_editor_property("u_tiling", SURFACES[name][4])
        coord.set_editor_property("v_tiling", SURFACES[name][4])
        for channel, ypos in (("BaseColor", -250), ("Normal", 100), ("ORM", 450)):
            sample = editor.create_material_expression(m, u.MaterialExpressionTextureSample, -450, ypos)
            sample.set_editor_property("texture", texture_assets[(name, channel)])
            if not editor.connect_material_expressions(coord, "", sample, "UVs"):
                raise RuntimeError("HOLD: UV graph connection rejected")
            targets = (("RGB", u.MaterialProperty.MP_BASE_COLOR),) if channel == "BaseColor" else (
                (("RGB", u.MaterialProperty.MP_NORMAL),) if channel == "Normal" else
                (("R", u.MaterialProperty.MP_AMBIENT_OCCLUSION),
                 ("G", u.MaterialProperty.MP_ROUGHNESS),
                 ("B", u.MaterialProperty.MP_METALLIC)))
            for output, target in targets:
                if not editor.connect_material_property(sample, output, target):
                    raise RuntimeError("HOLD: PBR graph connection rejected: " + name)
        errors = editor.recompile_material(m)
        if errors is not None and len(errors) > 0:
            raise RuntimeError("HOLD: material compilation reported errors: " + str(errors))
        if not u.EditorAssetLibrary.save_loaded_asset(m):
            raise RuntimeError("HOLD: material save failed")
        materials[name] = m

    actor_sys = u.get_editor_subsystem(u.EditorActorSubsystem)
    assignments = {}
    for scene in SCENES:
        src = BASE + "/" + scene
        dst = DEST + "/" + scene + "_SurfaceReview"
        if not u.EditorAssetLibrary.duplicate_asset(src, dst):
            raise RuntimeError("HOLD: native map duplicate failed: " + scene)
        if u.EditorLoadingAndSavingUtils.load_map(dst) is None:
            raise RuntimeError("HOLD: cannot load new map " + scene)
        count, missing = 0, []
        for actor in actor_sys.get_all_level_actors():
            if not actor.get_actor_label().startswith(PREFIX):
                continue
            comp = actor.get_component_by_class(u.StaticMeshComponent)
            if comp is None or comp.get_num_materials() == 0:
                continue
            existing = comp.get_material(0)
            key = next((k for k in SURFACES if existing and existing.get_name() ==
                        "M_VS_" + k.title().replace("_", "")), None)
            if key is None:
                missing.append(actor.get_actor_label())
                continue
            comp.set_material(0, materials[key])
            count += 1
        if missing:
            raise RuntimeError("HOLD: unmapped original review actors: " + ",".join(missing[:15]))
        if count < 1 or not u.EditorLoadingAndSavingUtils.save_current_level():
            raise RuntimeError("HOLD: scene material write failed: " + scene)
        assignments[scene] = count
    for fn, expected in report["sha256"].items():
        if hashlib.sha256((SOURCE / fn).read_bytes()).hexdigest() != expected:
            raise RuntimeError("HOLD: texture modified during native import")
    evidence = PROJECT / "Saved/SurfacePassV1/native_stage_receipt.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps({"source_head": sha, "materials": len(materials),
                                    "imported_textures": len(texture_assets),
                                    "scene_material_assignments": assignments,
                                    "status": "NATIVE_ASSETS_CREATED_REVIEW_ONLY_NOT_RENDER_APPROVED",
                                    "PIE_verified": False, "creator_approved": False},
                                   indent=2) + "\n", encoding="utf-8")
    return {"maps": len(assignments), "textures": len(texture_assets), "materials": len(materials)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--stage-native", action="store_true")
    args, _unknown = parser.parse_known_args()
    if args.stage_native:
        if os.environ.get("TSTSS_SURFACE_STAGE") != "1":
            raise RuntimeError("HOLD: explicit opt-in TSTSS_SURFACE_STAGE=1 required")
        result = native_stage()
    elif args.generate:
        result = generate()
    else:
        result = manifest()
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
