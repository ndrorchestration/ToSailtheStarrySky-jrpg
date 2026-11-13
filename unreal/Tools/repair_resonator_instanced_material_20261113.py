#!/usr/bin/env python3
"""Fail-closed native Unreal 5.8.4 usage repair for ONE Resonator VFX material.

Modifies only /Game/TSTSS/Magic/M_ResonatorGlow in the isolated review branch.
It does not unlock spells, touch ability execution, edit maps or auto-merge.
Native commandlet mode requires explicit environment opt-in and exact HEAD.
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
MATERIAL = PROJECT / "Content/TSTSS/Magic/M_ResonatorGlow.uasset"
V5_MAP = PROJECT / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview.umap"
SHORE_MAP = PROJECT / "Content/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review.umap"
ASSET_PACKAGE = "/Game/TSTSS/Magic/M_ResonatorGlow"
OPT_IN = "REPAIR_RESONATOR_INSTANCED_USAGE_ONLY"
EXPECTED_WORKTREE = "TSTSS_V5ObjectIntegration_20261112"
ASSET_REL = "unreal/Content/TSTSS/Magic/M_ResonatorGlow.uasset"
EDITOR_INI = "unreal/Config/DefaultEngine.ini"
RECEIPT = PROJECT / "Saved/ResonatorVfx/instancing_readback.json"


def sha(file: Path) -> str:
    return hashlib.sha256(file.read_bytes()).hexdigest()


def git(*args: str) -> str:
    r = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True,
        check=True, text=True, timeout=30
    ).stdout
    if args and args[0] == "status":
        # Preserve leading porcelain XY columns; never .strip() the first.
        return r.rstrip("\r\n")
    return r.strip()


def dirty_paths() -> set[str]:
    return {
        line[3:].replace("\\", "/")
        for line in git("status", "--porcelain", "-uall").splitlines() if line
    }


def known_editor_ini_append() -> bool:
    """Allow only UE's exact automatically appended AndroidFileServer block."""
    ini = ROOT / EDITOR_INI
    original = subprocess.run(
        ["git", "-C", str(ROOT), "show", "HEAD:" + EDITOR_INI],
        capture_output=True, text=True, check=True, timeout=30
    ).stdout.replace("\r\n", "\n")
    current = ini.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
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
    if ROOT.name != EXPECTED_WORKTREE or not MATERIAL.is_file() or (
        not V5_MAP.is_file() or not SHORE_MAP.is_file()
    ):
        raise RuntimeError("HOLD: wrong review worktree or missing native assets")
    mode = os.environ.get("TSTSS_RESONATOR_INSTANCING_MODE", "")
    if mode not in ("APPLY", "VERIFY"):
        print(json.dumps({
            "status": "PLAN_ONLY",
            "asset": ASSET_PACKAGE,
            "original_sha256": sha(MATERIAL),
            "map_sha256": {"v5": sha(V5_MAP), "shore": sha(SHORE_MAP)},
            "native_verified": False,
        }, sort_keys=True))
        return
    expected = os.environ.get("TSTSS_RESONATOR_INSTANCING_HEAD", "")
    if (not re.fullmatch(r"[0-9a-f]{40}", expected) or
        git("rev-parse", "HEAD") != expected or
        os.environ.get("TSTSS_RESONATOR_INSTANCING_OPT_IN") != OPT_IN):
        raise RuntimeError("HOLD: absent opt-in or HEAD changed")
    before = dirty_paths()
    if EDITOR_INI in before and not known_editor_ini_append():
        raise RuntimeError("HOLD: unrecognized editor config modifications")
    if mode == "APPLY" and before - {EDITOR_INI}:
        raise RuntimeError("HOLD: requires clean source/asset before APPLY")
    if mode == "VERIFY" and not (before - {EDITOR_INI}).issubset({ASSET_REL}):
        raise RuntimeError("HOLD: unknown dirty paths before VERIFY")

    initial_maps = {"v5": sha(V5_MAP), "shore": sha(SHORE_MAP)}
    import unreal as u

    if (Path(u.Paths.project_dir()).resolve() != PROJECT.resolve() or
        not str(u.SystemLibrary.get_engine_version()).startswith("5.8.4") or
        u.EditorLoadingAndSavingUtils.get_dirty_map_packages() or
        u.EditorLoadingAndSavingUtils.get_dirty_content_packages()):
        raise RuntimeError("HOLD: project/engine or editor cleanliness mismatch")
    material = u.load_asset(ASSET_PACKAGE)
    if material is None or not isinstance(material, u.Material):
        raise RuntimeError("HOLD: native Resonator material missing")
    usage = u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES
    editor = u.MaterialEditingLibrary
    changed = False
    if mode == "APPLY" and not editor.has_material_usage(material, usage):
        editor.set_base_material_usage(material, usage, True)
        errors = editor.recompile_material(material)
        if errors is not None and len(errors):
            raise RuntimeError("HOLD: material compile errors")
        if not editor.has_material_usage(material, usage):
            raise RuntimeError("HOLD: instanced material usage not set")
        if not u.EditorAssetLibrary.save_loaded_asset(material):
            raise RuntimeError("HOLD: material save failed")
        changed = True
    if not editor.has_material_usage(material, usage):
        raise RuntimeError("HOLD: missing persistent instanced material flag")
    after = dirty_paths()
    if EDITOR_INI in after and not known_editor_ini_append():
        raise RuntimeError("HOLD: unrelated editor startup config drift")
    if not (after - {EDITOR_INI}).issubset({ASSET_REL}):
        raise RuntimeError("HOLD: unexpected asset/content edits")
    if (git("rev-parse", "HEAD") != expected or
        initial_maps != {"v5": sha(V5_MAP), "shore": sha(SHORE_MAP)}):
        raise RuntimeError("HOLD: map or source SHA changed during repair")
    result = {
        "status": "RESONATOR_INSTANCED_USAGE_SAVED" if mode == "APPLY"
                  else "RESONATOR_INSTANCED_USAGE_FRESH_READBACK_PASS",
        "source_sha": expected,
        "engine": "5.8.4",
        "package": ASSET_PACKAGE,
        "asset_sha256": sha(MATERIAL),
        "changed": changed,
        "map_sha256_unchanged": initial_maps,
        "tracked_changes": sorted(after - {EDITOR_INI}),
        "generated_editor_config_not_committable": EDITOR_INI in after,
        "combat_unlock_or_story_changes": False,
        "creator_visual_approval": False,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    u.log("TSTSS_RESONATOR_INSTANCED_USAGE " + json.dumps(result, sort_keys=True))
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
