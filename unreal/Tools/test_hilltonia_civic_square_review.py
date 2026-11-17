"""Source-only contract for creator-requested Hilltonia board + round fountain.

Checks nonshipping civic preview geometry and explicit absent quest authority.
Does NOT prove native UE rendering, forest spawn or playable flyer acceptance.
"""
from pathlib import Path
import math
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaReviewExtension.cpp"
       ).read_text(encoding="utf-8")
LEGACY = (ROOT / "Tools/build_first_wake_prelude_interaction.py"
          ).read_text(encoding="utf-8")
DECISION = (ROOT.parent /
            "docs/reviews/FIRST_WAKE_CREATOR_LOCKED_HILLTONIA_TO_OFFSHORE_SPLASHDOWN_2026-11-16.md"
            ).read_text(encoding="utf-8")


def examine(source: str) -> list[str]:
    errors = []
    names = (
        "HilltoniaRoundStoneFountain", "HilltoniaFountainStoneRim",
        "HilltoniaFountainBrassSpout", "HilltoniaFountainDecorativeWater",
        "HilltoniaPostingBoardPosts", "HilltoniaPostingBoardPanel",
        "HilltoniaPostingBoardFlyerPaper", "HilltoniaPostingFlyerPreview",
    )
    for name in names:
        if source.count('TEXT("' + name + '")') != 1:
            errors.append("missing-or-duplicate:" + name)
    for fragment in (
        "for (int32 Segment = 0; Segment < 12; ++Segment)",
        "Place(FountainRim, X, Y, 70.f",
        "Place(FountainWater, FountainX, FountainY, 61.f",
        "TEXT(\"/Game/TSTSS/Review/VerticalSlice/M_VS_Ocean.M_VS_Ocean\")",
        "Make(Owner, Root, TEXT(\"HilltoniaFountainDecorativeWater\"),",
        "Cylinder, Ocean, false",
        'TEXT("CAPTAIN IONIA\\nENGINEER WANTED")',
        "town_flyer_preview=1 board_quest_authority=0 forest_player_spawn=0",
        "seven_firstwake_markers_unchanged=1 saved_map_unchanged=1",
    ):
        if fragment not in source:
            errors.append("missing-review-contract:" + fragment)
    if "FountainX = -7200.f;" not in source:
        errors.append("fountain-x-drift")
    if "FountainY = 600.f;" not in source:
        errors.append("fountain-y-drift")
    if "BoardX = -6810.f;" not in source:
        errors.append("board-x-drift")
    if "BoardY = 600.f;" not in source:
        errors.append("board-y-drift")
    # Check the source owns only geometry and cosmetic signs. No story/save or
    # fake actor-hit grant is permitted in an environmental extension.
    for forbidden in ("AdvanceTo(", "InspectStation(", "AdvanceWaterBeat(",
                      "SaveGameToSlot(", "ATSTSSMilestoneActor",
                      "SetActorLocation(", "TSTSSWaterVolume"):
        if forbidden in source:
            errors.append("unauthorized-civic-gameplay:" + forbidden)
    return errors


class HilltoniaSquareVisualReviewTests(unittest.TestCase):
    def test_review_visual_components_present_and_not_quest_authority(self):
        self.assertEqual(examine(CPP), [])

    def test_fountain_board_placement_clear_of_road_and_hall(self):
        # UE basic cylinders have 100cm diameter and scale=3.2 -> 160cm radius.
        fountain_x, fountain_y, radius = -7200, 600, 160
        board_x, board_y, board_half_x = -6810, 600, 2.55 * 50
        road_north_edge_y = -150 + 7.8 * 50
        hall_south_edge_y = 1110 - 6.3 * 50
        hall_east_edge_x = -7450 + 9.2 * 50
        self.assertGreater(fountain_y - radius, road_north_edge_y)
        self.assertLess(fountain_y + radius, hall_south_edge_y)
        self.assertGreater(board_y - 22 / 2, road_north_edge_y)
        self.assertGreater(board_x - board_half_x, hall_east_edge_x)
        self.assertGreater(math.dist((board_x, board_y),
                                     (fountain_x, fountain_y)),
                           radius + board_half_x + 60)
        # This is authoring-space clearance only; native pawn/collision remains
        # untested until the scene renders and is walked in an owned PIE map.

    def test_original_harbor_marker_route_remains_historical_not_approved(self):
        self.assertIn('ReviewStop("FlyerDiscovery", -2200, 0', LEGACY)
        self.assertIn('ReviewStop("LiftStation", -250, 0', LEGACY)
        self.assertIn("LEGACY REVIEW", DECISION)
        self.assertIn("physically inside the ship", DECISION.lower())

    def test_creator_flow_has_distinct_acceptance_and_delayed_lyra(self):
        for phrase in ("Accept quest / Not now", "only after acceptance",
                       "main engineering room", "docking clamps",
                       "eastward", "few hundred meters",
                       "phase alignment", "stressed components",
                       "Lyra", "after actual splashdown",
                       "Seabourne", "Starbourne"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), DECISION.lower())
        self.assertIn("visual geometry", DECISION)
        self.assertIn("NOT", DECISION)

    def test_mutation_drops_geometry_or_forges_quest_authority(self):
        self.assertTrue(examine(CPP.replace(
            'TEXT("HilltoniaPostingBoardFlyerPaper")',
            'TEXT("NoPaper")', 1)))
        self.assertTrue(examine(CPP.replace(
            "board_quest_authority=0", "board_quest_authority=1", 1)))
        self.assertTrue(examine(CPP.replace(
            "for (int32 Segment = 0; Segment < 12; ++Segment)",
            "for (int32 Segment = 0; Segment < 4; ++Segment)", 1)))


if __name__ == "__main__":
    unittest.main()
