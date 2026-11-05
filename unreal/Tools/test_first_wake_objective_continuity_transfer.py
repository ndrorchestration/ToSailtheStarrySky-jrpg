#!/usr/bin/env python3
"""Review-only bridge of the 16 distinct #734 objective regressions into #735.

Source consistency only: does NOT establish UE-native execution, input,
physical sea contact, persistence, rendered text readability or art approval.
"""
import re
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
NATIVE_TEST = ROOT / "Source/ToSailTheStarrySky/Private/Tests/TSTSSFirstWakeInteractionIntegrationTests.cpp"
STATE = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeState.cpp"

# Exact checkpoint order and creator-facing text from #734, no rewrites.
CHECKPOINTS = (
    ("Opening objective prompts Ender toward flyer", "Find Ionia's flyer", "Story"),
    ("Flyer changes objective to Captain Ionia", "Speak with Captain Ionia", "Story"),
    ("Rejected flyer keeps Ionia objective", "Speak with Captain Ionia", "Story"),
    ("Ionia hiring changes objective to ship boarding", "Board the Aureate Wake", "Story"),
    ("Boarding prompts lift inspection", "Inspect the levitation lift", "Story"),
    ("Lift check prompts pressure inspection", "Inspect the pressure systems", "Story"),
    ("Duplicate lift preserves pressure objective", "Inspect the pressure systems", "Story"),
    ("Pressure check prompts reserve inspection", "Inspect the reserve systems", "Story"),
    ("Three inspections prompt engineering signoff", "Complete engineering signoff", "Story"),
    ("Engineering signoff prompts launch", "Prepare for the First Wake launch", "Story"),
    ("Launch objective remains in Prelude flight", "Navigate the First Wake flight", "Story"),
    ("Sea contact prompts landing stabilization", "Stabilize the water landing", "Story"),
    ("Splashdown objective prompts empty reserve investigation", "Investigate the empty reserves", "Story"),
    ("Reserve inspection prompts berth recovery", "Return to berth", "Story"),
    ("Recovered story has final review objective", "First Wake review sequence complete", "Story"),
    ("Reset restores first objective", "Find Ionia's flyer", "Restored"),
)

EXTRACT = re.compile(
    r'TestEqual\(TEXT\("([^"]+)"\),\s*(Story|Restored)->GetReviewObjectiveText\(\),'
    r'\s*FString\(TEXT\("([^"]+)"\)\)\);'
)


def failures(native_source: str, state_source: str) -> list[str]:
    found = EXTRACT.findall(native_source)
    expected = [(label, actor, message) for label, message, actor in CHECKPOINTS]
    errors = []
    if found != expected:
        errors.append("Missing, duplicated, reordered or changed objective assertions")
    if native_source.count('"TSTSS.FirstWake.InteractionToSplashdown"') != 1:
        errors.append("Integration native test registration changed")
    if len(found) != 16:
        errors.append("Expected exactly sixteen source-visible native objective checks")
    for _, message, _ in CHECKPOINTS:
        if 'TEXT("' + message + '")' not in state_source:
            errors.append("Objective string missing from authoritative state: " + message)
    # Structural guard: opening and reset must bracket actual interaction checks.
    if (not native_source.index("Opening objective prompts Ender toward flyer")
            < native_source.index("Cannot board before discovering flyer")
            < native_source.index("Flyer changes objective to Captain Ionia")
            < native_source.index("Restored->Reset()")
            < native_source.index("Reset restores first objective")):
        errors.append("Opening/progression/reset checkpoint order changed")
    return errors


class FirstWakeObjectiveTransferSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = NATIVE_TEST.read_text(encoding="utf-8")
        cls.state = STATE.read_text(encoding="utf-8")

    def test_all_sixteen_native_checkpoints_present_in_order(self):
        self.assertEqual(failures(self.src, self.state), [])

    def test_remove_one_objective_fails_closed(self):
        source = self.src.replace(
            '    TestEqual(TEXT("Rejected flyer keeps Ionia objective"), Story->GetReviewObjectiveText(),\n'
            '        FString(TEXT("Speak with Captain Ionia")));\n', "", 1)
        self.assertTrue(failures(source, self.state))

    def test_mutate_incorrect_objective_fails_closed(self):
        source = self.src.replace(
            'TEXT("Pressure check prompts reserve inspection"), Story->GetReviewObjectiveText(),\n'
            '        FString(TEXT("Inspect the reserve systems"))',
            'TEXT("Pressure check prompts reserve inspection"), Story->GetReviewObjectiveText(),\n'
            '        FString(TEXT("Inspect the levitation lift"))', 1)
        self.assertTrue(failures(source, self.state))

    def test_wrong_story_object_for_progression_fails_closed(self):
        source = self.src.replace(
            'TEXT("Sea contact prompts landing stabilization"), Story->GetReviewObjectiveText()',
            'TEXT("Sea contact prompts landing stabilization"), Restored->GetReviewObjectiveText()', 1)
        self.assertTrue(failures(source, self.state))

    def test_changed_authoritative_string_fails_closed(self):
        state = self.state.replace('return TEXT("Return to berth");',
                                   'return TEXT("Navigate anywhere");', 1)
        self.assertTrue(failures(self.src, state))

    def test_objective_compiler_has_both_gnu_and_msvc_guarded_paths(self):
        helper = (TOOLS / "check_first_wake_objective_compiled.py").read_text(encoding="utf-8")
        for required in ('shutil.which("cl")', 'Path(compiler).name.lower() == "cl.exe"',
                         '"/std:c++17"', '"/W4"', '"/WX"', '"-std=c++17"',
                         '"-Werror"', 'tstss-objective-compiled-'):
            self.assertIn(required, helper)


if __name__ == "__main__":
    unittest.main()
