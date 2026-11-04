"""Source-only contracts for independent native asset-map readback.

No Unreal Editor is launched. Real native results require a separate commandlet,
exit verification, exact-stage receipt, hash custody, and per-actor mesh readback.
"""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "verify_first_wake_asset_scene_native.py"
STAGE = ROOT / "stage_first_wake_asset_scene.py"
DOC = ROOT.parent / "Docs/FIRST_WAKE_ASSET_ASSEMBLY_2026_11_04.md"


class NativeAssetReadbackSourceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = SCRIPT.read_text(encoding="utf-8")
        cls.stage = STAGE.read_text(encoding="utf-8")
        ast.parse(cls.src)
        ast.parse(cls.stage)

    def test_external_process_uses_saved_world_not_source_map(self):
        for token in (
            'FirstWake_AssetAssembly_20261104_REVIEW_V3',
            'first_wake_asset_scene_native_v3_20261104.json',
            'first_wake_asset_scene_readback_v3_20261104.json',
            'NATIVE_ASSET_WORLD_SAVED_PENDING_INDEPENDENT_READBACK',
            'level.load_level(stage["new_map_package"])',
            'OUT.exists()', 'sha(MAP_FILE)', 'sha(BASE_FILE)',
            'MAP_FILE) != stage["new_map_sha256"]',
        ):
            self.assertIn(token, self.src)

    def test_original_gameplay_actors_still_reflected(self):
        for stop in ("FlyerDiscovery", "IoniaHiring", "AureateBoarding",
                     "LiftStation", "PressureStation", "ReserveStation",
                     "EngineeringApproval"):
            self.assertIn('"' + stop + '"', self.src)
        self.assertIn('"TSTSS_PRELUDE_REVIEW_" + stop', self.src)
        self.assertIn('"TSTSSMilestoneActor"', self.src)
        self.assertIn('unreal.PlayerStart', self.src)

    def test_imported_native_mesh_paths_and_collision_checked(self):
        for name in ("AUREATE_HULL_PROXY_NOT_APPROVED",
                     "AUREATE_SHARED_V4_TRIM", "AUREATE_CURVED_QUARTERS",
                     "AUREATE_GEODESIC_BRIDGE", "AUREATE_FORE_PORT_LEAF",
                     "AUREATE_FORE_STARBOARD_LEAF", "AUREATE_AFT_PORT_LEAF",
                     "AUREATE_AFT_STARBOARD_LEAF",
                     "IONIA_STATIC_REVIEW_NOT_NPC",
                     "ENDER_STATIC_REVIEW_NOT_PAWN"):
            self.assertIn(name, self.src)
        for token in ("mesh.get_path_name()", "get_actor_enable_collision()",
                      "actor.get_component_by_class(unreal.StaticMeshComponent)",
                      "not isinstance(mesh, unreal.StaticMesh)",
                      'set(spec) != set(added)'):
            self.assertIn(token, self.src)

    def test_no_visual_or_playable_claim(self):
        for token in (
            '"real_player_input_verified": False',
            '"cinematic_art_approved": False',
            '"native_gpu_screenshot_produced": False',
            '"starbourne_player_unlocked": False',
            '"native_map_saved_during_readback": False',
            '"INDEPENDENT_NATIVE_SAVED_WORLD_READBACK_PASS_NOT_PIE"',
            'any("STARBOURNE" in label.upper() for label in labels)',
        ):
            self.assertIn(token, self.src)
        for operation in ("save_current_level(", "duplicate_asset(",
                          "new_level(", "SaveGameToSlot(", "DeleteGameInSlot("):
            self.assertNotIn(operation, self.src)

    def test_no_risky_change_to_original_staging_identity(self):
        self.assertIn("new_level_from_template(DEST_MAP, BASE_MAP)", self.stage)
        self.assertIn("TSTSS_PRELUDE_REVIEW_", self.stage)
        self.assertIn("NATIVE_ASSET_WORLD_SAVED_PENDING_INDEPENDENT_READBACK",
                      self.stage)
        self.assertIn("INDEPENDENT", DOC.read_text(encoding="utf-8").upper())


if __name__ == "__main__":
    unittest.main()
