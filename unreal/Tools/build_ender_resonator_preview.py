"""Unreal Editor Python: author an emissive material and disposable nine-cue preview level.

Run only from the isolated Ender-magic checkout, with the Editor otherwise idle:
UnrealEditor-Cmd.exe <uproject> -unattended -nop4 -ExecutePythonScript=<this_file>
Not a gameplay/sound approval. Does not touch First Wake maps or another agent's work.
"""
import json
from pathlib import Path
import unreal

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "DataSource" / "Magic" / "EnderResonator.vertical_slice.review.json"
PACKAGE = "/Game/TSTSS/Magic"
MAT_PATH = PACKAGE + "/M_ResonatorGlow"
MAP_PATH = PACKAGE + "/L_EnderResonatorCueReview"

def safe_property(obj, prop, value):
    try:
        obj.set_editor_property(prop, value)
        return True
    except Exception as exc:
        unreal.log_warning("PROPERTY SKIPPED %s: %s" % (prop, exc))
        return False

def make_material():
    unreal.EditorAssetLibrary.make_directory(PACKAGE)
    material = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
    if material:
        unreal.log("Material already exists; refusing to overwrite: " + MAT_PATH)
        return material
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    material = tools.create_asset("M_ResonatorGlow", PACKAGE,
                                  unreal.Material, unreal.MaterialFactoryNew())
    if not material:
        raise RuntimeError("Could not create material")
    safe_property(material, "blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    safe_property(material, "two_sided", True)
    safe_property(material, "shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    edit = unreal.MaterialEditingLibrary
    tint = edit.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -550, -130)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", unreal.LinearColor(0.1, 0.8, 1.0, 1.0))
    glow = edit.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -550, 80)
    glow.set_editor_property("parameter_name", "Glow")
    glow.set_editor_property("default_value", 14.0)
    multiplied = edit.create_material_expression(material, unreal.MaterialExpressionMultiply, -250, 0)
    edit.connect_material_expressions(tint, "", multiplied, "A")
    edit.connect_material_expressions(glow, "", multiplied, "B")
    edit.connect_material_property(multiplied, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    opacity = edit.create_material_expression(material, unreal.MaterialExpressionConstant, -200, 260)
    opacity.set_editor_property("r", 1.0)
    edit.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)
    # Required by UInstancedStaticMeshComponent renderer; without this, runtime falls back to DefaultMaterial.
    edit.set_base_material_usage(material, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES, True)
    edit.recompile_material(material)
    if not unreal.EditorAssetLibrary.save_loaded_asset(material):
        raise RuntimeError("Material save failed")
    unreal.log("Created: " + MAT_PATH)
    return material

def make_review_data_table():
    path = PACKAGE + "/DT_EnderResonatorReview"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.log("Review DataTable exists; refusing to overwrite: " + path)
        return
    row_struct = unreal.load_object(None, "/Script/ToSailTheStarrySky.TSTSSBattleSkillRow")
    if not row_struct:
        raise RuntimeError("Native TSTSSBattleSkillRow is unavailable")
    factory = unreal.DataTableFactory()
    if not (safe_property(factory, "struct", row_struct) or
            safe_property(factory, "row_struct", row_struct)):
        raise RuntimeError("Cannot set DataTable row struct on this UE version")
    table = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "DT_EnderResonatorReview", PACKAGE, unreal.DataTable, factory)
    if not table:
        raise RuntimeError("DataTable asset create failed")
    if not unreal.DataTableFunctionLibrary.fill_data_table_from_json_file(
            table, str(SRC)):
        raise RuntimeError("DataTable JSON import failed; do not mark magic usable")
    if not unreal.EditorAssetLibrary.save_loaded_asset(table):
        raise RuntimeError("DataTable save failed")
    unreal.log("Created review-only DataTable: " + path)

def make_level():
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        unreal.log("Review level exists; refusing to overwrite: " + MAP_PATH)
        return
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    cls = unreal.load_class(None, "/Script/ToSailTheStarrySky.TSTSSResonatorVfxActor")
    if not cls:
        raise RuntimeError("UE module not built: TSTSSResonatorVfxActor unavailable")
    if not unreal.EditorLevelLibrary.new_level(MAP_PATH):
        raise RuntimeError("Could not create isolated review level")
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for i, row in enumerate(rows):
        # Separate actors and lines of fire: a 3 x 3 VFX comparison stage.
        x = float((i % 3) * 880 - 880)
        y = float((i // 3) * 820 - 820)
        actor = subsystem.spawn_actor_from_class(cls, unreal.Vector(x, y, 15),
                                                unreal.Rotator(0, 0, 0))
        if not actor:
            raise RuntimeError("Failed to place cue " + row["VfxCueId"])
        actor.set_actor_label("REVIEW ONLY - " + row["SkillId"])
        actor.set_editor_property("preview_cue_id", row["VfxCueId"])
        actor.set_editor_property("preview_target_offset", unreal.Vector(320, 0, 0))
        actor.set_editor_property("loop_review", True)
    camera_cls = unreal.load_class(None, "/Script/Engine.CameraActor")
    # Unreal Python Rotator positional args are roll, pitch, yaw (not pitch, yaw, roll).
    # Resolve orientation geometrically so the camera faces the effects, not the sky.
    review_camera_location = unreal.Vector(0, -2200, 1050)
    review_camera_look_at = unreal.Vector(0, 0, 90)
    camera = subsystem.spawn_actor_from_class(camera_cls,
        review_camera_location,
        unreal.MathLibrary.find_look_at_rotation(review_camera_location, review_camera_look_at))
    if camera:
        camera.set_actor_label("Review overview - not a gameplay camera")
        # Dedicated review camera is the view target in isolated standalone play;
        # without auto-activation the nine-effect stage may not be framed.
        camera.set_editor_property("auto_activate_for_player", unreal.AutoReceiveInput.PLAYER0)
    # Neutral, non-canonical contrast/scale calibration stage for screenshots.
    # No First Wake gameplay, collisions, NPCs, or ship assets are added.
    mesh = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
    if not mesh:
        raise RuntimeError("Missing engine cube calibration mesh")
    floor = subsystem.spawn_actor_from_class(unreal.StaticMeshActor,
        unreal.Vector(0, 0, -95), unreal.Rotator(0, 0, 0))
    if not floor:
        raise RuntimeError("Could not create calibration floor")
    floor.set_actor_label("REVIEW CALIBRATION - floor")
    floor.get_editor_property("static_mesh_component").set_static_mesh(mesh)
    floor.set_actor_scale3d(unreal.Vector(44, 44, 0.3))
    floor.get_editor_property("static_mesh_component").set_collision_enabled(
        unreal.CollisionEnabled.NO_COLLISION)
    key_location = unreal.Vector(0, 0, 750)
    key_target = unreal.Vector(700, 350, 0)
    key = subsystem.spawn_actor_from_class(unreal.DirectionalLight,
        key_location,
        unreal.MathLibrary.find_look_at_rotation(key_location, key_target))
    if not key:
        raise RuntimeError("Could not create calibration key light")
    key.set_actor_label("REVIEW CALIBRATION - key light")
    key.get_component_by_class(unreal.DirectionalLightComponent).set_editor_property(
        "intensity", 30000.0)
    fill = subsystem.spawn_actor_from_class(unreal.PointLight,
        unreal.Vector(0, -300, 550), unreal.Rotator(0, 0, 0))
    if not fill:
        raise RuntimeError("Could not create calibration fill light")
    fill.set_actor_label("REVIEW CALIBRATION - fill light")
    fill_component = fill.get_component_by_class(unreal.PointLightComponent)
    fill_component.set_editor_property("intensity", 60000.0)
    fill_component.set_editor_property("attenuation_radius", 4500.0)
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError("Review map save failed")
    unreal.log("Created isolated cue preview map: " + MAP_PATH)

if __name__ == "__main__":
    make_material()
    make_review_data_table()
    make_level()
