"""Pure source/lockfile model of a scratch legacy npm wrapper removal.

Never calls npm, installs packages, edits manifests, runs NSIS or executes
historical binaries. Security observations are date-bound external evidence.
"""
from collections import deque
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "package-lock.json"
PACKAGE = ROOT / "package.json"
DOC = ROOT / "unreal/Docs/LEGACY_NWJS_WRAPPER_REMOVAL_SCRATCH_CANDIDATE_2026-11-02.md"
WORKFLOW = ROOT / ".github/workflows/unreal-source-preflight.yml"
SOURCE_HASH = "f9aecbddb8453d868627023bac06700df6082c0000fbf98876ec94dd482ffdce"
KEPT_HASH = "5f9cd3285febfa5852bdde3793dee7bab8b74ec4d87961197a1150beb195d350"
REMOVED_HASH = "85acffa1fb88e8eb7f79ebae3d4242685eea0e23a8b813920998ae0ead2edb31"
ROOT_BEFORE = {"nw", "nwjs", "nw-builder", "playwright"}
ROOT_AFTER = {"nw", "nw-builder", "playwright"}
SIX_RESIDUAL = {"@nwutils/builder", "archiver", "glob", "minimatch", "nw-builder", "readdir-glob"}
NWJS_ONLY_AFFECTED = {
    "aimer", "cheerio", "configstore", "css-select", "css-what", "dot-prop",
    "extract-zip", "form-data", "got", "latest-version", "lodash", "meow",
    "node-fetch", "nth-check", "nugget", "nwjs", "nwjs-versions",
    "package-json", "pget", "qs", "request", "shelljs", "tough-cookie",
    "trim-newlines", "update-notifier", "uuid",
}


class CandidateDrift(ValueError):
    pass


def _resolve(packages, origin, name):
    parent = origin
    while True:
        candidate = f"{parent}/node_modules/{name}" if parent else f"node_modules/{name}"
        if candidate in packages:
            return candidate
        if not parent:
            return None
        ancestor, separator, _ = parent.rpartition("/node_modules/")
        parent = ancestor if separator else ""


def _key_hash(paths):
    return hashlib.sha256("\n".join(sorted(paths)).encode("utf-8")).hexdigest()


def simulate(lock, pkg):
    """Project a root-only nwjs removal into Python memory, no disk writes."""
    packages = lock.get("packages", {})
    root = pkg.get("devDependencies", {})
    if lock.get("lockfileVersion") != 3 or len(packages) != 322:
        raise CandidateDrift("Historical lock schema or record count drift")
    if root != packages.get("", {}).get("devDependencies", {}) or set(root) != ROOT_BEFORE:
        raise CandidateDrift("Historical root devDependency inventory drift")
    if root.get("nwjs") != "^1.4.4":
        raise CandidateDrift("Unreviewed historical nwjs declaration")
    cli = pkg.get("scripts", {}).get("package:windows", "")
    if not (cli.startswith("npm run stage:desktop && nwbuild ")
            and "--version=0.116.0" in cli and cli.endswith(" .desktop-runtime")):
        raise CandidateDrift("Historical packaging command changed")
    retained = {""}
    queue = deque()
    for name in sorted(ROOT_AFTER):
        node = _resolve(packages, "", name)
        if node is None:
            raise CandidateDrift("Missing retained devDependency: " + name)
        queue.append(node)
    while queue:
        node = queue.popleft()
        if node in retained:
            continue
        retained.add(node)
        for kind in ("dependencies", "optionalDependencies"):
            for name in packages[node].get(kind, {}):
                child = _resolve(packages, node, name)
                if child is None:
                    raise CandidateDrift(f"Missing declared edge {node} to {name}")
                if child not in retained:
                    queue.append(child)
    removed = set(packages) - retained
    if (len(retained) != 94 or len(removed) != 228
            or _key_hash(retained) != KEPT_HASH
            or _key_hash(removed) != REMOVED_HASH):
        raise CandidateDrift("Candidate differs from tested npm scratch prune")
    if "node_modules/nwjs" in retained:
        raise CandidateDrift("nwjs wrapper unexpectedly remains reachable")
    candidate_lock = copy.deepcopy(lock)
    candidate_lock["packages"] = {
        name: copy.deepcopy(metadata)
        for name, metadata in packages.items() if name in retained
    }
    del candidate_lock["packages"][""]["devDependencies"]["nwjs"]
    candidate_pkg = copy.deepcopy(pkg)
    del candidate_pkg["devDependencies"]["nwjs"]
    if candidate_pkg["devDependencies"] != candidate_lock["packages"][""]["devDependencies"]:
        raise CandidateDrift("Candidate manifest and lock roots disagree")
    return candidate_lock, candidate_pkg, retained, removed


def check_doc(doc):
    required = (
        "NOT APPLIED OR APPROVED", "322", "94", "228",
        "MANIFEST_OR_LOCKFILE_UPDATE=NOT_APPLIED",
        "LEGACY_RELEASE_SECURITY_HOLD=ACTIVE",
        "PACKAGED_BINARY_COMPATIBILITY=UNVERIFIED",
        "npm ls --package-lock-only --all --json --offline",
        "no", "directory was created",
        "do not run, recover, whitelist, build or distribute",
        KEPT_HASH, REMOVED_HASH,
    )
    for phrase in required:
        if phrase.lower() not in doc.lower():
            raise CandidateDrift("Missing reviewed risk/evidence caveat: " + phrase)


class LegacyNwjsScratchCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = LOCK.read_bytes()
        cls.lock = json.loads(cls.raw)
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.doc = DOC.read_text(encoding="utf-8")

    def test_historical_source_remains_at_audited_lock(self):
        self.assertEqual(
            hashlib.sha256(self.raw.replace(bytes((13, 10)), bytes((10,)))).hexdigest(),
            SOURCE_HASH
        )

    def test_exact_candidate_node_set_matches_npm_scratch(self):
        lck, pkg, keep, remove = simulate(self.lock, self.package)
        self.assertEqual(len(keep), 94)
        self.assertEqual(len(remove), 228)
        self.assertEqual(set(pkg["devDependencies"]), ROOT_AFTER)
        self.assertEqual(pkg["scripts"], self.package["scripts"])
        self.assertNotIn("node_modules/nwjs", lck["packages"])

    def test_retained_package_versions_and_metadata_unchanged(self):
        projected, _, retained, _ = simulate(self.lock, self.package)
        for node in retained - {""}:
            with self.subTest(path=node):
                self.assertEqual(projected["packages"][node], self.lock["packages"][node])
        for name, version in (("nw", "0.116.0"), ("nw-builder", "4.20.0"), ("playwright", "1.63.0")):
            self.assertEqual(projected["packages"]["node_modules/" + name]["version"], version)

    def test_26_earlier_nwjs_only_audit_entries_removed(self):
        _, _, retained, _ = simulate(self.lock, self.package)
        names = {p.rsplit("node_modules/", 1)[-1] for p in retained if p}
        self.assertTrue(NWJS_ONLY_AFFECTED.isdisjoint(names))
        self.assertTrue(SIX_RESIDUAL.issubset(names))

    def test_no_source_runtime_wrapper_import_or_package_script_call(self):
        sources = [
            ROOT / "index-embedded.html", ROOT / "tosailthestarrysky.js",
            ROOT / "scripts/stage-memories-desktop.js",
            *(ROOT / "modules").rglob("*.js"),
        ]
        direct_import = re.compile(
            r"""(?:require\s*\(\s*|from\s+|import\s+)\s*['"]nwjs(?:/|['"])"""
        )
        for src in sources:
            with self.subTest(path=src.name):
                self.assertIsNone(direct_import.search(src.read_text(encoding="utf-8")))
        self.assertNotIn("nwjs", json.dumps(self.package["scripts"]).lower())

    def test_doc_keeps_non_release_non_install_classification(self):
        check_doc(self.doc)

    def test_mutant_root_declaration_rejected(self):
        altered = copy.deepcopy(self.package)
        altered["devDependencies"]["unreviewed-addon"] = "*"
        with self.assertRaises(CandidateDrift):
            simulate(self.lock, altered)

    def test_mutant_new_nwjs_transitive_edge_rejected(self):
        altered = copy.deepcopy(self.lock)
        altered["packages"]["node_modules/nw-builder"].setdefault("dependencies", {})["nwjs"] = "^1.4.4"
        with self.assertRaisesRegex(CandidateDrift, "npm scratch prune"):
            simulate(altered, self.package)

    def test_mutant_false_binary_approval_rejected(self):
        changed = self.doc.replace(
            "PACKAGED_BINARY_COMPATIBILITY=UNVERIFIED",
            "PACKAGED_BINARY_COMPATIBILITY=APPROVED",
        )
        with self.assertRaisesRegex(CandidateDrift, "caveat"):
            check_doc(changed)

    def test_ci_includes_new_review_document_and_pure_source_suite(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            "- 'unreal/Docs/LEGACY_NWJS_WRAPPER_REMOVAL_SCRATCH_CANDIDATE_2026-11-02.md'",
            workflow
        )
        self.assertIn("test_legacy_nwjs_removal_scratch_candidate.py", workflow)


if __name__ == "__main__":
    unittest.main()
