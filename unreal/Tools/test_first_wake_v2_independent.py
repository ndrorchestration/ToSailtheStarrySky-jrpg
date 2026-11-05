"""Source-only negative controls for an independent native First Wake V2 gate."""
import hashlib
from pathlib import Path
from unittest import TestCase, main, mock
import tempfile

import verify_first_wake_v2_independent as qa

PROJECT = Path(__file__).resolve().parents[1]


class IndependentV2GateTests(TestCase):
    def test_committed_v2_map_sha_is_exactly_locked(self):
        self.assertEqual(hashlib.sha256((PROJECT / qa.MAP_RELATIVE).read_bytes()).hexdigest(),
                         qa.MAP_SHA256)
        self.assertEqual(qa.MAP_PACKAGE, "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2")

    def test_original_sandbox_and_wrong_project_denied(self):
        # The *actual* independent checkout must be admitted, never rejected.
        # A missing or tampered copy is still refused by the map hash guard.
        if PROJECT.parent.name == qa.EXPECTED_PARENT:
            self.assertEqual(qa.project_guard(str(PROJECT)), PROJECT.resolve())
        else:
            with self.assertRaisesRegex(RuntimeError, "outside unique"):
                qa.project_guard(str(PROJECT))
        with tempfile.TemporaryDirectory() as parent:
            folder = Path(parent) / "NotTheIndependentSandbox" / "unreal"
            folder.mkdir(parents=True)
            with self.assertRaises(RuntimeError):
                qa.project_guard(str(folder))

    def test_wasd_camera_and_e_f5_f9_source_wiring(self):
        state = qa.inspect_input_source(PROJECT)
        self.assertFalse(state["player_keyboard_input_executed"])
        self.assertTrue(state["source_handlers_verified"])
        self.assertEqual(state["config_mapping_count"], 10)

    def test_fabricated_input_mapping_fails(self):
        with mock.patch.dict(qa.EXPECTED_ACTIONS, {"Interact": "Space"}, clear=False):
            with self.assertRaisesRegex(RuntimeError, "Missing gameplay input action"):
                qa.inspect_input_source(PROJECT)

    def test_missing_camera_bindings_fails(self):
        with mock.patch.object(qa, "EXPECTED_MAPPINGS",
                               qa.EXPECTED_MAPPINGS | {("Turn", "Thumbstick", "1.000000")}):
            with self.assertRaisesRegex(RuntimeError, "mapping drift"):
                qa.inspect_input_source(PROJECT)

    def test_pie_quicksave_cannot_reuse_production_slot(self):
        source = (PROJECT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(
            encoding="utf-8"
        )
        self.assertIn('bPIE ? TEXT("tstss_prelude_pie_quick") : TEXT("first_wake_quick")', source)
        self.assertIn("bPIEReviewQuickSlotOwned = false;", source)
        self.assertIn("UGameplayStatics::DoesSaveGameExist(Slot, 0)", source)

    def test_temp_save_slot_is_distinct_from_player_slot(self):
        self.assertNotEqual(qa.SLOT, "first_wake_quick")
        self.assertTrue(qa.SLOT.startswith("tstss_prelude_v2_independent"))
        self.assertLessEqual(len(qa.SLOT), 48)

    def test_native_source_requires_atomic_cleanup_and_no_game_map_save(self):
        source = Path(qa.__file__).read_text(encoding="utf-8")
        self.assertIn("if unreal.GameplayStatics.does_save_game_exist", source)
        self.assertIn("finally:", source)
        self.assertIn("unreal.GameplayStatics.delete_game_in_slot", source)
        self.assertIn('if sha(asset) != MAP_SHA256', source)
        self.assertIn('if output.exists()', source)
        self.assertNotIn("save_map(", source)
        self.assertNotIn("editor_request_begin_play(", source)
        self.assertNotIn("advance_water_beat", source)

    def test_duplicate_milestone_labels_forbidden(self):
        source = Path(qa.__file__).read_text(encoding="utf-8")
        self.assertIn('if label in by_name:', source)
        self.assertIn('if sum(isinstance(a, unreal.TSTSSMilestoneActor)', source)

    def test_source_does_not_claim_pie_or_art(self):
        source = Path(qa.__file__).read_text(encoding="utf-8")
        self.assertIn('"pie_keyboard_e_f5_f9_tested": False', source)
        self.assertIn('"actual_character_art_approved": False', source)
        self.assertIn('"chapter_one_act_one": False', source)


if __name__ == "__main__":
    main()
