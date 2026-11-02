#!/usr/bin/env python3
"""Fail-closed source-declaration audit for the First Wake review stack.

This is NOT an Unreal native build, package installation, SBOM, CVE scan,
license verification or evidence that installed tools match these versions.
No files are mutated; both positive and injected mismatch tests are safe.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path(__file__).with_name("first_wake_dependency_contract.json")
PROJECT = ROOT / "unreal"


class DependencyDrift(ValueError):
    pass


def require(condition: bool, description: str) -> None:
    if not condition:
        raise DependencyDrift(description)


def names_from_build_cs(source: str) -> list[str]:
    matches = re.findall(
        r'PublicDependencyModuleNames\.AddRange\s*\(\s*new\s+string\[\]\s*'
        r'\{([^}]*)\}\s*\)', source, flags=re.S,
    )
    require(len(matches) == 1, "Expected one explicit public Unreal dependency list")
    values = re.findall(r'"([^"]+)"', matches[0])
    require(len(values) == len(set(values)), "Repeated public native dependency name")
    require(bool(values), "Empty native dependency list")
    return values


def check_snapshot(
    contract: dict, project: dict, build_cs: str, game_target: str,
    editor_target: str, package: dict, lock: dict
) -> dict:
    require(contract.get("schema_version") == 1, "Unknown contract schema")
    require(contract.get("status") == "DRAFT_SOURCE_DECLARATIONS_ONLY_NO_INSTALL_OR_UPGRADE",
            "Contract claims more than declared-source inventory")
    expected = contract["project"]
    require(project.get("EngineAssociation") == expected["engine_association"],
            "Unreal engine family drift")
    module = project.get("Modules")
    require(isinstance(module, list) and len(module) == 1,
            "Unreal project module list differs from scoped baseline")
    require(module[0].get("Name") == expected["module"] and
            module[0].get("Type") == expected["module_type"],
            "Unreal module identity or role drift")
    plugins = project.get("Plugins")
    require(isinstance(plugins, list), "Plugin list absent (not equivalent to empty)")
    require(all(isinstance(item, dict) and "Name" in item and
                isinstance(item.get("Enabled"), bool) for item in plugins),
            "Plugin declarations are missing explicit boolean enabled status")
    enabled = [p["Name"] for p in plugins if p["Enabled"]]
    require(len(enabled) == len(set(enabled)), "Duplicate enabled project plugin")
    require(sorted(enabled) == sorted(expected["enabled_plugins"]),
            "Enabled Unreal plugins differ from exact branch baseline")
    names = names_from_build_cs(build_cs)
    require(sorted(names) == sorted(expected["native_module_dependencies"]),
            "Native module dependency drift")
    for label, source, target_type in (
        ("Game", game_target, "Game"), ("Editor", editor_target, "Editor")
    ):
        require(re.search(r'\bType\s*=\s*TargetType\.' + target_type + r'\s*;', source)
                is not None, label + " target kind drift")
        require("BuildSettingsVersion." + expected["target_build_settings"] in source,
                label + " build settings drift")
        require("EngineIncludeOrderVersion." + expected["target_include_order"] in source,
                label + " include order drift")
        require('ExtraModuleNames.Add("' + expected["module"] + '")' in source,
                label + " extra module drift")

    legacy = contract["legacy"]
    require(package.get("name") == legacy["package_name"], "Legacy npm name drift")
    require(package.get("private") is True, "Legacy npm package became public")
    require(package.get("devDependencies") == legacy["dev_dependencies"],
            "Legacy npm dev dependency versions changed")
    require(lock.get("lockfileVersion") == legacy["lockfile_version"],
            "Legacy lockfile schema drift")
    require(lock.get("name") == package.get("name") and
            lock.get("version") == package.get("version"),
            "Legacy npm lockfile identity drift")
    root = lock.get("packages", {}).get("")
    require(isinstance(root, dict) and
            root.get("devDependencies") == package.get("devDependencies"),
            "Legacy lockfile root is out of sync with package.json")
    require(root.get("name") == package.get("name") and
            root.get("version") == package.get("version"),
            "Legacy lockfile root identity drift")
    policy = contract["policy"]
    for flag in ("update_versions", "install_dependencies",
                 "native_unreal_build_verified", "release_authorized"):
        require(policy.get(flag) is False, "Dependency contract weakened: " + flag)
    return {
        "status": "SOURCE_DECLARATIONS_MATCH_NOT_NATIVE_VERIFICATION",
        "engine_family": expected["engine_association"],
        "module_count": len(names),
        "enabled_plugins": enabled,
        "legacy_dev_dependencies": sorted(package["devDependencies"]),
        "install_or_upgrade_performed": False,
        "unreal_native_execution": False,
        "release_authorized": False,
    }


def read_inputs(root: Path = ROOT) -> tuple:
    unreal = root / "unreal"
    read = lambda path: path.read_text(encoding="utf-8")
    return (
        json.loads(read(unreal / "Tools/first_wake_dependency_contract.json")),
        json.loads(read(unreal / "ToSailTheStarrySky.uproject")),
        read(unreal / "Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs"),
        read(unreal / "Source/ToSailTheStarrySky.Target.cs"),
        read(unreal / "Source/ToSailTheStarrySkyEditor.Target.cs"),
        json.loads(read(root / "package.json")),
        json.loads(read(root / "package-lock.json")),
    )


if __name__ == "__main__":
    print(json.dumps(check_snapshot(*read_inputs()), indent=2, sort_keys=True))
