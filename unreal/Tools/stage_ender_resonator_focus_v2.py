#!/usr/bin/env python3
"""Create a new, isolated focus arena V2 from the SHA-locked original review.

Never replaces the original V1 native review map or changes campaign game mode,
world settings/config, storyline assets, or save games. C++ focus GameMode and
review actor must first compile in real UE5.8.4 Win64 Editor.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT/"unreal"
V1="/Game/TSTSS/Review/ResonatorFocus/L_EnderCenteringPulseReview"
V2="/Game/TSTSS/Review/ResonatorFocus/L_EnderCenteringPulseReview_V2"
V1_FILE=PROJECT/"Content/TSTSS/Review/ResonatorFocus/L_EnderCenteringPulseReview.umap"
V2_FILE=PROJECT/"Content/TSTSS/Review/ResonatorFocus/L_EnderCenteringPulseReview_V2.umap"
MANIFEST=PROJECT/"Docs/Evidence/ender_resonator_focus_native_assets_20261111.json"
EXPECTED_ENV="TSTSS_FOCUS_V2_EXACT_HEAD"
EXPLICIT_ENV="TSTSS_FOCUS_V2_AUTHORIZE"
STATUS="FOCUS_V2_NATIVE_MAP_SAVE_AS_NOT_PIE_VERIFIED"

def git(*args):
    result=subprocess.run(["git","-C",str(ROOT),*args],
       check=True,capture_output=True,text=True,timeout=30)
    return result.stdout.strip()

def preflight(project=PROJECT):
    project=Path(project).resolve()
    if project.name!="unreal" or project.parent.name!="TSTSS_CenteringPulse_20261111":
        raise RuntimeError("HOLD: isolated dedicated review worktree only")
    head=os.environ.get(EXPECTED_ENV,"")
    if not re.fullmatch("[a-f0-9]{40}",head):
        raise RuntimeError("HOLD: exact expected source commit required")
    if os.environ.get(EXPLICIT_ENV)!="1":
        raise RuntimeError("HOLD: native V2 authoring not explicitly authorized")
    if git("rev-parse","HEAD")!=head or git("status","--porcelain","-uall"):
        raise RuntimeError("HOLD: changed or dirty source")
    source=json.loads(MANIFEST.read_text(encoding="utf8"))
    pin=source["assets"]["L_EnderCenteringPulseReview.umap"]
    if hashlib.sha256(V1_FILE.read_bytes()).hexdigest()!=pin:
        raise RuntimeError("HOLD: original native review map hash drift")
    if V2_FILE.exists():
        raise RuntimeError("HOLD: V2 map already exists; never overwrite")
    return head,pin

def create():
    import unreal as u
    head,pin=preflight()
    if not u.SystemLibrary.get_engine_version().startswith("5.8.4"):
        raise RuntimeError("HOLD: needs native UE 5.8.4")
    if u.EditorAssetLibrary.does_asset_exist(V2):
        raise RuntimeError("HOLD: V2 Unreal asset already exists")
    if (u.EditorLoadingAndSavingUtils.get_dirty_map_packages() or
        u.EditorLoadingAndSavingUtils.get_dirty_content_packages()):
        raise RuntimeError("HOLD: unsaved editor content")
    cls=u.load_class(None,"/Script/ToSailTheStarrySky.TSTSSResonatorFocusGameMode")
    if cls is None:
        raise RuntimeError("HOLD: dedicated compiled review GameMode missing")
    world=u.EditorLoadingAndSavingUtils.load_map(V1)
    if world is None:
        raise RuntimeError("HOLD: original native review map could not reopen")
    settings=world.get_world_settings()
    if not settings:
        raise RuntimeError("HOLD: WorldSettings unavailable")
    before=settings.get_editor_property("default_game_mode")
    if before is not None and before==cls:
        raise RuntimeError("HOLD: original map unexpectedly already uses the V2 GameMode")
    settings.set_editor_property("default_game_mode",cls)
    if settings.get_editor_property("default_game_mode")!=cls:
        raise RuntimeError("HOLD: review GameMode override did not stick")
    # Save Map As re-homes the World to a new target. Do not duplicate a
    # UWorld via EditorAssetLibrary; prior TSTSS evidence warns of leaks.
    if not u.EditorLoadingAndSavingUtils.save_map(world,V2):
        raise RuntimeError("HOLD: review map Save As failed")
    if not V2_FILE.is_file():
        raise RuntimeError("HOLD: new V2 .umap not created")
    if hashlib.sha256(V1_FILE.read_bytes()).hexdigest()!=pin:
        raise RuntimeError("HOLD: source map mutated by Save As")
    receipt={
        "status":STATUS,
        "source_commit":head,
        "engine":"5.8.4",
        "source_v1_sha256":pin,
        "new_v2_sha256":hashlib.sha256(V2_FILE.read_bytes()).hexdigest(),
        "new_v2_bytes":V2_FILE.stat().st_size,
        "map":V2,
        "game_mode":"/Script/ToSailTheStarrySky.TSTSSResonatorFocusGameMode",
        "review_only":True,
        "player_input":"NOT_VERIFIED",
        "screen_render":"NOT_VERIFIED",
        "speaker_output":"NOT_VERIFIED",
        "main_merge_authorized":False
    }
    dest=PROJECT/"Saved/ResonatorFocus/focus-v2-authoring.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("x",encoding="utf8") as stream:
        json.dump(receipt,stream,indent=2)
        stream.write("\n")
    u.log("TSTSS_FOCUS_V2_MAP_GAME_MODE_SAVED_NOT_PIE_VERIFIED")
    return receipt
if __name__=="__main__":create()
