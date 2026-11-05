#!/usr/bin/env python3
"""Zero-dependency preflight: required Unreal automation names must exist in C++.
This validates source registration only; it does not compile or execute Unreal.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Tools" / "Verify-Unreal.ps1"
TESTS = ROOT / "Source" / "ToSailTheStarrySky" / "Private" / "Tests"


def main() -> int:
    verify = SCRIPT.read_text(encoding="utf-8")
    match = re.search(r"\$RequiredTests\s*=\s*@\((.*?)\)", verify, re.S)
    if match is None:
        print("FAIL: required-test list missing", file=sys.stderr)
        return 1
    names = re.findall(r"'(TSTSS\.[^']+)'", match.group(1))
    if not names or len(names) != len(set(names)):
        print("FAIL: required-test list empty or contains duplicates", file=sys.stderr)
        return 1
    sources = list(TESTS.glob("*.cpp"))
    if not sources:
        print("FAIL: no Unreal test C++ files", file=sys.stderr)
        return 1
    registered = []
    pattern = re.compile(
        r"IMPLEMENT_(?:SIMPLE|COMPLEX)_AUTOMATION_TEST\s*\(\s*\w+\s*,\s*"
        r'"(TSTSS\.[^"]+)"', re.S
    )
    for source in sources:
        registered.extend(pattern.findall(source.read_text(encoding="utf-8")))
    duplicates = {name for name in registered if registered.count(name) > 1}
    unexpected = sorted(set(registered) - set(names))
    missing = sorted(set(names) - set(registered))
    if duplicates or missing or unexpected:
        for name in sorted(duplicates):
            print(f"FAIL: duplicate native registration: {name}", file=sys.stderr)
        for name in missing:
            print(f"FAIL: required name not registered: {name}", file=sys.stderr)
        for name in unexpected:
            print(f"FAIL: native test missing from required verification list: {name}", file=sys.stderr)
        return 1
    # A registration-only check is deliberately not a C++ compile or runtime test.
    print(f"PASS: {len(names)} required names registered in {len(sources)} test files (source-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
