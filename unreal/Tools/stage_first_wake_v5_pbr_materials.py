#!/usr/bin/env python3
"""Import existing TSTSS-authored PBR PNGs for V5 harbor; no level/map mutation.

Creates ONLY /Game/TSTSS/Review/PreludePBRV1/ material/texture assets in an
isolated, pinned, clean Neontic review worktree after full 38-test native proof.
No story changes, save slots, approval or production material replacement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unreal"
SOURCE = PROJECT / "DataSource/Textures/FirstWakeSurfaceV1"
TARGET = "/Game/TSTSS/Review/PreludePBRV1"
EXPECTED_WORKTREE = "TSTSS_V5InteractionMaterials_20261112"
OPT_IN = "IMPORT_REVIEW_PBR_ONLY"
FAMILIES = ("timber", "stone", "brass", "aether", "ocean")
CHANNELS = ("BaseColor", "Normal", "ORM")
SOURCE_MAP = PROJECT / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview.umap"


def git(*args: str) -> str:
    call = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True, text=True, check=True, timeout=30,
    )
    return call.stdout.strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_inventory() -> dict:
    manifest_path = SOURCE / "surface_manifest.review.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "tstss.firstwake.surfacepass.v1":
        raise RuntimeError("HOLD: PBR source schema drift")
    if not SOURCE_MAP.is_file():
        raise RuntimeError("HOLD: source V5 map missing")
    files: dict[str, str] = {}
    for family in FAMILIES:
        entry = manifest["textures"].get(family)
        if not entry or entry.get("channels") != list(CHANNELS):
            raise RuntimeError("HOLD: missing material family " + family)
        if entry.get("size") != 512 or not 1 <= entry.get("uv_tiling", 0) <= 8:
            raise RuntimeError("HOLD: bad PBR tiling/size " + family)
        for channel in CHANNELS:
            fn = f"T_FW_{family}_{channel}.png"
            path = SOURCE / fn
            digest = manifest.get("sha256", {}).get(fn)
            if not path.is_file() or sha256(path) != digest:
                raise RuntimeError("HOLD: PBR source hash mismatch: " + fn)
            files[fn] = digest
    return {
        "source_texture_family_count": len(FAMILIES),
        "source_texture_count": len(files),
        "files": files,
        "target_package": TARGET,
        "source_V5_map_sha256": sha256(SOURCE_MAP),
        "production_maps_changed": False,
        "scene_approved": False,
    }


def exact_native_receipt(expected: str) -> str:
    evidence_root = PROJECT / "Saved/MigrationEvidence"
    verifier = PROJECT / "Tools/Verify-Unreal.ps1"
    if not evidence_root.is_dir() or not verifier.is_file():
        raise RuntimeError("HOLD: no local native test evidence")
    names = re.findall(
        r"^\s*'(TSTSS\.[^']+)'",
        verifier.read_text(encoding="utf-8"), flags=re.MULTILINE,
    )
    if len(names) != 38 or len(set(names)) != 38:
        raise RuntimeError("HOLD: native test inventory drift")
    for folder in sorted(evidence_root.iterdir(), reverse=True):
        receipt = folder / "verified-native.json"
        report = folder / "AutomationReport/index.json"
        head = folder / "head.txt"
        if not all(p.is_file() for p in (receipt, report, head)):
            continue
        try:
            result = json.loads(receipt.read_text(encoding="utf-8-sig"))
            actual = json.loads(report.read_text(encoding="utf-8-sig"))
            if (
                result.get("status") != "WIN64_EDITOR_BUILD_AND_NATIVE_AUTOMATIONS_PASS_CLEAN_SOURCE"
                or result.get("source_sha") != expected
                or result.get("unreal_version") != "5.8.4"
                or type(result.get("required_native_tests")) is not int
                or result["required_native_tests"] != 38
                or result.get("pie_player_input") != "NOT_TESTED"
                or result.get("visual_approval") != "NOT_TESTED"
                or result.get("report_sha256") != sha256(report)
                or head.read_text(encoding="utf-8-sig").strip() != expected
                or any(type(actual.get(k)) is not int for k in ("succeeded", "failed", "notRun"))
                or actual["failed"] != 0
                or actual["notRun"] != 0
                or actual["succeeded"] != 38
            ):
                continue
            tests = actual.get("tests", [])
            if not isinstance(tests, list) or len(tests) != 38:
                continue
            status = {
                test.get("fullTestPath"): test.get("state")
                for test in tests if isinstance(test, dict)
            }
            if len(status) != 38 or any(status.get(name) != "Success" for name in names):
                continue
            return str(receipt)
        except (OSError, TypeError, ValueError, KeyError):
            continue
    raise RuntimeError("HOLD: full 38-native-test same-head receipt missing")


def stage() -> dict:
    if os.environ.get("TSTSS_V5_PBR_OPT_IN") != OPT_IN:
        raise RuntimeError("HOLD: explicit PBR opt-in missing")
    expected = os.environ.get("TSTSS_V5_PBR_EXPECTED_HEAD", "")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", expected):
        raise RuntimeError("HOLD: full source SHA pin missing")
    expected = expected.lower()
    if ROOT.name != EXPECTED_WORKTREE or git("rev-parse", "HEAD").lower() != expected:
        raise RuntimeError("HOLD: wrong worktree or changed source head")
    if git("status", "--porcelain", "-uall"):
        raise RuntimeError("HOLD: dirty source worktree")
    inventory = source_inventory()
    receipt = exact_native_receipt(expected)

    import unreal as u

    if Path(u.Paths.project_dir()).resolve() != PROJECT.resolve():
        raise RuntimeError("HOLD: incorrect Unreal project")
    if not str(u.SystemLibrary.get_engine_version()).startswith("5.8.4"):
        raise RuntimeError("HOLD: require Unreal 5.8.4")
    if u.EditorAssetLibrary.does_directory_exist(TARGET):
        raise RuntimeError("HOLD: review PBR destination already exists")
    if (u.EditorLoadingAndSavingUtils.get_dirty_map_packages() or
            u.EditorLoadingAndSavingUtils.get_dirty_content_packages()):
        raise RuntimeError("HOLD: dirty Editor packages")
    # No source-map load, duplication or save is needed for material-only import.
    before = inventory["source_V5_map_sha256"]
    if not u.EditorAssetLibrary.make_directory(TARGET):
        raise RuntimeError("HOLD: could not create isolated PBR review folder")
    asset_tools = u.AssetToolsHelpers.get_asset_tools()
    materials = {}
    tex_count = 0
    source_manifest = json.loads(
        (SOURCE / "surface_manifest.review.json").read_text(encoding="utf-8")
    )
    for family in FAMILIES:
        textures = {}
        for channel in CHANNELS:
            task = u.AssetImportTask()
            task.set_editor_property(
                "filename", str(SOURCE / f"T_FW_{family}_{channel}.png")
            )
            task.set_editor_property("destination_path", TARGET)
            task.set_editor_property("destination_name", f"T_FW_{family}_{channel}")
            task.set_editor_property("automated", True)
            task.set_editor_property("replace_existing", False)
            task.set_editor_property("save", True)
            asset_tools.import_asset_tasks([task])
            imported = list(task.get_editor_property("imported_object_paths"))
            if len(imported) != 1:
                raise RuntimeError("HOLD: texture import incomplete " + family + "/" + channel)
            texture = u.load_asset(str(imported[0]))
            if texture is None:
                raise RuntimeError("HOLD: texture load failed")
            if channel != "BaseColor":
                texture.set_editor_property("srgb", False)
                texture.set_editor_property(
                    "compression_settings",
                    u.TextureCompressionSettings.TC_NORMALMAP if channel == "Normal"
                    else u.TextureCompressionSettings.TC_MASKS,
                )
            if not u.EditorAssetLibrary.save_loaded_asset(texture):
                raise RuntimeError("HOLD: imported PBR texture save failed")
            textures[channel] = texture
            tex_count += 1

        material = asset_tools.create_asset(
            f"M_FW_{family}", TARGET, u.Material, u.MaterialFactoryNew()
        )
        if material is None:
            raise RuntimeError("HOLD: PBR material factory rejected " + family)
        editor = u.MaterialEditingLibrary
        coord = editor.create_material_expression(
            material, u.MaterialExpressionTextureCoordinate, -900, 0
        )
        tiling = source_manifest["textures"][family]["uv_tiling"]
        coord.set_editor_property("u_tiling", float(tiling))
        coord.set_editor_property("v_tiling", float(tiling))
        for channel, ypos in (("BaseColor", -250), ("Normal", 100), ("ORM", 450)):
            sample = editor.create_material_expression(
                material, u.MaterialExpressionTextureSample, -450, ypos
            )
            sample.set_editor_property("texture", textures[channel])
            if not editor.connect_material_expressions(coord, "", sample, "UVs"):
                raise RuntimeError("HOLD: PBR UV connector unavailable")
            targets = (
                (("RGB", u.MaterialProperty.MP_BASE_COLOR),)
                if channel == "BaseColor" else
                (("RGB", u.MaterialProperty.MP_NORMAL),)
                if channel == "Normal" else
                (("R", u.MaterialProperty.MP_AMBIENT_OCCLUSION),
                 ("G", u.MaterialProperty.MP_ROUGHNESS),
                 ("B", u.MaterialProperty.MP_METALLIC))
            )
            for output, prop in targets:
                if not editor.connect_material_property(sample, output, prop):
                    raise RuntimeError("HOLD: PBR graph connection failed " + family)
        # The timber/stone/brass/aether materials also dress hundreds of
        # InstancedStaticMeshComponents in V5. Without the explicit usage
        # permutation, Unreal substitutes the default checkerboard material.
        # Ocean uses a single StaticMesh and does not need this permutation.
        if family != "ocean":
            editor.set_base_material_usage(
                material, u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES, True
            )
            if not editor.has_material_usage(
                material, u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES
            ):
                raise RuntimeError("HOLD: instanced usage missing " + family)
        errors = editor.recompile_material(material)
        if errors is not None and len(errors):
            raise RuntimeError("HOLD: PBR material compilation failed " + family)
        if not u.EditorAssetLibrary.save_loaded_asset(material):
            raise RuntimeError("HOLD: PBR material save failed " + family)
        materials[family] = f"{TARGET}/M_FW_{family}"

    if sha256(SOURCE_MAP) != before:
        raise RuntimeError("HOLD: original review level changed during PBR import")
    if git("rev-parse", "HEAD").lower() != expected:
        raise RuntimeError("HOLD: source SHA moved during import")
    if any(sha256(SOURCE / filename) != digest for filename, digest
           in inventory["files"].items()):
        raise RuntimeError("HOLD: PBR inputs mutated during import")
    result = {
        "status": "PBR_TEXTURES_IMPORTED_ONLY_IN_ISOLATED_REVIEW_CONTENT",
        "source_head": expected,
        "native_receipt": receipt,
        "map_sha256_unchanged": before,
        "textures": tex_count,
        "material_assets": materials,
        "source_sha256": inventory["files"],
        "production_maps_changed": False,
        "gameplay_modified": False,
        "PIE_verified": False,
        "creator_approved": False,
    }
    path = PROJECT / "Saved/PreludePBRV1/native_import_receipt.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
    u.log("TSTSS_V5_PBR_IMPORT_ONLY " + json.dumps(result, sort_keys=True))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--stage-native", action="store_true")
    options, _unknown = parser.parse_known_args()
    if options.plan:
        result = source_inventory()
    elif options.stage_native or os.environ.get("TSTSS_V5_PBR_OPT_IN") == OPT_IN:
        # Unreal -ExecutePythonScript invokes the file without forwarding
        # arbitrary trailing CLI flags on every engine patch. The explicit,
        # single-purpose opt-in environment gate remains mandatory inside stage().
        result = stage()
    else:
        result = source_inventory()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
