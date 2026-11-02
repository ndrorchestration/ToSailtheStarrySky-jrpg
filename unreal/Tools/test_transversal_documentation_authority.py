"""Source-only public-safe transversal governance checks for PR #713.

This checks only active guidance and review provenance. It does not approve
gameplay, prove Windows native tests, or read any private Notion attachments.
Historical Godot pages may remain in their original dated form.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def check_canon(canon: str):
    required = (
        "**Ender, Ionia, Lyra, Reson, Aepex**, joined through the story in that order",
        "Splashdown marks the beginning of Chapter 1, Act 1",
        "Unreal-first",
    )
    for value in required:
        if value not in canon:
            raise ValueError("Creator's current Ionia-first/Prelude canon not reconciled: " + value)
    if "**Ender, Lyra, Ionia, Reson, Aepex**, joined through the story in that order" in canon:
        raise ValueError("Historical Lyra-first order incorrectly promoted as current canon")
    if "**First Wake** is Chapter I." in canon:
        raise ValueError("First Wake/Chapter 1 stage boundary has regressed")


def check_paths(files: dict):
    canon = files["docs/CANON_AND_REVEAL_POLICY.md"]
    check_canon(canon)
    agents = files["AGENTS.md"]
    root = files["README.md"]
    handoff = files["docs/AGENT_HANDOFF_INDEX.md"]
    roadmap = files["docs/CHAPTER_1_BETA_ROADMAP.md"]
    notion = files["docs/NOTION_SOURCE_INDEX.md"]
    unreal = files["unreal/README.md"]
    matrix = files["unreal/Docs/PRODUCTION_VERIFICATION_MATRIX.md"]
    dependency = files["unreal/Docs/FIRST_WAKE_DEPENDENCY_HANDOFF_2026-11-02.md"]
    gate = files["unreal/Docs/INTEGRATION_GATE_2026-11-02.md"]
    workflow = files[".github/workflows/unreal-source-preflight.yml"]

    for label, body, tokens in [
        ("AGENTS", agents, ["Unreal Engine 5.8.4", "Splashdown is the beginning of Chapter 1, Act 1",
                            "Ionia-before-Lyra"]),
        ("Root README", root, ["Current story/review authority", "Ionia → Lyra",
                               "Splashdown", "HISTORICAL browser-era behavior"]),
        ("Agent routing", handoff, ["CURRENT UNREAL-FIRST ROUTING", "Ionia joins before Lyra",
                                   "../unreal/Docs/INTEGRATION_GATE_2026-11-02.md"]),
        ("Roadmap", roadmap, ["ACTIVE ENGINE & STAGE OVERRIDE", "Unreal Engine 5.8.4",
                             "Splashdown begins Chapter 1, Act 1", "provisional planning targets"]),
        ("Notion index", notion, ["2026-11-02 cross-system reconciliation", "Ionia → Lyra",
                                 "40bf5bad238b81e3a3b0e0cbfa61ec6d",
                                 "3e2f5bad238b813cae95ee61e4b517cc",
                                 "3ecf5bad238b8128ab03e72edf1482de"]),
        ("Unreal README", unreal, ["native automations = HOLD", "DefaultEngine.ini",
                                   "P01–P13 PIE = NOT TESTED"]),
        ("Production matrix", matrix, ["fd0b68c28e6289d45f8b8c70228631c24577a352",
                                       "HOLD — CONFIG_MUTATION", "25 distinct Success",
                                       "DefaultInput.ini"]),
        ("Dependency register", dependency, ["installed", "5.8.4",
                                            "Android File Server", "not stage"]),
        ("Integration handoff", gate, ["25 distinct successful named",
                                      "P01–P13", "NOT MERGED"]),
    ]:
        for token in tokens:
            if token.lower() not in body.lower():
                raise ValueError(label + " missing cross-system authority marker: " + token)
    if root.index("Current story/review authority") >= root.index("Historical project orientation"):
        raise ValueError("Historical Godot-first directions outrank creator authority")
    if handoff.index("CURRENT UNREAL-FIRST ROUTING") >= handoff.index("Latest QA routing"):
        raise ValueError("Old native route is shown before Unreal-first instructions")
    if roadmap.index("ACTIVE ENGINE & STAGE OVERRIDE") >= roadmap.index("2026-10-28 evidence update"):
        raise ValueError("Roadmap still elevates superseded Godot evidence")
    for name in (
        "AGENTS.md",
        "README.md",
        "docs/CANON_AND_REVEAL_POLICY.md",
        "docs/AGENT_HANDOFF_INDEX.md",
        "docs/CHAPTER_1_BETA_ROADMAP.md",
        "docs/NOTION_SOURCE_INDEX.md",
        "unreal/Docs/**",
    ):
        if "'" + name + "'" not in workflow:
            raise ValueError("Unreal source preflight lacks authority/document trigger: " + name)
    if "test_transversal_documentation_authority.py" not in workflow:
        raise ValueError("Transversal document QA is not wired into source preflight")
    # The generated Android File Server token is local project state and must
    # NEVER be copied into a public GitHub document or test record.
    for path, body in files.items():
        if path.endswith(".md") and re.search(r"SecurityToken\s*=\s*[A-Za-z0-9]{20,}", body):
            raise ValueError("Unsafe generated host security token disclosed in " + path)


PATHS = (
    "AGENTS.md", "README.md",
    "docs/CANON_AND_REVEAL_POLICY.md",
    "docs/AGENT_HANDOFF_INDEX.md",
    "docs/CHAPTER_1_BETA_ROADMAP.md",
    "docs/NOTION_SOURCE_INDEX.md",
    "unreal/README.md",
    "unreal/Docs/PRODUCTION_VERIFICATION_MATRIX.md",
    "unreal/Docs/FIRST_WAKE_DEPENDENCY_HANDOFF_2026-11-02.md",
    "unreal/Docs/INTEGRATION_GATE_2026-11-02.md",
    ".github/workflows/unreal-source-preflight.yml",
)


class TransversalAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {path: read(path) for path in PATHS}

    def test_exact_current_source_authority(self):
        check_paths(self.files)

    def test_negative_wrong_recruitment_order(self):
        wrong = self.files["docs/CANON_AND_REVEAL_POLICY.md"].replace(
            "**Ender, Ionia, Lyra, Reson, Aepex**, joined through the story in that order",
            "**Ender, Lyra, Ionia, Reson, Aepex**, joined through the story in that order")
        with self.assertRaisesRegex(ValueError, "current Ionia-first"):
            check_canon(wrong)

    def test_negative_old_chapter_boundary(self):
        wrong = self.files["docs/CANON_AND_REVEAL_POLICY.md"].replace(
            "Splashdown marks the beginning of Chapter 1, Act 1", "First Wake is Chapter I")
        with self.assertRaisesRegex(ValueError, "current Ionia-first"):
            check_canon(wrong)

    def test_negative_legacy_routing_promoted(self):
        copies = dict(self.files)
        copies["docs/AGENT_HANDOFF_INDEX.md"] = copies["docs/AGENT_HANDOFF_INDEX.md"].replace(
            "CURRENT UNREAL-FIRST ROUTING", "LEGACY GODOT FIRST")
        with self.assertRaisesRegex(ValueError, "Agent routing"):
            check_paths(copies)

    def test_negative_unwired_doc_validation(self):
        copies = dict(self.files)
        copies[".github/workflows/unreal-source-preflight.yml"] = (
            copies[".github/workflows/unreal-source-preflight.yml"].replace(
                "test_transversal_documentation_authority.py", "removed_document_gate.py"))
        with self.assertRaisesRegex(ValueError, "not wired"):
            check_paths(copies)

    def test_negative_host_generated_secret_in_docs(self):
        copies = dict(self.files)
        copies["docs/NOTION_SOURCE_INDEX.md"] += "\nSecurityToken=" + ("A" * 32)
        with self.assertRaisesRegex(ValueError, "security token"):
            check_paths(copies)


if __name__ == "__main__":
    unittest.main()
