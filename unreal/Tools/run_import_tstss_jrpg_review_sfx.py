"""Native Unreal PythonScriptPlugin entrypoint."""
from pathlib import Path
import sys
p=str(Path(__file__).resolve().parent)
if p not in sys.path:
    sys.path.insert(0,p)
import import_tstss_jrpg_review_sfx as importer
importer.main(["--build"])
