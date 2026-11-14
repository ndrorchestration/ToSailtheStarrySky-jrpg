"""Negative and positive synthetic fixtures for read-only Hilltonia runtime telemetry.

No native Unreal execution is claimed: actual player movement is a separate
Windows Editor/PIE review gate.
"""
from pathlib import Path
import math
import re
import unittest

from check_hilltonia_runtime_route import (
    assess, EXPECTED, WAYPOINTS, RouteNotEstablished,
)

ROOT = Path(__file__).resolve().parents[1]
ROUTE_HEADER = (ROOT /
    "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaRouteTelemetry.h"
).read_text(encoding="utf-8")
EXPLORER_CPP = (ROOT /
    "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
).read_text(encoding="utf-8")
EXPLORER_H = (ROOT /
    "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h"
).read_text(encoding="utf-8")


def record(kind, name, now, x, y, z=130., grounded=1, footing=1):
    return (
        "[2026.11.13-22:00:00][0]LogTemp: Display: "
        f"TSTSS_HILLTONIA_ROUTE_{kind} map=V5 name={name} "
        f"time={now:.2f} x={x:.1f} y={y:.1f} z={z:.1f} "
        f"grounded={grounded} footing={footing}"
    )


def synthetic_round_trip():
    result = []
    t = 2.
    for index, name in enumerate(EXPECTED):
        x, y, _radius = WAYPOINTS[name]
        result.append(record("WAYPOINT", name, t, x, y))
        if index == len(EXPECTED) - 1:
            break
        next_x, next_y, _ = WAYPOINTS[EXPECTED[index + 1]]
        for step in range(1, 6):
            f = step / 6.
            sx = x + (next_x - x) * f
            sy = y + (next_y - y) * f
            # The production pawn emits its nearest recognized waypoint
            # while inside the radius; only distant samples are UNMARKED.
            label = next((
                key for key, (wx, wy, radius) in WAYPOINTS.items()
                if math.hypot(sx - wx, sy - wy) <= radius + 0.15
            ), "UNMARKED")
            result.append(record("SAMPLE", label, t + 2. * step, sx, sy))
        t += 12.
    return result


class HilltoniaRuntimeRouteFixtures(unittest.TestCase):
    def test_complete_ordered_route_is_consistent_not_approved(self):
        evidence = assess("\n".join(synthetic_round_trip()))
        self.assertEqual(evidence["waypoint_events"], 11)
        self.assertEqual(evidence["heartbeat_samples"], 50)
        self.assertGreater(evidence["measured_distance_cm"], 16000.)
        self.assertEqual(evidence["status"],
                         "REVIEW_ROUTE_LOG_CONSISTENT_NOT_NATIVE_ATTESTATION")
        for key in ("native_receipt_confirmed", "source_revision_confirmed",
                    "creator_visual_approval", "shipping_or_canon_authorization"):
            self.assertFalse(evidence[key])

    def test_missing_woodland_checkpoint_rejected(self):
        lines = synthetic_round_trip()
        lines = [x for x in lines if "name=FOREST_EDGE" not in x]
        with self.assertRaisesRegex(RouteNotEstablished, "Incomplete or unordered"):
            assess("\n".join(lines))

    def test_far_west_turnaround_required(self):
        lines = [x for x in synthetic_round_trip() if "name=TOWN_WEST_END" not in x]
        with self.assertRaisesRegex(RouteNotEstablished, "Incomplete or unordered"):
            assess("\n".join(lines))

    def test_wrong_order_rejected(self):
        lines = synthetic_round_trip()
        lines[0], lines[6] = lines[6], lines[0]
        with self.assertRaises(RouteNotEstablished):
            assess("\n".join(lines))

    def test_unsupported_footing_rejected(self):
        lines = synthetic_round_trip()
        lines[6] = lines[6].replace("footing=1", "footing=0")
        with self.assertRaisesRegex(RouteNotEstablished, "Unsupported or airborne"):
            assess("\n".join(lines))

    def test_airborne_heartbeat_rejected(self):
        lines = synthetic_round_trip()
        lines[4] = lines[4].replace("grounded=1", "grounded=0")
        with self.assertRaisesRegex(RouteNotEstablished, "Unsupported or airborne"):
            assess("\n".join(lines))

    def test_teleport_like_position_jump_rejected(self):
        lines = synthetic_round_trip()
        lines[3] = lines[3].replace("x=-", "x=9999")
        with self.assertRaisesRegex(RouteNotEstablished, "Implausible movement"):
            assess("\n".join(lines))

    def test_wrong_waypoint_coordinates_rejected(self):
        lines = synthetic_round_trip()
        lines[0] = lines[0].replace("x=-3650.0", "x=-2600.0")
        with self.assertRaisesRegex(RouteNotEstablished, "outside measured route radius"):
            assess("\n".join(lines))

    def test_too_few_actual_heartbeat_records_rejected(self):
        lines = []
        seen_samples = 0
        for line in synthetic_round_trip():
            if "ROUTE_SAMPLE" in line:
                seen_samples += 1
                if seen_samples > 3:
                    continue
            lines.append(line)
        with self.assertRaisesRegex(RouteNotEstablished, "Insufficient live"):
            assess("\n".join(lines))

    def test_fall_recovery_not_accepted_as_clean_walk(self):
        with self.assertRaisesRegex(RouteNotEstablished, "Fall/recovery"):
            assess("\n".join(synthetic_round_trip()) +
                   "\nLogTemp: Display: TSTSS_REVIEW_FALL_RETURN map=V5\n")

    def test_nonreview_map_not_substitutable(self):
        bogus = "\n".join(synthetic_round_trip()).replace(
            "map=V5", "map=Production")
        with self.assertRaisesRegex(RouteNotEstablished, "Malformed or unscoped"):
            assess(bogus)

    def test_corrupt_v5_telemetry_cannot_be_silently_ignored(self):
        lines = synthetic_round_trip()
        lines.append(record("SAMPLE", "UNMARKED", 150., -5000., -150.).replace(
            "grounded=1 footing=1", "grounded=1"))
        with self.assertRaisesRegex(RouteNotEstablished, "Malformed or unscoped"):
            assess("\n".join(lines))

    def test_extra_route_fields_are_not_silently_accepted(self):
        lines = synthetic_round_trip()
        lines[3] += " bogus_authority=approved"
        with self.assertRaisesRegex(RouteNotEstablished, "Malformed or unscoped"):
            assess("\n".join(lines))

    def test_heartbeat_duplicates_do_not_fake_observation(self):
        lines = synthetic_round_trip()
        lines[2] = lines[1]
        with self.assertRaisesRegex(RouteNotEstablished, "Repeated or too-fast"):
            assess("\n".join(lines))

    def test_sample_waypoint_label_matches_real_position(self):
        lines = synthetic_round_trip()
        i = next(i for i, line in enumerate(lines)
                 if "ROUTE_SAMPLE" in line and "name=UNMARKED" not in line)
        lines[i] = re.sub(r"name=[A-Z_]+", "name=UNMARKED", lines[i], count=1)
        with self.assertRaisesRegex(RouteNotEstablished, "Sample waypoint label disagrees"):
            assess("\n".join(lines))

    def test_unscoped_sample_not_substitutable_for_real_walk(self):
        lines = synthetic_round_trip()
        i = next(i for i, line in enumerate(lines) if "ROUTE_SAMPLE" in line)
        lines[i] = lines[i].replace("map=V5", "map=Other")
        with self.assertRaisesRegex(RouteNotEstablished, "Malformed or unscoped"):
            assess("\n".join(lines))

    def test_runtime_source_reads_real_pawn_and_footing_without_mutation(self):
        for token in (
            '#include "TSTSSHilltoniaRouteTelemetry.h"',
            "const FVector Current = GetActorLocation();",
            "TSTSSHilltoniaRouteTelemetry::IsScopedRouteRegion(Current)",
            "TSTSSHilltoniaRouteTelemetry::NearestWaypoint(Current)",
            "Movement->IsMovingOnGround();",
            "HasSupportedReviewFooting(World, Current)",
            "World->GetTimeSeconds()",
            "TSTSS_HILLTONIA_ROUTE_WAYPOINT",
            "TSTSS_HILLTONIA_ROUTE_SAMPLE",
            "World->GetNetMode() == NM_Standalone",
            'Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
            "NextHilltoniaProbeTimeSeconds = Now + 2.f;",
        ):
            self.assertIn(token, EXPLORER_CPP)
        for token in ("LastHilltoniaProbeWaypoint", "NextHilltoniaProbeTimeSeconds"):
            self.assertIn(token, EXPLORER_H)
        self.assertNotIn("TeleportTo(", ROUTE_HEADER)
        self.assertNotIn("AdvanceTo(", ROUTE_HEADER)
        self.assertNotIn("SaveGameToSlot(", ROUTE_HEADER)

    def test_native_source_waypoints_match_validator(self):
        matches = re.findall(
            r'\{TEXT\("([A-Z_]+)"\),\s*(-?[\d.]+)f,\s*'
            r'(-?[\d.]+)f,\s*([\d.]+)f\}',
            ROUTE_HEADER,
        )
        self.assertEqual(len(matches), len(WAYPOINTS))
        self.assertEqual(set(x[0] for x in matches), set(WAYPOINTS))
        for name, x, y, radius in matches:
            self.assertEqual((float(x), float(y), float(radius)), WAYPOINTS[name])

    def test_short_noisy_log_is_not_evidence(self):
        with self.assertRaises(RouteNotEstablished):
            assess("LogTemp: Display: title menu entered\n")


if __name__ == "__main__":
    unittest.main()
