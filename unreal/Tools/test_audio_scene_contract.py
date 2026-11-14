#!/usr/bin/env python3
"""Six-map audio review manifest preflight. Engine-free: no map edited or auditioned."""
from __future__ import annotations
import json
from pathlib import Path
import unittest

UNREAL = Path(__file__).resolve().parents[1]
MATRIX = UNREAL / "DataSource" / "Audio" / "FirstWakeSceneAudioBindings.review.json"
CATALOG = UNREAL / "DataSource" / "Audio" / "FirstWakeAudioEvents.review.json"

EXPECTED = {
    "VS01_DenithHarbor", "VS02_AureateInteriors", "VS03_FirstWakeSky",
    "VS04_SplashdownSea", "VS05_DenithFuelShanty", "VS06_SplashdownShore"
}

class AudioSceneSourceTests(unittest.TestCase):
    def setUp(self):
        self.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.events = {v["event_id"] for v in self.catalog["events"]}

    def test_six_real_review_map_paths_only(self):
        scenes = self.matrix["scenes"]
        self.assertEqual(len(scenes), 6)
        self.assertEqual({Path(s["map_source"]).stem for s in scenes}, EXPECTED)
        self.assertEqual(len({s["map_source"] for s in scenes}), len(scenes))
        for s in scenes:
            self.assertTrue(s["map_source"].startswith("unreal/Content/TSTSS/Review/VerticalSlice/"))
            self.assertTrue((UNREAL.parent / s["map_source"]).is_file(), s["map_source"])
            self.assertEqual("/Game/TSTSS/Review/VerticalSlice/" +
                             Path(s["map_source"]).stem, s["map_package"])
            self.assertFalse(s["actors_placed"])
            self.assertFalse(s["native_playback_verified"])
            self.assertFalse(s["mix_approved"])
            self.assertTrue(s["desired_event_ids"])
            self.assertTrue(set(s["desired_event_ids"]).issubset(self.events))

    def test_optional_actors_really_defined_in_review_source(self):
        for scene in self.matrix["scenes"]:
            for cls in scene["desired_review_actors"]:
                self.assertTrue(cls.startswith("ATSTSS"))
                h = UNREAL / "Source" / "ToSailTheStarrySky" / "Public" / (cls[1:] + ".h")
                self.assertTrue(h.is_file(), str(h))
        harbor = next(s for s in self.matrix["scenes"] if "VS01_" in s["map_package"])
        self.assertIn("ATSTSSFootstepAudioDirector", harbor["desired_review_actors"])
        self.assertIn("ATSTSSHarborAudioZone", harbor["desired_review_actors"])

    def test_postfloat_canon_overrides_legacy_audio_placeholders(self):
        # The legacy package survives for old map/save/source dependencies,
        # not because its original fuel-cache story is still accepted.
        constraints = self.matrix["post_splashdown_canon_constraints"]
        self.assertEqual(
            constraints["authority"],
            "CREATOR_DIRECTION_NOT_AUTOMATICALLY_IMPLEMENTED_BY_AUDIO")
        self.assertEqual(constraints["crash_side_denith_fuel_cache"], "REJECTED")
        self.assertEqual(
            constraints["ship_travel_form"], "SEABORNE_ONLY_MULTIPLE_STORY_ACTS")
        self.assertEqual(
            constraints["skyborne_flight_restoration"],
            "NOT_AUTHORIZED_BY_FUEL_OR_AUDIO")
        self.assertEqual(
            constraints["captain_denith"],
            "IONIA_PREVIOUS_CAPTAIN_NOT_CRASH_SITE_FUEL_CACHE")
        self.assertEqual(
            constraints["lyra_recruitment"], "EXPLICIT_POST_SPLASHDOWN_ONLY")
        self.assertFalse(constraints["reson_and_aepex_available"])
        self.assertEqual(constraints["starbourne"], "FAIL_CLOSED")

        legacy = [scene for scene in self.matrix["scenes"]
                  if "VS05_DenithFuelShanty" in scene["map_package"]]
        self.assertEqual(len(legacy), 1)
        scene = legacy[0]
        self.assertEqual(
            constraints["legacy_review_map_package"], scene["map_package"])
        self.assertEqual(
            scene["legacy_location_status"], "LEGACY_MAP_PACKAGE_NOT_APPROVED_LOCATION")
        self.assertEqual(
            scene["event_authority_status"], "PROPOSED_UNPLACED_NOT_STORY_TRIGGER_AUTHORIZED")
        self.assertEqual(
            scene["story_resolution_status"],
            "NO_CONVENIENT_FUEL_CACHE_NO_IMMEDIATE_FLIGHT_REPAIR")
        for candidate in ("music.shanty.clue", "story.lyra.recruited"):
            self.assertIn(candidate, scene["desired_event_ids"])
            self.assertIn(candidate, scene["notes"])
        self.assertFalse(scene["actors_placed"])
        self.assertFalse(scene["native_playback_verified"])
        self.assertFalse(scene["mix_approved"])
        self.assertIn("NOT authorized scene beats", scene["notes"])
        self.assertNotIn("fuel cache has been resolved", scene["notes"].lower())
        self.assertEqual(self.matrix["asset_bindings"]["rights"], "NOT_RELEASE_APPROVED")
        self.assertEqual(self.matrix["asset_bindings"]["binding_state"], "UNPLACED")

    def test_lyra_and_ship_gates_unmodified(self):
        for scene in self.matrix["scenes"]:
            self.assertNotIn("ship.starbourne.transition", scene["desired_event_ids"])
            self.assertNotIn("magic.water.current", scene["desired_event_ids"])
            self.assertNotIn("magic.resonator.guard", scene["desired_event_ids"])
            self.assertNotIn("Reson", ",".join(scene["desired_review_actors"]))
            self.assertNotIn("Aepex", ",".join(scene["desired_review_actors"]))
            if "story.lyra.recruited" in scene["desired_event_ids"]:
                self.assertIn("VS05_DenithFuelShanty", scene["map_source"])
        self.assertEqual(self.matrix["asset_bindings"]["rights"], "NOT_RELEASE_APPROVED")
        self.assertEqual(self.matrix["asset_bindings"]["binding_state"], "UNPLACED")

if __name__ == "__main__":
    unittest.main()
