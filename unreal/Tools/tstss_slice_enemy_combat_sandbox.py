#!/usr/bin/env python3
"""Stage a NEW disposable Unreal enemy battle map from verified native gallery.

--validate is portable and read-only. --build requires the exact native C++
editor build, exact source HEAD, clean enemy-review worktree and original map
digest. The existing gallery and all First Wake maps are never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT_NAME="TSTSS-Slice-Enemies-20261110"
BASE_PACKAGE="/Game/TSTSS/Review/SliceEnemyGallery_V0"
BASE_FILE="Content/TSTSS/Review/SliceEnemyGallery_V0.umap"
BASE_SHA256="deb70ffeecedf572c8bd5b2fab3a515e748d95d27fb2d31f8c0bef2f34c0a022"
TARGET_PACKAGE="/Game/TSTSS/Review/SliceEnemyCombatSandbox_V1"
TARGET_FILE="Content/TSTSS/Review/SliceEnemyCombatSandbox_V1.umap"
CONSOLE_CLASS="/Script/ToSailTheStarrySky.TSTSSSliceEnemyReviewBattleConsole"
EXPECTED_HEAD_ENV="TSTSS_ENEMY_COMBAT_EXPECTED_HEAD"
CONSOLE_LABEL="REVIEW_ONLY_ENEMY_COMBAT_BENCH"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate() -> dict:
    if BASE_PACKAGE == TARGET_PACKAGE or BASE_FILE == TARGET_FILE:
        raise RuntimeError("HOLD: no in-place alteration of existing gallery")
    if ".." in Path(TARGET_FILE).parts or Path(TARGET_FILE).is_absolute():
        raise RuntimeError("HOLD: map location cannot escape review folder")
    if not TARGET_PACKAGE.startswith("/Game/TSTSS/Review/"):
        raise RuntimeError("HOLD: sandbox cannot live in a narrative map")
    if not re.fullmatch("[0-9a-f]{64}",BASE_SHA256):
        raise RuntimeError("HOLD: original map receipt missing")
    return {
       "status": "SOURCE_PLAN_ONLY_NOT_PIE",
       "source_gallery":BASE_PACKAGE,
       "native_combat_review_map":TARGET_PACKAGE,
       "source_asset_sha256":BASE_SHA256,
       "console_actor_class":CONSOLE_CLASS,
       "keyboard_controls":"F7 Ender, F8 Ionia-recruited, F9 after-splashdown; J/K target",
       "default_wave":"Review_HarborBanditPatrol",
       "auto_story_encounter":False,
       "campaign_save_modified":False,
       "gpu_capture_verified":False,
       "pie_gameplay_verified":False,
    }


def checked_project(project_dir: Path) -> tuple[Path, str]:
    project=project_dir.resolve()
    repo=project.parent
    if project.name.lower() != "unreal" or repo.name != ROOT_NAME:
        raise RuntimeError("HOLD: exact dedicated enemy sandbox required")
    expected=os.environ.get(EXPECTED_HEAD_ENV,"")
    if not re.fullmatch("[0-9a-fA-F]{40}",expected):
        raise RuntimeError("HOLD: full expected Git HEAD required")
    def git(*args: str) -> str:
        result=subprocess.run(["git","-C",str(repo),*args],
            capture_output=True,text=True,check=False,timeout=30)
        if result.returncode:
            raise RuntimeError("HOLD: cannot establish source custody")
        return result.stdout.strip()
    if git("rev-parse","HEAD").lower()!=expected.lower():
        raise RuntimeError("HOLD: checkout HEAD changed")
    if git("status","--porcelain"):
        raise RuntimeError("HOLD: dirty worktree cannot be staged")
    if not (project/BASE_FILE).is_file():
        raise RuntimeError("HOLD: original source gallery missing")
    if sha256(project/BASE_FILE) != BASE_SHA256:
        raise RuntimeError("HOLD: original verified gallery SHA differs")
    if (project/TARGET_FILE).exists():
        raise RuntimeError("HOLD: sandbox map already exists: refuse overwrite")
    if (project/"Saved"/"EnemyGalleryV1"/"combat-receipt.json").exists():
        raise RuntimeError("HOLD: combat receipt exists: refuse overwrite")
    return project,expected.lower()


def build() -> dict:
    plan=validate()
    import unreal
    project,head=checked_project(Path(unreal.Paths.project_dir()))
    if unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
        raise RuntimeError("HOLD: editor has dirty maps")
    if unreal.EditorAssetLibrary.does_asset_exist(TARGET_PACKAGE):
        raise RuntimeError("HOLD: combat map already registered")
    actor_type=unreal.load_class(None,CONSOLE_CLASS)
    if actor_type is None:
        raise RuntimeError("HOLD: C++ console not compiled/reflected")
    world=unreal.EditorLoadingAndSavingUtils.load_map(BASE_PACKAGE)
    if world is None:
        raise RuntimeError("HOLD: cannot reload original verified gallery")
    editor=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if editor is None:
        raise RuntimeError("HOLD: no editor actor subsystem")

    foes=[a for a in editor.get_all_level_actors()
          if str(a.get_actor_label()).startswith("REVIEW_ONLY_ENEMY_")
          and a.get_class().get_name() == "TSTSSSliceEnemyActor"]
    if len(foes)!=15:
        raise RuntimeError("HOLD: original gallery has incorrect foe count")
    if any(str(a.get_actor_label())==CONSOLE_LABEL for a in editor.get_all_level_actors()):
        raise RuntimeError("HOLD: input console already exists")
    console=editor.spawn_actor_from_class(actor_type,
         unreal.Vector(0.0,850.0,0.0),unreal.Rotator(pitch=0,yaw=0,roll=0))
    if console is None:
        raise RuntimeError("HOLD: no native gameplay control actor")
    console.set_actor_label(CONSOLE_LABEL)
    console.set_editor_property("review_wave_preset",
                                 unreal.Name("Review_HarborBanditPatrol"))
    console.set_editor_property("tags",[
        unreal.Name("TSTSSReviewOnly"),
        unreal.Name("NotAuthorizedForFirstWake"),
        unreal.Name("NoCampaignSave")])

    created=[a for a in editor.get_all_level_actors()
             if str(a.get_actor_label())==CONSOLE_LABEL
             and a.get_class()==actor_type]
    if len(created)!=1:
        raise RuntimeError("HOLD: must stage exactly one battle console")
    if not unreal.EditorLoadingAndSavingUtils.save_map(world,TARGET_PACKAGE):
        raise RuntimeError("HOLD: review map could not save")
    target=project/TARGET_FILE
    if not target.is_file():
        raise RuntimeError("HOLD: no materialized .umap")
    if sha256(project/BASE_FILE)!=BASE_SHA256:
        raise RuntimeError("HOLD: original gallery modified by map copy")
    result=dict(plan,
       status="NATIVE_COMBAT_MAP_SAVED_NOT_PIE",
       exact_source_sha=head,
       target_map_sha256=sha256(target),
       native_foe_actors=15,
       battle_consoles=1)
    receipt=project/"Saved"/"EnemyGalleryV1"/"combat-receipt.json"
    receipt.parent.mkdir(parents=True,exist_ok=True)
    with receipt.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2)
        f.write("\n")
    unreal.log("TSTSS_ENEMY_COMBAT_MAP_SAVED_NOT_PIE "+result["target_map_sha256"])
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate",action="store_true")
    group.add_argument("--build",action="store_true")
    args=parser.parse_args(argv)
    print(json.dumps(build() if args.build else validate(),indent=2))


if __name__=="__main__":
    main()
