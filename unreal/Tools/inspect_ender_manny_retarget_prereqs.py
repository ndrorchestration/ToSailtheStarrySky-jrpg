"""Read-only Unreal 5.8.4 rig/animation compatibility audit for PRIVATE Ender review.

Run ONLY in a guarded disposable UnrealEditor-Cmd process. This script does
not create IK Rigs, retarget animations, save maps, or approve likeness.
Epic template assets and licensed Genesis9 assets must remain local/ignored.
"""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import traceback

import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
# Stable ancestor is the previously native-validated locomotion implementation.
# Actual audited HEAD is resolved live; a source file cannot safely pin its
# own Git commit hash without creating a self-referential hash.
VALIDATED_NATIVE_ANCESTOR = "cc7548ba53705f5f6d0fd331cf89d32d138a8e0f"
ROOT = PROJECT / "Content"
REPORT = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate/prerequisite_report.json"
PRIVATE_MESH = "/Game/ArtLookdev/Characters/Genesis9MergedFBXRigReview_20261109_NONCANONICAL/Genesis9_BaseShirtShorts_MergedRig_REVIEW"
SOURCE_MESH = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"
SOURCE_CLIPS = {
    "idle": "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle",
    "walk": "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd",
    "run_candidate": "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd",
}
SHA256 = {
    "Characters/Mannequins/Meshes/SKM_Manny_Simple.uasset": "be9f011191ee1887b97cd13bce09886a6066c2fd62c619991070ec142184e1bf",
    "Characters/Mannequins/Meshes/SK_Mannequin.uasset": "22029d47455f24471195b26a0e04a1e1389f27d6a924e88c9f46a0f600c9a530",
    "Characters/Mannequins/Anims/Unarmed/MM_Idle.uasset": "11ee7fdeb84db89c1a66785b43b9bfc1415782122b8ac229517f4c5125d9cb0d",
    "Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd.uasset": "c74b2fc0cb651c4924804b364e534856a1b44dee818127c408dc055e4bda5ed9",
    "Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.uasset": "0ccbe851f85a6d4cd7c6438c219cb6af8e281784107b5be8e9b052e4df3069cb",
    "ArtLookdev/Characters/Genesis9MergedFBXRigReview_20261109_NONCANONICAL/Genesis9_BaseShirtShorts_MergedRig_REVIEW.uasset": "6cd1b68e0e326e53ca40e984a7663b48dabbede7f213118c14544000861c462b",
    "ArtLookdev/Characters/Genesis9MergedFBXRigReview_20261109_NONCANONICAL/Genesis9_BaseShirtShorts_MergedRig_REVIEW_Skeleton.uasset": "73050dbe498b85e2ec922c9e53ede68da88dfdd3af24e2894209c1e30978157c",
}
BONE_CHAIN_PROPOSALS = {
    "Spine": (("spine_01", "spine_05"), ("spine1", "spine4")),
    "Head": (("neck_01", "head"), ("neck1", "head")),
    "LeftArm": (("upperarm_l", "hand_l"), ("l_upperarm", "l_hand")),
    "RightArm": (("upperarm_r", "hand_r"), ("r_upperarm", "r_hand")),
    "LeftLeg": (("thigh_l", "ball_l"), ("l_thigh", "l_toes")),
    "RightLeg": (("thigh_r", "ball_r"), ("r_thigh", "r_toes")),
}
REVIEW = {
    "status": "PENDING",
    "engine": unreal.SystemLibrary.get_engine_version(),
    "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "source_license": "UE_TEMPLATE_LOCAL_NO_PUBLICATION",
    "target_asset": "PRIVATE_NONCANONICAL_GENESIS9_REVIEW",
    "retarget_performed": False,
    "animation_playback_verified": False,
    "foot_contact_verified": False,
    "creator_art_approved": False,
    "map_or_asset_saved": False,
}


def require(condition, problem):
    if not condition:
        raise RuntimeError("HOLD_" + problem)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as src:
        for block in iter(lambda: src.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def trace_ancestry(mesh, start, end):
    """Return the actual end-to-start chain, refusing cycles or missing bones."""
    path = []
    seen = set()
    cursor = end
    for _ in range(96):
        if cursor in seen or cursor in ("", "None", "NAME_None"):
            return None
        path.append(cursor)
        if cursor == start:
            return path
        seen.add(cursor)
        cursor = str(mesh.get_bone_parent(unreal.Name(cursor)))
    return None


def inspect_saved_private_ik(source_mesh, target_mesh):
    """Reopen saved private assets in a NEW editor process; no writes."""
    package = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
    folder = ROOT / "TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"
    names = (
        "IK_Manny_EnderReview_NONCANONICAL",
        "IK_Genesis9_EnderReview_NONCANONICAL",
        "RTG_MannyToEnder_NONCANONICAL",
    )
    files = [folder / (name + ".uasset") for name in names]
    if not any(path.is_file() for path in files):
        REVIEW["saved_private_ik"] = "NONE_YET"
        return
    require(all(path.is_file() for path in files),
            "PARTIAL_PRIVATE_IK_OUTPUT")
    source_rig, target_rig, retargeter = [
        unreal.load_asset(package + "/" + name) for name in names
    ]
    require(isinstance(source_rig, unreal.IKRigDefinition) and
            isinstance(target_rig, unreal.IKRigDefinition) and
            isinstance(retargeter, unreal.IKRetargeter),
            "PRIVATE_IK_SAVED_ASSET_CLASS")
    details = {
        "status": "PENDING",
        "sha256": {name: sha256(path)
                   for name, path in zip(names, files)},
        "chain_checks": {},
    }
    for name, rig, expected_mesh, i in (
        (names[0], source_rig, source_mesh, 0),
        (names[1], target_rig, target_mesh, 1),
    ):
        controller = unreal.IKRigController.get_controller(rig)
        require(controller is not None, "REOPEN_IK_CONTROLLER_" + name)
        rig_mesh = controller.get_skeletal_mesh()
        require(rig_mesh and
                rig_mesh.get_path_name() == expected_mesh.get_path_name(),
                "REOPEN_IK_MESH_MISMATCH_" + name)
        require(str(controller.get_retarget_root()).casefold() == "pelvis",
                "REOPEN_IK_ROOT_" + name)
        existing = {str(chain.chain_name).casefold()
                    for chain in controller.get_retarget_chains()}
        require(len(existing) >= len(BONE_CHAIN_PROPOSALS),
                "REOPEN_IK_CHAIN_COUNT_" + name)
        details["chain_checks"][name] = {}
        for chain, mapping in BONE_CHAIN_PROPOSALS.items():
            require(chain.casefold() in existing,
                    "REOPEN_IK_CHAIN_MISSING_" + chain)
            start, end = mapping[i]
            got_start = str(controller.get_retarget_chain_start_bone(
                unreal.Name(chain)))
            got_end = str(controller.get_retarget_chain_end_bone(
                unreal.Name(chain)))
            require(got_start.casefold() == start.casefold() and
                    got_end.casefold() == end.casefold(),
                    "REOPEN_IK_CHAIN_ENDPOINT_" + chain)
            details["chain_checks"][name][chain] = [got_start, got_end]
    rtg = unreal.IKRetargeterController.get_controller(retargeter)
    require(rtg is not None, "REOPEN_RETARGETER_CONTROLLER")
    for mode, rig in ((unreal.RetargetSourceOrTarget.SOURCE, source_rig),
                      (unreal.RetargetSourceOrTarget.TARGET, target_rig)):
        assigned = rtg.get_ik_rig(mode)
        require(assigned and
                assigned.get_path_name() == rig.get_path_name(),
                "REOPEN_IK_RIG_ASSOCIATION")
    require(rtg.get_num_retarget_ops() >= 5,
            "REOPEN_RETARGET_OP_STACK")
    for chain in BONE_CHAIN_PROPOSALS:
        require(str(rtg.get_source_chain(unreal.Name(chain))).casefold() ==
                chain.casefold(), "REOPEN_RETARGET_CHAIN_MAP_" + chain)
    details["retarget_operations"] = rtg.get_num_retarget_ops()
    details["status"] = "REOPENED_SOURCE_AND_TARGET_IK_AND_RTG_PASS_NO_ANIM"
    REVIEW["saved_private_ik"] = details


def audit():
    require(str(PROJECT).lower() == "c:\\tstss_civicintegration_20261116\\unreal",
            "WRONG_PROJECT")
    require(REVIEW["engine"].startswith("5.8.4-"), "WRONG_ENGINE")
    head = subprocess.run(
        ["git", "-C", str(PROJECT.parent), "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=15
    )
    require(head.returncode == 0 and len(head.stdout.strip()) == 40,
            "GIT_HEAD_UNAVAILABLE")
    REVIEW["source_head"] = head.stdout.strip()
    ancestor = subprocess.run(
        ["git", "-C", str(PROJECT.parent), "merge-base", "--is-ancestor",
         VALIDATED_NATIVE_ANCESTOR, REVIEW["source_head"]],
        capture_output=True, timeout=15
    )
    require(ancestor.returncode == 0, "PREVIOUS_NATIVE_BASE_NOT_ANCESTOR")
    clean = subprocess.run(
        ["git", "-C", str(PROJECT.parent), "status", "--porcelain=v1",
         "--untracked-files=no"],
        capture_output=True, text=True, timeout=15
    )
    require(clean.returncode == 0 and not clean.stdout.strip(),
            "TRACKED_SOURCE_DIRTY")
    for relative, expected in SHA256.items():
        path = ROOT / relative
        require(path.is_file() and sha256(path) == expected,
                "LOCAL_UASSET_HASH_MISMATCH_" + Path(relative).name)

    source = unreal.load_asset(SOURCE_MESH)
    target = unreal.load_asset(PRIVATE_MESH)
    require(isinstance(source, unreal.SkeletalMesh) and
            isinstance(target, unreal.SkeletalMesh), "SKELETAL_MESH_LOAD_FAILED")
    source_skeleton = source.get_editor_property("skeleton")
    target_skeleton = target.get_editor_property("skeleton")
    require(source_skeleton and target_skeleton, "MISSING_SKELETON")
    require(source_skeleton.get_path_name() != target_skeleton.get_path_name(),
            "SOURCE_TARGET_SKELETON_COLLISION")
    REVIEW["source_skeleton"] = source_skeleton.get_path_name()
    REVIEW["target_skeleton"] = target_skeleton.get_path_name()

    REVIEW["clip_properties"] = {}
    REVIEW["source_root_motion_roles"] = []
    for role, path in SOURCE_CLIPS.items():
        clip = unreal.load_asset(path)
        require(isinstance(clip, unreal.AnimSequence),
                "SOURCE_NOT_ANIMSEQUENCE_" + role)
        skeleton = clip.get_editor_property("skeleton")
        require(skeleton and skeleton.get_path_name() == source_skeleton.get_path_name(),
                "CLIP_NOT_SOURCE_SKELETON_" + role)
        root_motion = bool(clip.get_editor_property("enable_root_motion"))
        REVIEW["clip_properties"][role] = {
            "path": clip.get_path_name(),
            "skeleton": skeleton.get_path_name(),
            "root_motion_enabled": root_motion,
            "duration_s": float(clip.get_play_length()),
        }
        # Source root motion is not automatically disqualifying for *rig*
        # construction. It DOES disqualify direct gameplay clip assignment.
        # Preserve the observation and require a separate private in-place
        # conversion and post-retarget root-translation measurement.
        if root_motion:
            REVIEW["source_root_motion_roles"].append(role)

    # UE mesh bone-parent queries: evidence of actual hierarchy, not asset
    # filename strings or assumptions about Genesis9 vs Manny naming.
    REVIEW["proposed_chain_end_bone_parents"] = {}
    for chain, (src, tgt) in BONE_CHAIN_PROPOSALS.items():
        source_parent = str(source.get_bone_parent(src[1]))
        target_parent = str(target.get_bone_parent(tgt[1]))
        REVIEW["proposed_chain_end_bone_parents"][chain] = {
            "source": [src[0], src[1], source_parent],
            "target": [tgt[0], tgt[1], target_parent],
        }
        require(source_parent not in ("None", "", "NAME_None") and
                target_parent not in ("None", "", "NAME_None"),
                "BONE_CHAIN_NOT_PRESENT_" + chain)
        source_path = trace_ancestry(source, src[0], src[1])
        target_path = trace_ancestry(target, tgt[0], tgt[1])
        REVIEW["proposed_chain_end_bone_parents"][chain]["ancestry"] = {
            "source_end_to_start": source_path,
            "target_end_to_start": target_path,
        }
        require(bool(source_path) and bool(target_path),
                "CHAIN_ANCESTRY_INVALID_" + chain)

    require(all(hasattr(unreal, name) for name in (
        "IKRigController", "IKRetargeterController", "IKRetargetBatchOperation",
    )), "IK_RIG_EDITOR_PLUGIN_MISSING")
    inspect_saved_private_ik(source, target)
    source_motion_requires_conversion = bool(REVIEW["source_root_motion_roles"])
    # This status admits **IK rig authoring only**, not animation playback:
    # the 2 motion flags are carried as explicit independent acceptance holds.
    REVIEW["status"] = "NATIVE_RETARGET_INPUTS_VALIDATED_NOT_RETARGETED"
    REVIEW["rig_compatibility_validated"] = True
    REVIEW["source_clip_conversion_required"] = source_motion_requires_conversion
    REVIEW["in_place_root_translation"] = (
        "PRIVATE_CONVERSION_AND_MEASUREMENT_REQUIRED"
        if source_motion_requires_conversion else "NOT_YET_MEASURED"
    )
    REVIEW["direct_source_clip_assignment_allowed"] = False
    REVIEW["pose_alignment_and_foot_contact"] = "REVIEW_REQUIRED"


try:
    audit()
except BaseException:
    REVIEW["status"] = "HOLD_RETARGET_INPUT_AUDIT"
    REVIEW["error"] = traceback.format_exc()[-2500:]
finally:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(REVIEW, indent=2, sort_keys=True), encoding="utf-8")
    unreal.log("TSTSS_ENDER_RETARGET_PREREQ " + REVIEW["status"])
    unreal.SystemLibrary.quit_editor()
