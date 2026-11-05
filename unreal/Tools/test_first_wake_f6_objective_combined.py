"""Fail-closed source check: F6-only PIE saving + 16 objective assertions coexist.

No Unreal Editor, user files, disk saves or gameplay input is exercised here.
"""
import re
import unittest
from pathlib import Path
from test_first_wake_objective_continuity_transfer import failures

UNREAL = Path(__file__).resolve().parents[1]
PAWN = UNREAL / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
STATE = UNREAL / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeState.cpp"
TEST = UNREAL / "Source/ToSailTheStarrySky/Private/Tests/TSTSSFirstWakeInteractionIntegrationTests.cpp"
CONFIG = UNREAL / "Config/DefaultInput.ini"

def reconcile(pawn: str, config: str, native_test: str, state: str) -> list[str]:
    errors = failures(native_test, state)
    start = "void ATSTSSExplorerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)"
    end = "void ATSTSSExplorerCharacter::MoveForward(float Value)"
    if pawn.count(start) != 1 or pawn.count(end) != 1:
        return errors + ["Input setup method boundaries invalid"]
    binding = pawn.split(start, 1)[1].split(end, 1)[0]
    pie = "if (InputWorld && InputWorld->WorldType == EWorldType::PIE)"
    game = "else if (InputWorld && InputWorld->WorldType == EWorldType::Game)"
    if binding.count(pie) != 1 or binding.count(game) != 1:
        errors.append("Expected one PIE branch and one distinct normal-Game branch")
    else:
        before, after = binding.split(pie, 1)[1].split(game, 1)
        pie_save = 'BindAction(TEXT("PIEReviewQuickSave"), IE_Pressed'
        game_save = 'BindAction(TEXT("QuickSave"), IE_Pressed'
        if (before.count(pie_save) != 1 or game_save in before or
                after.count(game_save) != 1 or pie_save in after):
            errors.append("F6 PIE and F5 normal-game handlers are not isolated")
    entries = re.findall(
        r'^\+ActionMappings=\(ActionName="([^"]+)",Key=([^)]*)\)',
        config, flags=re.M)
    if entries.count(("PIEReviewQuickSave", "F6")) != 1 or (
            entries.count(("QuickSave", "F5")) != 1 or
            entries.count(("QuickLoad", "F9")) != 1 or
            len(set(entries)) != len(entries)):
        errors.append("Review F6 / Game F5 / F9 mapping missing or duplicated")
    quick_save = pawn.split("void ATSTSSExplorerCharacter::QuickSave()", 1)
    quick_load = pawn.split("void ATSTSSExplorerCharacter::QuickLoad()", 1)
    if len(quick_save) != 2 or len(quick_load) != 2:
        errors.append("Save method boundaries missing")
    else:
        save = quick_save[1].split("void ATSTSSExplorerCharacter::QuickLoad()", 1)[0]
        load = quick_load[1].split("bool ATSTSSExplorerCharacter::SaveFirstWake(", 1)[0]
        for token in (
            'EWorldType::PIE', 'EKeys::LeftShift', 'EKeys::RightShift',
            'bPIEReviewQuickSlotOwned', 'UGameplayStatics::DoesSaveGameExist(Slot, 0)',
            'TEXT("tstss_prelude_pie_quick")', 'TEXT("first_wake_quick")'):
            if token not in save:
                errors.append("PIE save refusal or slot separation missing: " + token)
        if 'bPIE && !bPIEReviewQuickSlotOwned' not in load:
            errors.append("PIE load can adopt old-session review saves")
    return errors


class CombinedF6ObjectiveGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pawn = PAWN.read_text(encoding="utf-8")
        cls.config = CONFIG.read_text(encoding="utf-8")
        cls.native = TEST.read_text(encoding="utf-8")
        cls.state = STATE.read_text(encoding="utf-8")

    def validate(self, **replace):
        inputs = dict(pawn=self.pawn, config=self.config,
                      native_test=self.native, state=self.state)
        inputs.update(replace)
        return reconcile(**inputs)

    def test_exact_combined_current_source(self):
        self.assertEqual(self.validate(), [])

    def test_pie_f5_binding_mutation_is_rejected(self):
        mutation = self.pawn.replace(
            'BindAction(TEXT("PIEReviewQuickSave"), IE_Pressed',
            'BindAction(TEXT("QuickSave"), IE_Pressed', 1)
        self.assertTrue(self.validate(pawn=mutation))

    def test_game_f6_binding_mutation_is_rejected(self):
        mutation = self.pawn.replace(
            'BindAction(TEXT("QuickSave"), IE_Pressed',
            'BindAction(TEXT("PIEReviewQuickSave"), IE_Pressed', 1)
        self.assertTrue(self.validate(pawn=mutation))

    def test_f6_mapping_removal_is_rejected(self):
        self.assertTrue(self.validate(
            config=self.config.replace('ActionName="PIEReviewQuickSave",Key=F6',
                                       'ActionName="PIEReviewQuickSave",Key=F5', 1)))

    def test_existing_slot_protection_removal_is_rejected(self):
        mutation = self.pawn.replace(
            'UGameplayStatics::DoesSaveGameExist(Slot, 0)',
            'false', 1)
        self.assertTrue(self.validate(pawn=mutation))

    def test_objective_regression_removed_is_rejected(self):
        mutation = self.native.replace(
            'TEXT("Recovered story has final review objective")',
            'TEXT("Deleted final objective check")', 1)
        self.assertTrue(self.validate(native_test=mutation))

if __name__ == "__main__":
    unittest.main()
