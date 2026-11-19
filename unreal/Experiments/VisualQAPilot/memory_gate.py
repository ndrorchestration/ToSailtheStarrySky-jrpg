#!/usr/bin/env python3
"""Read-only UE Windows render memory guard. Advisory heuristic, not a safety certificate.

No installs, service changes, process termination, or private process enumeration.
"""
import argparse
import ctypes
import json
import math
import sys

GIB = 1024 ** 3
DEFAULT_MIN_FREE_GIB = 6.0  # Conservative experimental floor; not engine requirement.

def gate(free_bytes, min_gib=DEFAULT_MIN_FREE_GIB):
    if type(free_bytes) is not int or free_bytes < 0:
        raise ValueError("available RAM must be a nonnegative integer byte count")
    if type(min_gib) not in (int, float) or not math.isfinite(min_gib) or min_gib <= 0:
        raise ValueError("minimum free GiB must be a finite positive number")
    free_gib = free_bytes / GIB
    permitted = free_gib >= min_gib
    return {
        "check": "WINDOWS_FREE_PHYSICAL_MEMORY_ONLY",
        "free_physical_gib": round(free_gib, 3),
        "minimum_free_gib": float(min_gib),
        "status": "HEADROOM_GATE_PASS_NOT_RENDER_SAFETY_CERTIFICATION"
                  if permitted else "BLOCK_LOW_PHYSICAL_MEMORY",
        "render_launch_permitted_by_this_guard": permitted,
        "limits": "Heuristic floor; does not guarantee GPU VRAM, commit space, D3D12 startup, screenshots or application stability. Do not close any other process automatically."
    }

def read_windows_available_physical():
    if sys.platform != "win32":
        raise RuntimeError("Live sampling requires Windows; use --self-test elsewhere.")
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
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]
    state = MemoryStatusEx()
    state.dwLength = ctypes.sizeof(state)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state)):
        raise OSError("GlobalMemoryStatusEx failed")
    return int(state.ullAvailPhys)

def self_test():
    for free, outcome in [
        (int(.04 * GIB), False),
        (int(2.5 * GIB), False),
        (5 * GIB, False),
        (6 * GIB, True),
        (10 * GIB, True),
    ]:
        result = gate(free)
        assert result["render_launch_permitted_by_this_guard"] is outcome
    for invalid in (-1, 1.5, True, None):
        try:
            gate(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("malformed physical-memory value passed")
    for invalid in (-1, 0, float("nan"), float("inf"), True):
        try:
            gate(GIB, invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("malformed memory threshold passed")
    print("PASS: 5 synthetic free-RAM boundaries and 9 invalid-input controls; no native render")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--minimum-free-gib", type=float, default=DEFAULT_MIN_FREE_GIB)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    try:
        result = gate(read_windows_available_physical(), args.minimum_free_gib)
    except (ValueError, RuntimeError, OSError) as error:
        print(json.dumps({"status": "BLOCK_UNAVAILABLE_MEMORY_MEASUREMENT",
                          "reason": str(error)}))
        raise SystemExit(2)
    print(json.dumps(result, indent=2))
    if not result["render_launch_permitted_by_this_guard"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
