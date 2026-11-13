#!/usr/bin/env python3
"""Bounded source-locked First Wake gameplay atmosphere authoring.

Mutates ONLY the isolated feature-branch VS02 native map after explicit
Windows/UE5.8.4 admission. Reuses existing source-authored SurfacePassV1
recipe, removes exactly four duplicate sky actors, adds ONE native weather
authority and two proposed engine practicals. Never operates on main or the
original optical-review worktree. No automatic story, audio, camera or save
changes; no claim of PIE or cinematic approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import first_wake_surface_textures as surface  # noqa: E402

ROOT = HERE.parents[1]
PROJECT = ROOT / "unreal"
WORKTREE = "TSTSS_EngineGameplayFocus_20261112"
SCENE = "VS02_AureateInteriors"
MAP_ASSET = "/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors"
MAP_FILE = PROJECT / "Content/TSTSS/Review/VerticalSlice/VS02_AureateInteriors.umap"
EXPECTED_ORIGINAL_SHA = "a97fbb057cb87c0e35fe95195ca06c30de1a5cc60158bf31a657f738b22a9d69"
EXPECTED_ORIGINAL_ACTORS = 28
RECEIPT = PROJECT / "Saved/EngineFocusGameplayV1/map_atmosphere_stage.json"
NATIVE_CLASS = "/Script/ToSailTheStarrySky.TSTSSAtmosphereDirector"
CLOUD_ASSET = "/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst"
LABEL = "TSTSS_SURFACE_REVIEW_VS02_AureateInteriors_SingleAtmosphere"
ORIGINAL_LIGHTS = tuple(surface.OLD_SKY_LABELS)
PROTECTED_CONFIG = ("DefaultEngine.ini", "DefaultInput.ini")


def require(ok, reason: str) -> None:
    if not ok:
        raise RuntimeError("HOLD_PLAYABLE_ENGINE_MAP: " + reason)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *args], text=True, capture_output=True,
        check=False, timeout=20,
    )
    require(result.returncode == 0, "git custody unavailable")
    return result.stdout.strip()


def plan(strict_source: bool = True) -> dict:
    require(SCENE == "VS02_AureateInteriors"
            and surface.SCENE_LOOKS.get(SCENE) == ("Clear", 17.1, "engineering"),
            "existing authored atmospheric recipe drifted")
    require(tuple(surface.OLD_SKY_LABELS) == (
        "TSTSS_VS_REVIEW_SunKey", "TSTSS_VS_REVIEW_SkyAmbient",
        "TSTSS_VS_REVIEW_Atmosphere", "TSTSS_VS_REVIEW_AerialFog"),
        "sky-removal inventory drifted")
    require(surface.PRACTICAL_LAMPS.get(SCENE) == (
        (200, -250, 340, 2200), (-780, 150, 420, 1900)),
        "authored engine practical-light recipe drifted")
    require(MAP_FILE.is_file(), "original source VS02 package absent")
    raw = MAP_FILE.read_bytes()
    if strict_source:
        require(hashlib.sha256(raw).hexdigest() == EXPECTED_ORIGINAL_SHA,
                "gameplay VS02 original source map changed")
    for label in ("TSTSS_VS_REVIEW_InstrumentCore_LIFT",
                  "TSTSS_VS_REVIEW_MainHarmonicLevitationEngine_Proxy"):
        require(label.encode("ascii") in raw, "real engine focus anchor absent: " + label)
    if strict_source:
        for label in ORIGINAL_LIGHTS:
            require(label.encode("ascii") in raw,
                    "original sky actor to reconcile absent: " + label)
        require(b"TSTSSAtmosphereDirector" not in raw,
                "pre-existing world atmosphere director; do not duplicate")
        require(LABEL.encode("ascii") not in raw,
                "previously staged gameplay director cannot be overwritten")
    return {
        "schema": "tstss.firstwake.playable_engine_map_authoring.v1",
        "status": ("SOURCE_VERIFIED_NATIVE_STAGE_NOT_EXECUTED" if strict_source
                   else "RECIPE_VALIDATED_WITHOUT_NATIVE_STAGE"),
        "scope": "isolated feature-branch gameplay map ONLY",
        "source_map": MAP_ASSET,
        "expected_original_map_sha256": EXPECTED_ORIGINAL_SHA,
        "source_original_actor_count": EXPECTED_ORIGINAL_ACTORS,
        "remove_exactly": list(ORIGINAL_LIGHTS),
        "add_exactly_one": LABEL,
        "weather": "Clear",
        "initial_clock_hours": 17.1,
        "authored_lighting_recipe": "engineering",
        "proposed_practicals": [
            {"index": i, "x": v[0], "y": v[1], "z": v[2], "lumens": v[3]}
            for i, v in enumerate(surface.PRACTICAL_LAMPS[SCENE])
        ],
        "renderer": "native Unreal Engine 5.8.4",
        "gameplay_e_and_c_input_mutated": False,
        "saves_or_story_changed": False,
        "native_pie_verified": False,
        "cinematic_approved": False,
    }


def custody() -> dict:
    require(sys.platform == "win32", "native Windows editor required")
    require(ROOT.name == WORKTREE, "only the dedicated gameplay feature worktree")
    require(os.environ.get("TSTSS_GAMEPLAY_ENGINE_STAGE_EXPLICIT") == "1",
            "explicit stage authorization is absent")
    head = os.environ.get("TSTSS_GAMEPLAY_ENGINE_EXPECTED_HEAD", "").strip().lower()
    require(bool(re.fullmatch(r"[a-f0-9]{40}", head)), "exact 40-hex source commit required")
    require(git("rev-parse", "HEAD").lower() == head, "source HEAD drift")
    require(not git("status", "--porcelain", "-uall"),
            "source checkout contains tracked or untracked edits")
    require(not RECEIPT.exists(), "prior native-stage receipt occupies destination")
    require(digest(MAP_FILE) == EXPECTED_ORIGINAL_SHA,
            "original VS02 map sha no longer source-locked")
    return {
        "exact_head": head,
        "original_sha256": EXPECTED_ORIGINAL_SHA,
        "config_sha256": {
            n: digest(PROJECT / "Config" / n) for n in PROTECTED_CONFIG
        },
    }


def native_stage() -> dict:
    c = custody()
    p = plan()
    import unreal as u
    require(u.SystemLibrary.get_engine_version().startswith("5.8.4"),
            "native UE 5.8.4 required")
    require(not u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
            and not u.EditorLoadingAndSavingUtils.get_dirty_content_packages(),
            "Editor has unsaved maps/assets before VS02 stage")
    require(u.EditorAssetLibrary.does_asset_exist(MAP_ASSET),
            "actual playable route map missing from native registry")
    cls = u.load_class(None, NATIVE_CLASS)
    require(cls is not None, "compiled native atmosphere director unavailable")
    cloud = u.load_asset(CLOUD_ASSET)
    require(cloud is not None, "existing UE cloud material unavailable")
    world = u.EditorLoadingAndSavingUtils.load_map(MAP_ASSET)
    require(world is not None, "native VS02 map failed to load")
    actorsys = u.get_editor_subsystem(u.EditorActorSubsystem)
    require(actorsys is not None, "native EditorActorSubsystem unavailable")
    old = actorsys.get_all_level_actors()
    require(len(old) == EXPECTED_ORIGINAL_ACTORS,
            "source VS02 actor count changed; refuse in-place review edit")
    names = [a.get_actor_label() for a in old]
    require(len(names) == len(set(names)), "duplicated native actor labels")
    for label in (*ORIGINAL_LIGHTS, "TSTSS_VS_REVIEW_InstrumentCore_LIFT"):
        require(names.count(label) == 1, "missing/duplicate source actor: " + label)
    require(not any(a.get_class().get_name() == "TSTSSAtmosphereDirector" for a in old),
            "native director already owns weather; refuse a second")
    applied = surface.stage_scene_atmosphere(u, actorsys, SCENE, cls, cloud)
    require(applied["new_director"] == LABEL
            and applied["weather"] == "Clear"
            and applied["clock_hours"] == 17.1
            and set(applied["old_sky_actors_removed"]) == set(ORIGINAL_LIGHTS)
            and len(applied["practical_lights"]) == 2,
            "new authored weather/lighting inventory drifted")
    after = actorsys.get_all_level_actors()
    require(len(after) == EXPECTED_ORIGINAL_ACTORS - 4 + 3,
            "native actor delta not exactly -4+1+2")
    require(sum(a.get_class().get_name() == "TSTSSAtmosphereDirector"
                for a in after) == 1,
            "world has other weather authority")
    after_labels = [a.get_actor_label() for a in after]
    require(len(after_labels) == len(set(after_labels)),
            "native actor label collision after staging")
    require(digest(PROJECT / "Config" / "DefaultEngine.ini")
            == c["config_sha256"]["DefaultEngine.ini"]
            and digest(PROJECT / "Config" / "DefaultInput.ini")
            == c["config_sha256"]["DefaultInput.ini"],
            "protected game/project input config changed")
    require(u.EditorLoadingAndSavingUtils.save_map(world, MAP_ASSET),
            "cannot save source-locked draft VS02 native playable map")
    require(digest(MAP_FILE) != EXPECTED_ORIGINAL_SHA,
            "native staged map bytes did not change")
    result = {
        **p,
        **c,
        "status": "NATIVE_GAMEPLAY_MAP_AUTHORED_NOT_PIE_OR_APPROVED",
        "new_gameplay_map_sha256": digest(MAP_FILE),
        "new_actor_count": len(after),
        "added_world_director": applied["new_director"],
        "proposed_practicals": applied["practical_lights"],
        "source_map_only": MAP_ASSET,
        "world_authority_count": 1,
        "native_PIE": "NOT_RUN",
        "visual_approval": "NOT_ESTABLISHED",
        "committed": False,
        "merged": False,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    with RECEIPT.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    u.log("TSTSS_PLAYABLE_ENGINE_MAP_STAGED_NOT_PIE " + result["new_gameplay_map_sha256"])
    return result


def self_test() -> dict:
    # Can also be run after a separately verified native map stage.
    p = plan(strict_source=False)
    require(len(p["remove_exactly"]) == 4, "expected exactly four redundant sky actors")
    require(len(p["proposed_practicals"]) == 2, "expected exactly two authored practicals")
    require(p["weather"] == "Clear" and p["initial_clock_hours"] == 17.1,
            "authored environment profile changed")
    require(p["source_original_actor_count"] == 28,
            "native actor inventory unexpectedly changed")
    return {
        "status": "GAMEPLAY_ENGINE_AUTHORING_RECIPE_CHECK_PASS",
        "checks": 4,
        "native_scene_written": "NOT_CHECKED",
        "native_camera_test": "NOT_RUN",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan", action="store_true")
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--stage", action="store_true")
    args = parser.parse_args()
    try:
        if args.stage:
            output = native_stage()
        elif args.self_test:
            output = self_test()
        else:
            output = plan()
        print(json.dumps(output, indent=2))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
