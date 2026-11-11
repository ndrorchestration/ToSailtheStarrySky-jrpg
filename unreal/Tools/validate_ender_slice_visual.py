"""Source-only gate for Ender's review visual binding (not an Unreal/PIE test)."""
from __future__ import annotations

import json
from pathlib import Path
import sys

UNREAL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = UNREAL_ROOT / "DataSource" / "Characters" / "EnderFirstWakeVisualBridge.review.json"
HEADER = UNREAL_ROOT / "Source" / "ToSailTheStarrySky" / "Public" / "TSTSSExplorerCharacter.h"
SOURCE = UNREAL_ROOT / "Source" / "ToSailTheStarrySky" / "Private" / "TSTSSExplorerCharacter.cpp"


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def validate_contract(row: dict) -> None:
    require(row.get("schema") == "tstss.ender.firstwake.visual-bridge.v1", "schema drift")
    require(row.get("status") == "REVIEW_ONLY__PIE_NOT_TESTED", "false completion claim")
    require(row.get("engine") == "Unreal Engine 5.8.4", "engine version drift")
    source = row.get("based_on", {})
    require(source.get("integration_pr") == 799, "wrong integrated parent")
    authority = row.get("authority", {})
    require(authority.get("hero") == "Ender" and authority.get("affinity") == "Spirit",
            "Ender identity drift")
    require(authority.get("playable_pre_splashdown") == ["Ender", "Ionia"],
            "pre-splashdown party drift")
    require(authority.get("first_recruit_post_splashdown") == "Lyra",
            "Lyra recruitment drift")
    require(authority.get("unavailable_in_slice") == ["Reson", "Aepex"],
            "future party falsely recruited")
    require(authority.get("starbourne") == "LOCKED", "Starbourne must fail closed")
    for key in ("face", "eyes", "hair", "costume", "goggles", "staff"):
        require(isinstance(authority.get(key), str) and authority[key].strip(),
                "missing visual canon: " + key)
    approved = row.get("appearance_reference", {})
    require(approved.get("status") == "CREATOR_APPROVED_VISUAL_REFERENCE_ONLY",
            "Ender approved source identity missing")
    require(approved.get("approved_on") == "2026-11-11",
            "Ender latest creator approval not bound")
    require("SECOND PANEL FROM LEFT (ENDER)" in approved.get("source", ""),
            "approved Ender portrait locator lost")
    require(approved.get("prior_hair_reference") == "VERY_SHORT_AUBURN_BUZZ_CUT_SUPERSEDED",
            "old buzz-cut direction improperly restored")
    require(approved.get("accepted_hair") == "TOUSLED_DARK_COPPER_BROWN_FULL_VOLUME",
            "tousled copper hair lock altered")
    require("tousled" in authority.get("hair", "").lower() and
            "very short" not in authority.get("hair", "").lower(),
            "historical buzz-cut hair direction returned")
    require(approved.get("accepted_goggles") == "BRASS_TEAL_LENSES_ON_HEAD",
            "approved goggle reference drift")
    for name in ("avatar_model_approved", "mesh_rig_animation_approved",
                 "game_stats_and_job_redefined"):
        require(approved.get(name) is False,
                "visual reference approval was confused with production/model approval: " + name)
    rig = row.get("source_review", {})
    require(rig.get("observed_bones") == 152 and rig.get("observed_material_slots") == 25,
            "unreconciled source rig evidence")
    require(rig.get("native_motion", "").startswith("HOLD"),
            "native mesh deformation falsely passed")
    require("NOT" in rig.get("provenance", "").upper(), "source licensing boundary missing")
    binding = row.get("visual_binding", {})
    require(binding.get("world_type") == "PIE_ONLY", "runtime scope expanded")
    require(binding.get("engine_editor_only") is True, "editor-only boundary weakened")
    for name in ("default_goggles_visible", "default_staff_visible",
                 "changes_story_state", "changes_inventory", "changes_savegame",
                 "approval_on_asset_binding"):
        require(binding.get(name) is False, "unsafe source binding: " + name)
    require(binding.get("default_candidate_mesh") is None,
            "unapproved mesh must not be enabled by default")
    require(binding.get("required_bones") == ["head", "l_hand"],
            "attachment bone scope changed")
    gates = row.get("native_acceptance", {})
    for name in ("creator_signoff", "canonical_promotion"):
        require(gates.get(name) is False, "unauthorized promotion: " + name)
    for name in ("unreal_build", "pie_player_visual", "animation_deformation",
                 "clothing_tracking", "goggles_clearance", "staff_grip",
                 "head_likeness", "cinematic_multiview"):
        require(gates.get(name) in {"NOT_RUN_NEONTIC_OFFLINE",
                                   "NOT_RUN", "NOT_VERIFIED", "NOT_APPROVED"},
                "native gate falsely passed: " + name)
    require(len(gates.get("test_sequence", [])) >= 8, "incomplete test handoff")


def validate_cpp_guards(header: str, source: str) -> None:
    require("#if WITH_EDITORONLY_DATA" in header, "UHT review properties not editor-only")
    require("#if WITH_EDITOR" in source, "review method missing editor guard")
    require('World->WorldType != EWorldType::PIE' in source, "PIE-only runtime guard missing")
    require('EnderSliceReviewBody.IsNull()' in source, "missing no-asset guard")
    require('Bones.FindBoneIndex(EnderReviewHeadBone)' in source, "head binding not validated")
    require('Bones.FindBoneIndex(EnderReviewGripBone)' in source, "hand binding not validated")
    require('bShowEnderReviewGoggles = false' in header, "goggles visible by default")
    require('bShowEnderReviewStaff = false' in header, "staff visible by default")
    require('SetCollisionEnabled(ECollisionEnabled::NoCollision)' in source,
            "review accessories must not alter physics collision")
    require('SetSkeletalMeshAsset(Candidate)' in source, "no real pawn visual binding")
    require("!Body->DoesSocketExist(Bone)" in source, "missing valid-bone socket guard")
    require('FAttachmentTransformRules::SnapToTargetNotIncludingScale' in source,
            "uncontrolled attachment semantics")
    # Inspect only the bounded review method: prevent accidental gameplay state edits.
    begin = source.find("void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()")
    require(begin >= 0, "review method missing")
    end = source.find("#endif", begin)
    require(end > begin, "review method guard missing")
    method = source[begin:end]
    for forbidden in ("SaveFirstWake(", "LoadFirstWake(", "SetCurrentBeat(",
                      "RecruitedLyra", "Starbourne", "SetMovementMode(", "AddMovementInput("):
        require(forbidden not in method, "review method modified gameplay: " + forbidden)


def main() -> int:
    try:
        row = json.loads(MANIFEST.read_text(encoding="utf-8"))
        validate_contract(row)
        validate_cpp_guards(HEADER.read_text(encoding="utf-8"),
                            SOURCE.read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("ENDER_SLICE_SOURCE_GATE=HOLD", str(error), file=sys.stderr)
        return 2
    print("ENDER_SLICE_SOURCE_GATE=PASS (engine-free; not Unreal/PIE)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
