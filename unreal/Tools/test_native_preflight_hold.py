#!/usr/bin/env python3
"""Source-only checks for the non-destructive native Windows build preflight.
These are NOT Unreal build, editor, or runtime tests.
"""
from pathlib import Path
import unittest

SCRIPT = (Path(__file__).resolve().parents[1] / "Tools" / "Verify-Unreal.ps1")


class NativePreflightHoldSourceTests(unittest.TestCase):
    def test_editor_and_build_processes_are_checked_before_evidence_or_build(self):
        source = SCRIPT.read_text(encoding="utf-8")
        editor = source.index("Get-Process -Name UnrealEditor,UnrealEditor-Cmd")
        build = source.index("Get-CimInstance Win32_Process")
        receipt = source.index("Set-Content (Join-Path $Evidence 'head.txt')")
        invoke = source.index("& $BuildTool ToSailTheStarrySkyEditor")
        self.assertLess(editor, receipt)
        self.assertLess(build, receipt)
        self.assertLess(build, invoke)

    def test_native_editor_automation_cannot_rewrite_tracked_config(self):
        source = SCRIPT.read_text(encoding="utf-8")
        launch = next(line for line in source.splitlines()
                      if line.lstrip().startswith("& $EditorCmd $Project"))
        self.assertIn(" -NOINI ", launch)
        self.assertIn(" -nowrite ", launch)
        self.assertIn(" -NOAUTOINIUPDATE ", launch)
        self.assertIn("'-DisablePlugins=AndroidFileServer'", launch)
        self.assertNotIn("-NoEnginePlugins", launch)
        self.assertIn("-nullrhi", launch)
        self.assertIn("Automation RunTests TSTSS; Quit", launch)
        self.assertIn("Working tree changed during verification; refusing to bind PASS", source)
        self.assertIn("git -C (Join-Path $PSScriptRoot '../..') status --porcelain", source)

    def test_guards_explicitly_fail_closed_and_preserve_unrelated_processes(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("if ($ActiveEditors.Count -ne 0)", source)
        self.assertIn("if ($ExistingBuilds.Count -ne 0)", source)
        self.assertIn("cannot safely inspect competing Unreal builds", source)
        self.assertIn("Native verification HOLD", source)
        self.assertNotIn("Stop-Process", source)
        self.assertNotIn("taskkill", source)


if __name__ == "__main__":
    unittest.main()
