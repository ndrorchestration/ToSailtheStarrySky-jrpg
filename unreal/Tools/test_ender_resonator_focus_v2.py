"""Source-only safety gates for game-mode-isolated V2 focus map."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase,main,mock
import stage_ender_resonator_focus_v2 as stage

class FocusV2Tests(TestCase):
    def test_additive_source_and_no_canon_map_overwrite(self):
        self.assertNotEqual(stage.V1,stage.V2)
        self.assertIn("/Game/TSTSS/Review/ResonatorFocus/",stage.V2)
        self.assertTrue(stage.V2.endswith("_V2"))
        text=Path(stage.__file__).read_text(encoding="utf8")
        for check in ("get_editor_property(\"default_game_mode\")",
                      "set_editor_property(\"default_game_mode\",cls)",
                      "EditorLoadingAndSavingUtils.save_map(world,V2)",
                      "hashlib.sha256(V1_FILE.read_bytes())",
                      "if V2_FILE.exists()",
                      "get_dirty_map_packages"):
            self.assertIn(check,text)
        self.assertNotIn("replace_existing",text)
    def test_reject_other_worktree(self):
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(RuntimeError,"dedicated review worktree"):
                stage.preflight(Path(temp)/"unreal")
    def test_no_native_authoring_without_commit_and_opt_in(self):
        with mock.patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(RuntimeError,"exact expected"):
                stage.preflight()
        with mock.patch.dict(os.environ,{stage.EXPECTED_ENV:"a"*40},clear=True):
            with self.assertRaisesRegex(RuntimeError,"explicitly authorized"):
                stage.preflight()
if __name__=="__main__":main()
