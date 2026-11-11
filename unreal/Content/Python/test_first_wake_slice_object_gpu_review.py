"""UE PythonAutomationTest registration; exact isolated review script only."""
import runpy
from pathlib import Path
import unreal
if Path(unreal.Paths.project_dir()).resolve()==Path("C:/TSTSS_VSliceVisualRuntime_20261110/unreal"):
    runpy.run_path('C:/TSTSS_VSliceVisualRuntime_20261110/unreal/Tools/capture_first_wake_slice_objects_d3d11.py',run_name='__main__')
else:
    unreal.log("OLD_115_ACTOR_GPU_TEST_OUT_OF_SCOPE_FOR_NEW_200_ACTOR_RUNTIME")
