"""Source-only mutation and custody tests for native-agnostic input binding probe."""
import unittest
from pathlib import Path
from check_first_wake_input_binding_compiled import (
    CHARACTER, CONFIG, PREFIX, SUFFIX, config_guard, method_from
)


class FirstWakeInputBindingProbeContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.character = CHARACTER.read_text(encoding="utf-8")
        cls.config = CONFIG.read_text(encoding="utf-8")

    def test_actual_method_and_current_config_are_admissible(self):
        src = method_from(self.character)
        self.assertIn('BindAction(TEXT("PIEReviewQuickSave"), IE_Pressed', src)
        self.assertIn('BindAction(TEXT("QuickSave"), IE_Pressed', src)
        self.assertIn('TEXT("ReviewEquipment"), IE_Pressed', src)
        self.assertIn("InputWorld->WorldType == EWorldType::PIE ||", src)
        self.assertIsNone(config_guard(self.config))

    def test_ambiguous_method_boundaries_rejected(self):
        with self.assertRaises(ValueError):
            method_from(self.character.replace(
                "void ATSTSSExplorerCharacter::MoveForward(float Value)",
                "void ATSTSSExplorerCharacter::MoveBackward(float Value)", 1))

    def test_f6_to_f5_config_mutation_rejected(self):
        with self.assertRaises(ValueError):
            config_guard(self.config.replace(
                'ActionName="PIEReviewQuickSave",Key=F6',
                'ActionName="PIEReviewQuickSave",Key=F5', 1))

    def test_removed_g_equipment_mapping_rejected(self):
        with self.assertRaises(ValueError):
            config_guard(self.config.replace(
                'ActionName="ReviewEquipment",Key=G',
                'ActionName="ReviewEquipment",Key=H', 1))

    def test_missing_g_binding_rejected_by_source_guard(self):
        src = self.character.replace('TEXT("ReviewEquipment")',
                                     'TEXT("MissingEquipmentReview")',1)
        with self.assertRaises(ValueError):
            method_from(src)

    def test_duplicate_f6_input_mapping_rejected(self):
        with self.assertRaises(ValueError):
            config_guard(self.config + '\n+ActionMappings=(ActionName="PIEReviewQuickSave",Key=F6)\n')

    def test_compiler_probe_executes_no_savegame_operation(self):
        # Actual pawn method under test only binds actions. It never executes
        # methods QuickSave/QuickLoad. Those bodies have separate checks.
        src = method_from(self.character)
        self.assertNotIn("SaveProgress(", src)
        self.assertNotIn("DoesSaveGameExist(", src)
        self.assertNotIn("SaveGames/", PREFIX + SUFFIX)
        self.assertIn("std::count(actions.begin()", SUFFIX)

    def test_probe_checks_pie_game_editor_and_missing_world(self):
        for token in ("EWorldType::PIE", "EWorldType::Game", "EWorldType::Editor",
                      "missingWorld", "PIE illegally binds normal F5 QuickSave",
                      "Normal Game illegally binds PIE F6 review save"):
            self.assertIn(token, PREFIX + SUFFIX)


if __name__ == "__main__":
    unittest.main()
