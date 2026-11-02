"""Source-side negative controls for Unreal runtime startup log claims."""
import unittest
from check_unreal_game_startup_log import inspect_startup_log

GOOD = """[t]LogInit: Engine startup
[t]LogWorld: CleanupWorld
[t]LogExit: Exiting.
Log file closed, 11/01/26 21:00:00
"""


class StartupLogEvidenceTests(unittest.TestCase):
    def test_complete_clean_log_passes_only_process_gate(self):
        x = inspect_startup_log(GOOD)
        self.assertEqual(x["status"], "UNREAL_PROCESS_LOG_CLEAN_NOT_GAMEPLAY_APPROVAL")
        self.assertTrue(x["shutdown_complete"])
        self.assertFalse(x["gameplay_tested"])
        self.assertFalse(x["editor_automation_tested"])

    def test_actual_bufferreader_failure_fails_closed(self):
        s = """LogInit: Engine
LogAssetRegistry: Error: Failed to load premade asset registry. LoadResult == 1.
LogWindows: Error: Assertion failed: ReaderPos + Num <= ReaderSize
LogWindows: Error: === Critical error: ===
LogWindows: Error: Crash in runnable thread IOThreadPool #2
LogExit: Exiting.
Log file closed, 11/01/26 21:00:00
"""
        with self.assertRaisesRegex(ValueError, "Unreal startup error"):
            inspect_startup_log(s)

    def test_missing_exit_fails_even_without_errors(self):
        with self.assertRaisesRegex(ValueError, "shutdown"):
            inspect_startup_log("LogInit: Engine startup")

    def test_missing_log_fails(self):
        with self.assertRaisesRegex(ValueError, "No Unreal startup log"):
            inspect_startup_log("")

    def test_registry_failure_alone_is_not_a_clean_game(self):
        with self.assertRaisesRegex(ValueError, "Unreal startup error"):
            inspect_startup_log(GOOD + "\nLogAssetRegistry: Error: Failed to load premade asset registry")

    def test_crash_even_if_exit_string_present_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unreal startup error"):
            inspect_startup_log(GOOD + "\nLogWindows: Error: Exception")

    def test_no_spurious_claim_from_completely_unrelated_log(self):
        with self.assertRaisesRegex(ValueError, "lifecycle"):
            inspect_startup_log("LogExit: Exiting.\nLog file closed,")


if __name__ == "__main__":
    unittest.main()
