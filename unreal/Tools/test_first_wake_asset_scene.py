"""Source-side safeguards for draft native asset assembly. No Editor launch."""
import ast
import re
import unittest
from pathlib import Path

SOURCE = Path(__file__).with_name("stage_first_wake_asset_scene.py")
DOC = SOURCE.parents[1] / "Docs/FIRST_WAKE_ASSET_ASSEMBLY_2026_11_04.md"


class AssetWorldSourceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = SOURCE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.src, filename=str(SOURCE))

    def test_isolated_review_world_only(self):
        for token in (
            "TSTSS_AssetAssembly_20261104",
            "FirstWake_AssetAssembly_20261104_REVIEW",
            "FirstWake_PreludeInteraction_V2",
            "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80",
            "duplicate_asset(BASE_MAP, DEST_MAP)",
            "not DEST_FILE.exists()",
            "not RECEIPT.exists()",
            "BASE_FILE.is_file() and digest(BASE_FILE) == BASE_SHA",
            "Saved/SaveGames",
        ):
            self.assertIn(token, self.src)

    def test_seven_canonical_first_wake_stops_preserved(self):
        for stop in ("FlyerDiscovery", "IoniaHiring", "AureateBoarding",
                     "LiftStation", "PressureStation", "ReserveStation",
                     "EngineeringApproval"):
            self.assertIn('"' + stop + '"', self.src)
        self.assertIn("native map readback lost one or more staged assets", self.src)
        self.assertIn("native readback lost first-wake milestones", self.src)
        self.assertIn("original player start not preserved", self.src.replace("player start not preserved", "original player start not preserved"))

    def test_actual_existing_character_and_ship_packages_used(self):
        for mesh in ("AureateWake_Wing_Lookdev", "AureateWake_SharedExteriorTrim_V4_REVIEW",
                     "AureateWake_CoupledBridge_Geodesic_REVIEW",
                     "AureateWake_CurvedLivingQuarters_REVIEW",
                     "Ionia/Ionia/StaticMeshes/Ionia",
                     "Ender_ender_fidelity_v2/StaticMeshes/Ender_ender_fidelity_v2"):
            self.assertIn(mesh, self.src)
        self.assertIn('must(len(added) == 10', self.src)
        self.assertIn("isinstance(mesh, unreal.StaticMesh)", self.src)
        self.assertIn("material sections missing", self.src)

    def test_no_gameplay_or_canon_shortcuts(self):
        for marker in (
            '"pie_input_verified": False', '"cinematic_approval": False',
            '"collision_or_water_physics_verified": False',
            '"ender_rig_animation_verified": False',
            '"starbourne_player_unlocked": False',
            '"production_assets_modified": False',
            "set_actor_enable_collision(False)",
            "CollisionEnabled.NO_COLLISION",
            "IONIA_STATIC_REVIEW_NOT_NPC",
            "ENDER_STATIC_REVIEW_NOT_PAWN",
            "AUREATE_HULL_PROXY_NOT_APPROVED",
        ):
            self.assertIn(marker, self.src)
        for banned in ("SaveGameToSlot", "DeleteGameInSlot", "Remove-Item",
                       "git push --force", "merge_main", "open_level_in_editor"):
            self.assertNotIn(banned, self.src)

    def test_save_then_native_reload_before_pass(self):
        self.assertLess(self.src.index("duplicate_asset(BASE_MAP, DEST_MAP)"),
                        self.src.index("levels.save_current_level()"))
        self.assertLess(self.src.index("levels.save_current_level()"),
                        self.src.index("levels.load_level(DEST_MAP)), \"saved World cannot reload\""))
        self.assertLess(self.src.index("native map readback lost one or more staged assets"),
                        self.src.index('"status": "NATIVE_ASSET_WORLD_SAVED_AND_RELOADED_NOT_PIE"'))
        self.assertLess(self.src.index("digest(BASE_FILE) == BASE_SHA, \"original map changed during stage\""),
                        self.src.index('"status": "NATIVE_ASSET_WORLD_SAVED_AND_RELOADED_NOT_PIE"'))

    def test_documented_acceptance_holds(self):
        doc = DOC.read_text(encoding="utf-8")
        for phrase in ("NONCANONICAL", "Play in Editor", "Starbourne",
                       "Ender", "Ionia", "Aureate Wake", "not approved",
                       "not a playable acceptance"):
            self.assertIn(phrase, doc)


if __name__ == "__main__":
    unittest.main()
