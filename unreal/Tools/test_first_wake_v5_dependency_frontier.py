"""Fail-closed, read-only checks for the V5 cross-PR dependency frontier.

This is not a native Unreal integration or verification of other PR heads.
"""
import hashlib
import json
import unittest
from pathlib import Path

UNREAL = Path(__file__).resolve().parents[1]
ROOT = UNREAL.parent
FRONTIER = UNREAL / "DataSource/Integration/FirstWakeV5DependencyFrontier.review.json"
BASELINE = UNREAL / "Tools/first_wake_dependency_contract.json"


class V5DependencyFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        cls.baseline = json.loads(BASELINE.read_text(encoding="utf-8"))

    def test_review_status_cannot_launder_integration(self):
        f = self.frontier
        self.assertEqual(f["schema_version"], 1)
        self.assertEqual(f["status"], "REVIEW_ONLY_DEPENDENCY_RECONCILIATION_NOT_INTEGRATED")
        for key in ("new_runtime_dependency_admitted", "main_merge_authorized",
                    "production_art_promoted"):
            self.assertIs(f[key], False)
        self.assertEqual(f["Starbourne"], "LOCKED_FAIL_CLOSED")
        self.assertEqual(f["roster_gate"]["excluded"], ["Reson", "Aepex"])
        self.assertEqual(f["roster_gate"]["after_physical_splashdown_recruitment"], ["Lyra"])

    def test_current_native_declarations_are_not_accidentally_upgraded(self):
        baseline = self.baseline["project"]
        project = json.loads((UNREAL / "ToSailTheStarrySky.uproject").read_text(encoding="utf-8-sig"))
        build = (UNREAL / "Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs").read_text(encoding="utf-8-sig")
        self.assertEqual(project["EngineAssociation"], "5.8")
        self.assertEqual([x["Name"] for x in project["Plugins"] if x["Enabled"]],
                         baseline["enabled_plugins"])
        self.assertEqual(self.frontier["unchanged_baseline_plugins"], baseline["enabled_plugins"])
        self.assertEqual(self.frontier["proposed_native_modules_not_yet_admitted"], ["CinematicCamera"])
        self.assertNotIn('"CinematicCamera"', build)
        self.assertIn('"AudioMixer"', build)
        self.assertEqual(self.frontier["new_plugins_installed"], [])

    def test_same_playable_map_and_exact_source_custody(self):
        f = self.frontier
        p = UNREAL / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview.umap"
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),
                         "ff2b5c1423a370c4ac318b9b241088d8f20fec5eee993c998c2a5ed335cbb299")
        self.assertTrue((ROOT / f["evidence"]).is_file())
        self.assertEqual(len(f["verified_playability_head"]), 40)
        self.assertTrue(f["review_branch"].startswith("review/"))

    def test_pr_references_unique_and_categorized(self):
        f = self.frontier
        rows = f["workstreams"]
        prs = [x["pr"] for x in rows]
        self.assertEqual(len(prs), len(set(prs)))
        self.assertGreaterEqual(len(prs), 15)
        self.assertTrue({799, 813, 814, 804, 815, 808, 793, 810, 812, 794}.issubset(prs))
        for item in rows:
            self.assertIn(item["priority"], ("P0", "P1", "P2"))
            self.assertTrue(item["status"] and item["reconcile"])
            self.assertIsInstance(item["collision_surface"], list)
            self.assertIsInstance(item["depends_on"], list)
        self.assertIn("HOLD_LOW_DISK", f["environment_admission"]["heavy_unreal_now"])
        self.assertGreater(f["environment_admission"]["heavy_unreal_requires_free_disk_gib"],
                           f["environment_admission"]["last_observed_free_disk_gib"])
        self.assertTrue(f["environment_admission"]["observation_is_transient"])

    def test_do_not_mistake_dependencies_for_implementation(self):
        f = self.frontier
        self.assertIn("first_flyer_E_objective_advance", f["proven_runtime"])
        self.assertIn("physical_sea_contact_stability", f["unproven_runtime"])
        self.assertIn("music_or_audio_playback", f["unproven_runtime"])
        self.assertIn("packaged_build", f["unproven_runtime"])


if __name__ == "__main__":
    unittest.main()
