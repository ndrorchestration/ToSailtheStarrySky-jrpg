"""Explicit entrypoint for Unreal's PythonScriptPlugin commandlet."""
from pathlib import Path
import sys
tools=str(Path(__file__).resolve().parent)
if tools not in sys.path:
    sys.path.insert(0,tools)
import tstss_jrpg_hybrid_review_map as review
review.main(["--build"])
