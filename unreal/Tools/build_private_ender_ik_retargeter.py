"""Fail-closed, local-only IK rig/retargeter construction for Ender review.

Run through a resource-gated UE 5.8.4 editor runner ONLY AFTER the separate
native read-only prerequisite audit has passed on this workstation. By default
this script writes ONLY a receipt under Saved. Opt-in requires the owner-set
environment TSTSS_PRIVATE_IK_CREATE=1 and an exact Git local ignore rule.
Never commit or publish the private Genesis9 mesh or generated .uassets.

This creates the IKRig/IKRetargeter definitions only: it does NOT retarget,
copy, or play any animation, change pawn movement, or save a level.
"""
from pathlib import Path
import ctypes
import datetime
import hashlib
import json
import os
import subprocess
import traceback

import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
REPO = PROJECT.parent
SHA = "2235f3a4283f93a12f5d3e85ce1a8039b2c865b3"
AUDIT = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate/prerequisite_report.json"
FOLDER = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
LOCAL_FOLDER = PROJECT / "Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
OUTPUT = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate/rig_build_receipt.json"
MANNY = "/Game/Mannequins/Meshes/SKM_Manny_Simple"
ENDER = (
    "/Game/ArtLookdev/Characters/Genesis9MergedFBXRigReview_20261109_NONCANONICAL/"
    "Genesis9_BaseShirtShorts_MergedRig_REVIEW"
)
NAMES = (
    "IK_Manny_EnderReview_NONCANONICAL",
    "IK_Genesis9_EnderReview_NONCANONICAL",
    "RTG_MannyToEnder_NONCANONICAL",
)
# Source and target retargeting chains; the native parent walk must prove every
# endpoint is a descendant of its selected start bone before creation.
CHAINS = {
    "Spine": (("spine_01", "spine_05"), ("spine1", "spine4")),
    "Head": (("neck_01", "head"), ("neck1", "head")),
    "LeftArm": (("upperarm_l", "hand_l"), ("l_upperarm", "l_hand")),
    "RightArm": (("upperarm_r", "hand_r"), ("r_upperarm", "r_hand")),
    "LeftLeg": (("thigh_l", "ball_l"), ("l_thigh", "l_toes")),
    "RightLeg": (("thigh_r", "ball_r"), ("r_thigh", "r_toes")),
}
RECEIPT = {
    "status": "NOT_STARTED",
    "git_head_required": SHA,
    "output": FOLDER,
    "local_private_assets_only": True,
    "animation_sequences_generated": 0,
    "native_playback_verified": False,
    "rendered_foot_plant_verified": False,
    "creator_art_approved": False,
    "production_asset_saved": False,
    "review_map_saved": False,
    "engine_version": unreal.SystemLibrary.get_engine_version(),
    "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}


def require(ok, label):
    if not ok:
        raise RuntimeError("HOLD_" + label)


def git(*args):
    cmd = subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True,
        timeout=15, check=False
    )
    require(cmd.returncode == 0, "GIT_UNAVAILABLE")
    return cmd.stdout.strip()


def parent(mesh, bone):
    return str(mesh.get_bone_parent(unreal.Name(bone)))


def descends_from(mesh, start, end):
    seen = set()
    cursor = end
    for _ in range(96):
        if cursor == start:
            return True
        if cursor in ("", "None", "NAME_None") or cursor in seen:
            return False
        seen.add(cursor)
        cursor = parent(mesh, cursor)
    return False


def available_ram_gib():
    class Memory(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong), ("load", ctypes.c_ulong),
            ("total", ctypes.c_ulonglong), ("available", ctypes.c_ulonglong),
            ("tpf", ctypes.c_ulonglong), ("apf", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("extended", ctypes.c_ulonglong),
        ]
    m = Memory()
    m.length = ctypes.sizeof(m)
    require(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)),
            "RAM_PROBE_FAILED")
    return m.available / 2**30


def admitted():
    require(str(PROJECT).lower() ==
            r"c:\tstss_civicintegration_20261116\unreal",
            "WRONG_PROJECT")
    require(RECEIPT["engine_version"].startswith("5.8.4-"),
            "WRONG_UNREAL_VERSION")
    require(git("rev-parse", "HEAD") == SHA, "SOURCE_REVISION_DRIFT")
    require(not git("status", "--porcelain=v1", "--untracked-files=no"),
            "TRACKED_WORKTREE_DIRTY")
    require(os.environ.get("TSTSS_PRIVATE_IK_CREATE") == "1",
            "OWNER_OPT_IN_REQUIRED")
    require(available_ram_gib() >= 6.0, "RAM_RESERVE")
    require(ctypes.windll.kernel32.GetDiskFreeSpaceExW is not None,
            "DISK_PROBE_MISSING")
    import shutil
    require(shutil.disk_usage("C:\\").free >= 16 * 2**30,
            "DISK_RESERVE")
    require(AUDIT.is_file(), "MISSING_NATIVE_PREREQUISITE_AUDIT")
    audit = json.loads(AUDIT.read_text(encoding="utf8"))
    require(audit.get("status") == "NATIVE_RETARGET_INPUTS_VALIDATED_NOT_RETARGETED",
            "NATIVE_AUDIT_NOT_ACCEPTED")
    require(audit.get("engine", "").startswith("5.8.4-"),
            "NATIVE_AUDIT_ENGINE_MISMATCH")
    require(audit.get("retarget_performed") is False and
            audit.get("animation_playback_verified") is False,
            "MALFORMED_AUDIT_AUTHORITY")
    observed = datetime.datetime.fromisoformat(audit["created_utc"])
    require(observed.tzinfo is not None and
            abs((datetime.datetime.now(datetime.timezone.utc) -
                 observed).total_seconds()) < 6 * 3600,
            "NATIVE_AUDIT_STALE")
    # Never overwrite an existing generated .uasset and never create in the
    # project unless its entire exact directory is locally git-ignored.
    path = "unreal/Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/"
    check = subprocess.run(
        ["git", "-C", str(REPO), "check-ignore", "-q", path + NAMES[0] + ".uasset"],
        timeout=15, check=False
    )
    require(check.returncode == 0, "PRIVATE_OUTPUT_NOT_GIT_IGNORED")
    for name in NAMES:
        require(not unreal.EditorAssetLibrary.does_asset_exist(FOLDER + "/" + name),
                "GENERATED_ASSET_ALREADY_EXISTS")
        require(not (LOCAL_FOLDER / (name + ".uasset")).exists(),
                "GENERATED_FILE_ALREADY_EXISTS")
    return audit


def make_ik(asset_tools, name, mesh, chain_index):
    rig = asset_tools.create_asset(
        asset_name=name, package_path=FOLDER,
        asset_class=unreal.IKRigDefinition,
        factory=unreal.IKRigDefinitionFactory()
    )
    require(isinstance(rig, unreal.IKRigDefinition), "IK_RIG_FACTORY")
    ctrl = unreal.IKRigController.get_controller(rig)
    require(ctrl is not None and ctrl.set_skeletal_mesh(mesh),
            "IK_RIG_MESH_BIND")
    require(ctrl.set_retarget_root("pelvis"), "RETARGET_ROOT")
    for chain, pairs in CHAINS.items():
        start, end = pairs[chain_index]
        name_added = ctrl.add_retarget_chain(
            unreal.Name(chain), unreal.Name(start),
            unreal.Name(end), unreal.Name("None")
        )
        require(str(name_added) == chain, "RETARGET_CHAIN_CREATE_" + chain)
    return rig


def create_private_rigs(audit):
    source_mesh = unreal.load_asset(MANNY)
    target_mesh = unreal.load_asset(ENDER)
    require(isinstance(source_mesh, unreal.SkeletalMesh) and
            isinstance(target_mesh, unreal.SkeletalMesh),
            "REVIEW_MESH_LOAD")
    source_skeleton = source_mesh.get_editor_property("skeleton")
    target_skeleton = target_mesh.get_editor_property("skeleton")
    require(source_skeleton.get_path_name() == audit["source_skeleton"],
            "SOURCE_SKELETON_DRIFT")
    require(target_skeleton.get_path_name() == audit["target_skeleton"],
            "TARGET_SKELETON_DRIFT")
    for chain, (source, target) in CHAINS.items():
        require(descends_from(source_mesh, *source),
                "SOURCE_ANCESTRY_" + chain)
        require(descends_from(target_mesh, *target),
                "TARGET_ANCESTRY_" + chain)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    source_rig = make_ik(tools, NAMES[0], source_mesh, 0)
    target_rig = make_ik(tools, NAMES[1], target_mesh, 1)
    retargeter = tools.create_asset(
        asset_name=NAMES[2], package_path=FOLDER,
        asset_class=unreal.IKRetargeter, factory=unreal.IKRetargetFactory()
    )
    require(isinstance(retargeter, unreal.IKRetargeter),
            "RETARGETER_FACTORY")
    controller = unreal.IKRetargeterController.get_controller(retargeter)
    require(controller is not None, "RETARGETER_CONTROLLER_MISSING")
    controller.set_ik_rig(unreal.RetargetSourceOrTarget.SOURCE, source_rig)
    controller.set_ik_rig(unreal.RetargetSourceOrTarget.TARGET, target_rig)
    controller.set_preview_mesh(unreal.RetargetSourceOrTarget.SOURCE, source_mesh)
    controller.set_preview_mesh(unreal.RetargetSourceOrTarget.TARGET, target_mesh)
    require(controller.get_ik_rig(unreal.RetargetSourceOrTarget.SOURCE)
            == source_rig, "SOURCE_IK_BIND_FAILURE")
    require(controller.get_ik_rig(unreal.RetargetSourceOrTarget.TARGET)
            == target_rig, "TARGET_IK_BIND_FAILURE")
    for chain in CHAINS:
        controller.set_source_chain(chain, chain)
        require(str(controller.get_source_chain(chain)) == chain,
                "RETARGET_CHAIN_MAPPING_" + chain)
    # Save only the three newly-created review assets after all gates pass;
    # never use checkout or any broad directory operation.
    for asset in (source_rig, target_rig, retargeter):
        require(asset.get_path_name().startswith(FOLDER + "/"),
                "OUTPUT_OUTSIDE_REVIEW")
        require(unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=True),
                "PRIVATE_REVIEW_ASSET_SAVE_FAILED")
    RECEIPT["saved_assets"] = [
        asset.get_path_name() for asset in (source_rig, target_rig, retargeter)
    ]
    RECEIPT["status"] = "PRIVATE_IK_RIGS_CREATED_REVIEW_ONLY_NO_ANIMATION"


try:
    native_audit = admitted()
    create_private_rigs(native_audit)
except BaseException:
    RECEIPT["status"] = "HOLD_PRIVATE_IK_CREATE"
    RECEIPT["error"] = traceback.format_exc()[-3000:]
finally:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(RECEIPT, sort_keys=True, indent=2),
                      encoding="utf8")
    unreal.log("TSTSS_PRIVATE_ENDER_IK " + RECEIPT["status"])
    unreal.SystemLibrary.quit_editor()
