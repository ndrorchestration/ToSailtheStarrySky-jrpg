"""Explicit Unreal PythonScriptPlugin entrypoint; no reliance on __main__."""
from pathlib import Path
import sys

tool = str(Path(__file__).resolve().parent)
if tool not in sys.path:
    sys.path.insert(0, tool)
import tstss_slice_enemy_gallery as gallery

gallery.main(["--build"])
