"""Explicit Unreal Python commandlet entrypoint; not an ordinary import module.

Unreal's script execution context need not name the script __main__.
Always invoke the existing source-locked verifier from this dedicated runner.
"""
from pathlib import Path
import sys

tool_dir = str(Path(__file__).resolve().parent)
if tool_dir not in sys.path:
    sys.path.insert(0, tool_dir)
import verify_pr713_native_prelude_map

verify_pr713_native_prelude_map.main()
