"""Independent, read-only native review of the combined First Wake shore.

This script is intentionally distinct from the scene author. It verifies a
previously-created scene and its receipt; it NEVER creates actors or grants any
skills/equipment, gameplay outcomes, narrative advancement or art approval.

Source-only CLI: python verify_first_wake_multipath_shore.py --plan
Native execution: only in separate disposable UE 5.8.4 review process, after
the staged scene has passed exact-head 35-test admission and is saved.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import stage_first_wake_multipath_shore as stage

PROJECT = stage.PROJECT
DEST_FILE = PROJECT / "Content/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review.umap"
NATIVE_RECEIPT = stage.SAVED_RECEIPT
READBACK = PROJECT / "Saved/MultipathV1/shore_independent_readback.json"

def sha256(file: Path) -> str:
    return hashlib.sha256(file.read_bytes()).hexdigest()

def expected_labels() -> dict[str, str]:
    spells = stage.legacy_magic_preview_rows()
    labels = {"CoastalAtmosphere":"TSTSSAtmosphereDirector",
              "Overview_NotGameplayCamera":"CameraActor",
              "UnapprovedVisualsNotice":"TextRenderActor"}
    labels.update({("OriginalProp_" + name): "StaticMeshActor" for name in stage.REVIEW_OBJECTS})
    labels.update({("StaticGear_NotEquipped_" + name.replace(".", "_")): "StaticMeshActor"
                   for name in stage.GEAR_SHOWCASE})
    labels.update({("EnemyVisual_NoEncounter_" + name): "TSTSSSliceEnemyActor"
                   for name in stage.ENEMY_KINDS})
    labels.update({("NoAuthorizedCast_" + row["SkillId"]): "TSTSSResonatorVfxActor"
                   for row in spells})
    if len(labels) != 26:
        raise RuntimeError("HOLD: expected actor map does not contain 26 distinct review actors")
    return {stage.PREFIX + key: value for key, value in labels.items()}

def source_plan() -> dict:
    plan = stage.evidence_plan()
    if plan["native_staged"] or plan["visual_approved"] or plan["PIE_verified"]:
        raise RuntimeError("HOLD: source plan cannot pre-claim native/visual authority")
    labels = expected_labels()
    if len(labels) != plan["total_new_review_actors"]:
        raise RuntimeError("HOLD: review actor source count drift")
    return {"schema":"tstss.shore.independent-readback.v1",
            "source_map":stage.SOURCE_PACKAGE,
            "destination_map":stage.DEST_MAP,
            "expected_labels":labels,
            "expected_additional_actor_count":26,
            "native_scene_loaded":False,
            "pie_verified":False,
            "visual_approved":False}

def validate_native_receipt(expected_head: str) -> dict:
    if not expected_head or len(expected_head) != 40 or any(c not in "0123456789abcdef" for c in expected_head):
        raise RuntimeError("HOLD: full exact Git head required")
    if READBACK.exists():
        raise RuntimeError("HOLD: independent readback output already exists; never overwrite")
    if not NATIVE_RECEIPT.is_file() or not DEST_FILE.is_file():
        raise RuntimeError("HOLD: native shore map/stage receipt absent")
    data = json.loads(NATIVE_RECEIPT.read_text(encoding="utf-8"))
    if (data.get("status") != "NATIVE_REVIEW_MAP_SAVED_NOT_PIE_OR_VISUAL_APPROVED"
            or data.get("source_head") != expected_head
            or data.get("native_staged") is not True
            or data.get("PIE_verified") is not False
            or data.get("visual_approved") is not False):
        raise RuntimeError("HOLD: no exact-head review-only native staging evidence")
    if data.get("new_map_sha256") != sha256(DEST_FILE):
        raise RuntimeError("HOLD: authored map digest differs from stage receipt")
    if data.get("source_sha256") != sha256(stage.MAP_FILE):
        raise RuntimeError("HOLD: original source shore map changed")
    if data.get("new_unique_review_actors") != 26:
        raise RuntimeError("HOLD: staging actor-count evidence differs")
    removed = data.get("removed_duplicate_only_environment_actors")
    if not isinstance(removed, list) or not set(
        ("TSTSS_VS_REVIEW_SunKey", "TSTSS_VS_REVIEW_SkyAmbient")
    ).issubset(set(removed)) or not set(removed).issubset(set(stage.LEGACY_ENV_LABELS)):
        raise RuntimeError("HOLD: replaced base lighting/sky identity drift")
    if data.get("saved_actor_count") != 21 - len(removed) + 26:
        raise RuntimeError("HOLD: total staged actor count inconsistent")
    return data

def native_readback() -> dict:
    import re
    import unreal as ue
    head = os.environ.get("TSTSS_MP_EXPECTED_HEAD", "").lower()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise RuntimeError("HOLD: inherited exact-head custody missing")
    if os.environ.get("TSTSS_MP_INDEPENDENT_REVIEW") != "1":
        raise RuntimeError("HOLD: independent review must be explicitly invoked")
    if stage.ROOT.name != stage.WORKTREE or stage.git("rev-parse", "HEAD") != head:
        raise RuntimeError("HOLD: wrong source worktree or head")
    # Native review assets are necessarily untracked until separately accepted.
    # Source/config edits and arbitrary untracked files are still fail-closed.
    stage.assert_source_custody_for_phase("compose")
    if not ue.SystemLibrary.get_engine_version().startswith("5.8.4"):
        raise RuntimeError("HOLD: exact native UE version mismatch")
    receipt = validate_native_receipt(head)
    if not ue.EditorAssetLibrary.does_asset_exist(stage.DEST_MAP):
        raise RuntimeError("HOLD: native review package unavailable")
    world = ue.EditorLoadingAndSavingUtils.load_map(stage.DEST_MAP)
    if world is None:
        raise RuntimeError("HOLD: native saved level cannot be reopened")
    subsystem = ue.get_editor_subsystem(ue.EditorActorSubsystem)
    actors = subsystem.get_all_level_actors()
    all_labels = [actor.get_actor_label() for actor in actors]
    if len(all_labels) != len(set(all_labels)):
        raise RuntimeError("HOLD: duplicate actor labels in saved review world")
    if len(actors) != receipt["saved_actor_count"]:
        raise RuntimeError("HOLD: native actor count differs from stage receipt")
    labeled = {a.get_actor_label(): a for a in actors}
    expected = expected_labels()
    if {label for label in labeled if label.startswith(stage.PREFIX)} != set(expected):
        raise RuntimeError("HOLD: missing/extra native review actor")
    for label, expected_class in expected.items():
        actor = labeled[label]
        real_class = actor.get_class().get_name()
        if real_class != expected_class:
            raise RuntimeError("HOLD: spawned actor class mismatch " + label)
        if any(key in label for key in ("OriginalProp_", "StaticGear_NotEquipped_",
                                         "EnemyVisual_NoEncounter_", "NoAuthorizedCast_")):
            if actor.get_actor_enable_collision():
                raise RuntimeError("HOLD: review visual has unexpected collision: " + label)
    # Never infer gameplay, cast authorization, PIE, GPU rendering or art approval.
    result = {"schema":"tstss.shore.independent-readback.v1",
              "status":"NATIVE_EDITOR_MAP_REOPENED_SOURCE_LOCKED_NOT_PIE",
              "head":head,
              "map_sha256":sha256(DEST_FILE),
              "original_shore_map_sha256":sha256(stage.MAP_FILE),
              "map_path":stage.DEST_MAP,
              "native_actor_count":len(actors),
              "review_actor_count":len(expected),
              "classes":dict(sorted(expected.items())),
              "pie_verified":False,
              "gpu_render_verified":False,
              "creator_approved":False}
    if READBACK.exists():
        raise RuntimeError("HOLD: review receipt collision")
    READBACK.parent.mkdir(parents=True, exist_ok=True)
    with READBACK.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--native", action="store_true")
    args = parser.parse_args()
    print(json.dumps(source_plan() if args.plan else native_readback(), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
