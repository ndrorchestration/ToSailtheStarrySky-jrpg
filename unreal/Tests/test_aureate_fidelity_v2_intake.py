"""Source-side safe native-import contract; no Unreal Editor required."""
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ART=Path(__file__).resolve().parents[1]/"ArtSource"/"ShipReview"
sys.path.insert(0,str(ART))
import build_aureate_fidelity_v2 as generator
import import_aureate_fidelity_v2 as intake


class NativeV2ImportSafetyTests(unittest.TestCase):
    def test_source_integrity_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            generator.write_or_verify(Path(tmp),True)
            result=intake.inspect(Path(tmp))
            self.assertEqual(result["stage"],"REGENERATED_SOURCE_ONLY_NOT_NATIVE")
            self.assertEqual(set(result["sha256"]),set(generator.FILES))
            self.assertFalse(result["orbiter_authorized"])
            self.assertFalse(result["creator_3d_art_approval"])

    def test_tampered_manifest_or_mesh_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            generator.write_or_verify(folder,True)
            part=folder/generator.FILES[1]
            blob=part.read_bytes()
            part.write_bytes(blob[:-1]+bytes([blob[-1]^1]))
            with self.assertRaisesRegex(intake.FidelityImportHold,"mismatch"):
                intake.inspect(folder)

    def test_actual_unreal_missing_fails_closed(self):
        with patch.dict(sys.modules,{"unreal":None}):
            with self.assertRaisesRegex(intake.FidelityImportHold,"real Unreal Editor"):
                intake.import_in_editor(Path("."),{})

    def test_nonreview_import_paths_prohibited(self):
        self.assertEqual(len(intake.DESTINATIONS),2)
        self.assertNotEqual(*intake.DESTINATIONS)
        for path in intake.DESTINATIONS:
            self.assertTrue(path.startswith("/Game/TSTSS/Review/ShipArt/"))
        src=(ART/"import_aureate_fidelity_v2.py").read_text()
        self.assertIn('("replace_existing",False)',src.replace("set_editor_property",""))
        self.assertNotIn("RequestForm(",src)
        self.assertNotIn("save_map(",src)

    def test_ue_bounds_accept_correct_axes_only(self):
        class Mesh:
            def __init__(self,x,y,z):
                self.box_extent=types.SimpleNamespace(x=x/2,y=y/2,z=z/2)
        self.assertTrue(intake.bounds_ok(Mesh(798,210,82),intake.EXTENT_BANDS_CM[0]))
        self.assertTrue(intake.bounds_ok(Mesh(188,110,125),intake.EXTENT_BANDS_CM[1]))
        self.assertFalse(intake.bounds_ok(Mesh(82,210,798),intake.EXTENT_BANDS_CM[0]))
        self.assertFalse(intake.bounds_ok(Mesh(1880,1100,1250),intake.EXTENT_BANDS_CM[1]))
        self.assertFalse(intake.bounds_ok(object(),intake.EXTENT_BANDS_CM[0]))

    def test_preflight_requires_complete_actual_binary_audit(self):
        from audit_aureate_v2_glb_geometry import GeometryHold
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            generator.write_or_verify(folder,True)
            with patch("audit_aureate_v2_glb_geometry.audit_binary",
                       side_effect=GeometryHold("Forensic test rejection")):
                with self.assertRaisesRegex(intake.FidelityImportHold,"binary geometry audit"):
                    intake.inspect(folder)

    def test_direct_import_requires_fresh_complete_source_receipt(self):
        class Unreal:
            EditorAssetLibrary=type("EditorAssetLibrary",(),{})
            AssetImportTask=type("AssetImportTask",(),{})
            AssetToolsHelpers=type("AssetToolsHelpers",(),{})
            StaticMesh=type("StaticMesh",(),{})
            load_asset=staticmethod(lambda x:None)
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            generator.write_or_verify(folder,True)
            with patch.dict(sys.modules,{"unreal":Unreal}):
                with self.assertRaisesRegex(intake.FidelityImportHold,"Stale or incomplete"):
                    intake.import_in_editor(folder,{"stage":"REGENERATED_SOURCE_ONLY_NOT_NATIVE"})
                # No folder interactions or import tasks can occur for forged receipts.

    def test_preexisting_review_folder_refuses_import_before_ue_mutation(self):
        calls=[]
        class AssetLibrary:
            @staticmethod
            def does_directory_exist(path):
                calls.append(("exists",path))
                return True
            @staticmethod
            def list_assets(path,recursive=True,include_folder=False):
                calls.append(("list",path))
                return [path+"/Existing.Existing"]
        class Unreal:
            EditorAssetLibrary=AssetLibrary
            AssetImportTask=type("AssetImportTask",(),{})
            AssetToolsHelpers=type("AssetToolsHelpers",(),{})
            StaticMesh=type("StaticMesh",(),{})
            load_asset=staticmethod(lambda x:None)
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            generator.write_or_verify(folder,True)
            preflight=intake.inspect(folder)
            with patch.dict(sys.modules,{"unreal":Unreal}):
                with self.assertRaisesRegex(intake.FidelityImportHold,"already populated"):
                    intake.import_in_editor(folder,preflight)
        self.assertEqual(len(calls),2)


if __name__=="__main__":
    unittest.main()
