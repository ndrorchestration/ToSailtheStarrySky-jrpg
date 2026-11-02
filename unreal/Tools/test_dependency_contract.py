"""Negative controls for the declared Unreal/legacy dependency baseline."""
from pathlib import Path
from tempfile import TemporaryDirectory
import copy
import json
import shutil
import unittest

from check_dependency_contract import DependencyDrift, validate

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    "unreal/Tools/dependency_baseline.json",
    "unreal/ToSailTheStarrySky.uproject",
    "unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs",
    "unreal/Source/ToSailTheStarrySky.Target.cs",
    "unreal/Source/ToSailTheStarrySkyEditor.Target.cs",
    "package.json",
    "package-lock.json",
]


class DependencyDeclarationContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative in FILES:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def tearDown(self):
        self.temp.cleanup()

    def rewrite_json(self, path, edit):
        target = self.root / path
        data = json.loads(target.read_text(encoding="utf-8"))
        edit(data)
        target.write_text(json.dumps(data), encoding="utf-8")

    def test_ci_triggers_when_declared_dependencies_change(self):
        workflow = (ROOT/".github/workflows/unreal-source-preflight.yml").read_text(encoding="utf-8")
        for path in (
            "unreal/Source/**",
            "unreal/Tools/**",
            "unreal/ToSailTheStarrySky.uproject",
            "package.json",
            "package-lock.json",
        ):
            with self.subTest(path=path):
                self.assertIn("- '" + path + "'", workflow)

    def test_actual_declarations_match_inventory(self):
        check = validate(ROOT)
        self.assertEqual(check["engine_association"], "5.8")
        self.assertIn("PythonScriptPlugin", check["enabled_project_plugins"])
        self.assertFalse(check["runtime_build_executed"])

    def test_copy_matches_inventory(self):
        self.assertEqual(validate(self.root)["legacy_package_count"], 4)

    def test_engine_family_mismatch_refused(self):
        self.rewrite_json("unreal/ToSailTheStarrySky.uproject",
                          lambda data: data.update(EngineAssociation="5.9"))
        with self.assertRaisesRegex(DependencyDrift, "engine association"):
            validate(self.root)

    def test_unreviewed_plugin_rejected(self):
        self.rewrite_json("unreal/ToSailTheStarrySky.uproject",
                          lambda data: data["Plugins"].append({"Name": "NewRenderingAddon", "Enabled": True}))
        with self.assertRaisesRegex(DependencyDrift, "plugin"):
            validate(self.root)

    def test_cplusplus_module_dependency_change_rejected(self):
        p = self.root/"unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs"
        p.write_text(p.read_text(encoding="utf-8").replace('"InputCore"', '"Niagara"'),
                     encoding="utf-8")
        with self.assertRaisesRegex(DependencyDrift, "module dependencies"):
            validate(self.root)

    def test_unreviewed_single_module_add_is_detected(self):
        p = self.root/"unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs"
        text = p.read_text(encoding="utf-8").replace(
            'PublicDependencyModuleNames.AddRange(',
            'PublicDependencyModuleNames.Add("Niagara");\n        PublicDependencyModuleNames.AddRange('
        )
        p.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(DependencyDrift, "module dependencies"):
            validate(self.root)

    def test_dynamic_module_add_expression_fails_closed(self):
        p = self.root/"unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs"
        p.write_text(
            p.read_text(encoding="utf-8") +
            '\n        PrivateDependencyModuleNames.Add(ExtraModuleFromEnvironment);\n',
            encoding="utf-8"
        )
        with self.assertRaisesRegex(DependencyDrift, "dynamic runtime module"):
            validate(self.root)

    def test_target_build_settings_change_rejected(self):
        p = self.root/"unreal/Source/ToSailTheStarrySkyEditor.Target.cs"
        p.write_text(p.read_text(encoding="utf-8").replace("BuildSettingsVersion.V7",
                                                             "BuildSettingsVersion.V6"),encoding="utf-8")
        with self.assertRaisesRegex(DependencyDrift, "build settings"):
            validate(self.root)

    def test_target_include_order_change_rejected(self):
        p = self.root/"unreal/Source/ToSailTheStarrySky.Target.cs"
        p.write_text(p.read_text(encoding="utf-8").replace("EngineIncludeOrderVersion.Unreal5_8",
                                                             "EngineIncludeOrderVersion.Unreal5_7"),encoding="utf-8")
        with self.assertRaisesRegex(DependencyDrift, "include order"):
            validate(self.root)

    def test_legacy_manifest_without_lock_update_rejected(self):
        self.rewrite_json("package.json",
                          lambda data: data["devDependencies"].update(playwright="^1.65.0"))
        with self.assertRaisesRegex(DependencyDrift, "manifest/lockfile"):
            validate(self.root)

    def test_legacy_lock_without_manifest_update_rejected(self):
        self.rewrite_json("package-lock.json",
                          lambda data: data["packages"][""]["devDependencies"].update(nw="^0.117.0"))
        with self.assertRaisesRegex(DependencyDrift, "manifest/lockfile"):
            validate(self.root)

    def test_new_runtime_dependency_requires_explicit_review(self):
        self.rewrite_json("unreal/Tools/dependency_baseline.json",
                          lambda data: data["unreal"]["third_party_runtime_packages_added"].append("UnreviewedFX"))
        with self.assertRaisesRegex(DependencyDrift, "runtime dependencies"):
            validate(self.root)

    def test_release_hold_cannot_be_removed_by_inventory(self):
        self.rewrite_json("unreal/Tools/dependency_baseline.json",
                          lambda data: data["policy"].update(merge_or_release_authorized=True))
        with self.assertRaisesRegex(DependencyDrift, "merges or releases"):
            validate(self.root)


if __name__ == "__main__":
    unittest.main()
