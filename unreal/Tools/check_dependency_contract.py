"""Fail-closed, engine-free dependency inventory verification for TSTSS Unreal review.

Checks *declarations*, not installed engine, plugins, compiler, vulnerability
status, licensing, binary import, native build, packaged app or gameplay.
A review-only inventory is intentionally not a lockfile for Epic's engine.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


class DependencyDrift(ValueError):
    pass


def _json(root: Path, path: str) -> dict:
    p = root / path
    if not p.is_file():
        raise DependencyDrift(f"Required declaration missing: {path}")
    return json.loads(p.read_text(encoding="utf-8"))


def _read(root: Path, path: str) -> str:
    p = root / path
    if not p.is_file():
        raise DependencyDrift(f"Required source missing: {path}")
    return p.read_text(encoding="utf-8")


def _modules(code: str) -> list[str]:
    blocks = re.findall(
        r"(?:Public|Private)DependencyModuleNames\s*\.\s*AddRange\s*\("
        r"\s*new\s+string\[\]\s*\{([^}]*)\}",
        code, re.DOTALL
    )
    if not blocks:
        raise DependencyDrift("No explicit runtime module dependency block found")
    names = []
    for block in blocks:
        names += re.findall(r'"([^"]+)"', block)
    if len(set(names)) != len(names):
        raise DependencyDrift("Duplicate runtime module dependency")
    return names


def validate(root: Path) -> dict:
    root = Path(root)
    base = _json(root, "unreal/Tools/dependency_baseline.json")
    if base.get("schema_version") != 1:
        raise DependencyDrift("Unrecognized dependency baseline schema")
    if base.get("status") != "REVIEW_ONLY_DEPENDENCY_INVENTORY_NOT_AN_UPGRADE_OR_DEPLOYMENT_APPROVAL":
        raise DependencyDrift("Review-only disclaimer removed")
    engine = base["engine"]
    unreal_spec = base["unreal"]
    legacy = base["legacy_nwjs"]

    project = _json(root, "unreal/ToSailTheStarrySky.uproject")
    if project.get("EngineAssociation") != engine["association"]:
        raise DependencyDrift("Unreal engine association drift")
    plugins = [p["Name"] for p in project.get("Plugins", []) if p.get("Enabled")]
    if sorted(plugins) != sorted(unreal_spec["enabled_project_plugins"]):
        raise DependencyDrift("Enabled Unreal project plugin set drift")
    if len(set(plugins)) != len(plugins):
        raise DependencyDrift("Duplicate enabled plugin")
    modules = _modules(_read(root, "unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs"))
    if sorted(modules) != sorted(unreal_spec["runtime_module_dependencies"]):
        raise DependencyDrift("Unreal module dependencies drift")

    for kind in ("", "Editor"):
        path = f"unreal/Source/ToSailTheStarrySky{kind}.Target.cs"
        text = _read(root, path)
        if not re.search(r"DefaultBuildSettings\s*=\s*BuildSettingsVersion\."
                         + re.escape(engine["target_build_settings"]) + r"\b", text):
            raise DependencyDrift(f"{kind or 'Game'} target build settings drift")
        if not re.search(r"IncludeOrderVersion\s*=\s*EngineIncludeOrderVersion\."
                         + re.escape(engine["include_order"]) + r"\b", text):
            raise DependencyDrift(f"{kind or 'Game'} target include order drift")
        if not re.search(r"Type\s*=\s*TargetType\." + ("Editor" if kind else "Game") + r"\b", text):
            raise DependencyDrift(f"{kind or 'Game'} target role drift")

    pkg = _json(root, legacy["package_manifest"])
    lock = _json(root, legacy["lockfile"])
    if pkg.get("private") is not True or legacy.get("private") is not True:
        raise DependencyDrift("Legacy private-package guard removed")
    if lock.get("lockfileVersion") != legacy["lockfile_version"]:
        raise DependencyDrift("Legacy lockfile version drift")
    if (pkg.get("devDependencies") != legacy["dev_dependencies"]
        or lock.get("packages", {}).get("", {}).get("devDependencies") != legacy["dev_dependencies"]):
        raise DependencyDrift("Legacy npm manifest/lockfile differ from reviewed inventory")
    if (pkg.get("name") != lock.get("name")
        or pkg.get("version") != lock.get("version")
        or pkg.get("name") != lock.get("packages", {}).get("", {}).get("name")):
        raise DependencyDrift("Legacy package identity/lockfile drift")
    if not legacy.get("release_hold") or base["policy"].get("auto_upgrade") is not False:
        raise DependencyDrift("Legacy hold / no-auto-upgrade policy drift")
    if base["policy"].get("merge_or_release_authorized") is not False:
        raise DependencyDrift("Inventory cannot authorize merges or releases")
    if unreal_spec.get("third_party_runtime_packages_added") != []:
        raise DependencyDrift("New runtime dependencies require independent review")

    return {
        "status": "DECLARATIONS_MATCH_REVIEW_BASELINE_NOT_NATIVE_OR_SECURITY_PROOF",
        "engine_association": project["EngineAssociation"],
        "target_build_settings": engine["target_build_settings"],
        "include_order": engine["include_order"],
        "runtime_module_dependencies": modules,
        "enabled_project_plugins": plugins,
        "legacy_package_count": len(legacy["dev_dependencies"]),
        "engine_installed": None,
        "runtime_build_executed": False,
        "dependency_security_scan_executed": False,
        "third_party_licenses_approved": False,
        "production_upgrade_authorized": False,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        result = validate(args.repo)
    except (DependencyDrift, KeyError, ValueError, json.JSONDecodeError) as e:
        parser.exit(status=1, message=f"HOLD: dependency declaration mismatch: {e}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
