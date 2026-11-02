"""Source-only TSTSS dependency and new-engine handoff consistency checks.

This test proves that the manifest inventory matches source declarations.
It does NOT install dependencies, build Unreal, release games, or grant canon.
"""
import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class UnrealDocumentationDependencyTests(unittest.TestCase):
    def test_project_engine_and_module_declarations_match_documentation(self):
        p=json.loads((ROOT/"unreal/ToSailTheStarrySky.uproject").read_text(encoding="utf-8"))
        self.assertEqual(p["EngineAssociation"],"5.8")
        self.assertEqual([m["Name"] for m in p["Modules"]],["ToSailTheStarrySky"])
        self.assertEqual(p.get("Plugins",[]),[])
        build=(ROOT/"unreal/Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs").read_text()
        names=re.findall(r'"([A-Za-z0-9_]+)"',build.split("PublicDependencyModuleNames.AddRange(",1)[1])
        self.assertEqual(names,["Core","CoreUObject","Engine","InputCore"])
        audit=(ROOT/"docs/UNREAL_DEPENDENCY_AND_DOCUMENTATION_AUTHORITY_2026-11-01.md").read_text(encoding="utf-8")
        self.assertIn("Core, CoreUObject, Engine, InputCore",audit)
        self.assertIn("No plugin enabled or declared",audit)

    def test_legacy_npm_manifest_lock_are_in_sync_not_unreal_dependencies(self):
        package=json.loads((ROOT/"package.json").read_text(encoding="utf-8"))
        lock=json.loads((ROOT/"package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(package["name"],"Aetherwake")
        self.assertEqual(lock["lockfileVersion"],3)
        self.assertEqual(package.get("devDependencies"),lock.get("packages",{}).get("",{}).get("devDependencies"))
        for name in ("nw","nwjs","nw-builder","playwright"):
            self.assertIn(name,package["devDependencies"])
        audit=(ROOT/"docs/UNREAL_DEPENDENCY_AND_DOCUMENTATION_AUTHORITY_2026-11-01.md").read_text(encoding="utf-8")
        self.assertIn("Leave existing package names, versions, scripts and lockfile unchanged",audit)

    def test_current_routing_and_form_names_visible_to_all_agents(self):
        current=("Skybourne","Seabourne","Submersible","Starbourne")
        for path in ("AGENTS.md","README.md","docs/AGENT_HANDOFF_INDEX.md","unreal/README.md"):
            with self.subTest(path=path):
                content=(ROOT/path).read_text(encoding="utf-8")
                self.assertIn("Unreal Engine 5.8.4",content)
                for name in current:self.assertIn(name,content)
        naming=json.loads((ROOT/"unreal/ArtSource/ShipReview/aureate_wake_canonical_form_names_v2.json").read_text())
        self.assertEqual(naming["canonical_display_order"],list(current))
        self.assertEqual([f["internal_enum"] for f in naming["forms"]],
                         ["Skyborne","Seaborne","Submersible","Orbiter"])
        self.assertTrue(naming["guardrails"]["starbourne_story_locked"])

    def test_referenced_local_authority_files_exist(self):
        for filename in (
            "unreal/Docs/PRODUCTION_VERIFICATION_MATRIX.md",
            "unreal/Docs/STARBOURNE_NATIVE_REFLECTION_ACCEPTANCE.md",
            "unreal/Docs/AUREATE_WAKE_CANONICAL_CONFIGURATION_NAMES_2026-11-01.md",
            "unreal/Docs/AUREATE_WAKE_APPROVED_ART_REFERENCE_2026-11-01.md",
            "docs/GODOT_MIGRATION_COORDINATION.md",
            "docs/CANON_AND_REVEAL_POLICY.md",
            "unreal/Tools/Check-UnrealHost.ps1",
            "unreal/Tools/Verify-StarbourneNames.ps1",
            "unreal/Tools/TSTSS-UE58.vsconfig",
        ):
            with self.subTest(filename=filename):
                self.assertTrue((ROOT/filename).is_file())

    def test_no_unreal_dep_install_or_release_claim_in_authority(self):
        text=(ROOT/"docs/UNREAL_DEPENDENCY_AND_DOCUMENTATION_AUTHORITY_2026-11-01.md").read_text(encoding="utf-8")
        for statement in (
            "separate dependency PR",
            "No merge, publication, dependency installation, release",
            "not automatically the target",
            "exact base SHA",
        ):
            self.assertIn(statement,text)

if __name__=="__main__":unittest.main()
