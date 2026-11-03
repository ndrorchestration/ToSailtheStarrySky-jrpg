"""Dated lockfile-only root-path snapshot tests (no network / npm install).

The affected package list reflects the original 2026-11-02 read-only npm audit.
These tests validate ONLY declared dependency graph paths in that exact lock.
They do NOT fetch current advisories, execute the toolchain, scan binaries,
test vulnerabilities, or authorize release.
"""
from __future__ import annotations

from collections import defaultdict, deque
import copy
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "package-lock.json"
PACKAGE = ROOT / "package.json"
DOCUMENT = ROOT / "unreal/Docs/LEGACY_NPM_ADVISORY_ROOT_PATH_RECONCILIATION_2026-11-02.md"
WORKFLOW = ROOT / ".github/workflows/unreal-source-preflight.yml"
EXPECTED_LOCK_LF_SHA256 = "f9aecbddb8453d868627023bac06700df6082c0000fbf98876ec94dd482ffdce"

# Freeze *which 32 package entries* npm audit reported on the dated source.
# GitHub's 18 alerts are advisory records, a DIFFERENT reporting unit.
AFFECTED_NWJS_ONLY = frozenset((
    "aimer", "cheerio", "configstore", "css-select", "css-what",
    "dot-prop", "extract-zip", "form-data", "got", "latest-version",
    "lodash", "meow", "node-fetch", "nth-check", "nugget", "nwjs",
    "nwjs-versions", "package-json", "pget", "qs", "request",
    "shelljs", "tough-cookie", "trim-newlines", "update-notifier", "uuid",
))
AFFECTED_BUILDER_ONLY = frozenset((
    "@nwutils/builder", "archiver", "nw-builder", "readdir-glob",
))
AFFECTED_SHARED = frozenset(("glob", "minimatch"))
AFFECTED = AFFECTED_NWJS_ONLY | AFFECTED_BUILDER_ONLY | AFFECTED_SHARED
EXPECTED_DIRECT = frozenset(("nw", "nwjs", "nw-builder", "playwright"))


class SourceLockDrift(ValueError):
    pass


def _resolve(packages: dict, parent: str, dependency: str) -> str | None:
    """Resolve an installed package path with Node's ancestor folder rule."""
    current = parent
    while True:
        candidate = f"{current}/node_modules/{dependency}" if current else f"node_modules/{dependency}"
        if candidate in packages:
            return candidate
        if not current:
            return None
        before, separator, _last = current.rpartition("/node_modules/")
        current = before if separator else ""
        # At top-level node_modules/name, rpartition has no separator; try root.


def source_root_paths(lock: dict) -> tuple[dict[str, set[str]], dict[tuple[str, str], tuple[str, ...]]]:
    packages = lock.get("packages", {})
    if lock.get("lockfileVersion") != 3 or len(packages) != 322:
        raise SourceLockDrift("Dated lockfile v3 record count changed")
    root_direct = packages.get("", {}).get("devDependencies", {})
    if set(root_direct) != EXPECTED_DIRECT:
        raise SourceLockDrift("Dated root devDependency inventory changed")
    children = {}
    for location, meta in packages.items():
        paths = []
        for dependency_type in ("dependencies", "optionalDependencies"):
            for depname in meta.get(dependency_type, {}):
                located = _resolve(packages, location, depname)
                if located is None:
                    raise SourceLockDrift("Unresolved declared package edge: " + location + " -> " + depname)
                paths.append(located)
        children[location] = paths
    reached: dict[str, set[str]] = defaultdict(set)
    shortest: dict[tuple[str, str], tuple[str, ...]] = {}
    pending = deque()
    for root in sorted(root_direct):
        located = _resolve(packages, "", root)
        if located is None:
            raise SourceLockDrift("Root package node missing: " + root)
        reached[located].add(root)
        shortest[(located, root)] = (root,)
        pending.append((located, root))
    while pending:
        current, root = pending.popleft()
        for child in children[current]:
            next_path = shortest[(current, root)] + (child.rsplit("node_modules/", 1)[-1],)
            if root not in reached[child]:
                reached[child].add(root)
                shortest[(child, root)] = next_path
                pending.append((child, root))
            elif len(next_path) < len(shortest[(child, root)]):
                shortest[(child, root)] = next_path
                pending.append((child, root))
    observed: dict[str, set[str]] = {}
    for package in AFFECTED:
        path_nodes = [
            n for n in packages
            if n and n.rsplit("node_modules/", 1)[-1] == package
        ]
        if not path_nodes:
            raise SourceLockDrift("Audited package missing from lock: " + package)
        roots = set()
        for n in path_nodes:
            roots.update(reached.get(n, set()))
        observed[package] = roots
    return observed, shortest


def check_dated_source(lock: dict, package: dict, doc: str) -> None:
    if package.get("devDependencies") != lock["packages"][""]["devDependencies"]:
        raise SourceLockDrift("Root manifest differs from lock")
    observed, shortest = source_root_paths(lock)
    expected = {
        **{x: {"nwjs"} for x in AFFECTED_NWJS_ONLY},
        **{x: {"nw-builder"} for x in AFFECTED_BUILDER_ONLY},
        **{x: {"nwjs", "nw-builder"} for x in AFFECTED_SHARED},
    }
    if observed != expected:
        mismatch = sorted(x for x in expected if observed.get(x) != expected[x])
        raise SourceLockDrift("Dated affected package root path mapping drift: " + ",".join(mismatch))
    # Critical packages: verify intermediate nodes rather than just root totals.
    for node, expected_path in (
        ("form-data", ("nwjs", "pget", "nugget", "request", "form-data")),
        ("request", ("nwjs", "pget", "nugget", "request")),
        ("lodash", ("nwjs", "nwjs-versions", "aimer", "cheerio", "lodash")),
    ):
        if shortest.get(("node_modules/" + node, "nwjs")) != expected_path:
            raise SourceLockDrift("Critical-root representative chain changed: " + node)
    for token in (
        "18 OPEN alerts", "2 critical, 8 high and 8 medium",
        "scope=development", "manifest_path=package-lock.json",
        "32 distinct affected package entries", "25 distinct inline GHSA IDs",
        "18 unique GHSA IDs", "The **7** additional",
        "28 + 6", "zero unmapped affected packages",
        "READ-ONLY SECURITY TRIAGE", "HISTORICAL BINARY DISTRIBUTION EXPOSURE: UNVERIFIED",
        "SECURITY REMEDIATION: NOT PERFORMED", "no release",
    ):
        if token.lower() not in doc.lower():
            raise SourceLockDrift("Missing dated scope or source interpretation: " + token)


class LegacyAdvisoryRootMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw_lock = LOCK.read_bytes()
        cls.lock = json.loads(cls.raw_lock)
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.doc = DOCUMENT.read_text(encoding="utf-8")

    def test_all_dated_affected_packages_have_declared_roots(self):
        self.assertEqual(len(AFFECTED), 32)
        checked, _ = source_root_paths(self.lock)
        self.assertEqual(sum("nwjs" in s for s in checked.values()), 28)
        self.assertEqual(sum("nw-builder" in s for s in checked.values()), 6)
        self.assertEqual(sum(len(s) > 1 for s in checked.values()), 2)
        self.assertEqual(sum(not s for s in checked.values()), 0)

    def test_lock_hash_is_cross_platform_exact_snapshot(self):
        normalized = self.raw_lock.replace(bytes((13, 10)), bytes((10,)))
        self.assertEqual(hashlib.sha256(normalized).hexdigest(), EXPECTED_LOCK_LF_SHA256)

    def test_doc_and_lock_agree_and_caveats_preserved(self):
        check_dated_source(self.lock, self.package, self.doc)

    def test_mutation_breaking_critical_form_data_path_rejected(self):
        damaged = copy.deepcopy(self.lock)
        # Remove its single request -> form-data edge. No lockfile mutation in repo.
        del damaged["packages"]["node_modules/request"]["dependencies"]["form-data"]
        with self.assertRaisesRegex(SourceLockDrift, "mapping drift|Critical-root"):
            check_dated_source(damaged, self.package, self.doc)

    def test_mutation_adding_unaudited_direct_dependency_rejected(self):
        changed = copy.deepcopy(self.lock)
        changed["packages"][""]["devDependencies"]["unsafe-new-root"] = "*"
        with self.assertRaisesRegex(SourceLockDrift, "Root manifest|inventory"):
            check_dated_source(changed, self.package, self.doc)

    def test_mutation_misleading_github_alert_claim_rejected(self):
        distorted = self.doc.replace("18 OPEN alerts", "32 OPEN alerts")
        with self.assertRaisesRegex(SourceLockDrift, "Missing dated"):
            check_dated_source(self.lock, self.package, distorted)

    def test_mutation_claiming_binary_distribution_safety_rejected(self):
        distorted = self.doc.replace(
            "HISTORICAL BINARY DISTRIBUTION EXPOSURE: UNVERIFIED",
            "HISTORICAL BINARY DISTRIBUTION EXPOSURE: SAFE",
        )
        with self.assertRaisesRegex(SourceLockDrift, "Missing dated"):
            check_dated_source(self.lock, self.package, distorted)

    def test_ci_is_doc_and_path_source_triggered(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("- 'unreal/Docs/LEGACY_NPM_ADVISORY_ROOT_PATH_RECONCILIATION_2026-11-02.md'", workflow)
        self.assertIn("test_legacy_npm_advisory_roots.py", workflow)
        self.assertIn("- 'package-lock.json'", workflow)


if __name__ == "__main__":
    unittest.main()
