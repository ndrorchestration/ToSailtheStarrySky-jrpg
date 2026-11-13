#!/usr/bin/env python3
"""Bounded UE 5.8.4 native repair for 4 V5 review PBR material usage flags.

This MUST execute inside UnrealEditor-Cmd's PythonScriptPlugin, not system Python
for --apply/--verify. It never creates/rebuilds levels, edits gameplay, mutates
materials outside four exact names, or upgrades visual approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
PACKAGE = "/Game/TSTSS/Review/PreludePBRV1"
EXPECTED_WORKTREE = "TSTSS_V5ObjectIntegration_20261112"
OPT_IN = "REPAIR_V5_INSTANCED_MATERIALS_ONLY"
FAMILIES = ("timber", "stone", "brass", "aether")
SOURCE_MAP = PROJECT / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview.umap"
MATERIALS = {
    family: PROJECT / f"Content/TSTSS/Review/PreludePBRV1/M_FW_{family}.uasset"
    for family in FAMILIES
}
RECEIPT = PROJECT / "Saved/PreludePBRV1/instanced_material_repair.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True, text=True, check=True, timeout=30
    ).stdout
    # Porcelain status has significant leading XY columns. strip() drops
    # its leading blank status char and corrupts path parsing.
    return result.rstrip("\r\n") if args[:2] == ("status", "--porcelain") else result.strip()


def status_paths() -> set[str]:
    # Git records tracked modifications in the 2-char XY prefix.
    return {
        line[3:].replace("\\", "/")
        for line in git("status", "--porcelain", "-uall").splitlines()
        if line
    }


def inventory() -> dict:
    if REPO.name != EXPECTED_WORKTREE or not SOURCE_MAP.is_file():
        raise RuntimeError("HOLD: wrong isolated project or missing V5 source map")
    if any(not path.is_file() for path in MATERIALS.values()):
        raise RuntimeError("HOLD: 4 imported V5 PBR material assets required")
    return {
        "source_map_sha256": sha256(SOURCE_MAP),
        "material_sha256": {key: sha256(path) for key, path in MATERIALS.items()},
        "worktree": str(REPO),
        "package": PACKAGE,
        "families": list(FAMILIES),
        "gameplay_modified": False,
        "source_map_modified": False,
        "creator_approved": False,
    }


def is_generated_android_config_only() -> bool:
    """Recognize exactly the automatic UE editor startup append, no more.

    The AndroidFileServer plugin writes DefaultEngine.ini at launch even when
    this task has nothing to do with Android. This one editor side-effect is
    not a modification requested by the repair and must NOT be committed.
    """
    rel = "unreal/Config/DefaultEngine.ini"
    path = REPO / rel
    if not path.is_file():
        return False
    original = subprocess.run(
        ["git", "-C", str(REPO), "show", "HEAD:" + rel],
        capture_output=True, text=True, check=True, timeout=30
    ).stdout.replace("\r\n", "\n")
    current = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    if current == original:
        return True
    if not current.startswith(original):
        return False
    extra = current[len(original):]
    expected = (
        "\n[/Script/AndroidFileServerEditor.AndroidFileServerRuntimeSettings]\n"
        "bEnablePlugin=True\n"
        "bAllowNetworkConnection=True\n"
        "SecurityToken={token}\n"
        "bIncludeInShipping=False\n"
        "bAllowExternalStartInShipping=False\n"
        "bCompileAFSProject=False\n"
        "bUseCompression=False\n"
        "bLogFiles=False\n"
        "bReportStats=False\n"
        "ConnectionType=USBOnly\n"
        "bUseManualIPAddress=False\n"
        "ManualIPAddress=\n"
    )
    found = re.fullmatch(r"[0-9A-Fa-f]{32}", (
        extra.split("SecurityToken=", 1)[1].split("\n", 1)[0]
        if extra.count("SecurityToken=") == 1 else ""
    ))
    # Unreal serializes a final optional blank line in this generated block.
    # Permit no other keys, values, prefix edits, or trailing whitespace.
    trailing = len(extra) - len(extra.rstrip("\n"))
    return bool(
        found and 1 <= trailing <= 2 and
        extra.rstrip("\n") == expected.format(token=found.group(0)).rstrip("\n")
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args, _ = parser.parse_known_args()
    # -run=pythonscript -script=<path> often does not forward CLI flags.
    # Require an additional explicit mode variable for headless commandlets.
    mode = os.environ.get("TSTSS_V5_INSTANCING_MODE", "")
    if mode not in ("", "APPLY", "VERIFY"):
        raise RuntimeError("HOLD: unknown native material command mode")
    apply = args.apply or mode == "APPLY"
    verify = args.verify or mode == "VERIFY"
    if apply and verify:
        raise RuntimeError("HOLD: conflicting repair/readback modes")
    baseline = inventory()
    if args.plan or (not apply and not verify):
        print(json.dumps(baseline, sort_keys=True, indent=2))
        return

    expected = os.environ.get("TSTSS_V5_INSTANCING_EXPECTED_HEAD", "").lower()
    if not re.fullmatch(r"[0-9a-f]{40}", expected) or git("rev-parse", "HEAD") != expected:
        raise RuntimeError("HOLD: source HEAD pin absent or drifted")
    if os.environ.get("TSTSS_V5_INSTANCING_OPT_IN") != OPT_IN:
        raise RuntimeError("HOLD: explicit opt-in absent")
    allowed = {
        f"unreal/Content/TSTSS/Review/PreludePBRV1/M_FW_{family}.uasset"
        for family in FAMILIES
    }
    before_paths = status_paths()
    editor_config = "unreal/Config/DefaultEngine.ini"
    if editor_config in before_paths and not is_generated_android_config_only():
        raise RuntimeError("HOLD: non-engine DefaultEngine.ini modifications")
    unexpected_before = before_paths - {editor_config}
    if (apply and unexpected_before) or (verify and not unexpected_before.issubset(allowed)):
        raise RuntimeError("HOLD: unapproved dirty source paths: " + str(unexpected_before))

    import unreal as u

    if Path(u.Paths.project_dir()).resolve() != PROJECT.resolve():
        raise RuntimeError("HOLD: loaded Unreal project differs")
    if not str(u.SystemLibrary.get_engine_version()).startswith("5.8.4"):
        raise RuntimeError("HOLD: require UE 5.8.4")
    if u.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: unsaved Editor map packages")
    if u.EditorLoadingAndSavingUtils.get_dirty_content_packages():
        raise RuntimeError("HOLD: pre-existing dirty Editor content")

    usage = u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES
    edit = u.MaterialEditingLibrary
    changed = []
    for family in FAMILIES:
        path = f"{PACKAGE}/M_FW_{family}"
        material = u.load_asset(path)
        if material is None or not isinstance(material, u.Material):
            raise RuntimeError("HOLD: missing native UMaterial " + path)
        was_enabled = bool(edit.has_material_usage(material, usage))
        if apply and not was_enabled:
            # Use the UE5.8-supported material-editor API; the reflected
            # Material property is read-only in current Python bindings.
            edit.set_base_material_usage(material, usage, True)
            compile_errors = edit.recompile_material(material)
            if compile_errors is not None and len(compile_errors):
                raise RuntimeError("HOLD: material compile errors for " + family)
            if not edit.has_material_usage(material, usage):
                raise RuntimeError("HOLD: usage flag failed for " + family)
            if not u.EditorAssetLibrary.save_loaded_asset(material):
                raise RuntimeError("HOLD: material save failed for " + family)
            changed.append(family)
        if not edit.has_material_usage(material, usage):
            raise RuntimeError("HOLD: material still lacks instancing usage: " + family)

    if sha256(SOURCE_MAP) != baseline["source_map_sha256"]:
        raise RuntimeError("HOLD: V5 source map changed")
    if git("rev-parse", "HEAD") != expected:
        raise RuntimeError("HOLD: source SHA drift during Unreal repair")
    after_paths = status_paths()
    if editor_config in after_paths and not is_generated_android_config_only():
        raise RuntimeError("HOLD: DefaultEngine.ini was edited beyond known auto-config")
    if not (after_paths - {editor_config}).issubset(allowed):
        raise RuntimeError("HOLD: unexpected tracked/untracked content " + str(after_paths))
    result = {
        "status": "V5_INSTANCED_PBR_MATERIAL_USAGE_ENABLED" if apply
                  else "V5_INSTANCED_PBR_MATERIAL_USAGE_READBACK_PASS",
        "source_head": expected,
        "ue_version": "5.8.4",
        "changed_families": changed,
        "verified_families": list(FAMILIES),
        "usage": "MATUSAGE_INSTANCED_STATIC_MESHES",
        "source_map_sha256_unchanged": baseline["source_map_sha256"],
        "materials_after": {key: sha256(path) for key, path in MATERIALS.items()},
        "changed_repo_paths": sorted(after_paths - {editor_config}),
        "editor_startup_config_generated_not_for_commit": editor_config in after_paths,
        "source_maps_edited": False,
        "story_authority_changed": False,
        "creator_approved": False,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(result, sort_keys=True, indent=2), encoding="utf-8")
    u.log("TSTSS_V5_INSTANCED_PBR_REPAIR " + json.dumps(result, sort_keys=True))
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
