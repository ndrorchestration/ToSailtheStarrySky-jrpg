from pathlib import Path
import sys
src=str(Path(__file__).resolve().parent)
if src not in sys.path:sys.path.insert(0,src)
import build_ender_focus_native_review
build_ender_focus_native_review.generate()
