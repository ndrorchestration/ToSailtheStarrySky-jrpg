#!/usr/bin/env python3
"""TSTSS original 3D enemy gallery: source-locked, noncanonical Unreal review.

--validate: no UE import, filesystem mutation or editor process.
--build: only in a clean exact-head named disposable UE Editor worktree.
The authored .umap is new and review-only. No story/party/save/encounter writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

SANDBOX_NAME = "TSTSS-Slice-Enemies-20261110"
MAP = "/Game/TSTSS/Review/SliceEnemyGallery_V0"
MAP_FILE = "Content/TSTSS/Review/SliceEnemyGallery_V0.umap"
NATIVE_CLASS = "/Script/ToSailTheStarrySky.TSTSSSliceEnemyActor"
ENV_SHA = "TSTSS_ENEMY_GALLERY_EXPECTED_HEAD"
# All coordinates are centimeters, 1m = 100 Unreal units.
# Kind strings map to the actual C++ enum, not speculative numeric values.
# 15 independent actor identities. Five category aisles, three plinths each.
# Each y-coordinate is a separate gallery bay; x is the camera-facing spread.
GALLERY_FAMILIES = (
    ("Anomaly", 0.0),
    ("Bandit", 850.0),
    ("Flora", 1700.0),
    ("Aquatic", 2550.0),
    ("Fauna", 3400.0),
)
ENEMIES = (
    ("Shear_01", "HarmonicShear", -480.0, 0.0, "HARMONIC SHEAR"),
    ("Wisp_01", "AetherLeakWisp", 0.0, 0.0, "AETHER WISP"),
    ("Skitter_01", "DockSkitter", 480.0, 0.0, "DOCK SKITTER"),
    ("Cutpurse_01", "BanditCutpurse", -480.0, 850.0, "QUAYSIDE CUTPURSE"),
    ("Slinger_01", "BanditSlinger", 0.0, 850.0, "QUAYSIDE SLINGER"),
    ("Captain_01", "BanditCaptain", 480.0, 850.0, "BANDIT CAPTAIN / LEADER"),
    ("Thornvine_01", "Thornvine", -480.0, 1700.0, "THORNVINE CREEPER"),
    ("Sporecap_01", "Sporecap", 0.0, 1700.0, "SPORECAP STALKER"),
    ("Sentinel_01", "RootSentinel", 480.0, 1700.0, "ROOT SENTINEL"),
    ("Eel_01", "ReefEel", -480.0, 2550.0, "REEF EEL"),
    ("Tidefin_01", "TidefinRaptor", 0.0, 2550.0, "TIDEFIN HUNTER"),
    ("Shellback_01", "ShellbackCrab", 480.0, 2550.0, "SHELLBACK CRAB"),
    ("Lynx_01", "CliffLynx", -480.0, 3400.0, "CLIFF LYNX"),
    ("Boar_01", "Bristleboar", 0.0, 3400.0, "BRISTLEBOAR"),
    ("Glider_01", "NightGlider", 480.0, 3400.0, "NIGHT GLIDER"),
)
ACTOR_PREFIX = "REVIEW_ONLY_ENEMY_"
PREVIEW_STATUS = "SOURCE_PLAN_ONLY_NOT_NATIVE_RENDERED"


def validate_plan() -> dict:
    ids = [entry[0] for entry in ENEMIES]
    kinds = [entry[1] for entry in ENEMIES]
    positions = [(entry[2], entry[3]) for entry in ENEMIES]
    if len(ENEMIES) != 15 or len(set(ids)) != 15 or len(set(kinds)) != 15:
        raise RuntimeError("HOLD: gallery must contain 15 unique enemy identities")
    expected_aisles = [0.0, 850.0, 1700.0, 2550.0, 3400.0]
    if [y for _,y in GALLERY_FAMILIES] != expected_aisles:
        raise RuntimeError("HOLD: category aisle locations drifted")
    if len(set(positions)) != 15:
        raise RuntimeError("HOLD: duplicate gallery placement")
    for i, (name, kind, x, y, caption) in enumerate(ENEMIES):
        if not name or not kind or not caption:
            raise RuntimeError("HOLD: incomplete gallery slot")
        if y != expected_aisles[i // 3] or x != (-480.0,0.0,480.0)[i % 3]:
            raise RuntimeError("HOLD: gallery category layout or overlap drifted")
        if any((x-x2)**2+(y-y2)**2 < 400.0**2
               for x2,y2 in positions[:i]):
            raise RuntimeError("HOLD: gallery silhouettes overlap")
    if MAP_FILE.startswith("/") or ".." in Path(MAP_FILE).parts:
        raise RuntimeError("HOLD: unsafe destination")
    return {
        "status": PREVIEW_STATUS,
        "new_review_map": MAP,
        "native_actor_class": NATIVE_CLASS,
        "staged_enemy_ids": ids,
        "families": [name for name,_ in GALLERY_FAMILIES],
        "gallery_slots": len(ids),
        "species_or_revised_encounter_placement_approved": False,
        "combat_player_actions_granted": False,
        "saves_or_protected_maps_modified": False,
        "new_skeletal_mesh_or_niagara_created": False,
        "ue_compilation_tested_by_this_script": False,
        "native_3d_review_pass": False,
    }


def checked_sandbox(unreal_project_dir: Path) -> tuple[Path, str]:
    """Fail before touching a map, map registry, game save or source."""
    project = unreal_project_dir.resolve()
    repo = project.parent
    if project.name.lower() != "unreal" or repo.name != SANDBOX_NAME:
        raise RuntimeError("HOLD: gallery requires the named disposable enemy worktree")
    expected = os.environ.get(ENV_SHA, "")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", expected):
        raise RuntimeError("HOLD: full exact expected SHA required")
    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, check=False, timeout=25)
        if result.returncode:
            raise RuntimeError("HOLD: cannot verify source custody")
        return result.stdout.strip()
    if git("rev-parse", "HEAD").lower() != expected.lower():
        raise RuntimeError("HOLD: gallery checkout HEAD mismatch")
    if git("status", "--porcelain"):
        raise RuntimeError("HOLD: gallery requires initially clean source and assets")
    for name in ("DefaultEngine.ini", "DefaultInput.ini"):
        if not (project / "Config" / name).is_file():
            raise RuntimeError("HOLD: protected Unreal config missing: " + name)
    if (project / MAP_FILE).exists():
        raise RuntimeError("HOLD: destination already exists; refuse overwrite")
    saves = project / "Saved" / "SaveGames"
    if saves.is_dir() and any(saves.glob("*.sav")):
        raise RuntimeError("HOLD: existing SaveGames in this worktree")
    return project, expected.lower()


def enum_member(enum_type, canonical: str):
    token = canonical.replace("_", "").upper()
    matches = [getattr(enum_type, name) for name in dir(enum_type)
               if name.isupper() and name.replace("_", "") == token]
    if len(matches) != 1:
        raise RuntimeError("HOLD: native enemy enum mismatch: " + canonical)
    return matches[0]


def build_in_unreal() -> dict:
    """Runs inside UnrealEditor-Cmd with the compiled C++ actor available."""
    plan = validate_plan()
    import unreal

    project, expected_head = checked_sandbox(Path(unreal.Paths.project_dir()))
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):
        raise RuntimeError("HOLD: review gallery already in asset registry")
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: dirty Editor world cannot be discarded")

    editor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    enemy_class = unreal.load_class(None, NATIVE_CLASS)
    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if editor is None or enemy_class is None or cube is None:
        raise RuntimeError("HOLD: real native actor/Editor subsystem/engine mesh unavailable")
    enum_type = getattr(unreal, "TSTSSSliceEnemyKind", None)
    if enum_type is None:
        raise RuntimeError("HOLD: native enemy enum not reflected; build C++ module first")
    for item in ENEMIES:
        enum_member(enum_type, item[1])

    if not unreal.EditorAssetLibrary.does_directory_exist("/Game/TSTSS/Review"):
        unreal.EditorAssetLibrary.make_directory("/Game/TSTSS/Review")
    world = unreal.EditorLoadingAndSavingUtils.new_blank_map(False)
    if world is None:
        raise RuntimeError("HOLD: Unreal could not create blank review map")

    def spawn(cls, name, pos, rotation=None):
        value = editor.spawn_actor_from_class(
            cls, unreal.Vector(*pos),
            rotation or unreal.Rotator(pitch=0, yaw=0, roll=0))
        if value is None:
            raise RuntimeError("HOLD: failed to spawn review geometry " + name)
        value.set_actor_label(ACTOR_PREFIX + name)
        return value

    def cube_actor(name, pos, scale):
        actor = spawn(unreal.StaticMeshActor, name, pos)
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        if component is None:
            raise RuntimeError("HOLD: review stage cube component missing")
        component.set_static_mesh(cube)
        actor.set_actor_scale3d(unreal.Vector(*scale))
        component.set_collision_profile_name("NoCollision")
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        return actor

    # Stage + individual plinths; source C++ enemy geometry remains the only
    # source for silhouettes. Level has no player input, monster spawning, or
    # automatic encounter initiation.
    cube_actor("NEUTRAL_STAGE", (0,1700,-80), (22.0,46.0,0.6))
    for name, kind, x, y, caption in ENEMIES:
        cube_actor("PLINTH_"+name, (x,y,-24), (3.3,3.2,.32))
        creature = spawn(enemy_class, name, (x,y,0))
        creature.set_editor_property("kind", enum_member(enum_type, kind))
        creature.set_editor_property("instance_id", unreal.Name(name))
        creature.set_editor_property("reduced_motion", True)
        creature.refresh_review_geometry()
        creature.set_editor_property("tags",
                                     [unreal.Name("TSTSSReviewOnly"),
                                      unreal.Name("StoryPlacementNotApproved")])
        sign = spawn(unreal.TextRenderActor, "CAPTION_"+name, (x,y,315),
                     unreal.Rotator(pitch=0, yaw=-90, roll=0))
        text = sign.get_component_by_class(unreal.TextRenderComponent)
        if text is None:
            raise RuntimeError("HOLD: source gallery text component unavailable")
        text.set_text(caption)
        text.set_editor_property("world_size", 27.0)

    # Deliberate three-quarter lighting for silhouette/scale inspection.
    sun = spawn(unreal.DirectionalLight, "KEY_LIGHT", (300,-550,800),
                unreal.Rotator(pitch=-45, yaw=22, roll=0))
    sun_comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
    if sun_comp is None:
        raise RuntimeError("HOLD: key light missing")
    sun_comp.set_editor_property("intensity", 3.5)
    fill = spawn(unreal.PointLight, "COOL_FILL", (-250,0,420))
    fill_comp = fill.get_component_by_class(unreal.PointLightComponent)
    if fill_comp is None:
        raise RuntimeError("HOLD: fill light missing")
    fill_comp.set_editor_property("intensity", 2200.0)
    fill_comp.set_editor_property("attenuation_radius", 1350.0)
    fill_comp.set_editor_property("light_color", unreal.LinearColor(.17,.58,1.0,1.0))
    # Five per-family camera presets. Gallery is staged, never entered as a
    # narrative encounter; camera placement does not select playable party.
    for family, y in GALLERY_FAMILIES:
        category = spawn(unreal.TextRenderActor,
                         "FAMILY_"+family, (-770,y,360),
                         unreal.Rotator(pitch=0,yaw=-90,roll=0))
        label = category.get_component_by_class(unreal.TextRenderComponent)
        if label is None:
            raise RuntimeError("HOLD: gallery family label unavailable")
        label.set_text(family.upper() + " / PROVISIONAL REVIEW")
        label.set_editor_property("world_size", 32.0)
        view = spawn(unreal.CameraActor, "CAMERA_"+family,
                     (0,y-1450,480),
                     unreal.Rotator(pitch=-12,yaw=90,roll=0))
        lens = view.get_component_by_class(unreal.CameraComponent)
        if lens is None:
            raise RuntimeError("HOLD: gallery family camera unavailable")
        lens.set_editor_property("field_of_view", 58.0)
        side = spawn(unreal.PointLight,"FILL_"+family,(0,y-220,380))
        light = side.get_component_by_class(unreal.PointLightComponent)
        if light is None:
            raise RuntimeError("HOLD: gallery lighting component unavailable")
        light.set_editor_property("intensity",1600.0)
        light.set_editor_property("attenuation_radius",950.0)

    enemy_actors = [a for a in editor.get_all_level_actors()
                    if str(a.get_actor_label()).startswith(ACTOR_PREFIX)
                    and a.get_class() == enemy_class]
    if len(enemy_actors) != 15:
        raise RuntimeError("HOLD: gallery does not contain all fifteen native enemy actors")
    if not unreal.EditorLoadingAndSavingUtils.save_map(world, MAP):
        raise RuntimeError("HOLD: native gallery failed to save")
    output = project / MAP_FILE
    if not output.is_file():
        raise RuntimeError("HOLD: gallery map not materialized")
    receipt = project / "Saved" / "EnemyGalleryV0" / "gallery-receipt.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    result = dict(plan,
                  status="GALLERY_MAP_SAVED_NOT_PIE_OR_VISUAL_QA",
                  exact_source_sha=expected_head,
                  generated_map_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
    with receipt.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2)
        f.write("\n")
    unreal.log("TSTSS_ENEMY_GALLERY_MAP_SAVED_NOT_PIE " + str(output))
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate",action="store_true")
    group.add_argument("--build",action="store_true")
    args=parser.parse_args(argv)
    print(json.dumps(build_in_unreal() if args.build else validate_plan(),indent=2))


if __name__ == "__main__":
    main()
