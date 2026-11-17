"""Read-only Unreal 5.8.4 rig/animation compatibility audit for PRIVATE Ender review.

Run ONLY in a guarded disposable UnrealEditor-Cmd process. This script does
not create IK Rigs, retarget animations, save maps, or approve likeness.
Epic template assets and licensed Genesis9 assets must remain local/ignored.
"""
from pathlib import Path
import datetime
import hashlib
import json
import traceback

import unreal


PROJECT = Path(unreal.Paths.project_dir()).resolve()
ROOT = PROJECT / "Content"
REPORT = PROJECT / "Saved/MigrationEvidence/EnderRetargetPrivate/prerequisite_report.json"
PRIVATE_MESH = "/Game/ArtLookdev/Characters/Genesis9MergedFBXRigReview_20261109_NONCANONICAL/Genesis9_BaseShirtShorts_MergedRig_REVIEW"
SOURCE_MESH = "/Game/Mannequins/Meshes/SKM_Manny_Simple"
SOURCE_CLIPS = {
    "idle": "/Game/Mannequins/Anims/Unarmed/MM_Idle",
    "walk": "/Game/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd",
    "run_candidate": "/Game/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd",
}
SHA256 = {
    "Mannequins/Meshes/SKM_Manny_Simple.uasset": "be9f011191ee1887b97cd13bce09886a6066c2fd62c619991070ec142184e1bf",
    "Mannequins/Meshes/SK_Mannequin.uasset": "22029d47455f24471195b26a0e04a1e1389f27d6a924e88c9f46a0f600c9a530",
    "Mannequins/Anims/Unarmed/MM_Idle.uasset": "11ee7fdeb84db89c1a66785b43b9bfc1415782122b8ac229517f4c5125d9cb0d",
    "Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd.uasset": "c74b2fc0cb651c4924804b364e534856a1b44dee818127c408dc055e4bda5ed9",
    "Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd.uasset": "0ccbe851f85a6d4cd7c6438c219cb6af8e281784107b5be8e9b052e4df3069cb",
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


def audit():
    require(str(PROJECT).lower() == "c:\\tstss_civicintegration_20261116\\unreal",
            "WRONG_PROJECT")
    require(REVIEW["engine"].startswith("5.8.4-"), "WRONG_ENGINE")
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
        require(not root_motion, "ROOT_MOTION_ENABLED_" + role)

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

    require(all(hasattr(unreal, name) for name in (
        "IKRigController", "IKRetargeterController", "IKRetargetBatchOperation",
    )), "IK_RIG_EDITOR_PLUGIN_MISSING")
    REVIEW["status"] = "NATIVE_RETARGET_INPUTS_VALIDATED_NOT_RETARGETED"
    REVIEW["in_place_root_translation"] = "NOT_YET_MEASURED"
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
