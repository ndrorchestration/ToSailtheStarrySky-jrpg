"""Toolchain manifest and consent-guard regression; does not install software."""
from pathlib import Path
import json
import unittest

BASE = Path(__file__).resolve().parents[1]
MANIFEST = BASE / "Tools/TSTSS-UE58.vsconfig"
SETUP = BASE / "Tools/Prepare-UnrealBuildTools.ps1"


class UE58BuildToolsConfig(unittest.TestCase):
    def test_manifest_is_minimal_free_supported_cpp_sdk(self):
        obj = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(obj["version"], "1.0")
        expected = {
            "Microsoft.VisualStudio.Workload.VCTools",
            "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
            "Microsoft.VisualStudio.Component.Windows11SDK.26100",
        }
        self.assertEqual(set(obj["components"]), expected)
        self.assertEqual(len(obj["components"]), len(expected))

    def test_no_implicit_install_or_ue_engine_mutation(self):
        script = SETUP.read_text(encoding="utf-8")
        self.assertIn("[switch]$Install", script)
        self.assertIn("[switch]$AcceptPackageAgreements", script)
        self.assertLess(script.index("if (-not $Install) { exit 0 }"),
                        script.index("& $Command.Source @Arguments"))
        self.assertIn("if (-not $AcceptPackageAgreements)", script)
        self.assertIn("'--source', 'winget'", script)
        self.assertIn("'Microsoft.VisualStudio.BuildTools'", script)
        self.assertIn("'--passive --norestart --config", script)
        self.assertIn("'--accept-package-agreements'", script)
        self.assertIn("'--accept-source-agreements'", script)
        for forbidden in ("winget uninstall", "Remove-Item", "Stop-Process",
                          "EpicGamesLauncher.exe", "Engine/Build/BatchFiles"):
            self.assertNotIn(forbidden, script)

    def test_source_manifest_requires_all_three_components(self):
        script = SETUP.read_text(encoding="utf-8")
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for c in data["components"]:
            self.assertIn(c, script)
        self.assertIn("$Config.components -notcontains $Item", script)


if __name__ == "__main__":
    unittest.main()
