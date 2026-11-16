#!/usr/bin/env python3
"""Create a NEW hybrid walking-to-battle review map without editing V0 or V1.

This is a deliberately separate prototype; it proves encounter flow mechanics
without claiming that any TSTSS story biome, enemy placement or loot is canon.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT_NAME = "TSTSS-Slice-Enemies-20261110"
BASE_PACKAGE = "/Game/TSTSS/Review/SliceEnemyCombatSandbox_V1"
BASE_FILE = "Content/TSTSS/Review/SliceEnemyCombatSandbox_V1.umap"
BASE_HASH = "108c7582ef8f8073907fbd9d78bd7f487a98b5fb6df927335fadb0fb500f4250"
ORIGINAL_GALLERY = "Content/TSTSS/Review/SliceEnemyGallery_V0.umap"
GALLERY_HASH = "deb70ffeecedf572c8bd5b2fab3a515e748d95d27fb2d31f8c0bef2f34c0a022"
NEW_PACKAGE = "/Game/TSTSS/Review/JRPGHybridEncounterReview_V2"
NEW_FILE = "Content/TSTSS/Review/JRPGHybridEncounterReview_V2.umap"
EXPLORER_CLASS = "/Script/ToSailTheStarrySky.TSTSSJRPGEncounterFieldReview"
CONSOLE_CLASS = "/Script/ToSailTheStarrySky.TSTSSSliceEnemyReviewBattleConsole"
SOURCE_HEAD_ENV = "TSTSS_JRPG_HYBRID_EXPECTED_HEAD"
RECEIPT_FILE = "Saved/EnemyGalleryV2/hybrid-receipt.json"
EXPLORER_LABEL = "TSTSS_REVIEW_HYBRID_WALKING_EXPLORER"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan() -> dict:
    if BASE_FILE == NEW_FILE or BASE_PACKAGE == NEW_PACKAGE:
        raise RuntimeError("HOLD: cannot overwrite parent map")
    if (not NEW_PACKAGE.startswith("/Game/TSTSS/Review/")
            or ".." in Path(NEW_FILE).parts or Path(NEW_FILE).is_absolute()):
        raise RuntimeError("HOLD: escape from disposable review namespace")
    if any(not re.fullmatch("[0-9a-f]{64}",x)
           for x in (BASE_HASH,GALLERY_HASH)):
        raise RuntimeError("HOLD: source map digest missing")
    return {
        "status":"PLAN_ONLY_NOT_NATIVE_OR_PIE",
        "source_map":BASE_PACKAGE,
        "target_map":NEW_PACKAGE,
        "original_gallery_preserved":True,
        "combat_map_preserved":True,
        "walking_actor":EXPLORER_CLASS,
        "encounter_biomes":["HarborOutskirts","Woodland","Coast","Highlands"],
        "context_requirements":"traversal, area, party, no safe/story/ship lock",
        "controls":"WASD walk; 1/2/3 party; P rate; V biome; F2 scripted review; Enter return; battle J/K",
        "random_min_distance_cm":1800,
        "random_guaranteed_by_cm":5700,
        "world_story_enemy_placement_approved":False,
        "pie_controls_tested":False,
        "gpu_visual_qa_tested":False,
        "save_or_rewards_modified":False,
    }


def checked_project(project_dir: Path) -> tuple[Path,str]:
    project=project_dir.resolve()
    repo=project.parent
    if repo.name != ROOT_NAME or project.name.lower() != "unreal":
        raise RuntimeError("HOLD: wrong isolated enemy review worktree")
    expected=os.environ.get(SOURCE_HEAD_ENV,"")
    if not re.fullmatch("[0-9a-fA-F]{40}",expected):
        raise RuntimeError("HOLD: full exact Git HEAD required")
    def git(*args):
        result=subprocess.run(["git","-C",str(repo),*args],
            capture_output=True,text=True,check=False,timeout=30)
        if result.returncode:
            raise RuntimeError("HOLD: git custody unavailable")
        return result.stdout.strip()
    if git("rev-parse","HEAD").lower()!=expected.lower():
        raise RuntimeError("HOLD: source HEAD drift")
    if git("status","--porcelain"):
        raise RuntimeError("HOLD: dirty review worktree")
    if not (project/BASE_FILE).is_file() or digest(project/BASE_FILE)!=BASE_HASH:
        raise RuntimeError("HOLD: native-verified V1 map changed")
    if not (project/ORIGINAL_GALLERY).is_file() or digest(project/ORIGINAL_GALLERY)!=GALLERY_HASH:
        raise RuntimeError("HOLD: original 15-actor gallery changed")
    if (project/NEW_FILE).exists():
        raise RuntimeError("HOLD: refuse existing V2 map overwrite")
    if (project/RECEIPT_FILE).exists():
        raise RuntimeError("HOLD: refuse existing receipt overwrite")
    return project,expected.lower()


def build() -> dict:
    result=plan()
    import unreal
    project,head=checked_project(Path(unreal.Paths.project_dir()))
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: dirty editor maps")
    if unreal.EditorAssetLibrary.does_asset_exist(NEW_PACKAGE):
        raise RuntimeError("HOLD: V2 package already exists")
    explorer_class=unreal.load_class(None,EXPLORER_CLASS)
    console_class=unreal.load_class(None,CONSOLE_CLASS)
    if explorer_class is None or console_class is None:
        raise RuntimeError("HOLD: compiled C++ encounter classes missing")
    world=unreal.EditorLoadingAndSavingUtils.load_map(BASE_PACKAGE)
    if world is None:
        raise RuntimeError("HOLD: cannot load source V1")
    editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if editor is None:
        raise RuntimeError("HOLD: no editor actor subsystem")
    actors=editor.get_all_level_actors()
    if len([a for a in actors if a.get_class().get_name()=="TSTSSSliceEnemyActor"])!=15:
        raise RuntimeError("HOLD: expected native 15-foe V1 composition")
    if len([a for a in actors if a.get_class()==console_class])!=1:
        raise RuntimeError("HOLD: expected exact one native battle console")
    if any(str(a.get_actor_label())==EXPLORER_LABEL for a in actors):
        raise RuntimeError("HOLD: V2 explorer already present")
    explorer=editor.spawn_actor_from_class(explorer_class,
        unreal.Vector(3500.,850.,0.),unreal.Rotator(pitch=0.,yaw=0.,roll=0.))
    if explorer is None:
        raise RuntimeError("HOLD: cannot create encounter walker")
    explorer.set_actor_label(EXPLORER_LABEL)
    explorer.set_editor_property("enable_review_traversal",True)
    explorer.set_editor_property("tags",[
        unreal.Name("TSTSSReviewOnly"),
        unreal.Name("NoStoryEnemyPlacement"),
        unreal.Name("NoSaveGame"),
        unreal.Name("NoWorldTravel")])

    shape=unreal.load_asset("/Engine/BasicShapes/Cube")
    if shape is None:
        raise RuntimeError("HOLD: engine floor mesh unavailable")
    stage=editor.spawn_actor_from_class(unreal.StaticMeshActor,
        unreal.Vector(5500.,850.,-20.),unreal.Rotator(pitch=0.,yaw=0.,roll=0.))
    if stage is None:
        raise RuntimeError("HOLD: no field platform")
    stage.set_actor_label("REVIEW_ONLY_ENCOUNTER_FIELD_PLATFORM")
    mesh=stage.get_component_by_class(unreal.StaticMeshComponent)
    if mesh is None:
        raise RuntimeError("HOLD: no field mesh component")
    mesh.set_editor_property("static_mesh",shape)
    stage.set_actor_scale3d(unreal.Vector(90.,36.,.4))

    # Visualize the no-random-encounter camp and its threshold.
    safe=editor.spawn_actor_from_class(unreal.StaticMeshActor,
        unreal.Vector(3500.,850.,-5.),unreal.Rotator(pitch=0.,yaw=0.,roll=0.))
    if safe is None:
        raise RuntimeError("HOLD: no safe camp disk")
    safe.set_actor_label("REVIEW_ONLY_SAFE_CAMP_VISUAL_MARKER")
    surface=safe.get_component_by_class(unreal.StaticMeshComponent)
    if surface is None:
        raise RuntimeError("HOLD: no safe disk mesh")
    surface.set_editor_property("static_mesh",shape)
    safe.set_actor_scale3d(unreal.Vector(12.8,12.8,.045))
    text=editor.spawn_actor_from_class(unreal.TextRenderActor,
        unreal.Vector(3500.,1550.,290.),
        unreal.Rotator(pitch=0.,yaw=180.,roll=0.))
    if text is None:
        raise RuntimeError("HOLD: cannot place safe camp label")
    text.set_actor_label("REVIEW_ONLY_SAFE_CAMP_SIGN")
    label=text.get_component_by_class(unreal.TextRenderComponent)
    if label is None:
        raise RuntimeError("HOLD: safe camp label component missing")
    label.set_text("SAFE CAMP / RANDOM ENCOUNTERS OFF WITHIN 6.5m")
    label.set_editor_property("world_size",38.)

    fresh=editor.get_all_level_actors()
    if len([a for a in fresh if a.get_class()==explorer_class])!=1:
        raise RuntimeError("HOLD: exactly one explorer required")
    if not unreal.EditorLoadingAndSavingUtils.save_map(world,NEW_PACKAGE):
        raise RuntimeError("HOLD: native V2 map save failed")
    if not (project/NEW_FILE).is_file():
        raise RuntimeError("HOLD: saved V2 .umap missing")
    if digest(project/BASE_FILE)!=BASE_HASH or digest(project/ORIGINAL_GALLERY)!=GALLERY_HASH:
        raise RuntimeError("HOLD: historical maps changed during authoring")
    result.update(status="NATIVE_HYBRID_MAP_SAVED_NOT_PIE",
        exact_head=head,
        map_sha256=digest(project/NEW_FILE),
        native_enemy_count=15,native_battle_consoles=1,
        native_walk_explorers=1,
        native_safe_zone_markers=1)
    receipt=project/RECEIPT_FILE
    receipt.parent.mkdir(parents=True,exist_ok=True)
    with receipt.open("x",encoding="utf-8") as handle:
        json.dump(result,handle,indent=2)
        handle.write("\n")
    unreal.log("TSTSS_NATIVE_HYBRID_REVIEW_MAP_SAVED_NOT_PIE "+result["map_sha256"])
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate",action="store_true")
    group.add_argument("--build",action="store_true")
    args=parser.parse_args(argv)
    print(json.dumps(build() if args.build else plan(),indent=2))


if __name__=="__main__":
    main()
