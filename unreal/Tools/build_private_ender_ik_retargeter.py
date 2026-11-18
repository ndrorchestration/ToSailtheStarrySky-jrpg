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
# Never pin the build script to its own Git SHA: every commit changes that SHA.
# Require a clean current HEAD matching the fresh native prerequisite report.
VALIDATED_NATIVE_ANCESTOR = "cc7548ba53705f5f6d0fd331cf89d32d138a8e0f"
AUDIT = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate/prerequisite_report.json"
FOLDER = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
LOCAL_FOLDER = PROJECT / "Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
OUTPUT = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate/rig_build_receipt.json"
STARTUP_GATE = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate/startup_gate.json"
MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
ENDER = (
    "/Game/ArtLookdev/Characters/Genesis9MergedFBXRigReview_20261109_NONCANONICAL/"
    "Genesis9_BaseShirtShorts_MergedRig_REVIEW"
)
NAMES = (
    "IK_Manny_EnderReview_NONCANONICAL",
    "IK_Genesis9_EnderReview_NONCANONICAL",
    "RTG_MannyToEnder_NONCANONICAL",
)
# Rehash all private and Epic template binaries at execution time. The native
# prerequisite report alone is not sufficient if files changed between runs.
SHA256_INPUTS = {
    "Characters/Mannequins/Meshes/SKM_Manny_Simple.uasset": "be9f011191ee1887b97cd13bce09886a6066c2fd62c619991070ec142184e1bf",
    "Characters/Mannequins/Meshes/SK_Mannequin.uasset": "22029d47455f24471195b26a0e04a1e1389f27d6a924e88c9f46a0f600c9a530",
    "Characters/Mannequins/Anims/Unarmed/MM_Idle.uasset": "11ee7fdeb84db89c1a66785b43b9bfc1415782122b8ac229517f4c5125d9cb0d",
    "Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd.uasset": "c74b2fc0cb651c4924804b364e534856a1b44dee818127c408dc055e4bda5ed9",
    "Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.uasset": "0ccbe851f85a6d4cd7c6438c219cb6af8e281784107b5be8e9b052e4df3069cb",
    "ArtLookdev/Characters/Genesis9MergedFBXRigReview_20261109_NONCANONICAL/Genesis9_BaseShirtShorts_MergedRig_REVIEW.uasset": "6cd1b68e0e326e53ca40e984a7663b48dabbede7f213118c14544000861c462b",
    "ArtLookdev/Characters/Genesis9MergedFBXRigReview_20261109_NONCANONICAL/Genesis9_BaseShirtShorts_MergedRig_REVIEW_Skeleton.uasset": "73050dbe498b85e2ec922c9e53ede68da88dfdd3af24e2894209c1e30978157c",
}
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
    "git_head_required": "MATCH_NATIVE_AUDIT_SOURCE_HEAD",
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


def hash_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
    head = git("rev-parse", "HEAD")
    require(len(head) == 40, "SOURCE_HEAD_MALFORMED")
    base = subprocess.run(
        ["git", "-C", str(REPO), "merge-base", "--is-ancestor",
         VALIDATED_NATIVE_ANCESTOR, head], timeout=15, check=False
    )
    require(base.returncode == 0, "SOURCE_NATIVE_ANCESTOR_DRIFT")
    RECEIPT["source_head"] = head
    require(not git("status", "--porcelain=v1", "--untracked-files=no"),
            "TRACKED_WORKTREE_DIRTY")
    require(os.environ.get("TSTSS_PRIVATE_IK_CREATE") == "1",
            "OWNER_OPT_IN_REQUIRED")
    # The 6.5 GiB RAM / 16.5 GiB disk STARTUP reserve must be measured
    # before Unreal launches by the independent guarded host. Requiring
    # the entire startup reserve INSIDE UE rejects healthy editor sessions.
    # Keep lower, continuously monitored safety floors inside UE instead.
    require(STARTUP_GATE.is_file(), "MISSING_HOST_STARTUP_GATE")
    startup = json.loads(STARTUP_GATE.read_text(encoding="utf8"))
    require(startup.get("status") == "HOST_ADMITTED" and
            startup.get("source_head") == head and
            startup.get("mode") == "create-rigs" and
            startup.get("run_id") and
            startup.get("run_id") == os.environ.get("TSTSS_PRIVATE_IK_RUN_ID"),
            "HOST_STARTUP_GATE_MISMATCH")
    gate_time = datetime.datetime.fromisoformat(startup["utc"])
    require(gate_time.tzinfo is not None and
            abs((datetime.datetime.now(datetime.timezone.utc) -
                 gate_time).total_seconds()) < 15 * 60,
            "HOST_STARTUP_GATE_STALE")
    require(startup.get("disk_start_gib", 0) >= 16.5 and
            startup.get("ram_start_gib", 0) >= 6.5,
            "HOST_STARTUP_RESERVE_UNPROVEN")
    import shutil
    require(available_ram_gib() >= 2.5, "RAM_RUNTIME_FLOOR")
    require(shutil.disk_usage("C:\\").free >= 14.3 * 2**30,
            "DISK_RUNTIME_FLOOR")
    RECEIPT["host_startup_gate_run_id"] = startup["run_id"]
    require(AUDIT.is_file(), "MISSING_NATIVE_PREREQUISITE_AUDIT")
    audit = json.loads(AUDIT.read_text(encoding="utf8"))
    require(audit.get("status") == "NATIVE_RETARGET_INPUTS_VALIDATED_NOT_RETARGETED",
            "NATIVE_AUDIT_NOT_ACCEPTED")
    require(audit.get("engine", "").startswith("5.8.4-"),
            "NATIVE_AUDIT_ENGINE_MISMATCH")
    require(audit.get("source_head") == head, "NATIVE_AUDIT_HEAD_MISMATCH")
    for relative, expected in SHA256_INPUTS.items():
        file_path = PROJECT / "Content" / relative
        require(file_path.is_file() and hash_file(file_path) == expected,
                "PRIVATE_OR_TEMPLATE_FILE_HASH_DRIFT_" + Path(relative).name)
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
    # UE5.8 retargeters use an explicit operation stack; a new factory asset
    # may start with no FK/IK mapping ops. Epic's controller adds the standard
    # Pelvis Motion, FK Chains, IK Chains, IK Solve and Root Motion ops.
    controller.add_default_ops()
    require(controller.get_num_retarget_ops() >= 5,
            "RETARGETER_HAS_NO_FK_IK_CHAIN_OPS")
    for chain in CHAINS:
        require(controller.set_source_chain(chain, chain),
                "RETARGET_CHAIN_SET_" + chain)
        require(str(controller.get_source_chain(chain)) == chain,
                "RETARGET_CHAIN_MAPPING_" + chain)
    # Save only the three newly-created review assets after all gates pass;
    # never use checkout or any broad directory operation.
    for asset in (source_rig, target_rig, retargeter):
        require(asset.get_path_name().startswith(FOLDER + "/"),
                "OUTPUT_OUTSIDE_REVIEW")
        require(unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=True),
                "PRIVATE_REVIEW_ASSET_SAVE_FAILED")
    for relative, expected in SHA256_INPUTS.items():
        file_path = PROJECT / "Content" / relative
        require(file_path.is_file() and hash_file(file_path) == expected,
                "SOURCE_FILE_CHANGED_DURING_IK_CREATE")
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
