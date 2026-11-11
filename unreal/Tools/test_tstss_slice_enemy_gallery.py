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
        self.assertEqual(len(plan["staged_enemy_ids"]),15)
        self.assertFalse(plan["native_3d_review_pass"])
        self.assertFalse(plan["species_or_revised_encounter_placement_approved"])
        self.assertFalse(plan["combat_player_actions_granted"])

    def test_fifteen_exact_distinct_slots(self):
        self.assertEqual(len(gallery.ENEMIES), 15)
        self.assertEqual(len(set(x[0] for x in gallery.ENEMIES)),15)
        self.assertEqual(len(set(x[1] for x in gallery.ENEMIES)),15)
        self.assertEqual([x[0] for x in gallery.GALLERY_FAMILIES],
                         ["Anomaly","Bandit","Flora","Aquatic","Fauna"])
        self.assertEqual(gallery.ENEMIES[5][1],"BanditCaptain")

    def test_reject_mutated_overlap(self):
        wrong = list(gallery.ENEMIES)
        name, kind, _x, y, caption = wrong[1]
        wrong[1] = (name, kind, -480.0, y, caption)
        with mock.patch.object(gallery,"ENEMIES",tuple(wrong)):
            with self.assertRaisesRegex(RuntimeError,"duplicate gallery placement"):
                gallery.validate_plan()

    def test_reject_duplicate_kind(self):
        wrong=list(gallery.ENEMIES)
        a=wrong[1]
        wrong[1]=(a[0],wrong[0][1],a[2],a[3],a[4])
        with mock.patch.object(gallery,"ENEMIES",tuple(wrong)):
            with self.assertRaisesRegex(RuntimeError,"unique enemy identities"):
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

    def test_reject_row_drift(self):
        wrong=list(gallery.ENEMIES)
        name,kind,x,y,caption=wrong[8]
        wrong[8]=(name,kind,x,y+3.0,caption)
        with mock.patch.object(gallery,"ENEMIES",tuple(wrong)):
            with self.assertRaisesRegex(RuntimeError,"category layout"):
                gallery.validate_plan()

    def test_reject_removed_family(self):
        with mock.patch.object(gallery,"GALLERY_FAMILIES",gallery.GALLERY_FAMILIES[:-1]):
            with self.assertRaisesRegex(RuntimeError,"aisle"):
                gallery.validate_plan()

    def test_source_catalog_and_gallery_kind_parity(self):
        import re
        root=Path(gallery.__file__).resolve().parents[1]
        header=(root/"Source/ToSailTheStarrySky/Public/Enemies/TSTSSSliceEnemyCatalog.h").read_text(encoding="utf-8")
        cpp=(root/"Source/ToSailTheStarrySky/Private/Enemies/TSTSSSliceEnemyCatalog.cpp").read_text(encoding="utf-8")
        actor=(root/"Source/ToSailTheStarrySky/Private/Enemies/TSTSSSliceEnemyActor.cpp").read_text(encoding="utf-8")
        kinds=[slot[1] for slot in gallery.ENEMIES]
        for kind in kinds:
            self.assertIn("    "+kind,header)
            self.assertIn("case ETSTSSSliceEnemyKind::"+kind+":",cpp)
            self.assertIn("case ETSTSSSliceEnemyKind::"+kind+":",actor)
        self.assertEqual(len(re.findall(r'AddRow\\(Table, TEXT\\("SliceReview_',cpp)),30)


if __name__ == "__main__":
    main()
