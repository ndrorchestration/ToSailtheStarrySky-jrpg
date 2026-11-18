"""One-shot, noncanonical UE5.8 Editor prep for Ender's playable PIE review.

Creates ONLY two previously absent, Git-ignored review assets: a private
GameMode Blueprint and private cloned V5 level with the same basename. The
latter is important: the existing C++ player gate refuses renamed scenes.
This script NEVER starts PIE, changes project GameMode, or writes source levels.
Requires a separate guarded host with explicit local opt-in and custody checks.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import traceback

import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parent
PROJECT = ROOT / "unreal"
BASE_HEAD = "c4576432e3025993190d6a126e7198725368c007"
PRIVATE = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
PRIVATE_BP = PRIVATE + "/BP_EnderLocomotionPreview_NONCANONICAL"
PRIVATE_GAMEMODE = PRIVATE + "/BP_EnderPIEGameMode_NONCANONICAL"
NAME = "FirstWake_PreludeInteraction_V5_VisualReview"
SOURCE_LEVEL = "/Game/TSTSS/Review/" + NAME
PRIVATE_LEVEL = PRIVATE + "/" + NAME
PRIVATE_DIR = PROJECT / "Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
SOURCE_LEVEL_FILE = PROJECT / "Content/TSTSS/Review" / (NAME + ".umap")
SOURCE_BP_FILE = PROJECT / "Content/TSTSS/Review/Characters/EnderSliceVisualV1_NONCANONICAL/BP_EnderSlice_PIEReview.uasset"
STAGED_BP_FILE = PRIVATE_DIR / "BP_EnderLocomotionPreview_NONCANONICAL.uasset"
GAMEMODE_FILE = PRIVATE_DIR / "BP_EnderPIEGameMode_NONCANONICAL.uasset"
LEVEL_FILE = PRIVATE_DIR / (NAME + ".umap")
EVIDENCE = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate"
RECEIPT = EVIDENCE / "PIE_private_map_prepare_receipt.json"
REPORT = {
    "status": "NOT_STARTED", "source_head": None,
    "date_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "source_maps_saved": 0, "original_blueprint_modified": False,
    "actual_pie_started": False, "playback_verified": False,
    "art_approved": False, "production_approved": False,
}


def require(condition, token):
    if not condition:
        raise RuntimeError("HOLD_" + token)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args):
    result = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                            text=True, timeout=20, check=False)
    require(result.returncode == 0, "GIT")
    return result.stdout.strip()


def run():
    require(str(PROJECT).lower() == r"c:\tstss_civicintegration_20261116\unreal", "PROJECT")
    require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"), "ENGINE")
    require(os.getenv("TSTSS_PRIVATE_ENDER_PIE_MAP") == "1", "EXPLICIT_OPT_IN")
    current = git("rev-parse", "HEAD")
    require(len(current) == 40 and all(c in "0123456789abcdef" for c in current),
            "INVALID_HEAD")
    REPORT["source_head"] = current
    ancestor = subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor",
                               BASE_HEAD, current], capture_output=True, timeout=20)
    require(ancestor.returncode == 0, "NATIVE_ANCESTOR_NOT_PRESENT")
    require(not git("status", "--porcelain=v1"), "DIRTY_WORKTREE")
    # Rebuild on THIS head before asset writes. An ancestor's successful native
    # C++/automation report is not evidence for source-changed review code.
    native_root = PROJECT / "Saved/MigrationEvidence"
    accepted = False
    for path in native_root.glob(current[:12] + "-*/verified-native.json"):
        report_path = path.parent / "AutomationReport/index.json"
        if not report_path.is_file():
            continue
        receipt = json.loads(path.read_text(encoding="utf-8-sig"))
        tests = json.loads(report_path.read_text(encoding="utf-8-sig"))
        entries = tests.get("tests")
        if (receipt.get("status") == "WIN64_EDITOR_BUILD_AND_NATIVE_AUTOMATIONS_PASS_CLEAN_SOURCE"
            and receipt.get("source_sha") == current and receipt.get("required_native_tests") == 38
            and receipt.get("unreal_version") == "5.8.4"
            and receipt.get("report_sha256") == sha(report_path)
            and (tests.get("succeeded"), tests.get("failed"), tests.get("notRun")) == (38, 0, 0)
            and isinstance(entries, list) and len(entries) == 38
            and len({x.get("fullTestPath") for x in entries if isinstance(x, dict)}) == 38
            and all(isinstance(x, dict) and x.get("state") == "Success" for x in entries)):
            accepted = True
            REPORT["exact_head_native_receipt"] = str(path)
            break
    require(accepted, "EXACT_HEAD_NATIVE_38_EVIDENCE_MISSING")
    require(git("branch", "--show-current").startswith("review/ender"), "REVIEW_BRANCH")
    require(not RECEIPT.exists(), "RECEIPT_EXISTS")
    require(SOURCE_LEVEL_FILE.is_file() and SOURCE_BP_FILE.is_file() and
            STAGED_BP_FILE.is_file(), "INPUT_ASSET_MISSING")
    for package, dest in ((PRIVATE_GAMEMODE, GAMEMODE_FILE),
                          (PRIVATE_LEVEL, LEVEL_FILE)):
        require(not dest.exists() and not unreal.EditorAssetLibrary.does_asset_exist(package),
                "PRIVATE_OUTPUT_EXISTS")
        rel = "unreal/" + str(dest.relative_to(PROJECT)).replace("\\", "/")
        check = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", rel],
                               timeout=20, check=False)
        require(check.returncode == 0, "OUTPUT_NOT_GIT_EXCLUDED")
    # The native-created opt-in BP must remain unchanged, with the exact
    # three expected private skeleton clips and NONE of the public content.
    prior = json.loads((EVIDENCE / "BP_EnderLocomotion_20261118_stage_receipt.json").read_text(encoding="utf8"))
    require(prior.get("status") == "PRIVATE_BP_CLIP_TRIPLET_STAGED_REVIEW_ONLY_NOT_PIE_VERIFIED" and
            prior.get("source_head") == BASE_HEAD and
            prior.get("private_clone_sha256") == sha(STAGED_BP_FILE), "BP_CUSTODY")
    protected = (PROJECT / "ToSailTheStarrySky.uproject",
                 PROJECT / "Config/DefaultEngine.ini",
                 PROJECT / "Config/DefaultInput.ini")
    require(all(p.is_file() for p in protected), "PROTECTED_FILES_MISSING")
    guarded = (SOURCE_LEVEL_FILE, SOURCE_BP_FILE, STAGED_BP_FILE, *protected)
    original = {str(p): sha(p) for p in guarded}
    REPORT["original_hashes_before"] = original
    clone_class = unreal.EditorAssetLibrary.load_blueprint_class(PRIVATE_BP)
    require(clone_class, "PRIVATE_PLAYER_CLASS")
    cdo = unreal.get_default_object(clone_class)
    require(cdo and cdo.get_editor_property("enable_ender_pie_locomotion_preview") and
            cdo.get_editor_property("allow_ender_pie_root_motion_extraction_review") and
            cdo.get_editor_property("enable_ender_pie_walk_run_controls"), "PRIVATE_OPT_INS")
    for prop, clip in (("ender_pie_idle_animation", "MM_Idle"),
                       ("ender_pie_walk_animation", "MF_Unarmed_Walk_Fwd"),
                       ("ender_pie_run_animation", "MF_Unarmed_Jog_Fwd")):
        path = str(cdo.get_editor_property(prop))
        require(path.find("EnderRetarget_NONCANONICAL") >= 0 and
                clip in path, "PRIVATE_CLIP_NOT_BOUND")
    gamemode_base = unreal.load_class(None, "/Script/ToSailTheStarrySky.TSTSSGameMode")
    require(gamemode_base, "GAME_MODE_CXX_CLASS")
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", gamemode_base)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mode = tools.create_asset("BP_EnderPIEGameMode_NONCANONICAL", PRIVATE,
                              unreal.Blueprint, factory)
    require(isinstance(mode, unreal.Blueprint), "PRIVATE_MODE_FACTORY")
    mode_class = unreal.EditorAssetLibrary.load_blueprint_class(PRIVATE_GAMEMODE)
    require(mode_class, "PRIVATE_MODE_CLASS")
    game_cdo = unreal.get_default_object(mode_class)
    game_cdo.set_editor_property("default_pawn_class", clone_class)
    require(game_cdo.get_editor_property("default_pawn_class") == clone_class,
            "PRIVATE_PAWN_BINDING")
    require(unreal.EditorAssetLibrary.save_loaded_asset(mode, only_if_is_dirty=False),
            "PRIVATE_MODE_SAVE")
    subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(subsystem and not subsystem.is_in_play_in_editor(), "EDITOR_NOT_IDLE")
    # UE 5.8 template API clones the map into a new package and loads it.
    # The NEW map has the original basename, satisfying gated C++ scene checks.
    require(subsystem.new_level_from_template(PRIVATE_LEVEL, SOURCE_LEVEL),
            "PRIVATE_TEMPLATE_LEVEL_CREATION")
    editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor.get_editor_world() if editor else None
    require(world and world.get_outermost().get_name() == PRIVATE_LEVEL,
            "WRONG_EDITOR_WORLD_AFTER_CLONE")
    settings = world.get_world_settings()
    require(settings and settings.get_outermost().get_name() == PRIVATE_LEVEL,
            "WRONG_WORLD_SETTINGS_PACKAGE")
    settings.set_editor_property("default_game_mode", mode_class)
    require(settings.get_editor_property("default_game_mode") == mode_class,
            "PRIVATE_GAME_MODE_OVERRIDE")
    # Only the currently loaded private clone is allowed to be saved.
    require(world.get_outermost().get_name() == PRIVATE_LEVEL and
            subsystem.save_current_level(), "PRIVATE_MAP_SAVE")
    require(LEVEL_FILE.is_file() and GAMEMODE_FILE.is_file(),
            "PRIVATE_FILES_MISSING")
    REPORT["original_hashes_after"] = {str(p): sha(p) for p in guarded}
    require(REPORT["original_hashes_after"] == original, "SOURCE_MAP_OR_BP_CHANGED")
    REPORT["private_outputs_sha256"] = {str(p): sha(p) for p in (GAMEMODE_FILE, LEVEL_FILE)}
    REPORT["source_maps_saved"] = 0
    REPORT["status"] = "PRIVATE_V5_PIE_REVIEW_LEVEL_STAGED_NOT_PLAYED"


try:
    run()
except BaseException:
    REPORT["status"] = "HOLD_PRIVATE_PIE_MAP_PREPARATION"
    REPORT["error"] = traceback.format_exc()[-3800:]
finally:
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(REPORT, indent=2, sort_keys=True), encoding="utf8")
    unreal.log("TSTSS_ENDER_PRIVATE_PIE_MAP_" + REPORT["status"])
    unreal.SystemLibrary.quit_editor()
