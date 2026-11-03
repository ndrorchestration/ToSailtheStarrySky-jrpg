#!/usr/bin/env python3
"""Fail-closed source/design review for the noncanonical Aureate Wake internals.

Validates Unreal preview component ancestry, module inventory, and known
non-habitable proxy dimensions. Does not run Unreal or grant crew access.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "ReviewData/aureate_internals_review_v1.json"
HEADER = ROOT / "Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h"
SOURCE = ROOT / "Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp"

ANCHORS = {
    "bridge": ("BridgeHelmReviewAnchor", "BridgeHabitationPivot"),
    "quarters": ("QuartersDeckReviewAnchor", "BridgeHabitationPivot"),
    "engineering": ("FixedEngineeringReviewAnchor", "VesselRoot"),
    "boarding": ("FixedBoardingReviewAnchor", "VesselRoot"),
}
INTERFACES = {
    ("bridge", "quarters"): ("SHARED_ROTATING_PIVOT", "ATTACHMENT_ONLY_NO_CREW_ACCESS"),
    ("quarters", "engineering"): ("ROTATING_TO_FIXED_COUPLER", "HOLD_SEAL_AND_WALKWAY_UNVERIFIED"),
    ("engineering", "boarding"): ("FIXED_HULL_SERVICE_ROUTE", "HOLD_WALKWAY_UNVERIFIED"),
}
REQUIRED_SYSTEM_IDS = frozenset((
    "helm_controls", "navigation_star_charts", "comms_and_sensors",
    "bridge_instruments", "crew_berths", "galley_common_space",
    "sanitation_water", "child_safe_space", "cabin_atmosphere",
    "crew_emergency_supplies", "power_bus", "harmonic_levitation_engine",
    "four_wing_actuators", "two_hydrofoil_drives", "submersible_ballast",
    "pressure_integrity", "air_recirculation", "water_recovery",
    "thermal_management", "fire_detection", "maintenance_access",
    "starbourne_sail_system", "boarding_interface", "emergency_egress",
))
EXPECTED_ACCEPTANCE = {
    "native_unreal_build": "NOT_TESTED_AT_THIS_HEAD",
    "native_automation": "NOT_TESTED_AT_THIS_HEAD",
    "walkable_crew_route": "NOT_TESTED",
    "motion_swept_clearance": "NOT_TESTED",
    "evacuation_and_child_safety": "NOT_TESTED",
    "approved_interior_art": "NOT_APPROVED",
    "release": "NOT_AUTHORIZED",
}


class InteriorHold(ValueError):
    pass


def require(ok: bool, description: str):
    if not ok:
        raise InteriorHold(description)


def validate(data: dict, header: str, cpp: str) -> dict:
    require(data.get("schema") == "tstss.aureate-internals.review.v1",
            "Unsupported interior contract schema")
    require(data.get("authority") == "NONCANONICAL_UNREAL_ENGINEERING_REVIEW_NOT_PRODUCTION",
            "Authority changed or unapproved canon promotion")
    require(data.get("actor") == "AAureateWakePreviewActor",
            "Review must target actual Aureate Wake actor")
    require(data.get("display_forms") ==
            ["Skybourne", "Seabourne", "Submersible", "Starbourne"],
            "Player-facing configuration names drifted")
    require(data.get("serialized_forms") ==
            ["Skyborne", "Seaborne", "Submersible", "Orbiter"],
            "Serialized Unreal enum identifiers cannot change here")
    perms = data.get("review_permissions")
    expected_perms = (
        "enabled_by_default", "crew_walkable", "life_support_operational",
        "pressure_rated", "rotating_coupler_operational", "starbourne_unlocked",
        "native_approval", "creator_art_approved"
    )
    require(isinstance(perms, dict) and set(perms) == set(expected_perms)
            and all(perms[k] is False for k in expected_perms),
            "Unsafe review permission or unsupported authorization claim")
    require(data.get("acceptance") == EXPECTED_ACCEPTANCE,
            "Unverified test, creative approval or release promoted")

    # The present mesh is a 35 cm-high envelope, not an actual sleeping room.
    scale = re.search(
        r"LivingQuartersEnvelope->SetRelativeScale3D\(FVector\("
        r"\s*((?:\d+(?:\.\d*)?|\.\d+))\s*,\s*((?:\d+(?:\.\d*)?|\.\d+))\s*,"
        r"\s*((?:\d+(?:\.\d*)?|\.\d+))\s*\)\);", cpp
    )
    require(scale is not None, "Quarters scale is not source-bound")
    actual_cm = [100 * float(v) for v in scale.groups()]
    geo = data.get("geometry", {})
    extent = geo.get("quarters_proxy_extents_cm")
    require(isinstance(extent, list) and len(extent) == 3 and
            all(isinstance(x, (int, float)) and not isinstance(x, bool)
                for x in extent) and
            all(abs(actual_cm[i] - extent[i]) < 0.001 for i in range(3)),
            "Quarters proxy extent and C++ geometry disagree")
    headroom = geo.get("minimum_review_headroom_cm")
    require(isinstance(headroom, (int, float)) and not isinstance(headroom, bool)
            and headroom == 180 and extent[2] < headroom and
            geo.get("habitation_verdict") == "HOLD_NONHABITABLE_PROXY" and
            geo.get("dimensions_are_canon") is False,
            "Quarters proxy cannot be admitted as habitable geometry")

    required_source = (
        "bool bPreviewCentralBridgeHabitation = false;",
        "bool bAllowOrbiterPreview = false;",
        "TObjectPtr<USceneComponent> BridgeHabitationPivot;",
    )
    for token in required_source:
        require(token in header, "Original review defaults/authority changed: " + token)
    require("BridgeHabitationPivot->SetupAttachment(VesselRoot);" in cpp,
            "Central assembly must remain coupled to vessel")
    require("!HasFiniteHabitationReviewRotation(RequestedForm)" in cpp,
            "Do not remove nonfinite pose protection")
    require("(bPreviewCentralBridgeHabitation &&" in cpp and
            "RequestedForm == EAureateWakeForm::Orbiter && !bAllowOrbiterPreview" in cpp,
            "Starbourne/Orbiter transition gate weakened")

    anchors = data.get("anchors")
    require(isinstance(anchors, list) and len(anchors) == len(ANCHORS),
            "Missing or extra interior frame anchor")
    by_zone = {a.get("zone"): a for a in anchors if isinstance(a, dict)}
    require(len(by_zone) == len(ANCHORS), "Duplicate zone or malformed anchor")
    for zone, (component, parent) in ANCHORS.items():
        a = by_zone.get(zone)
        require(a is not None and a.get("component") == component and
                a.get("parent") == parent and
                a.get("crew_access_verified") is False,
                "Interior attachment/frame contract drifted for " + zone)
        require(
            f'TObjectPtr<USceneComponent> {component};' in header and
            f'{component} = CreateDefaultSubobject<USceneComponent>(TEXT("{component}"));' in cpp and
            f'{component}->SetupAttachment({parent});' in cpp,
            "Unreal attachment missing or reparented: " + zone
        )
    require(
        "BridgeHelmReviewAnchor->SetRelativeLocation(FVector(0, 0, 80));" in cpp and
        "BridgeHelmReviewAnchor->SetRelativeLocation(FVector(240, 0, 95));" in cpp and
        "QuartersDeckReviewAnchor->SetRelativeLocation(FVector(0, 0, -25));" in cpp,
        "Coupled interior anchor pose/legacy rollback changed"
    )

    links = data.get("interfaces")
    require(isinstance(links, list) and len(links) == len(INTERFACES),
            "Interior passage interface inventory changed")
    seen_links = set()
    for x in links:
        require(isinstance(x, dict), "Malformed passage interface")
        k = (x.get("from"), x.get("to"))
        require(k not in seen_links and k in INTERFACES,
                "Unknown/duplicate passage or bypass")
        seen_links.add(k)
        require((x.get("type"), x.get("status")) == INTERFACES[k],
                "Unverified rotating coupler or passage promoted")
    require(seen_links == set(INTERFACES), "Missing pivot-to-hull passage hold")

    systems = data.get("systems")
    require(isinstance(systems, list) and len(systems) == len(REQUIRED_SYSTEM_IDS),
            "Required ship subsystem inventory incomplete")
    names = [s.get("id") for s in systems if isinstance(s, dict)]
    require(len(names) == len(systems) and set(names) == REQUIRED_SYSTEM_IDS,
            "Missing/duplicate/unknown ship system")
    graph = {}
    for s in systems:
        name = s["id"]
        depends = s.get("depends_on")
        require(s.get("zone") in ANCHORS and
                s.get("review_state") == "DESIGN_ONLY" and
                s.get("gameplay_enabled") is False and
                isinstance(s.get("description"), str) and bool(s["description"].strip()),
                "Invented implemented or operational ship subsystem: " + name)
        require(isinstance(depends, list) and len(depends) == len(set(depends))
                and all(v in REQUIRED_SYSTEM_IDS and v != name for v in depends),
                "Bad or unknown subsystem dependency: " + name)
        graph[name] = depends
    require(next(s for s in systems if s["id"] == "starbourne_sail_system")["zone"]
            == "engineering", "Locked sail system location authority changed")
    seen, active = set(), set()
    def visit(node):
        require(node not in active, "Cyclic ship system dependency: " + node)
        if node in seen:
            return
        active.add(node)
        for dep in graph[node]:
            visit(dep)
        active.remove(node)
        seen.add(node)
    for name in graph:
        visit(name)

    return {
        "status": "HOLD_UNBUILT_INTERNALS_AND_UNVERIFIED_PASSAGE",
        "preview_quarters_headroom_cm": extent[2],
        "anchors": len(anchors), "systems": len(systems),
        "interfaces_unverified": len(links),
        "starbourne_unlocked": False,
        "native_verified": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    args = ap.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = validate(data, HEADER.read_text(encoding="utf-8"),
                      SOURCE.read_text(encoding="utf-8"))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
