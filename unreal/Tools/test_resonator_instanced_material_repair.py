"""Strict source scope checks for the ISOLATED Resonator instanced shader copy."""
from pathlib import Path
import hashlib
import unittest

UNREAL = Path(__file__).resolve().parents[1]
SCRIPT = (UNREAL / "Tools/repair_resonator_instanced_material_20261113.py"
          ).read_text(encoding="utf-8")
CREATOR = (UNREAL / "Tools/build_ender_resonator_preview.py"
           ).read_text(encoding="utf-8")
ACTOR = (UNREAL / "Source/ToSailTheStarrySky/Private/TSTSSResonatorVfxActor.cpp"
         ).read_text(encoding="utf-8")
ORIGINAL = UNREAL / "Content/TSTSS/Magic/M_ResonatorGlow.uasset"
REVIEW = (UNREAL / "Content/TSTSS/Review/ResonatorMaterialV1/"
          "M_ResonatorGlow_InstancedReview.uasset")
ORIGINAL_HASH = "117698d8314f2afecdefa5feacf8778dd443abd61443df8768db234b3d85d20b"


class ResonatorInstancedReviewMaterialTests(unittest.TestCase):
    def test_original_material_and_historical_creator_remain_immutable(self):
        self.assertTrue(ORIGINAL.is_file())
        self.assertEqual(hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(), ORIGINAL_HASH)
        self.assertIn("ORIGINAL_SHA256 = ", SCRIPT)
        self.assertIn("sha(ORIGINAL) != ORIGINAL_SHA256", SCRIPT)
        self.assertIn("Material already exists; refusing to overwrite", CREATOR)
        self.assertNotIn("MATUSAGE_INSTANCED_STATIC_MESHES", CREATOR)

    def test_new_review_namespace_is_single_native_material_asset(self):
        self.assertIn('REVIEW_DIR = "/Game/TSTSS/Review/ResonatorMaterialV1"', SCRIPT)
        self.assertIn("M_ResonatorGlow_InstancedReview", SCRIPT)
        self.assertIn("u.EditorAssetLibrary.duplicate_asset(", SCRIPT)
        self.assertIn("ORIGINAL_PACKAGE, REVIEW_PACKAGE", SCRIPT)
        self.assertIn("MATUSAGE_INSTANCED_STATIC_MESHES", SCRIPT)
        self.assertIn("editor.set_base_material_usage(material, usage, True)", SCRIPT)
        self.assertIn("editor.has_material_usage(material, usage)", SCRIPT)
        self.assertIn("editor.recompile_material(material)", SCRIPT)
        self.assertIn("u.EditorAssetLibrary.save_loaded_asset(material)", SCRIPT)
        self.assertIn("not (after - {EDITOR_INI}).issubset({REVIEW_REL})", SCRIPT)

    def test_deny_unknown_worlds_and_mutating_story(self):
        for token in (
            "TSTSS_RESONATOR_INSTANCING_HEAD",
            "TSTSS_RESONATOR_INSTANCING_OPT_IN",
            "CREATE_ISOLATED_RESONATOR_INSTANCED_REVIEW_ONLY",
            "EXPECTED_WORKTREE = ",
            "known_editor_ini_append()",
            "get_dirty_map_packages()",
            "get_dirty_content_packages()",
            'sha(V5_MAP)', 'sha(SHORE_MAP)',
            '"historical_snapshot_modified": False',
            '"story_or_spell_authority_changed": False',
            '"creator_visual_approval": False',
        ):
            self.assertIn(token, SCRIPT)
        for forbidden in (
            "save_current_level(", "save_map(", "OpenLevel(", "AdvanceTo(",
            "InspectStation(", "TryActivate(", "SetActorLocation(", "rmtree(",
            "git push", "git reset --hard",
        ):
            self.assertNotIn(forbidden, SCRIPT)

    def test_live_runtime_prefers_review_copy_only_in_explicit_review_scenes(self):
        for token in (
            '#if WITH_EDITOR',
            'ReviewWorld->WorldType == EWorldType::PIE',
            'ReviewWorld->WorldType == EWorldType::Game',
            'ReviewWorld->GetNetMode() == NM_Standalone',
            'StartsWith(',
            'TEXT("/Game/TSTSS/Review/")',
            'Scene == TEXT("L_VS06_ShoreMagicEnemyGear_Review")',
            'Scene == TEXT("L_EnderResonatorFocusReview_V2")',
            "M_ResonatorGlow_InstancedReview",
            "TSTSS_RESONATOR_REVIEW_INSTANCED_MATERIAL_APPLIED",
            "TSTSS_RESONATOR_REVIEW_INSTANCED_MATERIAL_HOLD",
            'TEXT("/Game/TSTSS/Magic/M_ResonatorGlow.M_ResonatorGlow")',
        ):
            self.assertIn(token, ACTOR)
        self.assertEqual(ACTOR.count("CreateDefaultSubobject<UInstancedStaticMeshComponent>"), 3)
        self.assertIn("UMaterialInstanceDynamic::Create(Material, this)", ACTOR)
        self.assertIn("RingMeshes->SetMaterial(0, Dynamic)", ACTOR)
        self.assertIn("MoteMeshes->SetMaterial(0, Dynamic)", ACTOR)
        self.assertIn("CoreMesh->SetMaterial(0, Dynamic)", ACTOR)

    def test_new_asset_can_only_be_appended_to_separate_review_location(self):
        if REVIEW.exists():
            self.assertGreater(REVIEW.stat().st_size, 1000)
        # The 222-file sealed MultipathV1 snapshot cannot grow at all.
        self.assertNotIn("/Game/TSTSS/Review/MultipathV1/", SCRIPT)
        self.assertNotIn('M_ResonatorGlow_InstancedReview', CREATOR)


if __name__ == "__main__":
    unittest.main()
