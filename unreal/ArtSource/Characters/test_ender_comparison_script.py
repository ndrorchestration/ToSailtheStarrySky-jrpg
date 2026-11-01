"""Prohibit production game mutation in native Ender compare automation script."""
import ast
from pathlib import Path
import unittest

SCRIPT = Path(__file__).with_name("capture_ender_comparison_native.py")


class NativeScriptSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_camera_angles_use_keywords_only(self):
        calls = [node for node in ast.walk(self.tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute) and node.func.attr == "Rotator"
                 and isinstance(node.func.value, ast.Name) and node.func.value.id == "unreal"]
        self.assertGreaterEqual(len(calls), 4)
        for call in calls:
            self.assertEqual(call.args, [])
            self.assertEqual({v.arg for v in call.keywords}, {"pitch", "yaw", "roll"})

    def test_does_not_save_or_write_to_production(self):
        for bad in ("save_current_level", "import_asset_tasks", "save_asset(",
                    "replace_existing=True", "Game/Characters", "Game/Maps/FirstWake"):
            self.assertNotIn(bad, self.source)
        self.assertIn("check_project(unreal.Paths.project_dir())", self.source)
        self.assertIn("load_intake_receipts(PROJECT)", self.source)
        self.assertIn("refuse overwrite", self.source)

    def test_unreal_automation_tasks_do_not_claim_art_pass(self):
        self.assertIn("UNREAL_SCREENSHOT_TASKS_COMPLETE_NATIVE_PNG_QA_PENDING", self.source)
        self.assertIn("reference_likeness_approved", self.source)
        self.assertIn("saved_unreal_map_modified", self.source)


if __name__ == "__main__":
    unittest.main()
