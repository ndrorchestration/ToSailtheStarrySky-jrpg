#!/usr/bin/env python3
"""Bind reviewed ship meshes to the *already-open* isolated First Wake map.

--inspect is pure Python and changes nothing.
--bind-in-editor requires Unreal Editor 5.8 Python and compiled TSTSS C++.
No spawn/delete/save, no asset import/reimport, no gameplay or story effects.
The user must manually inspect and choose whether to save the review map.
"""
from __future__ import annotations

import argparse
import json
import re

MAP = "/Game/TSTSS/Review/FirstWake_Benchmark_V1"
SHIP_LABEL = "TSTSS_REVIEW_AureateWake"
WING_DIR = "/Game/TSTSS/Review/ShipArt/WingCandidateV2/"
SUPPORT_DIR = "/Game/TSTSS/Review/ShipArt/RootSupportCandidateV1/"
AUTHORITY = "UNSAVED_REVIEW_WORLD_ONLY_NOT_GAMEPLAY_OR_ART_ACCEPTED"


class ShipReviewHold(ValueError):
    pass


def validate_plan(wing_asset: str, support_asset: str) -> dict:
    for name, path, root in (("wing", wing_asset, WING_DIR), ("root_support", support_asset, SUPPORT_DIR)):
        if not isinstance(path, str) or not path.startswith(root):
            raise ShipReviewHold(name + " must be in its isolated review candidate folder")
        suffix = path[len(root):]
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)?", suffix):
            raise ShipReviewHold(name + " asset has an unsafe or invalid Unreal object name")
    if wing_asset == support_asset:
        raise ShipReviewHold("A wing and root support must be different assets")
    return {
        "map": MAP, "ship_actor_label": SHIP_LABEL,
        "wing_asset": wing_asset, "root_support_asset": support_asset,
        "expected_wings": 4, "expected_root_supports": 4,
        "expected_hydrofoils": 2,
        "authority": AUTHORITY, "requires_manual_save": True,
    }


def read_property(actor, names):
    # UE reflection may strip the C++ bool 'b' prefix, depending on the build.
    for name in names:
        try:
            return name, actor.get_editor_property(name)
        except (AttributeError, ValueError, TypeError):
            continue
    raise ShipReviewHold("Compiled preview actor is missing editor property: " + "/".join(names))


def bind_in_editor(plan: dict) -> dict:
    try:
        import unreal
    except ImportError as exc:
        raise ShipReviewHold("Use --bind-in-editor only inside Unreal Editor Python") from exc
    required = ("UnrealEditorSubsystem", "EditorActorSubsystem", "StaticMesh",
                "AureateWakePreviewActor", "get_editor_subsystem", "load_asset")
    if not all(hasattr(unreal, key) for key in required):
        raise ShipReviewHold("UE Editor plugins or compiled TSTSS module unavailable")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world is None or world.get_path_name().split(".", 1)[0] != MAP:
        raise ShipReviewHold("Refusing to bind outside the exact FirstWake_Benchmark_V1 review world")

    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    matches = [actor for actor in actors if actor.get_actor_label(False) == SHIP_LABEL]
    if len(matches) != 1 or not isinstance(matches[0], unreal.AureateWakePreviewActor):
        raise ShipReviewHold("Expected exactly one compiled review-only AureateWakePreviewActor")
    ship = matches[0]

    if any(not hasattr(ship, method) for method in ("get_wing_count", "get_hydrofoil_count",
                "get_root_support_count", "is_transitioning", "get_current_form",
                "refresh_wing_meshes", "refresh_root_supports")):
        raise ShipReviewHold("Unreal Python could not reflect the compiled ship review API")
    if (ship.get_wing_count(),ship.get_root_support_count(),ship.get_hydrofoil_count()) != (4,4,2):
        raise ShipReviewHold("Ship component inventory changed")
    if ship.is_transitioning() or not str(ship.get_current_form()).lower().endswith("skyborne"):
        raise ShipReviewHold("Actor must be stationary and in Skyborne form")
    orbiter_flag, orbiter_value = read_property(ship, ("allow_orbiter_preview", "b_allow_orbiter_preview"))
    if orbiter_value:
        raise ShipReviewHold("Hidden Orbiter preview must be disabled")

    wing_prop, original_wing = read_property(ship, ("authored_wing_mesh",))
    support_prop, original_support = read_property(ship, ("authored_root_support_mesh",))
    pose_prop, original_pose = read_property(ship, ("use_root_pivoted_wing_pose", "b_use_root_pivoted_wing_pose"))
    if original_wing is not None or original_support is not None or original_pose:
        raise ShipReviewHold("Existing authored wing/support binding found; never overwrite")

    wing = unreal.load_asset(plan["wing_asset"])
    root = unreal.load_asset(plan["root_support_asset"])
    if (wing is None or root is None or not isinstance(wing,unreal.StaticMesh)
            or not isinstance(root,unreal.StaticMesh) or wing is root):
        raise ShipReviewHold("Reviewed assets must resolve to two distinct Unreal StaticMesh objects")

    # All preflights above execute before any editor mutation.
    try:
        ship.set_editor_property(wing_prop,wing)
        ship.set_editor_property(support_prop,root)
        ship.set_editor_property(pose_prop,True)
        ship.refresh_wing_meshes()
        ship.refresh_root_supports()
    except Exception as exc:
        # Do not silently leave a half-applied art lookdev transaction.
        try:
            ship.set_editor_property(pose_prop,original_pose)
            ship.set_editor_property(support_prop,original_support)
            ship.set_editor_property(wing_prop,original_wing)
            ship.refresh_wing_meshes()
            ship.refresh_root_supports()
        except Exception as rollback_exc:
            raise ShipReviewHold("Review bind failed and rollback needs manual inspection: " + str(rollback_exc)) from exc
        raise ShipReviewHold("Review binding failed; original actor properties restored") from exc

    return {"result":"REVIEW_ACTOR_BOUND_UNSAVED", "map":MAP, "label":SHIP_LABEL,
            "wing_asset":plan["wing_asset"], "root_support_asset":plan["root_support_asset"],
            "requires_manual_save":True, "no_native_render_proven":True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wing-asset",required=True)
    parser.add_argument("--root-support-asset",required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect",action="store_true")
    mode.add_argument("--bind-in-editor",action="store_true")
    args=parser.parse_args(argv)
    try:
        plan=validate_plan(args.wing_asset,args.root_support_asset)
        result=bind_in_editor(plan) if args.bind_in_editor else plan
        print(json.dumps(result,indent=2))
    except (ShipReviewHold,ValueError,TypeError,OSError) as exc:
        parser.exit(1,"SHIP REVIEW HOLD: "+str(exc)+"\n")


if __name__=="__main__":
    main()
