#!/usr/bin/env python3
"""Unreal Editor only: safely import original wing OBJ/texture study + preview material.

Run inside UE Python Editor with environment TSTSS_AUREATE_ASSET_DIR set to the
directory containing generated asset files. No user artwork is overwritten.
UE 5.8 native execution remains unverified while the Windows machine is offline.
"""
import os
from pathlib import Path
import unreal

FOLDER = '/Game/TSTSS/Ships/AureateWake/PrototypeWing'
MATERIAL_NAME = 'M_AureateWing_Preview'
ASSET_DIR_ENV = 'TSTSS_AUREATE_ASSET_DIR'


def asset_folder():
    configured = os.environ.get(ASSET_DIR_ENV)
    if not configured:
        raise RuntimeError(f'Set {ASSET_DIR_ENV} to generated asset directory')
    src = Path(configured).expanduser().resolve()
    for name in ('aureate_wing.obj', 'aureate_wing.mtl',
                 'aureate_wing_atmospheric_albedo.png',
                 'aureate_wing_atmospheric_orm.png'):
        if not (src / name).is_file():
            raise FileNotFoundError(src / name)
    return src


def import_one(tools, path, required_class):
    task = unreal.AssetImportTask()
    for key, value in (
        ('filename', str(path)), ('destination_path', FOLDER),
        ('automated', True), ('replace_existing', False),
        ('save', True), ('async_', False)
    ):
        task.set_editor_property(key, value)
    tools.import_asset_tasks([task])
    for asset_path in task.get_editor_property('imported_object_paths'):
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if isinstance(asset, required_class):
            return asset
    raise RuntimeError('No matching imported asset for ' + path.name)


def create_preview_material(tools, albedo, orm):
    mat = tools.create_asset(MATERIAL_NAME, FOLDER, unreal.Material, unreal.MaterialFactoryNew())
    if not mat:
        raise RuntimeError('Failed to create original preview material')
    mat.set_editor_property('two_sided', True)
    mel = unreal.MaterialEditingLibrary

    def node(kind, x, y):
        result = mel.create_material_expression(mat, kind, x, y)
        if not result:
            raise RuntimeError('Failed to create node: ' + kind.__name__)
        return result

    def connect(a, b, pin):
        if not mel.connect_material_expressions(a, '', b, pin):
            raise RuntimeError('Failed to connect material input ' + pin)

    def output(a, prop):
        if not mel.connect_material_property(a, '', prop):
            raise RuntimeError('Failed to bind material property ' + str(prop))

    def scalar(name, default, x, y):
        param = node(unreal.MaterialExpressionScalarParameter, x, y)
        param.set_editor_property('parameter_name', name)
        param.set_editor_property('default_value', default)
        return param

    def tint(name, rgba, x, y):
        param = node(unreal.MaterialExpressionVectorParameter, x, y)
        param.set_editor_property('parameter_name', name)
        param.set_editor_property('default_value', unreal.LinearColor(*rgba))
        return param

    def multiply(a, b, x, y):
        mul = node(unreal.MaterialExpressionMultiply, x, y)
        connect(a, mul, 'A')
        connect(b, mul, 'B')
        return mul

    def lerp(a, b, alpha, x, y):
        blend_node = node(unreal.MaterialExpressionLinearInterpolate, x, y)
        connect(a, blend_node, 'A')
        connect(b, blend_node, 'B')
        connect(alpha, blend_node, 'Alpha')
        return blend_node

    alb = node(unreal.MaterialExpressionTextureSample, -1100, -650)
    alb.set_editor_property('texture', albedo)
    orm_node = node(unreal.MaterialExpressionTextureSample, -1100, 150)
    orm_node.set_editor_property('texture', orm)
    blend = scalar('OrbiterSailBlend', 0.0, -900, -350)
    orbital_blue = tint('OrbiterTint', (0.19, 0.43, 0.74, 1), -660, -700)
    output(lerp(alb, orbital_blue, blend, -300, -650),
           unreal.MaterialProperty.MP_BASE_COLOR)

    rough_mask = node(unreal.MaterialExpressionComponentMask, -900, 180)
    for k, v in [('r', False), ('g', True), ('b', False), ('a', False)]:
        rough_mask.set_editor_property(k, v)
    connect(orm_node, rough_mask, 'Input')
    smooth_sail = scalar('OrbiterRoughness', 0.16, -660, 300)
    output(lerp(rough_mask, smooth_sail, blend, -300, 180),
           unreal.MaterialProperty.MP_ROUGHNESS)

    metal_mask = node(unreal.MaterialExpressionComponentMask, -900, 420)
    for k, v in [('r', False), ('g', False), ('b', True), ('a', False)]:
        metal_mask.set_editor_property(k, v)
    connect(orm_node, metal_mask, 'Input')
    metallic_sail = scalar('OrbiterMetallic', 0.7, -660, 500)
    output(lerp(metal_mask, metallic_sail, blend, -300, 430),
           unreal.MaterialProperty.MP_METALLIC)

    # Art-directed Fresnel edge glow, not verified spectral diffraction.
    fresnel = node(unreal.MaterialExpressionFresnel, -850, 730)
    glow = scalar('OrbiterEdgeGlow', 0.13, -620, 720)
    iridescent_tint = tint('EdgeIridescence', (0.16, 0.66, 0.86, 1), -650, 950)
    edge = multiply(fresnel, glow, -400, 790)
    edge = multiply(edge, blend, -190, 790)
    edge = multiply(edge, iridescent_tint, 20, 790)
    output(edge, unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    mel.recompile_material(mat)
    if not unreal.EditorAssetLibrary.save_loaded_asset(mat, only_if_is_dirty=False):
        raise RuntimeError('Failed to save material')
    return mat


def main():
    src = asset_folder()
    # Fail closed before touching the content browser; separate test-only path.
    if unreal.EditorAssetLibrary.does_directory_exist(FOLDER):
        existing = unreal.EditorAssetLibrary.list_assets(
            FOLDER, recursive=False, include_folder=False
        )
        if existing:
            raise FileExistsError('Prototype folder not empty; refusing overwrite: ' + str(existing))
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    albedo = import_one(tools, src / 'aureate_wing_atmospheric_albedo.png', unreal.Texture2D)
    orm = import_one(tools, src / 'aureate_wing_atmospheric_orm.png', unreal.Texture2D)
    orm.set_editor_property('srgb', False)
    orm.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_MASKS)
    unreal.EditorAssetLibrary.save_loaded_asset(orm, only_if_is_dirty=False)
    mesh = import_one(tools, src / 'aureate_wing.obj', unreal.StaticMesh)
    material = create_preview_material(tools, albedo, orm)
    unreal.log('Aureate mesh created: ' + mesh.get_path_name())
    unreal.log('Aureate material created: ' + material.get_path_name())
    unreal.log('Assign mesh to AuthoredWingMesh, material to WingMaterial on a preview actor')
    unreal.log('Native import/shader/visual acceptance must still be manually verified')


if __name__ == '__main__':
    main()
