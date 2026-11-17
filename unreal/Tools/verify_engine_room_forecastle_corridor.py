"""Fail-closed source-geometry witness for earned VS02 engine-room E markers.

Not Unreal collision, navmesh, camera line-of-sight or playtest evidence. Reads
existing authoring geometry and the provisional, in-memory station manifest.
No map, actor, save, or production asset is modified.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
AUTHORING = PROJECT / "Tools/build_vertical_slice_environment_maps.py"
PLAYER = PROJECT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
MANIFEST = PROJECT / "DataSource/Integration/FirstWakeEngineRoomReboard.review.json"

# Coordinates are 2D centimeters. The standing pawn stays on the original
# MainWalkableDeck at Z=0; the higher Forecastle has no approved ramp.
SOLID_NAMES = ("MainWalkableDeck", "Forecastle", "BridgeDeck")
MARKER_NAMES = ("LiftStation", "PressureStation", "ReserveStation", "EngineeringApproval")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError("HOLD: " + message)


def authored_solids(authoring: str) -> dict:
    ship = authoring.split("    def ship():", 1)[1].split("\n    def sky():", 1)[0]
    matches = re.findall(
        r'prop\("([^"]+)", "Cube", \(([^)]+)\),\s*'
        r'\(([^)]+)\), "[^"]+", True\)', ship)
    result = {}
    for name, position, scale in matches:
        center = [float(v) for v in position.split(",")]
        size = [float(v) for v in scale.split(",")]
        require(len(center) == len(size) == 3, "malformed solid " + name)
        result[name] = dict(zip(
            ("x_min", "x_max", "y_min", "y_max", "z_min", "z_max"),
            (center[0] - 50 * size[0], center[0] + 50 * size[0],
             center[1] - 50 * size[1], center[1] + 50 * size[1],
             center[2] - 50 * size[2], center[2] + 50 * size[2])))
    require(tuple(result) == SOLID_NAMES, "unexpected authored solid inventory")
    return result


def actual_stations(source: str) -> dict:
    region = source.split("void StageEarnedEngineRoomReview(", 1)[1].split(
        "ATSTSSExplorerCharacter::ATSTSSExplorerCharacter()", 1)[0]
    stations = {}
    for name in MARKER_NAMES:
        match = re.search(r'\{TEXT\("' + name +
                          r'"\), FVector\(([-.\d]+)f, ([-.\d]+)f, '
                          r'([-.\d]+)f\)', region)
        require(match is not None, "missing source marker " + name)
        stations[name] = tuple(float(v) for v in match.groups())
    require(len(stations) == 4, "wrong marker count")
    return stations


def inside_xy_with_margin(point, box: dict, radius: float) -> bool:
    x, y = point
    return (box["x_min"] - radius <= x <= box["x_max"] + radius
            and box["y_min"] - radius <= y <= box["y_max"] + radius)


def witness(authoring: str, source: str, manifest: dict) -> dict:
    require(manifest["status"] ==
            "RESEARCH_REVIEW_LAYOUT_NOT_NATIVE_VERIFIED_OR_CREATOR_ART_APPROVED",
            "review-only manifest status changed")
    require(manifest["active_on"] == "earned one-use boarding arrival ticket only",
            "earned arrival gate lost")
    require(manifest["no_art_promotion"] and not manifest["starbourne_unlocked"],
            "prohibited authorization promotion")
    require(not manifest["savegame_schema_changed"], "unexpected savegame change")
    solids = authored_solids(authoring)
    bounds = manifest["authored_world_static_bounds_cm"]
    for name in SOLID_NAMES:
        for field in ("x_min", "x_max", "y_min", "y_max"):
            require(solids[name][field] == bounds[name][field],
                    "authored solid drift: " + name + "." + field)
        if name == "MainWalkableDeck":
            require(solids[name]["z_max"] == bounds[name]["top_z"],
                    "main deck floor drift")
        else:
            for field in ("z_min", "z_max"):
                require(solids[name][field] == bounds[name][field],
                        "elevated solid drift: " + name + "." + field)

    stations = actual_stations(source)
    declared = manifest["stations"]
    require([s["id"] for s in declared] == list(MARKER_NAMES),
            "marker sequence no longer matches story order")
    require([s.get("story_bit") for s in declared[:3]] == [1, 2, 4],
            "inspection bit order changed")
    require(declared[-1].get("requires_mask") == 7,
            "signoff mask gate missing")
    require(all(tuple(s["location_cm"]) == stations[s["id"]] for s in declared),
            "source/manifest marker drift")

    audit = manifest["forecastle_route_source_audit"]
    require(audit["status"] ==
            "SOURCE_GEOMETRY_WITNESS_NOT_NATIVE_COLLISION_OR_NAVMESH",
            "misleading verification claim")
    require(audit["no_higher_deck_transition_claimed"] is True,
            "unsupported stair/ramp claim")
    radius = float(manifest["review_player_capsule_radius_cm"])
    require(0 < radius <= 60, "invalid pawn capsule assumption")
    reach = float(manifest["interaction_reach_cm"])
    require(0 < reach <= 350, "interaction range drift")
    center_z = float(audit["provisional_actor_center_z_cm"])
    require(70 <= center_z <= 115, "invalid walking actor center assumption")
    waypoints = [tuple(float(v) for v in w) for w in audit["approach_waypoints_cm"]]
    require(len(waypoints) == 5 and all(len(w) == 2 for w in waypoints),
            "incomplete approach route")
    require(waypoints[0] == tuple(manifest["review_entry_cm"][:2]),
            "route no longer starts at earned arrival")

    # Sample every corridor segment. All conservative capsule footprints
    # remain on the original level deck, outside the two raised solid decks.
    samples = 0
    min_deck_margin = math.inf
    min_raised_margin = math.inf
    floor = solids["MainWalkableDeck"]
    for a, b in zip(waypoints, waypoints[1:]):
        for step in range(65):
            t = step / 64
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            margin = min(x - floor["x_min"], floor["x_max"] - x,
                         y - floor["y_min"], floor["y_max"] - y) - radius
            require(margin >= 0, "pawn corridor falls off main deck")
            min_deck_margin = min(min_deck_margin, margin)
            for name in ("BridgeDeck", "Forecastle"):
                raised = solids[name]
                dx = max(raised["x_min"] - x, 0, x - raised["x_max"])
                dy = max(raised["y_min"] - y, 0, y - raised["y_max"])
                separation = math.hypot(dx, dy) - radius
                require(separation > 0, "pawn corridor clips raised " + name)
                min_raised_margin = min(min_raised_margin, separation)
            samples += 1

    # Markers must not overlap a raised deck in XY *at their actual Z*.
    # An E line trace to a marker buried in solid geometry is not a route.
    for name, position in stations.items():
        x, y, z = position
        require(floor["x_min"] < x < floor["x_max"] and
                floor["y_min"] < y < floor["y_max"],
                "marker leaves floor " + name)
        for raised_name in ("BridgeDeck", "Forecastle"):
            raised = solids[raised_name]
            require(not (raised["z_min"] <= z <= raised["z_max"] + 70 and
                         inside_xy_with_margin((x, y), raised, 35)),
                    name + " buried into solid " + raised_name)

    # The route provides one conservative camera/pawn approach to each E
    # marker; no marker, story beat, or input interaction is pre-granted.
    distances = {}
    for i, name in enumerate(MARKER_NAMES):
        target = stations[name]
        approach = waypoints[i + 1]
        dist = math.dist((*approach, center_z), target)
        require(dist <= reach - 35, name + " beyond modeled E approach reach")
        distances[name] = round(dist, 3)
    return {
        "status": "SOURCE_GEOMETRY_WITNESS_NOT_NATIVE_PIE_OR_COLLISION",
        "station_count": 4, "route_sample_count": samples,
        "capsule_radius_cm_assumed": radius,
        "min_deck_edge_margin_cm": round(min_deck_margin, 3),
        "min_raised_collision_margin_cm": round(min_raised_margin, 3),
        "witness_e_distances_cm": distances,
        "engagement_verified_in_unreal": False,
        "enclosed_engine_room_established": False,
    }


def verify() -> dict:
    return witness(AUTHORING.read_text(encoding="utf-8"),
                   PLAYER.read_text(encoding="utf-8"),
                   json.loads(MANIFEST.read_text(encoding="utf-8")))


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
