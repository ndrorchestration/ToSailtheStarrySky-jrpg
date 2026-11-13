"""Static negative controls for native V5 material usage repair.

These tests cannot certify compiled shaders or visual appearance; a separate
UE 5.8.4 reopen/readback and standalone screenshot are required.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
UNREAL = ROOT / "unreal"
REPAIR = (UNREAL / "Tools/repair_first_wake_v5_instanced_material_usage.py"
          ).read_text(encoding="utf-8")
STAGING = (UNREAL / "Tools/stage_first_wake_v5_pbr_materials.py"
           ).read_text(encoding="utf-8")


class V5InstancedMaterialSafety(unittest.TestCase):
    def test_fixed_4_materials_existing_in_isolated_review_folder(self):
        for family in ("timber", "stone", "brass", "aether"):
            self.assertTrue((UNREAL / "Content/TSTSS/Review/PreludePBRV1"
                             / f"M_FW_{family}.uasset").is_file())
        self.assertIn('FAMILIES = ("timber", "stone", "brass", "aether")', REPAIR)
        self.assertIn('PACKAGE = "/Game/TSTSS/Review/PreludePBRV1"', REPAIR)
        self.assertNotIn('"ocean",', REPAIR)

    def test_native_usage_and_reopen_readback_are_required(self):
        self.assertIn("MATUSAGE_INSTANCED_STATIC_MESHES", REPAIR)
        self.assertIn("edit.set_base_material_usage(material, usage, True)", REPAIR)
        self.assertIn("edit.recompile_material(material)", REPAIR)
        self.assertIn("edit.has_material_usage(material, usage)", REPAIR)
        self.assertIn("u.EditorAssetLibrary.save_loaded_asset(material)", REPAIR)
        self.assertIn("args.verify", REPAIR)

    def test_no_unbounded_asset_or_source_changes(self):
        for token in (
            'EXPECTED_WORKTREE = "TSTSS_V5ObjectIntegration_20261112"',
            'OPT_IN = "REPAIR_V5_INSTANCED_MATERIALS_ONLY"',
            'TSTSS_V5_INSTANCING_EXPECTED_HEAD',
            "get_dirty_map_packages()",
            "get_dirty_content_packages()",
            "sha256(SOURCE_MAP)",
            "before_paths",
            "(after_paths - {editor_config}).issubset(allowed)",
            'result["status"]' if False else '"source_maps_edited": False',
            '"creator_approved": False',
        ):
            self.assertIn(token, REPAIR)
        for forbidden in (
            "save_current_level", "save_map(", "EditorLevelLibrary",
            "OpenLevel(", "TryActivate(", "AdvanceTo(", "InspectStation(",
            "SetActorLocation(", "Remove-Item", "shutil.rmtree",
            "git reset --hard", "git push",
        ):
            self.assertNotIn(forbidden, REPAIR)

    def test_future_asset_staging_creates_materials_with_instanced_usage(self):
        self.assertIn("editor.set_base_material_usage(", STAGING)
        self.assertIn("material, u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES, True", STAGING)
        self.assertIn("MATUSAGE_INSTANCED_STATIC_MESHES", STAGING)
        self.assertIn('if family != "ocean":', STAGING)


if __name__ == "__main__":
    unittest.main()
