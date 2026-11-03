"""Fail-closed source-only historical NW.js staging and release-hold review.

No npm build/install, no NW.js executable execution, no installer, no network.
These checks do not prove actual packaged binary contents or safety.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE = ROOT / "scripts/stage-memories-desktop.js"
PACKAGE = ROOT / "package.json"
WF = ROOT / ".github/workflows/desktop-package.yml"
LOCAL = ROOT / "scripts/build-windows-release.ps1"
DOC = ROOT / "unreal/Docs/LEGACY_DESKTOP_STAGING_EXPOSURE_BOUNDARY_2026-11-02.md"
SOURCE_FILES = (
    "index-embedded.html",
    "tosailthestarrysky.js",
    "p5.min.js",
    "embedded-fonts.css",
    "icon.svg",
    "icon.ico",
)
AFFECTED_IMPORT_NAMES = ("nwjs", "nw-builder", "lodash", "request", "form-data")


class StagingHold(ValueError):
    pass


def _literal_js_list(code: str, name: str) -> list[str]:
    found = re.search(
        r"\bconst\s+" + re.escape(name) + r"\s*=\s*\[([^\]]*)\]\s*;",
        code,
        flags=re.S,
    )
    if not found:
        raise StagingHold("Expected static " + name + " list unavailable")
    content = found.group(1)
    values = re.findall(r"""['"]([^'"]+)['"]""", content)
    if not values or re.sub(r"""['"][^'"]+['"]|[\s,]""", "", content):
        raise StagingHold("Nonliteral entries in " + name + " need independent review")
    return values


def check_boundary(
    stage: str, package: dict, workflow: str, local: str,
    module_paths: list[str], app_texts: dict[str, str],
    doc: str,
) -> bool:
    files = _literal_js_list(stage, "runtimeFiles")
    if files != list(SOURCE_FILES):
        raise StagingHold("Staging runtime file inventory changed")
    if "fs.cpSync(modulesSrc, modulesDst, { recursive: true });" not in stage:
        raise StagingHold("Staged module tree copy changed")
    if "const modulesSrc = path.join(repo, 'modules');" not in stage:
        raise StagingHold("Module source changed")
    if "const modulesDst = path.join(www, 'modules');" not in stage:
        raise StagingHold("Module destination changed")
    forbidden = _literal_js_list(stage, "forbidden")
    required_forbidden = {"node_modules", "package-lock.json", "tests", "docs", ".github"}
    if not required_forbidden.issubset(set(forbidden)):
        raise StagingHold("Development-only file exclusion removed")
    if "main: 'www/index-embedded.html'" not in stage:
        raise StagingHold("Staged entrypoint changed")
    manifest = stage.split("const manifest = {", 1)
    if len(manifest) != 2:
        raise StagingHold("Desktop manifest definition missing")
    manifest_block = manifest[1].split("\n};", 1)[0]
    if "devDependencies" in manifest_block:
        raise StagingHold("Development dependencies introduced into staged manifest")
    expected_deps = {"nw", "nwjs", "nw-builder", "playwright"}
    if package.get("private") is not True or set(package.get("devDependencies", {})) != expected_deps:
        raise StagingHold("Audited root development package declaration changed")
    cmd = package.get("scripts", {}).get("package:windows", "")
    if not cmd.startswith("npm run stage:desktop && nwbuild ") or not cmd.endswith(" .desktop-runtime"):
        raise StagingHold("Legacy packager input changed")
    if "--version=0.116.0" not in cmd:
        raise StagingHold("Legacy NW.js runtime version changed")
    if not module_paths or any(
        "node_modules" in Path(p).parts or Path(p).name in {"package.json", "package-lock.json"}
        for p in module_paths
    ):
        raise StagingHold("Nested npm dependencies or manifests in tracked module sources")
    imported = re.compile(
        r"""(?:require\s*\(\s*|from\s+|import\s+)\s*['"]"""
        + r"(?:" + "|".join(map(re.escape, AFFECTED_IMPORT_NAMES)) + r")"
        + r"""(?:/|['"])"""
    )
    if any(imported.search(s) for s in app_texts.values()):
        raise StagingHold("Audited npm package name imported by tracked game files")
    if "name: Legacy NW.js Windows release — BLOCKED" not in workflow:
        raise StagingHold("Historical publisher must remain explicitly blocked")
    active = "\n".join(
        x for x in workflow.splitlines() if not x.lstrip().startswith("#")
    )
    if re.search(r"^\s*(?:push|tags):", active, flags=re.M):
        raise StagingHold("Legacy publication push/tag trigger added")
    if not re.search(r"permissions:\s*\n\s*contents:\s*read", active):
        raise StagingHold("Read-only workflow token removed")
    if "Refuse manual execution" not in active or "exit 1" not in active:
        raise StagingHold("Manual release denial changed")
    guard = 'throw "SECURITY_HOLD_293:'
    if guard not in local or (
        not (local.index(guard) < local.index("$repo = ") < local.index("npm ci"))
    ):
        raise StagingHold("Local security hold no longer precedes npm/build")
    for claim in (
        "BINARY CONTENT AND TRANSITIVE RUNTIME EXPOSURE NOT VERIFIED",
        "SOURCE-ONLY STAGING PLAN INSPECTED",
        "SECURITY HOLD",
        "no direct literal imports",
        "No downloaded archived release binary",
        "No live legacy game or uninstaller was run",
    ):
        if claim.lower() not in doc.lower():
            raise StagingHold("Risk/verification limitation removed: " + claim)
    return True


class LegacyDesktopStagingExposureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage = STAGE.read_text(encoding="utf-8")
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.workflow = WF.read_text(encoding="utf-8")
        cls.local = LOCAL.read_text(encoding="utf-8")
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.modules = sorted(
            p.relative_to(ROOT).as_posix()
            for p in (ROOT / "modules").rglob("*") if p.is_file()
        )
        cls.app_texts = {
            str(p): p.read_text(encoding="utf-8")
            for p in [*(ROOT / x for x in SOURCE_FILES), *(ROOT / x for x in cls.modules)]
            if p.suffix in (".js", ".cjs", ".mjs", ".html", ".css", ".json")
        }

    def check(self, **edits):
        state = dict(
            stage=self.stage, package=self.package, workflow=self.workflow,
            local=self.local, module_paths=self.modules,
            app_texts=self.app_texts, doc=self.doc,
        )
        state.update(edits)
        return check_boundary(**state)

    def test_audited_source_staging_boundary_and_hold(self):
        self.assertTrue(self.check())
        self.assertEqual(len(self.modules), 29)

    def test_missing_node_modules_exclusion_rejected(self):
        self.assertNotEqual(self.stage.find("'node_modules'"), -1)
        with self.assertRaisesRegex(StagingHold, "exclusion"):
            self.check(stage=self.stage.replace("'node_modules',", "", 1))

    def test_unreviewed_staged_file_rejected(self):
        with self.assertRaisesRegex(StagingHold, "runtime file inventory"):
            self.check(stage=self.stage.replace("'icon.ico'", "'node_modules'"))

    def test_nested_module_dependency_copy_rejected(self):
        with self.assertRaisesRegex(StagingHold, "Nested npm"):
            self.check(module_paths=self.modules + ["modules/node_modules/request/index.js"])

    def test_direct_audited_package_import_rejected(self):
        changed = dict(self.app_texts)
        changed["modules/core.js"] += "\nrequire('request');\n"
        with self.assertRaisesRegex(StagingHold, "imported"):
            self.check(app_texts=changed)

    def test_legacy_packager_input_change_rejected(self):
        p = json.loads(json.dumps(self.package))
        p["scripts"]["package:windows"] = p["scripts"]["package:windows"].replace(
            " .desktop-runtime", " ."
        )
        with self.assertRaisesRegex(StagingHold, "input changed"):
            self.check(package=p)

    def test_legacy_workflow_push_trigger_rejected(self):
        with self.assertRaisesRegex(StagingHold, "push/tag"):
            self.check(workflow=self.workflow.replace(
                "  workflow_dispatch:", "  push:\n  workflow_dispatch:", 1
            ))

    def test_local_security_hold_removal_rejected(self):
        with self.assertRaisesRegex(StagingHold, "security hold"):
            self.check(local=self.local.replace(
                'throw "SECURITY_HOLD_293:', 'Write-Output "SECURITY_HOLD_293:', 1
            ))

    def test_false_binary_clearance_claim_rejected(self):
        with self.assertRaisesRegex(StagingHold, "limitation"):
            self.check(doc=self.doc.replace(
                "BINARY CONTENT AND TRANSITIVE RUNTIME EXPOSURE NOT VERIFIED",
                "BINARY CONTENT IS SAFE"
            ))


if __name__ == "__main__":
    unittest.main()
