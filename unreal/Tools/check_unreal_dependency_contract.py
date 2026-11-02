#!/usr/bin/env python3
"""Fail-closed dependency graph/source-only contract for Unreal 5.8 review work.

Does NOT install dependencies, compile C++, prove UE renderer status, or
upgrade any runtime. Historical NW.js root dependencies are deliberately separate.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED_MODULES = ("Core", "CoreUObject", "Engine", "InputCore")
REQUIRED_NATIVE_TESTS = 15
OPTIONAL_GEOMETRY_PIN = "numpy==2.5.1"


class DependencyContractHold(ValueError):
    pass


def validate_deps(uproject_text, module_text, game_target, editor_target,
                  optional_requirements, legacy_package, native_verifier):
    try:
        uproject = json.loads(uproject_text)
        root_pkg = json.loads(legacy_package)
    except (ValueError, TypeError) as exc:
        raise DependencyContractHold("Invalid dependency manifest JSON") from exc
    if uproject.get("EngineAssociation") != "5.8":
        raise DependencyContractHold("Unreviewed Unreal engine version drift")
    mods = uproject.get("Modules")
    if (not isinstance(mods, list) or len(mods) != 1 or
        mods[0].get("Name") != "ToSailTheStarrySky" or
        mods[0].get("Type") != "Runtime"):
        raise DependencyContractHold("Unreal module graph changed")
    for name, text in (("Game", game_target), ("Editor", editor_target)):
        if "BuildSettingsVersion.V7" not in text or "EngineIncludeOrderVersion.Unreal5_8" not in text:
            raise DependencyContractHold(name + " toolchain version contract changed")
    match = re.search(r"PublicDependencyModuleNames\.AddRange\(new string\[\]\s*\{([^}]+)\}", module_text)
    if not match:
        raise DependencyContractHold("Unreal module dependency declaration missing")
    modules = tuple(re.findall(r'"([^"]+)"', match.group(1)))
    if modules != REQUIRED_MODULES:
        raise DependencyContractHold("Unreviewed C++ module dependency changes")
    dependencies = [line.strip() for line in optional_requirements.splitlines()
                    if line.strip() and not line.strip().startswith("#")]
    if dependencies != [OPTIONAL_GEOMETRY_PIN]:
        raise DependencyContractHold("Optional geometry dependency pin changed without review")
    dev = root_pkg.get("devDependencies")
    if not isinstance(dev, dict) or not all(k in dev for k in ("nw", "nwjs", "nw-builder", "playwright")):
        raise DependencyContractHold("Historical browser/NW.js dependency lane changed")
    if root_pkg.get("private") is not True:
        raise DependencyContractHold("Historical npm source suddenly non-private: review HOLD")
    paths = re.findall(r"'(TSTSS\.[A-Za-z0-9_.]+)'", native_verifier)
    if len(paths) != REQUIRED_NATIVE_TESTS or len(set(paths)) != len(paths):
        raise DependencyContractHold("Native test requirement inventory no longer 15 unique names")
    if "TSTSS.Ship.CentralBridgeHabitationReview" not in paths:
        raise DependencyContractHold("Required coupled bridge/quarters native regression removed")
    return {
        "authority":"SOURCE_DEPENDENCY_CONTRACT_ONLY",
        "engine_association":"5.8",
        "module_dependencies":list(modules),
        "optional_python_geometry":OPTIONAL_GEOMETRY_PIN,
        "native_required_tests_registered_in_verifier":len(paths),
        "legacy_browser_dev_dependency_names":sorted(dev),
        "not_proven":"native build, geometry library compatibility on fresh install, real render, art/release"
    }


def check_repository(root=ROOT):
    files = {
        "uproject_text": "unreal/ToSailTheStarrySky.uproject",
        "module_text": "unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs",
        "game_target": "unreal/Source/ToSailTheStarrySky.Target.cs",
        "editor_target": "unreal/Source/ToSailTheStarrySkyEditor.Target.cs",
        "optional_requirements": "unreal/Tools/requirements-geometry.txt",
        "legacy_package": "package.json",
        "native_verifier": "unreal/Tools/Verify-Unreal.ps1",
    }
    return validate_deps(**{
        key: (root / path).read_text(encoding="utf-8")
        for key,path in files.items()
    })


if __name__ == "__main__":
    print(json.dumps(check_repository(),indent=2,sort_keys=True))
