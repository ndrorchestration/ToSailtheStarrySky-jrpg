"""Run deliberately under Unreal PythonScriptPlugin commandlet."""
from pathlib import Path
import sys
tool=str(Path(__file__).resolve().parent)
if tool not in sys.path:
    sys.path.insert(0,tool)
import tstss_slice_enemy_combat_sandbox as stage
stage.main(["--build"])
