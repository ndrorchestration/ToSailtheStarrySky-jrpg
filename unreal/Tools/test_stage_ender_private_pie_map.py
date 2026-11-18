"""Engine-free fail-closed contract checks for the private PIE map generator."""
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name("stage_ender_private_pie_map.py").read_text(encoding="utf8")

class PrivatePIEMapSourceTests(unittest.TestCase):
    def test_private_destination_keeps_original_basename(self):
        self.assertIn('NAME = "FirstWake_PreludeInteraction_V5_VisualReview"', SOURCE)
        self.assertIn('SOURCE_LEVEL = "/Game/TSTSS/Review/" + NAME', SOURCE)
        self.assertIn('PRIVATE_LEVEL = PRIVATE + "/" + NAME', SOURCE)
        self.assertIn('subsystem.new_level_from_template(PRIVATE_LEVEL, SOURCE_LEVEL)', SOURCE)

    def test_private_game_mode_uses_only_new_player_class(self):
        for token in ('factory.set_editor_property("parent_class", gamemode_base)',
                      'game_cdo.set_editor_property("default_pawn_class", clone_class)',
                      'settings.set_editor_property("default_game_mode", mode_class)'):
            self.assertIn(token, SOURCE)
        self.assertIn('PRIVATE = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"', SOURCE)

    def test_gates_and_no_implicit_pie_or_production_map_save(self):
        for token in ('TSTSS_PRIVATE_ENDER_PIE_MAP', 'not git("status", "--porcelain=v1")',
                      '"OUTPUT_NOT_GIT_EXCLUDED"', '"PRIVATE_BP_NOT_BASELINE"',
                      '"PRIVATE_OPT_INS"', '"WRONG_EDITOR_WORLD_AFTER_CLONE"',
                      '"SOURCE_MAP_OR_BP_CHANGED"'):
            if token == '"PRIVATE_BP_NOT_BASELINE"':
                self.assertIn('"BP_CUSTODY"', SOURCE)
            else:
                self.assertIn(token, SOURCE)
        self.assertNotIn("editor_request_begin_play(", SOURCE)
        self.assertNotIn("editor_play_simulate(", SOURCE)
        self.assertNotIn("save_all_dirty_levels(", SOURCE)
        self.assertNotIn("unreal.EditorAssetLibrary.delete_", SOURCE)
        self.assertIn('"source_maps_saved": 0', SOURCE)
        self.assertIn('"actual_pie_started": False', SOURCE)

    def test_private_saves_scope_matches_target(self):
        self.assertIn('settings.get_outermost().get_name() == PRIVATE_LEVEL', SOURCE)
        self.assertIn('world.get_outermost().get_name() == PRIVATE_LEVEL and', SOURCE)
        self.assertIn('subsystem.save_current_level()', SOURCE)

    def test_only_git_ignored_outputs_and_source_hashes(self):
        self.assertIn('"check-ignore", "-q", rel', SOURCE)
        self.assertIn('REPORT["original_hashes_after"] == original', SOURCE)
        self.assertIn('"PRIVATE_V5_PIE_REVIEW_LEVEL_STAGED_NOT_PLAYED"', SOURCE)

if __name__ == "__main__":
    unittest.main()
