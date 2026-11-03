#!/usr/bin/env python3
"""Source-only reconciliation of a composed UE review, not native gameplay proof.

The branch is intentionally stacked on #712, and selected documents/checkers
were copied from #657/#711 without importing their unrelated Git ancestors.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

from check_first_wake_dependency_contract import check_snapshot, read_inputs
from check_dependency_contract import validate as verify_legacy_dependency_register

ROOT = Path(__file__).resolve().parents[2]


class CompositionHold(ValueError):
    pass


def require(condition: bool, reason: str):
    if not condition:
        raise CompositionHold(reason)


def check_consistency(authority: str, root_readme: str, rank: dict,
                      primary: dict, secondary: dict, project: dict,
                      handoff: str, pie_protocol: str, verifier: str) -> None:
    require("Unreal Engine 5.8.4" in authority and
            "active forward game-development target" in authority,
            "Root AGENTS.md missing creator Unreal-first authority")
    require("Current forward-engine authority" in root_readme and
            "NOT Godot" in root_readme and
            "historical" in root_readme.lower(),
            "Root README not superseding legacy Godot instructions")
    require(root_readme.index("Current forward-engine authority") <
            root_readme.index("Historical project orientation"),
            "Root engine guidance would put legacy instruction first")
    require(rank.get("numeric_values_approved") is False and
            rank.get("gameplay_implementation_authorized") is False,
            "Stat contract improperly approves unreviewed numbers/gameplay")
    rules = {(r["stat"], r["direction"], r["first"], r["second"])
             for r in rank["strict_rank_rules"]}
    require(rules == {
        ("mag", "descending", "ender", "lyra"),
        ("mp", "descending", "ender", "lyra"),
        ("hp", "ascending", "lyra", "ender"),
    }, "Creator relative-stat rules changed")
    require(set(rank.get("roster", [])) ==
            {"ender", "ionia", "lyra", "reson", "aepex"} and
            len(rank.get("roster", [])) == 5,
            "Creator 5-member roster altered")
    declared = sorted(p["Name"] for p in project["Plugins"] if p["Enabled"] is True)
    require(declared == sorted(primary["project"]["enabled_plugins"]) ==
            sorted(secondary["unreal"]["enabled_project_plugins"]),
            "Two dependency baselines or manifest disagree on enabled plugin")
    require(primary["project"]["engine_association"] ==
            secondary["engine"]["association"] == project["EngineAssociation"] == "5.8",
            "Two dependency baselines or project disagree on Unreal family")
    require(sorted(primary["project"]["native_module_dependencies"]) ==
            sorted(secondary["unreal"]["runtime_module_dependencies"]),
            "Two dependency baselines disagree on runtime modules")
    require(primary["project"]["target_build_settings"] ==
            secondary["engine"]["target_build_settings"] == "V7" and
            primary["project"]["target_include_order"] ==
            secondary["engine"]["include_order"] == "Unreal5_8",
            "Two dependency baselines disagree on build target options")
    require(primary["legacy"]["dev_dependencies"] ==
            secondary["legacy_nwjs"]["dev_dependencies"],
            "Historical npm declarations differ across baselines")
    require(primary["policy"]["update_versions"] is False and
            primary["policy"]["install_dependencies"] is False and
            primary["policy"]["release_authorized"] is False and
            primary["policy"]["native_unreal_build_verified"] is False and
            secondary["policy"]["auto_upgrade"] is False and
            secondary["policy"]["merge_or_release_authorized"] is False,
            "A dependency baseline allows install, native PASS, release or merge")
    require("#657" in handoff and "#711" in handoff and
            "not" in handoff.lower(),
            "Cross-branch ancestry/authority distinctions removed")
    for case in range(1, 14):
        require(f"| P{case:02} |" in pie_protocol,
                f"Missing manual PIE acceptance case P{case:02}")
    require("MAIN_MERGE=NOT_AUTHORIZED" in pie_protocol and
            "NATIVE_AUTOMATION_25=NOT_TESTED" in pie_protocol,
            "PIE acceptance protocol weakens native/release evidence")
    require("TSTSS.FirstWake.ReviewObjectivesAreReadOnly" in verifier,
            "Previously established native objective automation was removed")
    # This integration draft adds exactly one new actor-to-water native test
    # to the prior 25-name registry. Old native receipts stay SHA-scoped;
    # neither the source list nor this checker can assert a runtime PASS.
    block = re.search(r"\$RequiredTests\s*=\s*@\((.*?)\)", verifier, re.S)
    require(block is not None, "Native automation registry unavailable")
    required_names = re.findall(r"'(TSTSS\.[^']+)'", block.group(1))
    require(len(required_names) == 26 and len(set(required_names)) == 26 and
            "TSTSS.FirstWake.InteractionToSplashdown" in required_names,
            "Integrated 26-name native automation registry missing or duplicated")


def verify(root: Path = ROOT) -> dict:
    def read(path: str) -> str:
        return (root / path).read_text(encoding="utf-8")
    def read_json(path: str) -> dict:
        return json.loads(read(path))
    primary = read_json("unreal/Tools/first_wake_dependency_contract.json")
    secondary = read_json("unreal/Tools/dependency_baseline.json")
    project = read_json("unreal/ToSailTheStarrySky.uproject")
    check_consistency(
        read("AGENTS.md"), read("README.md"),
        read_json("data/design/level-one-rank-constraints.json"),
        primary, secondary, project,
        read("unreal/Docs/FIRST_WAKE_DEPENDENCY_HANDOFF_2026-11-02.md"),
        read("unreal/Docs/FIRST_WAKE_V2_PIE_ACCEPTANCE_MATRIX_2026-11-02.md"),
        read("unreal/Tools/Verify-Unreal.ps1"),
    )
    strict = check_snapshot(*read_inputs(root))
    previous = verify_legacy_dependency_register(root)
    require(strict["status"] == "SOURCE_DECLARATIONS_MATCH_NOT_NATIVE_VERIFICATION" and
            previous["status"] ==
                "DECLARATIONS_MATCH_REVIEW_BASELINE_NOT_NATIVE_OR_SECURITY_PROOF",
            "An independent dependency baseline checker did not pass")
    return {
        "result": "COMPOSED_SOURCE_DECLARATIONS_PASS",
        "unreal_native_build": "NOT_TESTED",
        "native_automation_25": "NOT_TESTED",  # Historical document gate (unchanged)
        "native_automation_26": "NOT_TESTED",  # Current proposed integration
        "pie_cases_13": "NOT_TESTED",
        "merges_or_releases_authorized": False,
        "dependency_versions_changed": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
