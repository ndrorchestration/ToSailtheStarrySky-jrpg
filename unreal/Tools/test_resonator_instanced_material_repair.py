"""Engine-free fail-closed contract tests for native Resonator instancing repair."""
from pathlib import Path
import unittest

UNREAL = Path(__file__).resolve().parents[1]
SCRIPT = (UNREAL / "Tools/repair_resonator_instanced_material_20261113.py"
          ).read_text(encoding="utf-8")
GENERATOR = (UNREAL / "Tools/build_ender_resonator_preview.py"
             ).read_text(encoding="utf-8")
ACTOR = (UNREAL / "Source/ToSailTheStarrySky/Private/TSTSSResonatorVfxActor.cpp"
         ).read_text(encoding="utf-8")


class ResonatorInstancingFixContract(unittest.TestCase):
    def test_single_existing_material_only(self):
        self.assertTrue((UNREAL / "Content/TSTSS/Magic/M_ResonatorGlow.uasset").is_file())
        self.assertIn('ASSET_REL = "unreal/Content/TSTSS/Magic/M_ResonatorGlow.uasset"', SCRIPT)
        self.assertIn('ASSET_PACKAGE = "/Game/TSTSS/Magic/M_ResonatorGlow"', SCRIPT)
        self.assertIn('EXPECTED_WORKTREE = "TSTSS_V5ObjectIntegration_20261112"', SCRIPT)
        self.assertIn('OPT_IN = "REPAIR_RESONATOR_INSTANCED_USAGE_ONLY"', SCRIPT)
        self.assertIn('TSTSS_RESONATOR_INSTANCING_HEAD', SCRIPT)
        self.assertIn('if mode == "APPLY"', SCRIPT)
        self.assertIn('if mode == "VERIFY"', SCRIPT)
        self.assertIn("MATUSAGE_INSTANCED_STATIC_MESHES", SCRIPT)
        self.assertIn("editor.set_base_material_usage(material, usage, True)", SCRIPT)
        self.assertIn("editor.has_material_usage(material, usage)", SCRIPT)
        self.assertIn("editor.recompile_material(material)", SCRIPT)
        self.assertIn("u.EditorAssetLibrary.save_loaded_asset(material)", SCRIPT)

    def test_native_readback_and_map_hash_gates(self):
        for term in (
            "get_dirty_map_packages()",
            "get_dirty_content_packages()",
            "not (after - {EDITOR_INI}).issubset({ASSET_REL})",
            "known_editor_ini_append()",
            "initial_maps",
            "sha(V5_MAP)",
            "sha(SHORE_MAP)",
            '"combat_unlock_or_story_changes": False',
            '"creator_visual_approval": False',
            '"status": "RESONATOR_INSTANCED_USAGE_SAVED"',
            '"RESONATOR_INSTANCED_USAGE_FRESH_READBACK_PASS"',
        ):
            self.assertIn(term, SCRIPT)
        for forbidden in (
            "OpenLevel(", "TryActivate(", "AdvanceTo(", "InspectStation(",
            "SetActorLocation(", "EditorLevelLibrary", "save_current_level",
            "save_map(", "subprocess.run([\"git\", \"push\"", "shutil.rmtree",
        ):
            self.assertNotIn(forbidden, SCRIPT)

    def test_original_vfx_geometry_uses_instanced_material(self):
        self.assertEqual(ACTOR.count("CreateDefaultSubobject<UInstancedStaticMeshComponent>"), 3)
        self.assertIn("M_ResonatorGlow.M_ResonatorGlow", ACTOR)
        self.assertIn("UMaterialInstanceDynamic::Create(Material, this)", ACTOR)
        self.assertIn("RingMeshes->SetMaterial(0, Dynamic)", ACTOR)
        self.assertIn("MoteMeshes->SetMaterial(0, Dynamic)", ACTOR)
        self.assertIn("CoreMesh->SetMaterial(0, Dynamic)", ACTOR)

    def test_future_authoring_also_preserves_instanced_material(self):
        self.assertIn("edit.set_base_material_usage(material, usage, True)", GENERATOR)
        self.assertIn("edit.has_material_usage(material, usage)", GENERATOR)
        self.assertIn("MATUSAGE_INSTANCED_STATIC_MESHES", GENERATOR)
        self.assertIn("Material already exists; refusing to overwrite", GENERATOR)


if __name__ == "__main__":
    unittest.main()
