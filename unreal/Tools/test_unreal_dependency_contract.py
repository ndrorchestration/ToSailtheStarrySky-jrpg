#!/usr/bin/env python3
"""Engine-free negative controls for the Unreal dependency inventory contract."""
from __future__ import annotations

import json
import unittest

from check_unreal_dependency_contract import (
    ROOT, DependencyContractHold, check_repository, validate_deps,
)


class UnrealDependencyBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = {
            "uproject_text": "unreal/ToSailTheStarrySky.uproject",
            "module_text": "unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs",
            "game_target": "unreal/Source/ToSailTheStarrySky.Target.cs",
            "editor_target": "unreal/Source/ToSailTheStarrySkyEditor.Target.cs",
            "optional_requirements": "unreal/Tools/requirements-geometry.txt",
            "legacy_package": "package.json",
            "native_verifier": "unreal/Tools/Verify-Unreal.ps1",
        }
        cls.inputs = {name: (ROOT / path).read_text(encoding="utf-8")
                      for name,path in p.items()}

    def altered(self, name, old, new):
        kwargs=dict(self.inputs)
        if kwargs[name].count(old)!=1:
            raise AssertionError("Test mutation anchor changed: "+old)
        kwargs[name]=kwargs[name].replace(old,new)
        return kwargs

    def test_real_checked_in_graph_passes(self):
        result=check_repository()
        self.assertEqual(result["engine_association"],"5.8")
        self.assertEqual(result["native_required_tests_registered_in_verifier"],15)
        self.assertEqual(result["optional_python_geometry"],"numpy==2.5.1")

    def test_engine_version_drift_holds(self):
        with self.assertRaisesRegex(DependencyContractHold,"engine version"):
            validate_deps(**self.altered("uproject_text",'"5.8"','"5.9"'))

    def test_build_settings_drift_holds(self):
        with self.assertRaisesRegex(DependencyContractHold,"toolchain"):
            validate_deps(**self.altered("editor_target",
                                        "BuildSettingsVersion.V7",
                                        "BuildSettingsVersion.V6"))

    def test_include_order_drift_holds(self):
        with self.assertRaisesRegex(DependencyContractHold,"toolchain"):
            validate_deps(**self.altered("game_target",
                                        "EngineIncludeOrderVersion.Unreal5_8",
                                        "EngineIncludeOrderVersion.Unreal5_7"))

    def test_runtime_module_addition_requires_review(self):
        with self.assertRaisesRegex(DependencyContractHold,"module dependency"):
            validate_deps(**self.altered(
                "module_text",'"Core", "CoreUObject", "Engine", "InputCore"',
                '"Core", "CoreUObject", "Engine", "InputCore", "UMG"'))

    def test_geometry_numpy_pin_drift_holds(self):
        with self.assertRaisesRegex(DependencyContractHold,"geometry dependency"):
            validate_deps(**self.altered("optional_requirements",
                                         "numpy==2.5.1","numpy>=2.0"))

    def test_geometry_import_of_unreviewed_scipy_holds(self):
        with self.assertRaisesRegex(DependencyContractHold,"geometry dependency"):
            kwargs=dict(self.inputs)
            kwargs["optional_requirements"]+="scipy==1.18.0\n"
            validate_deps(**kwargs)

    def test_unlisted_native_regression_holds(self):
        with self.assertRaisesRegex(DependencyContractHold,"native regression removed"):
            validate_deps(**self.altered(
                "native_verifier",
                "'TSTSS.Ship.CentralBridgeHabitationReview'",
                "'TSTSS.Ship.NonexistentPreview'"))

    def test_legacy_package_cannot_become_public(self):
        with self.assertRaisesRegex(DependencyContractHold,"non-private"):
            validate_deps(**self.altered("legacy_package",'"private": true',
                                        '"private": false'))

    def test_missing_legacy_builder_holds(self):
        with self.assertRaisesRegex(DependencyContractHold,"Historical"):
            kwargs=dict(self.inputs)
            package=json.loads(kwargs["legacy_package"])
            del package["devDependencies"]["nw-builder"]
            kwargs["legacy_package"]=json.dumps(package)
            validate_deps(**kwargs)


if __name__=="__main__":
    unittest.main()
