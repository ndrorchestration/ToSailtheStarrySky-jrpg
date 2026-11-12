"""Fail-closed source contracts for the native V3 visual review map authoring."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "Tools/stage_first_wake_prelude_v3_visual.py").read_text(encoding="utf-8")
BASE = ROOT / "Content/TSTSS/Review/FirstWake_PreludeInteraction_V2.umap"

class V3VisualReviewSourceTests(unittest.TestCase):
    def test_immutable_v2_baseline(self):
        import hashlib
        self.assertEqual(hashlib.sha256(BASE.read_bytes()).hexdigest(),
                         "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80")
        self.assertIn('if hashlib.sha256(original.read_bytes()).hexdigest() != SOURCE_SHA256:', SCRIPT)

    def test_isolation_and_exact_source_authorization(self):
        for phrase in ("TSTSS_DockOpening_20261111", "TSTSS_V3_EXPECTED_HEAD",
                       "TSTSS_V3_OPT_IN", "AUTHOR_V3_REVIEW_VISUAL_ONLY",
                       "NATIVE_V3_REVIEW_SAVED_NO_RUNTIME_APPROVAL",
                       "git", "status", "--porcelain"):
            self.assertIn(phrase, SCRIPT)
        self.assertIn("if target.exists() or u.EditorAssetLibrary.does_asset_exist(TARGET):", SCRIPT)
        self.assertIn("save_map(world, TARGET)", SCRIPT)
        self.assertNotIn("save_map(world, SOURCE)", SCRIPT)

    def test_signs_and_static_lighting_are_replaced(self):
        for phrase in ('SIGN_PREFIX = "TSTSS_PRELUDE_REVIEW_SIGN_"',
                       "len(signs) != 7", "len(originals)", "u.Rotator(0., 180., 0.)",
                       'set_editor_property("world_size", 33.)',
                       '"force_no_precomputed_lighting", True',
                       "u.SkyAtmosphere", "u.ExponentialHeightFog",
                       "u.PointLight", "u.DirectionalLight",
                       "u.PostProcessVolume"):
            self.assertIn(phrase, SCRIPT)

    def test_no_gameplay_or_story_state_edit(self):
        for forbidden in ("AdvanceTo(", "QueueShore(", "SeaContact(", "Starbourne(",
                          "SaveGameToSlot(", "DefaultGameMode", "GameDefaultMap="):
            self.assertNotIn(forbidden, SCRIPT)
        self.assertIn('"approved":False, "merged":False', SCRIPT)

if __name__ == "__main__":
    unittest.main()
