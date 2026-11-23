"""Fail-closed guards for read-only template-source evidence."""
import ast
import unittest
from pathlib import Path

SOURCE = (Path(__file__).parent / "audit_ender_directional_template_sources.py").read_text(encoding="utf8")


class DirectionalTemplateInventorySourceTests(unittest.TestCase):
    def test_parse_and_six_distinct_locked_candidates(self):
        ast.parse(SOURCE)
        for name in ("Walk_Bwd", "Walk_Left", "Walk_Right",
                     "Jog_Bwd", "Jog_Left", "Jog_Right"):
            self.assertIn("MF_Unarmed_" + name + ".uasset", SOURCE)
        self.assertEqual(SOURCE.count('"Walk/MF_Unarmed_Walk_') +
                         SOURCE.count('"Jog/MF_Unarmed_Jog_'), 6)

    def test_exact_head_and_no_existing_receipt(self):
        for gate in ("expected-head", "SOURCE_CHANGED", "RECEIPT_PATH",
                     "INVALID_HEAD", "SIZE_", "HASH_", "sha256",
                     "source_copied_or_modified"):
            self.assertIn(gate, SOURCE)

    def test_read_only_with_unapproved_retarget_explicit(self):
        for field in ("NOT_RETARGETED", "NOT_TESTED", "NOT_EXECUTED",
                      "NOT_ESTABLISHED"):
            self.assertIn(field, SOURCE)
        for forbidden in ("shutil.copy(", "copyfile(", "rename(", "os.remove(",
                          "EditorAssetLibrary", "AssetToolsHelpers",
                          "unreal.save", "subprocess.Popen(", "git push"):
            self.assertNotIn(forbidden, SOURCE)


if __name__ == "__main__":
    unittest.main()
