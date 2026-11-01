#!/usr/bin/env python3
"""Read-only Windows UE native compile resource preflight (heuristic, not assurance).

Uses only GlobalMemoryStatusEx; changes no settings, files or processes.
Refuses native builds if free physical memory OR global commit headroom is low.
"""
import argparse
import ctypes
import json
import math
import sys

GIB = 1024 ** 3
DEFAULT_MIN_FREE_GIB = 6.0
DEFAULT_MIN_AVAILABLE_COMMIT_GIB = 4.0

def assess(free_physical_bytes, available_commit_bytes,
           min_physical_gib=DEFAULT_MIN_FREE_GIB,
           min_commit_gib=DEFAULT_MIN_AVAILABLE_COMMIT_GIB):
    if any(type(n) is not int or n < 0 for n in
           (free_physical_bytes, available_commit_bytes)):
        raise ValueError("memory values must be nonnegative integer byte counts")
    if any(type(n) not in (int, float) or not math.isfinite(n) or n <= 0
           for n in (min_physical_gib, min_commit_gib)):
        raise ValueError("memory floors must be finite positive GiB values")
    phys = free_physical_bytes / GIB
    commit = available_commit_bytes / GIB
    ok = phys >= min_physical_gib and commit >= min_commit_gib
    return {
        "status": "RESOURCE_PREFLIGHT_PASS_NOT_BUILD_GUARANTEE"
                  if ok else "BLOCK_INSUFFICIENT_BUILD_HEADROOM",
        "free_physical_gib": round(phys, 3),
        "available_pagefile_or_commit_gib": round(commit, 3),
        "minimum_free_physical_gib": float(min_physical_gib),
        "minimum_available_commit_gib": float(min_commit_gib),
        "launch_allowed_by_this_guard": ok,
        "independent_native_build_or_test_result": "NOT_ESTABLISHED",
        "limits": "Conservative nonvalidated floors; available pagefile is approximate global commit headroom. Does not predict compilation peak or prevent unrelated processes from consuming memory. No processes are stopped."
    }

def sample_win32():
    if sys.platform != "win32":
        raise RuntimeError("live samples require Windows")
    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)
        ]
    m = MemoryStatusEx()
    m.dwLength = ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise OSError("GlobalMemoryStatusEx failed")
    return int(m.ullAvailPhys), int(m.ullAvailPageFile)

def self_test():
    cases = [
        (6, 4, True), (7, 6, True),
        (3.37, 6, False), (6, 1.58, False),
        (5.99, 3.99, False), (0.16, 0.5, False),
    ]
    for phys, commit, decision in cases:
        r = assess(int(phys*GIB), int(commit*GIB))
        assert r["launch_allowed_by_this_guard"] == decision, (phys, commit)
    for bad in (True, -1, 1.5, None):
        try:
            assess(bad, GIB)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid free physical amount accepted")
        try:
            assess(GIB, bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid available commit amount accepted")
    for bad in (True, 0, float("nan"), float("inf"), -1):
        try:
            assess(GIB, GIB, min_physical_gib=bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid physical floor accepted")
        try:
            assess(GIB, GIB, min_commit_gib=bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid commit floor accepted")
    print("PASS: six synthetic build preflight boundary cases and eighteen invalid-input controls; no UE launched")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--minimum-free-gib", type=float, default=DEFAULT_MIN_FREE_GIB)
    p.add_argument("--minimum-commit-gib", type=float, default=DEFAULT_MIN_AVAILABLE_COMMIT_GIB)
    opts = p.parse_args()
    if opts.self_test:
        self_test()
        return
    try:
        phys, commit = sample_win32()
        result = assess(phys, commit, opts.minimum_free_gib, opts.minimum_commit_gib)
    except (ValueError, RuntimeError, OSError) as e:
        print(json.dumps({"status": "BLOCK_UNAVAILABLE_RESOURCE_SAMPLE", "reason": str(e)}))
        raise SystemExit(2)
    print(json.dumps(result, indent=2))
    if not result["launch_allowed_by_this_guard"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
