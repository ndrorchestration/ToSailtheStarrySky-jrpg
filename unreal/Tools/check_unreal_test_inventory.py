#!/usr/bin/env python3
"""Source-only audit: each TSTSS UE automation declaration is required by native verifier."""
from collections import Counter
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
tests = sorted((root / "Source/ToSailTheStarrySky/Private/Tests").glob("*.cpp"))
verification = root / "Tools/Verify-Unreal.ps1"
declaration = re.compile(r'IMPLEMENT_(?:SIMPLE|COMPLEX)_AUTOMATION_TEST\s*\(\s*\w+\s*,\s*"([^"]+)"', re.MULTILINE)
required_block = re.compile(r'\$RequiredTests\s*=\s*@\((.*?)\)', re.DOTALL)
try:
    if not tests: raise ValueError("No test source files")
    declared = [name for f in tests for name in declaration.findall(f.read_text(encoding="utf-8"))]
    block = required_block.search(verification.read_text(encoding="utf-8"))
    if not block: raise ValueError("No required test inventory in Verify-Unreal.ps1")
    required = re.findall(r"'(TSTSS\.[^']+)'", block.group(1))
    if not required or not declared: raise ValueError("Empty test inventory")
    for label, values in (("declared", declared), ("required", required)):
        duplicates = sorted(name for name, n in Counter(values).items() if n != 1)
        if duplicates: raise ValueError(f"Duplicate {label} names: {duplicates}")
    if set(declared) != set(required):
        raise ValueError(f"Missing from verifier: {sorted(set(declared)-set(required))}; missing source declaration: {sorted(set(required)-set(declared))}")
    print(f"PASS: {len(declared)} declared TSTSS tests each required once by native verifier")
    print("Source-only result, NOT an Unreal compilation or automation PASS")
except (OSError, ValueError) as exc:
    print(f"FAIL: {exc}", file=sys.stderr)
    sys.exit(1)
