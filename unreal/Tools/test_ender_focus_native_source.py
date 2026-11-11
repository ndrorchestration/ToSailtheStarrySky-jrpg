"""Source-only negative preflight for Unreal review asset authoring."""
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase,main,mock
import build_ender_focus_native_review as native

class FocusNativeSourceTests(TestCase):
    def test_package_is_review_only(self):
        self.assertTrue(native.PACKAGE.startswith("/Game/TSTSS/Review/"))
        self.assertEqual(set(native.SOUNDS),{"SFX_Centering","SFX_ResonantPulse"})
    def test_other_project_denied(self):
        with TemporaryDirectory() as path:
            with self.assertRaisesRegex(RuntimeError,"isolated focus"):
                native.source_preflight(Path(path)/"unreal")
    def test_exact_head_required_before_git(self):
        with TemporaryDirectory() as path:
            target=Path(path)/"TSTSS_CenteringPulse_20261111"/"unreal"
            target.mkdir(parents=True)
            with mock.patch.dict(os.environ,{},clear=True):
                with self.assertRaisesRegex(RuntimeError,"exact commit"):
                    native.source_preflight(target)
    def test_no_unapproved_admission(self):
        src=Path(__file__).resolve().parents[1]/"DataSource/Magic/EnderResonator.vertical_slice.review.json"
        rows=json.loads(src.read_text(encoding="utf8"))
        self.assertEqual(len(rows),10)
        self.assertEqual({r["SkillId"] for r in rows
            if r["Admission"]=="ReviewExecutable"},
            {"Ender_Centering","Ender_ResonantPulse"})
if __name__=="__main__":main()
