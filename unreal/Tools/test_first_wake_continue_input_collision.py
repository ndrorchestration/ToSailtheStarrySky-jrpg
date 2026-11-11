"""Source-only fail-closed check that PIE save and explicit Continue cannot collide."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
CONFIG = (ROOT / "Config/DefaultInput.ini").read_text(encoding="utf-8")
HUD = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeReviewHUD.cpp").read_text(encoding="utf-8")

def actions(config):
    result = {}
    for name, key in re.findall(r'\+ActionMappings=\(ActionName="([^"]+)",Key=([^,)]+)', config):
        result.setdefault(key, []).append(name)
    return result

class ContinueInputSeparationTests(unittest.TestCase):
    def test_pie_save_continue_and_load_have_independent_keys(self):
        mapping = actions(CONFIG)
        self.assertEqual(mapping.get("F6"), ["PIEReviewQuickSave"])
        self.assertEqual(mapping.get("F7"), ["ReviewContinue"])
        self.assertEqual(mapping.get("F9"), ["QuickLoad"])
        self.assertEqual(mapping.get("F5"), ["QuickSave"])
        self.assertEqual(len({*mapping.get("F5", []), *mapping.get("F6", []), *mapping.get("F7", []), *mapping.get("F9", [])}), 4)

    def test_pie_vs_game_binding_is_explicit(self):
        input_body = SOURCE.split("void ATSTSSExplorerCharacter::SetupPlayerInputComponent", 1)[1].split("void ATSTSSExplorerCharacter::MoveForward",1)[0]
        self.assertIn("InputWorld->WorldType == EWorldType::PIE", input_body)
        self.assertIn("InputWorld->WorldType == EWorldType::Game", input_body)
        self.assertIn('BindAction(TEXT("PIEReviewQuickSave")', input_body)
        self.assertIn('BindAction(TEXT("QuickSave")', input_body)
        self.assertIn('BindAction(TEXT("ReviewContinue")', input_body)
        self.assertIn('BindAction(TEXT("QuickLoad")', input_body)

    def test_editor_shortcut_shift_f5_cannot_write_pie_slot(self):
        save_body = SOURCE.split("void ATSTSSExplorerCharacter::QuickSave()",1)[1].split("void ATSTSSExplorerCharacter::QuickLoad()",1)[0]
        self.assertIn("PC->IsInputKeyDown(EKeys::LeftShift)", save_body)
        self.assertIn("PC->IsInputKeyDown(EKeys::RightShift)", save_body)
        self.assertIn('TEXT("tstss_prelude_pie_quick")',save_body)
        self.assertIn("if (bPIE && !bPIEReviewQuickSlotOwned", save_body)

    def test_continue_uses_two_press_guard_without_silent_restore(self):
        body = SOURCE.split("void ATSTSSExplorerCharacter::ReviewContinue()",1)[1]
        self.assertIn("bPendingReviewContinue",body)
        self.assertIn("World->GetTimeSeconds() + 30.f",body)
        self.assertIn("bPIEReviewQuickSlotOwned",body)
        self.assertIn("TSTSS_PIE_REVIEW_CONTINUE_PREVIEW",body)
        self.assertIn("TSTSS_PIE_REVIEW_CONTINUE_ACCEPT",body)
        self.assertIn("F7 AGAIN", body)
        self.assertLess(body.index("if (!bConfirm)"),body.index("LoadFirstWake(ReviewPrimarySlot)"))

    def test_hud_names_exact_pie_keys(self):
        self.assertIn("PIE F6: save F9: load", HUD)
        self.assertIn("F7: Continue preview/confirm",HUD)
        self.assertNotIn("F6: Continue",HUD)

    def test_collision_mutation_rejected(self):
        mutated = CONFIG.replace('ActionName="ReviewContinue",Key=F7',
                                 'ActionName="ReviewContinue",Key=F6')
        self.assertNotEqual(actions(mutated).get("F6"), ["PIEReviewQuickSave"])
        self.assertEqual(len(actions(mutated).get("F6")), 2)

if __name__ == "__main__":
    unittest.main()
