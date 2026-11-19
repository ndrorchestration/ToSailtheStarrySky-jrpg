"""Unreal Python Editor: import cropped SpriteCook images as REFERENCE ONLY.
Run after splitting each 3x3 atlas into individual PNG images.
Set TSTSS_REFERENCE_ROOT to directory containing props/, vfx/, materials/ folders.
Does not produce usable meshes, PBR maps or Niagara systems.
"""
import os
from pathlib import Path
import unreal

root_string = os.environ.get("TSTSS_REFERENCE_ROOT")
if not root_string:
    raise RuntimeError("Set TSTSS_REFERENCE_ROOT before editor import")
root = Path(root_string)
if not root.is_dir():
    raise FileNotFoundError(root)
tools = unreal.AssetToolsHelpers.get_asset_tools()
for category in ("props", "vfx", "materials"):
    folder = root / category
    for image in sorted(folder.glob("*.png")):
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", str(image.resolve()))
        task.set_editor_property("destination_path", "/Game/TSTSS/Art/Reference/SpriteCook/" + category.capitalize())
        task.set_editor_property("destination_name", image.stem)
        task.set_editor_property("automated", True)
        task.set_editor_property("replace_existing", False)
        task.set_editor_property("save", True)
        tools.import_asset_tasks([task])
        if not task.get_editor_property("imported_object_paths"):
            raise RuntimeError("Unreal import failed: " + str(image))
unreal.log("TSTSS SpriteCook reference import completed. ART ACCEPTANCE PENDING.")
