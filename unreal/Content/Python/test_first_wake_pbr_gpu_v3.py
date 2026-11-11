"""Registered genuine UE5.8.4 First Wake 200-actor PBR GPU review test only."""
from pathlib import Path
import runpy
import unreal
project=Path(unreal.Paths.project_dir()).resolve()
expected=Path("C:/TSTSS_V3_GPU_20261111/TSTSS_VSliceLookdev_20261111/unreal")
if project!=expected:
    raise RuntimeError("GPU_CAPTURE_HOLD: registered PBR test used outside isolated runtime")
runpy.run_path("C:/TSTSS_V3_GPU_20261111/TSTSS_VSliceLookdev_20261111/unreal/Tools/capture_first_wake_pbr_gpu_v3.py",run_name="__main__")
