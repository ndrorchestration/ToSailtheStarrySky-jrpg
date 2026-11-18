"""Create three private NONCANONICAL animation review candidates with UE5.8 IK.

This does NOT assign animations to a pawn, modify gameplay, or approve gait.
Requires a host-bound explicit local opt-in and the existing native proof that
all three private IKRig/IKRetargeter assets reopened successfully.
Source walk/jog retain root-motion concerns: NO DIRECT PLAYBACK AUTHORIZED.
The guarded host must independently verify all three output .uasset files.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import traceback

import unreal

PROJECT = Path(unreal.Paths.project_dir()).resolve()
REPO = PROJECT.parent
EVIDENCE = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate"
AUDIT = EVIDENCE / "prerequisite_report.json"
GATE = EVIDENCE / "startup_gate.json"
REPORT = EVIDENCE / "animation_candidate_receipt.json"
OUTPUT = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/Animations"
LOCAL_OUTPUT = PROJECT / "Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/Animations"
SOURCE_MESH = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
TARGET_MESH = ("/Game/ArtLookdev/Characters/"
               "Genesis9MergedFBXRigReview_20261109_NONCANONICAL/"
               "Genesis9_BaseShirtShorts_MergedRig_REVIEW")
RETARGETER = ("/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/"
              "RTG_MannyToEnder_NONCANONICAL")
SUFFIX = "_EnderPreview_NONCANONICAL"
SOURCE_CLIPS = (
    ("/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle", False),
    ("/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd", True),
    ("/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd", True),
)
NAMES = [source.rsplit("/", 1)[-1] + SUFFIX for source, _ in SOURCE_CLIPS]
INPUT_SHA = {
    "Characters/Mannequins/Anims/Unarmed/MM_Idle.uasset": "11ee7fdeb84db89c1a66785b43b9bfc1415782122b8ac229517f4c5125d9cb0d",
    "Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd.uasset": "c74b2fc0cb651c4924804b364e534856a1b44dee818127c408dc055e4bda5ed9",
    "Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.uasset": "0ccbe851f85a6d4cd7c6438c219cb6af8e281784107b5be8e9b052e4df3069cb",
    "ArtLookdev/Characters/Genesis9MergedFBXRigReview_20261109_NONCANONICAL/Genesis9_BaseShirtShorts_MergedRig_REVIEW.uasset": "6cd1b68e0e326e53ca40e984a7663b48dabbede7f213118c14544000861c462b",
}
RECEIPT = {
    "status": "NOT_STARTED",
    "engine": unreal.SystemLibrary.get_engine_version(),
    "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "private_local_review_only": True,
    "characters_modified": 0, "maps_saved": 0,
    "animation_pawn_assignment": False,
    "gameplay_motion_accepted": False,
    "rendered_foot_contact_verified": False,
    "creator_art_approved": False,
    "source_root_motion_roles": ["walk", "run_candidate"],
    "in_place_conversion_verified": False,
    "allow_direct_source_clip_assignment": False,
}

def require(condition, label):
    if not condition:
        raise RuntimeError("HOLD_" + label)

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def git(*args):
    result = subprocess.run(["git", "-C", str(REPO), *args],
                            capture_output=True, text=True, timeout=20)
    require(result.returncode == 0, "GIT_ERROR")
    return result.stdout.strip()

def admitted():
    require(str(PROJECT).lower() ==
            r"c:\tstss_civicintegration_20261116\unreal", "PROJECT")
    require(RECEIPT["engine"].startswith("5.8.4-"), "ENGINE")
    require(os.environ.get("TSTSS_PRIVATE_ANIM_RETARGET") == "1",
            "EXPLICIT_OPT_IN")
    require(GATE.is_file(), "HOST_GATE_ABSENT")
    gate = json.loads(GATE.read_text(encoding="utf8"))
    head = git("rev-parse", "HEAD")
    require(len(head) == 40 and not
            git("status", "--porcelain=v1", "--untracked-files=no"),
            "TRACKED_SOURCE_DRIFT")
    RECEIPT["source_head"] = head
    require(gate.get("status") == "HOST_ADMITTED" and
            gate.get("mode") == "retarget-clips" and
            gate.get("source_head") == head and
            gate.get("run_id") == os.environ.get("TSTSS_PRIVATE_IK_RUN_ID"),
            "HOST_GATE_MISMATCH")
    gate_time = datetime.datetime.fromisoformat(gate["utc"])
    require(gate_time.tzinfo and
            abs((datetime.datetime.now(datetime.timezone.utc) -
                 gate_time).total_seconds()) < 15 * 60,
            "HOST_GATE_STALE")
    require(gate.get("ram_start_gib", 0) >= 6.5 and
            gate.get("disk_start_gib", 0) >= 16.5,
            "HOST_STARTUP_RESERVE")
    import ctypes
    class Mem(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
                    ("total", ctypes.c_ulonglong), ("available", ctypes.c_ulonglong),
                    ("pft", ctypes.c_ulonglong), ("pfa", ctypes.c_ulonglong),
                    ("vt", ctypes.c_ulonglong), ("va", ctypes.c_ulonglong),
                    ("extra", ctypes.c_ulonglong)]
    mem = Mem();mem.length = ctypes.sizeof(mem)
    require(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem)) and
            mem.available >= 2.5 * 2**30, "RUNTIME_RAM")
    require(shutil.disk_usage("C:\\").free >= 14.3 * 2**30,
            "RUNTIME_DISK")
    require(AUDIT.is_file(), "NATIVE_AUDIT_MISSING")
    a = json.loads(AUDIT.read_text(encoding="utf8"))
    require(a.get("source_head") == head and
            a.get("status") == "NATIVE_RETARGET_INPUTS_VALIDATED_NOT_RETARGETED",
            "AUDIT_NOT_CURRENT_OR_VALID")
    require(a.get("source_clip_conversion_required") is True and
            a.get("direct_source_clip_assignment_allowed") is False,
            "ROOT_MOTION_HOLD_NOT_ENFORCED")
    rig = a.get("saved_private_ik", {})
    require(rig.get("status") ==
            "REOPENED_SOURCE_AND_TARGET_IK_AND_RTG_PASS_NO_ANIM" and
            len(rig.get("sha256", {})) == 3,
            "REOPENED_IK_PROOF_ABSENT")
    require(datetime.datetime.fromisoformat(a["created_utc"]).tzinfo is not None and
            (datetime.datetime.now(datetime.timezone.utc) -
             datetime.datetime.fromisoformat(a["created_utc"])).total_seconds()
            < 6 * 3600, "AUDIT_STALE")
    for relative, expected in INPUT_SHA.items():
        path = PROJECT / "Content" / relative
        require(path.is_file() and sha256(path) == expected,
                "INPUT_SHA_" + path.name)
    for name, digest in rig["sha256"].items():
        path = PROJECT / "Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL" / (name + ".uasset")
        require(path.is_file() and sha256(path) == digest,
                "IK_DRIFT_" + name)
    for name in NAMES:
        path = LOCAL_OUTPUT / (name + ".uasset")
        require(not path.exists() and
                not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT + "/" + name),
                "REVIEW_OUTPUT_ALREADY_EXISTS_" + name)
        check = subprocess.run(["git", "-C", str(REPO), "check-ignore", "-q",
            "unreal/Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/Animations/"
            + name + ".uasset"], timeout=20)
        require(check.returncode == 0, "PRIVATE_OUTPUT_NOT_EXCLUDED")
    return a

def run():
    audit = admitted()
    source_mesh = unreal.load_asset(SOURCE_MESH)
    target_mesh = unreal.load_asset(TARGET_MESH)
    rtg = unreal.load_asset(RETARGETER)
    require(isinstance(source_mesh, unreal.SkeletalMesh) and
            isinstance(target_mesh, unreal.SkeletalMesh) and
            isinstance(rtg, unreal.IKRetargeter), "BAD_RETARGET_INPUT_ASSETS")
    require(source_mesh.get_editor_property("skeleton").get_path_name()
            == audit["source_skeleton"], "SOURCE_SKELETON_DRIFT")
    require(target_mesh.get_editor_property("skeleton").get_path_name()
            == audit["target_skeleton"], "TARGET_SKELETON_DRIFT")
    source_asset_data = []
    for full_path, expected_rootmotion in SOURCE_CLIPS:
        anim = unreal.load_asset(full_path)
        require(isinstance(anim, unreal.AnimSequence), "SOURCE_CLIP_TYPE")
        require(bool(anim.get_editor_property("enable_root_motion")) ==
                expected_rootmotion, "SOURCE_ROOT_MOTION_FLAG_DRIFT")
        data = unreal.EditorAssetLibrary.find_asset_data(full_path)
        require(data and data.is_valid(), "SOURCE_ASSET_DATA_INVALID")
        source_asset_data.append(data)
    inputs = unreal.IKRetargetBatchOperationInputs(
        assets_to_retarget=source_asset_data,
        source_mesh=source_mesh, target_mesh=target_mesh,
        ik_retarget_asset=rtg,
        target_path=OUTPUT, use_source_path=False,
        suffix=SUFFIX, include_referenced_assets=False,
        overwrite_existing_files=False,
    )
    RECEIPT["batch_invocation"] = "UNREAL_5_8_RUN_BATCH_RETARGET"
    RECEIPT["status"] = "BATCH_IN_PROGRESS"
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(RECEIPT, indent=2), encoding="utf8")
    result = unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)
    RECEIPT["returned_asset_data_count"] = len(result)
    require(len(result) == 3, "BATCH_RETURN_COUNT")
    retargeted = []
    for data in result:
        path = str(data.get_soft_object_path())
        require(path.startswith(OUTPUT + "/"), "OUTPUT_PACKAGE_ESCAPE")
        asset = unreal.load_asset(path)
        require(isinstance(asset, unreal.AnimSequence),
                "OUTPUT_NOT_ANIM_SEQUENCE")
        skel = asset.get_editor_property("skeleton")
        require(skel and skel.get_path_name() == audit["target_skeleton"],
                "OUTPUT_TARGET_SKELETON_MISMATCH")
        retargeted.append((path, asset))
    require(sorted(path.split("/")[-1].split(".")[0] for path, _ in retargeted)
            == sorted(NAMES), "OUTPUT_NAMES_NOT_EXACT")
    for path, asset in retargeted:
        require(unreal.EditorAssetLibrary.save_loaded_asset(
            asset, only_if_is_dirty=True), "SAVED_PRIVATE_CLIP_FAILED")
    for name in NAMES:
        require((LOCAL_OUTPUT / (name + ".uasset")).is_file(),
                "MISSING_SAVED_PRIVATE_ANIM")
    RECEIPT["output_animations"] = [
        {"asset": path,
         "duration_s": float(asset.get_play_length()),
         "enable_root_motion": bool(asset.get_editor_property("enable_root_motion")),
         "preview_only": True,
         "in_place_checked": False}
        for path, asset in retargeted
    ]
    RECEIPT["saved_assets"] = len(retargeted)
    RECEIPT["status"] = "PRIVATE_RETARGET_CLIP_CANDIDATES_CREATED_NOT_PLAYBACK_ACCEPTED"

try:
    run()
except BaseException:
    RECEIPT["status"] = "HOLD_PRIVATE_RETARGET_CLIPS"
    RECEIPT["error"] = traceback.format_exc()[-3600:]
finally:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(RECEIPT, indent=2, sort_keys=True), encoding="utf8")
    unreal.log("TSTSS_ENDER_PRIVATE_ANIM " + RECEIPT["status"])
    unreal.SystemLibrary.quit_editor()
