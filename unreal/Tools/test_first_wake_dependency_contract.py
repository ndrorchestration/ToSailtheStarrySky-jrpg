"""Source-only positive and negative dependency-contract controls.

All mutation tests work in memory, never editing actual manifests/lockfiles.
Passing means declarations match; it is not a native Unreal build or CVE scan.
"""
import copy
import unittest
from pathlib import Path

import check_first_wake_dependency_contract as checker


class FirstWakeDependencyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = checker.read_inputs()

    def assert_rejected(self, changed, expected):
        with self.assertRaisesRegex(checker.DependencyDrift, expected):
            checker.check_snapshot(*changed)

    def test_exact_checkout_source_declarations_match(self):
        result = checker.check_snapshot(*self.original)
        self.assertEqual(result["status"], "SOURCE_DECLARATIONS_MATCH_NOT_NATIVE_VERIFICATION")
        self.assertEqual(result["engine_family"], "5.8")
        self.assertEqual(result["module_count"], 5)
        self.assertEqual(result["enabled_plugins"], ["PythonScriptPlugin"])
        self.assertFalse(result["unreal_native_execution"])
        self.assertFalse(result["install_or_upgrade_performed"])

    def test_engine_family_change_must_be_reviewed(self):
        args = list(copy.deepcopy(self.original))
        args[1]["EngineAssociation"] = "5.9"
        self.assert_rejected(args, "engine family drift")

    def test_plugin_toggle_must_be_reviewed(self):
        args = list(copy.deepcopy(self.original))
        args[1]["Plugins"][0]["Enabled"] = False
        self.assert_rejected(args, "Enabled Unreal plugins")

    def test_explicit_plugin_list_cannot_silently_disappear(self):
        args = list(copy.deepcopy(self.original))
        args[1].pop("Plugins")
        self.assert_rejected(args, "Plugin list absent")

    def test_new_disabled_plugin_must_also_be_reviewed(self):
        args = list(copy.deepcopy(self.original))
        args[1]["Plugins"].append({"Name": "UnexpectedOptionalEditorPlugin", "Enabled": False})
        self.assert_rejected(args, "Project plugin declarations differ")

    def test_duplicate_disabled_plugin_is_rejected(self):
        args = list(copy.deepcopy(self.original))
        args[1]["Plugins"].extend([
            {"Name": "OptionalReview", "Enabled": False},
            {"Name": "OptionalReview", "Enabled": False},
        ])
        self.assert_rejected(args, "Duplicate project plugin")

    def test_native_module_loading_phase_drift(self):
        args = list(copy.deepcopy(self.original))
        args[1]["Modules"][0]["LoadingPhase"] = "PostEngineInit"
        self.assert_rejected(args, "module loading phase")

    def test_extra_public_dependency_add_not_hidden(self):
        args = list(copy.deepcopy(self.original))
        args[2] += '\nPublicDependencyModuleNames.Add("Slate");\n'
        self.assert_rejected(args, "Native module dependency drift")

    def test_private_cpp_module_addition_must_be_reviewed(self):
        args = list(copy.deepcopy(self.original))
        args[2] += '\nPrivateDependencyModuleNames.Add("Slate");\n'
        self.assert_rejected(args, "PrivateDependencyModuleNames declaration drift")

    def test_dynamic_cpp_module_addition_must_be_reviewed(self):
        args = list(copy.deepcopy(self.original))
        args[2] += '\nDynamicallyLoadedModuleNames.Add("OptionalRuntime");\n'
        self.assert_rejected(args, "DynamicallyLoadedModuleNames declaration drift")

    def test_nonliteral_native_dependency_declaration_fails_closed(self):
        args = list(copy.deepcopy(self.original))
        args[2] += '\nPrivateDependencyModuleNames.Add(SelectedModule);\n'
        self.assert_rejected(args, "Unparsed or nonliteral PrivateDependencyModuleNames")

    def test_extra_target_module_addition_must_be_reviewed(self):
        args = list(copy.deepcopy(self.original))
        args[3] += '\nExtraModuleNames.Add("Unexpected");\n'
        self.assert_rejected(args, "Game extra module drift")

    def test_cpp_module_addition_must_be_reviewed(self):
        args = list(copy.deepcopy(self.original))
        args[2] = args[2].replace('"InputCore"','"InputCore", "Slate"')
        self.assert_rejected(args, "Native module dependency drift")

    def test_editor_build_settings_change_must_be_reviewed(self):
        args = list(copy.deepcopy(self.original))
        args[4] = args[4].replace("BuildSettingsVersion.V7", "BuildSettingsVersion.V6")
        self.assert_rejected(args, "Editor build settings drift")

    def test_package_manifest_version_drift_must_be_reviewed(self):
        args = list(copy.deepcopy(self.original))
        args[5]["devDependencies"]["nw"] = "^0.117.0"
        self.assert_rejected(args, "Legacy npm dev dependency versions")

    def test_lockfile_root_inconsistency_must_be_reviewed(self):
        args = list(copy.deepcopy(self.original))
        args[6]["packages"][""]["devDependencies"]["playwright"] = "^1.64.0"
        self.assert_rejected(args, "Legacy lockfile root")

    def test_claim_of_native_build_in_baseline_is_refused(self):
        args = list(copy.deepcopy(self.original))
        args[0]["policy"]["native_unreal_build_verified"] = True
        self.assert_rejected(args, "Dependency contract weakened")

    def test_doc_links_existing_ownership_and_holds(self):
        doc = (checker.PROJECT / "Docs/FIRST_WAKE_DEPENDENCY_HANDOFF_2026-11-02.md").read_text(
            encoding="utf-8"
        )
        for token in ("#711", "#657", "PythonScriptPlugin", "25 named native",
                      "P01–P13", "NOT TESTED", "NOT AUTHORIZED",
                      "No dependency version was upgraded"):
            self.assertIn(token, doc)


if __name__ == "__main__":
    unittest.main()
