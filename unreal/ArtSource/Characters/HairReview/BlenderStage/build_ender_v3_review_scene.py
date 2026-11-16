"""TSTSS original Ender V3 hair -> editable Blender .blend review stage.

To be run ONLY by the checked launcher after resource gates. Does not use DAZ,
MetaHuman proprietary binaries or any private reference pixels. This makes a
scene with the original review-only static glTF geometry and four labelled,
orthographic study cameras. No render, art approval or Unreal import is claimed.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

def fail(message):
    raise RuntimeError("TSTSS_BLENDER_HAIR_FAIL_CLOSED: "+message)

def main():
    if "--" not in sys.argv:
        fail("explicit output path required after --")
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=2 or args[0]!="--outdir":
        fail("Use -- --outdir PRIVATE_DIRECTORY")
    out=Path(args[1]).resolve()
    if not out.is_dir():
        fail("output directory must already exist")
    destination=out/"Ender_V3_Hair_EDITABLE_DCC_REVIEW_NONCANONICAL.blend"
    receipt=out/"Ender_V3_Hair_DCC_SourceReceipt.json"
    if destination.exists() or receipt.exists():
        fail("existing project/evidence; never overwrite")
    import bpy
    from mathutils import Vector
    if tuple(bpy.app.version[:3])!=(5,2,4):
        fail("exact Blender 5.2.4 LTS required")
    source=Path(r"C:\TSTSS_EnderHairNativeV1_20261104\unreal\ArtSource\Characters\HairReview\CandidatesV3\Ender_BroadLayerHair_V3_NONCANONICAL.glb")
    pinned="bd8286a142294a86784180099db6e8298dc85367632c5a3673fcec50d893d09e"
    if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=pinned:
        fail("original source missing or changed")
    # No third-party characters or their meshes are needed or copied.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    subjects=[obj for obj in bpy.context.scene.objects if obj.type=="MESH"]
    if len(subjects)!=1:
        fail("expected one static hair mesh; got "+str(len(subjects)))
    hair=subjects[0]
    hair.name="EnderV3_ORIGINAL_StaticHair_ART_HOLD"
    # V3's original generator authors Z-up/+Y-front coordinates directly
    # into glTF. Restore that authored frame after Blender's Y-up conversion.
    # The importer uses quaternion mode, so set the rotation mode explicitly.
    hair.rotation_mode="XYZ"
    hair.rotation_euler=(-math.pi/2,0,0)
    bpy.context.view_layer.update()
    source_top=hair.matrix_world @ hair.data.vertices[0].co
    if abs(source_top.z-.10498965)>0.0001 or abs(source_top.y)>0.0001:
        fail("authored scalp up-axis not restored")
    # Geometry in Blender scene remains imported source data; never rewrite GLB.
    geometry_bbox=[hair.matrix_world @ Vector(corner) for corner in hair.bound_box]
    x0=min(p.x for p in geometry_bbox)
    x1=max(p.x for p in geometry_bbox)
    y0=min(p.y for p in geometry_bbox)
    y1=max(p.y for p in geometry_bbox)
    z0=min(p.z for p in geometry_bbox)
    z1=max(p.z for p in geometry_bbox)
    if not (0.14<x1-x0<0.35 and 0.14<y1-y0<0.35 and 0.12<z1-z0<0.32):
        fail("source metre-unit bounds outside allowed study range")
    center=Vector(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
    target=center
    cameras=[
       ("01_FRONT_plus_Y",(0.,1.,.10)),
       ("02_THREE_QUARTER_plus_XY",(.75,.90,.18)),
       ("03_RIGHT_plus_X",(1.,0.,.10)),
       ("04_REAR_minus_Y",(0.,-1.,.10)),
    ]
    collection=bpy.data.collections.new("NONCANONICAL_4_CAMERA_STUDY")
    bpy.context.scene.collection.children.link(collection)
    for name,unit in cameras:
        direction=Vector(unit).normalized()
        cam_data=bpy.data.cameras.new(name)
        cam=bpy.data.objects.new(name,cam_data)
        collection.objects.link(cam)
        cam.location=center+direction*.65
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.type='ORTHO'
        cam.data.ortho_scale=.37
        cam.data.lens=65
        if name.startswith("01_"):
            bpy.context.scene.camera=cam
    # Give studio lighting for later manual comparison; DO NOT render now.
    for name,offset,power,size in (
        ("KEY_for_future_review",(0.2,0.30,0.50),100.0,.50),
        ("FILL_for_future_review",(-0.3,0.18,0.20),45.0,.60),
    ):
        lamp=bpy.data.lights.new(name,'AREA')
        lamp.energy=power
        lamp.shape='DISK'
        lamp.size=size
        obj=bpy.data.objects.new(name,lamp)
        collection.objects.link(obj)
        obj.location=center+Vector(offset)
        obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
    scene=bpy.context.scene
    scene.render.resolution_x=1024
    scene.render.resolution_y=1024
    scene.render.resolution_percentage=100
    # Built file is editable scene only. No final render, head, goggles or animation.
    hair["TSTSS_ART_APPROVED"]=False
    hair["TSTSS_NATIVE_UNREAL"]=False
    hair["TSTSS_HEAD_FIT_VERIFIED"]=False
    hair["TSTSS_RIGGED_GROOM"]=False
    hair["TSTSS_SOURCE_GLB_SHA256"]=pinned
    hair["TSTSS_SOURCE_UP_AXIS_CORRECTED"]=True
    scene["TSTSS_REVIEW_ONLY"]=True
    scene["TSTSS_APPROVED_ENDER_LIKENESS"]=False
    bpy.ops.wm.save_as_mainfile(filepath=str(destination),check_existing=True)
    if not destination.is_file():
        fail("Blender scene was not written")
    result={
       "state":"EDITABLE_DCC_SCENE_CREATED_ART_HOLD",
       "blender":"5.2.4 LTS",
       "source_sha256":pinned,
       "blend_sha256":hashlib.sha256(destination.read_bytes()).hexdigest(),
       "blend_file_size":destination.stat().st_size,
       "source_asset_has_not_been_modified":hashlib.sha256(source.read_bytes()).hexdigest()==pinned,
       "source_up_axis_corrected":True,
       "four_cameras":[x[0] for x in cameras],
       "creator_approved":False,
       "native_unreal":False,
       "actual_facial_or_goggle_fit":False,
       "animation_verified":False,
       "daz_data_used":False,
       "gpu_render_executed":False,
    }
    receipt.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("TSTSS_BLEND_SOURCE_SCENE_CREATED",json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
