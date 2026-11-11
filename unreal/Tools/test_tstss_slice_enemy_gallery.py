"""Portable, negative-heavy gallery authoring tests. Do not start Unreal."""
import os
from pathlib import Path
import tempfile
from unittest import TestCase, main, mock

import tstss_slice_enemy_gallery as gallery


class SourceOnlyGalleryTests(TestCase):
    def test_no_unreal_import_in_plan(self):
        plan=gallery.validate_plan()
        self.assertEqual(plan["status"],gallery.PREVIEW_STATUS)
        self.assertEqual(len(plan["staged_enemy_ids"]),3)
        self.assertFalse(plan["native_3d_review_pass"])
        self.assertFalse(plan["species_or_revised_encounter_placement_approved"])
        self.assertFalse(plan["combat_player_actions_granted"])

    def test_three_exact_distinct_slots(self):
        self.assertEqual([x[1] for x in gallery.ENEMIES],
                         ["HarmonicShear","AetherLeakWisp","DockSkitter"])
        self.assertEqual(len(set(x[0] for x in gallery.ENEMIES)),3)

    def test_reject_mutated_overlap(self):
        with mock.patch.object(gallery,"ENEMIES",(
            ("FoeA","HarmonicShear",0,"x"),
            ("FoeB","AetherLeakWisp",10,"x"),
            ("FoeC","DockSkitter",50,"x"))):
            with self.assertRaisesRegex(RuntimeError,"overlap"):
                gallery.validate_plan()

    def test_reject_duplicate_kind(self):
        with mock.patch.object(gallery,"ENEMIES",(
            ("FoeA","HarmonicShear",-500,"x"),
            ("FoeB","HarmonicShear",0,"x"),
            ("FoeC","DockSkitter",500,"x"))):
            with self.assertRaisesRegex(RuntimeError,"distinct"):
                gallery.validate_plan()

    def test_reject_unknown_enum(self):
        class FakeEnum:
            HARMONIC_SHEAR = 1
        self.assertEqual(gallery.enum_member(FakeEnum,"HarmonicShear"),1)
        with self.assertRaisesRegex(RuntimeError,"mismatch"):
            gallery.enum_member(FakeEnum,"DockSkitter")

    def test_reject_foreign_project_before_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(gallery.subprocess,"run") as run:
                with self.assertRaisesRegex(RuntimeError,"named disposable"):
                    gallery.checked_sandbox(Path(tmp)/"unreal")
                run.assert_not_called()

    def test_reject_missing_exact_head_before_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/gallery.SANDBOX_NAME/"unreal"
            root.mkdir(parents=True)
            with mock.patch.dict(os.environ,{},clear=True):
                with mock.patch.object(gallery.subprocess,"run") as run:
                    with self.assertRaisesRegex(RuntimeError,"full exact"):
                        gallery.checked_sandbox(root)
                    run.assert_not_called()

    def test_reject_dirty_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/gallery.SANDBOX_NAME/"unreal"
            root.mkdir(parents=True)
            def run_git(cmd,**_):
                value = "a"*40 if "rev-parse" in cmd else "?? unsafe.umap"
                return mock.Mock(returncode=0,stdout=value)
            with mock.patch.dict(os.environ,{gallery.ENV_SHA:"a"*40}):
                with mock.patch.object(gallery.subprocess,"run",side_effect=run_git):
                    with self.assertRaisesRegex(RuntimeError,"initially clean"):
                        gallery.checked_sandbox(root)

    def test_reject_existing_gallery_before_unreal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/gallery.SANDBOX_NAME/"unreal"
            (root/"Config").mkdir(parents=True)
            (root/"Config"/"DefaultEngine.ini").write_text("",encoding="utf-8")
            (root/"Config"/"DefaultInput.ini").write_text("",encoding="utf-8")
            target=root/gallery.MAP_FILE
            target.parent.mkdir(parents=True)
            target.write_bytes(b"protected-existing-map")
            original=target.read_bytes()
            def git(cmd,**_):
                return mock.Mock(returncode=0,stdout="b"*40 if "rev-parse" in cmd else "")
            with mock.patch.dict(os.environ,{gallery.ENV_SHA:"b"*40}):
                with mock.patch.object(gallery.subprocess,"run",side_effect=git):
                    with self.assertRaisesRegex(RuntimeError,"refuse overwrite"):
                        gallery.checked_sandbox(root)
            self.assertEqual(target.read_bytes(),original)


if __name__ == "__main__":
    main()
