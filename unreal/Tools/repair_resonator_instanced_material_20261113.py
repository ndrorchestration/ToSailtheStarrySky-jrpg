#!/usr/bin/env python3
"""Create/read back a NEW isolated Resonator instanced-shader review material.

The immutable historical /Game/TSTSS/Magic/M_ResonatorGlow and 222-file
shoreline snapshot must NEVER be changed. No maps, state, sounds or unlocks.
Uses native UE 5.8.4, explicit opt-in, clean source SHA and asset whitelist.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "unreal"
ORIGINAL = PROJECT / "Content/TSTSS/Magic/M_ResonatorGlow.uasset"
ORIGINAL_SHA256 = "117698d8314f2afecdefa5feacf8778dd443abd61443df8768db234b3d85d20b"
ORIGINAL_PACKAGE = "/Game/TSTSS/Magic/M_ResonatorGlow"
REVIEW_DIR = "/Game/TSTSS/Review/ResonatorMaterialV1"
REVIEW_PACKAGE = REVIEW_DIR + "/M_ResonatorGlow_InstancedReview"
REVIEW_ASSET = PROJECT / "Content/TSTSS/Review/ResonatorMaterialV1/M_ResonatorGlow_InstancedReview.uasset"
REVIEW_REL = "unreal/Content/TSTSS/Review/ResonatorMaterialV1/M_ResonatorGlow_InstancedReview.uasset"
V5_MAP = PROJECT / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview.umap"
SHORE_MAP = PROJECT / "Content/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review.umap"
EXPECTED_WORKTREE = "TSTSS_V5ObjectIntegration_20261112"
OPT_IN = "CREATE_ISOLATED_RESONATOR_INSTANCED_REVIEW_ONLY"
EDITOR_INI = "unreal/Config/DefaultEngine.ini"
RECEIPT = PROJECT / "Saved/ResonatorVfx/instanced_review_copy_readback.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args], text=True,
        capture_output=True, check=True, timeout=30
    ).stdout
    # Keep leading XY spaces in porcelain status; never use strip() there.
    return result.rstrip("\r\n") if args and args[0] == "status" else result.strip()


def dirty_paths() -> set[str]:
    return {line[3:].replace("\\", "/") for line in
            git("status", "--porcelain", "-uall").splitlines() if line}


def known_editor_ini_append() -> bool:
    """Recognize only UE's exact automatically generated AndroidFileServer block."""
    original = subprocess.run(
        ["git", "-C", str(ROOT), "show", "HEAD:" + EDITOR_INI],
        capture_output=True, text=True, check=True, timeout=30
    ).stdout.replace("\r\n", "\n")
    current = (ROOT / EDITOR_INI).read_text(
        encoding="utf-8-sig"
    ).replace("\r\n", "\n")
    if current == original:
        return True
    if not current.startswith(original):
        return False
    extra = current[len(original):]
    pattern = (
        r"\n\[/Script/AndroidFileServerEditor\.AndroidFileServerRuntimeSettings\]\n"
        r"bEnablePlugin=True\nbAllowNetworkConnection=True\n"
        r"SecurityToken=[0-9A-Fa-f]{32}\n"
        r"bIncludeInShipping=False\nbAllowExternalStartInShipping=False\n"
        r"bCompileAFSProject=False\nbUseCompression=False\n"
        r"bLogFiles=False\nbReportStats=False\nConnectionType=USBOnly\n"
        r"bUseManualIPAddress=False\nManualIPAddress=\n{1,2}"
    )
    return re.fullmatch(pattern, extra) is not None


def main() -> None:
    if (ROOT.name != EXPECTED_WORKTREE or not ORIGINAL.is_file() or
        sha(ORIGINAL) != ORIGINAL_SHA256 or not V5_MAP.is_file() or
        not SHORE_MAP.is_file()):
        raise RuntimeError("HOLD: immutable original source, review checkout or map mismatch")
    mode = os.environ.get("TSTSS_RESONATOR_INSTANCING_MODE", "")
    if mode not in ("APPLY", "VERIFY"):
        print(json.dumps({
            "status": "PLAN_ONLY",
            "source_original_sha256": sha(ORIGINAL),
            "review_asset_exists": REVIEW_ASSET.is_file(),
            "native_verified": False,
        }, sort_keys=True))
        return
    expected = os.environ.get("TSTSS_RESONATOR_INSTANCING_HEAD", "")
    if (not re.fullmatch(r"[0-9a-f]{40}", expected) or
        git("rev-parse", "HEAD") != expected or
        os.environ.get("TSTSS_RESONATOR_INSTANCING_OPT_IN") != OPT_IN):
        raise RuntimeError("HOLD: exact SHA or affirmative single-asset opt-in absent")
    before = dirty_paths()
    if EDITOR_INI in before and not known_editor_ini_append():
        raise RuntimeError("HOLD: unknown editor config mutation")
    if mode == "APPLY" and (REVIEW_ASSET.exists() or before - {EDITOR_INI}):
        raise RuntimeError("HOLD: destination exists or review checkout is dirty")
    if mode == "VERIFY" and (
        not REVIEW_ASSET.is_file() or
        not (before - {EDITOR_INI}).issubset({REVIEW_REL})
    ):
        raise RuntimeError("HOLD: missing review copy or unrelated asset changes")
    maps_before = {"v5": sha(V5_MAP), "shore": sha(SHORE_MAP)}

    import unreal as u

    if (Path(u.Paths.project_dir()).resolve() != PROJECT.resolve() or
        not str(u.SystemLibrary.get_engine_version()).startswith("5.8.4") or
        u.EditorLoadingAndSavingUtils.get_dirty_map_packages() or
        u.EditorLoadingAndSavingUtils.get_dirty_content_packages()):
        raise RuntimeError("HOLD: wrong native project/engine or dirty Editor packages")
    if mode == "APPLY":
        if u.EditorAssetLibrary.does_asset_exist(REVIEW_PACKAGE):
            raise RuntimeError("HOLD: refusing to overwrite existing review copy")
        if not u.EditorAssetLibrary.does_directory_exist(REVIEW_DIR):
            if not u.EditorAssetLibrary.make_directory(REVIEW_DIR):
                raise RuntimeError("HOLD: isolated review directory creation failed")
        material = u.EditorAssetLibrary.duplicate_asset(
            ORIGINAL_PACKAGE, REVIEW_PACKAGE
        )
        if not material:
            raise RuntimeError("HOLD: native review material duplicate failed")
    else:
        material = u.load_asset(REVIEW_PACKAGE)
    if material is None or not isinstance(material, u.Material):
        raise RuntimeError("HOLD: review copy is not native UMaterial")
    usage = u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES
    editor = u.MaterialEditingLibrary
    changed = False
    if mode == "APPLY":
        editor.set_base_material_usage(material, usage, True)
        errors = editor.recompile_material(material)
        if errors is not None and len(errors):
            raise RuntimeError("HOLD: review material shader compile errors")
        if not editor.has_material_usage(material, usage):
            raise RuntimeError("HOLD: instanced review shader usage not set")
        if not u.EditorAssetLibrary.save_loaded_asset(material):
            raise RuntimeError("HOLD: native review material save failed")
        changed = True
    if not editor.has_material_usage(material, usage):
        raise RuntimeError("HOLD: review shader usage missing after fresh load")

    after = dirty_paths()
    if EDITOR_INI in after and not known_editor_ini_append():
        raise RuntimeError("HOLD: auto config modified beyond expected generated block")
    if (not (after - {EDITOR_INI}).issubset({REVIEW_REL}) or
        sha(ORIGINAL) != ORIGINAL_SHA256 or
        maps_before != {"v5": sha(V5_MAP), "shore": sha(SHORE_MAP)} or
        git("rev-parse", "HEAD") != expected):
        raise RuntimeError("HOLD: historical material/map or source custody drift")
    result = {
        "status": "ISOLATED_RESONATOR_INSTANCED_REVIEW_COPY_SAVED" if mode == "APPLY"
                  else "ISOLATED_RESONATOR_INSTANCED_FRESH_READBACK_PASS",
        "source_sha": expected, "engine": "5.8.4",
        "original_sha256_unchanged": ORIGINAL_SHA256,
        "review_asset": REVIEW_PACKAGE,
        "review_sha256": sha(REVIEW_ASSET), "changed": changed,
        "map_sha256_unchanged": maps_before,
        "asset_changes_only": sorted(after - {EDITOR_INI}),
        "generated_editor_config_not_committable": EDITOR_INI in after,
        "historical_snapshot_modified": False,
        "story_or_spell_authority_changed": False,
        "creator_visual_approval": False,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(result, sort_keys=True, indent=2), encoding="utf-8")
    u.log("TSTSS_RESONATOR_INSTANCED_REVIEW_COPY " + json.dumps(result, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
