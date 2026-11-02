"""Fail-closed Unreal Game startup log gate.

Unreal Windows GUI executables can detach from a PowerShell command. Shell
exit status 0 is therefore insufficient evidence of actual process success.
Never claim game startup PASS without a verified clean Unreal shutdown log.
This parses existing logs; it does not launch software or delete evidence.
"""
import argparse
import json
from pathlib import Path


FATAL_SIGNATURES = (
    "Assertion failed:",
    "=== Critical error:",
    "Crash in runnable thread",
    "LogWindows: Error:",
    "LogCore: Error:",
    "LogAssetRegistry: Error: Failed to load premade asset registry",
)
CLEAN_SHUTDOWN = ("LogExit: Exiting.", "Log file closed,")


def inspect_startup_log(text: str):
    if not text.strip():
        raise ValueError("No Unreal startup log text")
    errors = [p for p in FATAL_SIGNATURES if p in text]
    if errors:
        raise ValueError("Unreal startup error(s): " + ", ".join(errors))
    if not all(s in text for s in CLEAN_SHUTDOWN):
        raise ValueError("No complete clean shutdown recorded by Unreal")
    if "LogInit:" not in text or "LogExit:" not in text:
        raise ValueError("Startup or exit lifecycle evidence missing")
    return {
        "status": "UNREAL_PROCESS_LOG_CLEAN_NOT_GAMEPLAY_APPROVAL",
        "fatal_signatures": [],
        "shutdown_complete": True,
        "gameplay_tested": False,
        "editor_automation_tested": False,
        "art_approved": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    if not args.log.is_file():
        raise SystemExit("HOLD: startup log missing")
    try:
        result = inspect_startup_log(args.log.read_text(encoding="utf-8", errors="replace"))
    except ValueError as exc:
        raise SystemExit("HOLD: " + str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
