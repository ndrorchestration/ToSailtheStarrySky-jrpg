"""Native UE5.8.4 noncanonical Ender WALK directional clip retarget.

Requires exact-head host admission and pre-copied SHA-locked local Unreal
template clips. Creates only three new ignored private AnimationSequences.
No pawn ownership/AnimBP assignment, skin/spine correction, or game acceptance.
Never overwrite/delete existing assets or save scenes.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import traceback

import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
REPO = PROJECT.parent
ROOT = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
SOURCE = ROOT + "/MannequinWalkSources_PRIVATE"
OUTPUT = ROOT + "/DirectionalWalkV1_PRIVATE"
SUFFIX = "_EnderDirectionalV1_PRIVATE"
SOURCE_MESH = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
TARGET_MESH = ("/Game/ArtLookdev/Characters/"
               "Genesis9MergedFBXRigReview_20261109_NONCANONICAL/"
               "Genesis9_BaseShirtShorts_MergedRig_REVIEW")
RETARGETER = ROOT + "/RTG_MannyToEnder_NONCANONICAL"
TARGET_IDLE = ROOT + "/Animations/MM_Idle_EnderPreview_NONCANONICAL"
CLIPS = {
    "MF_Unarmed_Walk_Bwd": (606821, "ae0c2ee1c1178fd1b9493f6c327e52d10a3d6bbde29eae54dcb07c13a27dcf46"),
    "MF_Unarmed_Walk_Left": (486552, "81500e4fcdd9ae9aa6433e652e67dea8f9dd9fa7b9ef1714e29f6ab0a1bb9d97"),
    "MF_Unarmed_Walk_Right": (491934, "f5922b4e632351353224b32f719af97e85512ab4f6553b15315cf14ad04f675f"),
}
REPORT = {"status": "NOT_STARTED", "retarget_review_only": True,
          "character_assigned": False, "maps_saved": False,
          "spinefix_applied": False, "creator_approved": False,
          "native_playback_verified": False, "created": []}


def require(condition, label):
    if not condition:
        raise RuntimeError("HOLD_ENDER_DIRECTIONAL_" + label)


def git(*args):
    p = subprocess.run(["git", "-C", str(REPO), *args],
                       check=True, capture_output=True, text=True, timeout=20)
    return p.stdout.strip()


def admitted():
    head = os.getenv("TSTSS_DIRECTIONAL_EXPECTED_HEAD")
    receipt = os.getenv("TSTSS_DIRECTIONAL_RECEIPT")
    require(head and len(head) == 40 and git("rev-parse", "HEAD") == head,
            "WRONG_HEAD")
    # This editor writes exactly these two tracked defaults during startup.
    # The host independently verified a clean HEAD BEFORE launch and restores
    # only these paths AFTER exit. No other tracked or staged changes admitted.
    expected_editor_drift = {"unreal/Config/DefaultEngine.ini",
                             "unreal/Config/DefaultInput.ini"}
    drift = [line for line in git("status", "--porcelain").splitlines()
             if line]
    require(all(line.startswith(" M ") and line[3:] in expected_editor_drift
                for line in drift), "UNEXPECTED_SOURCE_DRIFT")
    require(os.getenv("TSTSS_PRIVATE_DIRECTIONAL_CREATE") == "1",
            "OPT_IN_MISSING")
    require(unreal.SystemLibrary.get_engine_version().startswith("5.8.4-"),
            "WRONG_ENGINE")
    path = Path(receipt).resolve() if receipt else None
    require(path is not None and
            (PROJECT / "Saved/MigrationEvidence").resolve() in path.parents and
            path.parent.is_dir() and path.name == "author-receipt.json" and
            not path.exists(), "RECEIPT_PATH")
    for name, (size, expected_hash) in CLIPS.items():
        relative = "unreal/Content" + SOURCE.replace("/Game", "") + "/" + name + ".uasset"
        disk = PROJECT / "Content" / SOURCE.replace("/Game/", "") / (name + ".uasset")
        require(disk.is_file() and disk.stat().st_size == size,
                "SOURCE_BYTES_" + name)
        require(hashlib.sha256(disk.read_bytes()).hexdigest() == expected_hash,
                "SOURCE_HASH_" + name)
        ignored = subprocess.run(["git", "-C", str(REPO), "check-ignore",
                                  "-q", "--no-index", relative], timeout=20)
        require(ignored.returncode == 0, "SOURCE_NOT_IGNORED_" + name)
        outname = name + SUFFIX
        dest = PROJECT / "Content" / OUTPUT.replace("/Game/", "") / (outname + ".uasset")
        require(not dest.exists() and
                not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT + "/" + outname),
                "OUTPUT_ALREADY_EXISTS_" + outname)
        outrelative = "unreal/Content" + OUTPUT.replace("/Game", "") + "/" + outname + ".uasset"
        require(subprocess.run(["git", "-C", str(REPO), "check-ignore",
                                "-q", "--no-index", outrelative], timeout=20).returncode == 0,
                "OUTPUT_NOT_IGNORED")
    return head, path


def run():
    head, path = admitted()
    REPORT["source_sha"] = head
    source_mesh = unreal.load_asset(SOURCE_MESH)
    target_mesh = unreal.load_asset(TARGET_MESH)
    rtg = unreal.load_asset(RETARGETER)
    target_idle = unreal.load_asset(TARGET_IDLE)
    require(isinstance(source_mesh, unreal.SkeletalMesh) and
            isinstance(target_mesh, unreal.SkeletalMesh) and
            isinstance(rtg, unreal.IKRetargeter) and
            isinstance(target_idle, unreal.AnimSequence),
            "RETARGETER_OR_MESH_INPUT_MISSING")
    source_skeleton = source_mesh.get_editor_property("skeleton")
    target_skeleton = target_mesh.get_editor_property("skeleton")
    require(source_skeleton and target_skeleton and
            target_idle.get_editor_property("skeleton") == target_skeleton and
            source_skeleton != target_skeleton,
            "SKELETON_CONTRACT")
    source_data = []
    for name in CLIPS:
        sequence = unreal.load_asset(SOURCE + "/" + name)
        require(isinstance(sequence, unreal.AnimSequence) and
                sequence.get_editor_property("skeleton") == source_skeleton and
                float(sequence.get_play_length()) > .1,
                "SOURCE_SEQUENCE_OR_SKELETON_" + name)
        data = unreal.EditorAssetLibrary.find_asset_data(SOURCE + "/" + name)
        require(data and data.is_valid(), "SOURCE_ASSETDATA_" + name)
        source_data.append(data)
    inputs = unreal.IKRetargetBatchOperationInputs(
        assets_to_retarget=source_data,
        source_mesh=source_mesh, target_mesh=target_mesh,
        ik_retarget_asset=rtg, target_path=OUTPUT,
        use_source_path=False, suffix=SUFFIX,
        include_referenced_assets=False, overwrite_existing_files=False,
    )
    REPORT["status"] = "BATCH_IN_PROGRESS"
    path.write_text(json.dumps(REPORT, indent=2), encoding="utf8")
    outputs = unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)
    require(len(outputs) == len(CLIPS), "OUTPUT_COUNT")
    expected = {name + SUFFIX for name in CLIPS}
    found = set()
    for data in outputs:
        name = str(data.asset_name)
        object_path = str(data.package_name) + "." + name
        require(name in expected and
                object_path.startswith(OUTPUT + "/") and name not in found,
                "UNEXPECTED_OUTPUT")
        asset = unreal.load_asset(object_path)
        require(isinstance(asset, unreal.AnimSequence) and
                asset.get_editor_property("skeleton") == target_skeleton and
                float(asset.get_play_length()) > .1,
                "OUTPUT_INVALID_" + name)
        require(unreal.EditorAssetLibrary.save_loaded_asset(
            asset, only_if_is_dirty=True), "OUTPUT_NOT_SAVED_" + name)
        file = PROJECT / "Content" / OUTPUT.replace("/Game/", "") / (name + ".uasset")
        require(file.is_file() and file.stat().st_size > 1024,
                "OUTPUT_BYTES_" + name)
        REPORT["created"].append({
            "name": name, "object_path": object_path,
            "bytes": file.stat().st_size,
            "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
            "duration_s": float(asset.get_play_length()),
            "root_motion_enabled": bool(asset.get_editor_property("enable_root_motion")),
            "skeletal_target": target_skeleton.get_path_name()})
        found.add(name)
    require(found == expected, "OUTPUT_NAMES")
    REPORT["status"] = "PRIVATE_DIRECTIONAL_RETARGET_CREATED_NOT_PLAYBACK_ACCEPTED"


receipt = os.environ.get("TSTSS_DIRECTIONAL_RECEIPT")
try:
    run()
except BaseException:
    REPORT["status"] = "HOLD_PRIVATE_DIRECTIONAL_RETARGET"
    REPORT["error"] = traceback.format_exc()[-4200:]
finally:
    REPORT["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if receipt:
        path = Path(receipt)
        if path.parent.is_dir():
            path.write_text(json.dumps(REPORT, indent=2), encoding="utf8")
    unreal.log("TSTSS_PRIVATE_ENDER_DIRECTIONAL " + REPORT["status"])
    unreal.SystemLibrary.quit_editor()
