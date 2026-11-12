"""Author exactly one disposable First Wake title level; never set project startup.
Native Unreal Editor Python only. Requires explicit opt-in and exact source head.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess

PACKAGE = "/Game/TSTSS/Review/Opening"
TITLE = PACKAGE + "/L_FirstWake_TitleReview"
PRELUDE = "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2"
MODE_CLASS = "/Script/ToSailTheStarrySky.TSTSSOpeningReviewMode"
OPT_IN = "AUTHOR_REVIEW_TITLE_MAP"


def stage() -> dict:
    import unreal as u

    project = Path(u.Paths.project_dir()).resolve()
    repo = project.parent
    expected = os.environ.get("TSTSS_TITLE_REVIEW_EXPECTED_HEAD", "")
    if repo.name != "TSTSS_DockOpening_20261111":
        raise RuntimeError("HOLD: wrong worktree")
    if os.environ.get("TSTSS_TITLE_REVIEW_OPT_IN") != OPT_IN:
        raise RuntimeError("HOLD: no explicit title authoring opt-in")
    if len(expected) != 40:
        raise RuntimeError("HOLD: missing exact commit pin")
    result = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=True)
    if result.stdout.strip() != expected:
        raise RuntimeError("HOLD: source head drift")
    dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                           capture_output=True, text=True, check=True)
    if dirty.stdout.strip():
        raise RuntimeError("HOLD: dirty review worktree")
    if not str(u.SystemLibrary.get_engine_version()).startswith("5.8.4"):
        raise RuntimeError("HOLD: engine version not 5.8.4")
    target = project / "Content/TSTSS/Review/Opening/L_FirstWake_TitleReview.umap"
    prelude = project / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"
    if not prelude.is_file() or target.exists() or u.EditorAssetLibrary.does_asset_exist(TITLE):
        raise RuntimeError("HOLD: missing prelude or existing review title")
    if u.EditorLoadingAndSavingUtils.get_dirty_map_packages() or \
       u.EditorLoadingAndSavingUtils.get_dirty_content_packages():
        raise RuntimeError("HOLD: dirty Editor packages")
    cls = u.load_class(None, MODE_CLASS)
    if not cls:
        raise RuntimeError("HOLD: compiled title GameMode unavailable")
    before = hashlib.sha256(prelude.read_bytes()).hexdigest()

    u.EditorAssetLibrary.make_directory(PACKAGE)
    if not u.EditorLevelLibrary.new_level(TITLE):
        raise RuntimeError("HOLD: failed to create title review world")
    subsystem = u.get_editor_subsystem(u.UnrealEditorSubsystem)
    world = subsystem.get_editor_world() if subsystem else None
    if not world:
        raise RuntimeError("HOLD: no editable title world")
    settings = world.get_world_settings()
    if not settings:
        raise RuntimeError("HOLD: no title WorldSettings")
    settings.set_editor_property("default_game_mode", cls)
    if settings.get_editor_property("default_game_mode") != cls:
        raise RuntimeError("HOLD: title GameMode override not retained")
    if not u.EditorLevelLibrary.save_current_level():
        raise RuntimeError("HOLD: title map save failed")
    if not target.is_file():
        raise RuntimeError("HOLD: native title .umap missing")
    if hashlib.sha256(prelude.read_bytes()).hexdigest() != before:
        raise RuntimeError("HOLD: source prelude map changed")

    receipt = {
        "schema": "tstss.firstwake.review_title.native.v1",
        "status": "NATIVE_TITLE_MAP_SAVED_NOT_PIE_OR_VISUALLY_APPROVED",
        "exact_head": expected,
        "engine": str(u.SystemLibrary.get_engine_version()),
        "target_map": TITLE,
        "game_mode": MODE_CLASS,
        "first_playable_prelude": PRELUDE,
        "prelude_sha256_unchanged": before,
        "title_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "title_bytes": target.stat().st_size,
        "start_map_config_changed": False,
        "native_clickthrough_tested": False,
        "pie_tested": False,
        "visual_approved": False,
        "merged": False,
    }
    out = project / "Saved/OpeningDockReview/title_native_authoring.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as fd:
        json.dump(receipt, fd, indent=2)
    u.log("TSTSS_TITLE_REVIEW_MAP_CREATED_NOT_PIE_VERIFIED " + receipt["title_sha256"])
    print(json.dumps(receipt, indent=2))
    return receipt


if __name__ == "__main__":
    stage()
