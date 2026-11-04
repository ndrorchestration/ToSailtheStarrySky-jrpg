"""TSTSS original evocative granular-surface lookdev, opt-in Unreal 5.8 material review.

Artistic reference: Journey's *experience* of luminous dunes and expressive winter.
All HLSL and scene composition here are original; no Journey assets/code or
proprietary implementations. No gameplay, terrain geometry, physics or saves.
--validate is engine-free; --build requires an idle, clean Unreal Editor.
"""
from __future__ import annotations
import argparse
import hashlib
import json

ROOT = "/Game/TSTSS/Review/EvocativeGranular_V2"
SURFACES = ("SilkenDune", "WindCrustSnow")
ART_AUTHORITY = "JOURNEY_INSPIRED_ORIGINAL_NONCANONICAL_REVIEW"
NATIVE_RENDER = "NOT_RUN"

# RGB outputs are linear albedo, A is material roughness. Static wind/ripple
# cues represent a single unapproved study orientation, not world-scale climate.
COLOR_HLSL = r"""
float2 p = UV * clamp(Tiling, 0.25, 32.0);
float2 wind = normalize(float2(0.79, 0.61));
float2 crosswind = float2(-wind.y, wind.x);
float across = dot(p, wind);
float lateral = dot(p, crosswind);
float ripple = 0.5 + 0.5 * sin(22.0*across + 1.3*sin(3.1*lateral));
float detail = 0.5 + 0.5 * sin(p.x*143.0 + sin(p.y*117.0));
if (Mode < 0.5) {
    float3 lo = float3(0.26, 0.125, 0.05);
    float3 hi = float3(0.70, 0.47, 0.19);
    float3 golden = lerp(lo, hi, saturate(0.17 + 0.83*ripple));
    float roughness = lerp(0.72, 0.52, ripple);
    return float4(golden*(0.96 + 0.04*detail), saturate(roughness));
}
float windCrust = saturate(Crust);
float drift = 0.5 + 0.5*sin(5.3*across + 0.9*sin(2.4*lateral));
float3 powder = float3(0.66, 0.79, 0.87);
float3 crest = float3(0.93, 0.955, 0.975);
float3 snow = lerp(powder, crest, 0.22 + 0.78*drift);
return float4(snow*(0.97 + 0.03*detail),
    saturate(lerp(0.80, 0.65, windCrust)));
"""

# Tangent-space shading perturbation only, never displacement or physics data.
NORMAL_HLSL = r"""
float2 p = UV * clamp(Tiling, 0.25, 32.0);
float angle = p.x*21.0 + sin(p.y*3.1)*1.3;
float windCrust = saturate(Crust);
float2 slope;
if (Mode < 0.5) {
    slope = float2(cos(angle)*0.16,
        cos(angle)*cos(p.y*3.1)*0.032);
} else {
    float crustPhase = p.x*5.3 + sin(p.y*2.4)*0.9;
    slope = float2(cos(crustPhase)*lerp(0.045,0.082,windCrust),
                   cos(crustPhase)*cos(p.y*2.4)*0.038);
}
return normalize(float3(-slope.x,-slope.y,1.0));
"""

# Stylized daylight lobe & sparse sun-gated glints. IMPORTANT: the fixed light
# direction is a review fixture parameter and MUST be fed by the single actual
# world sun controller before gameplay admission. No genuine volumetric snow.
HIGHLIGHT_HLSL = r"""
float q = saturate(Quality);
float sun = saturate(SunStrength);
float3 n = normalize(NormalWS);
float3 v = normalize(ViewDir);
float3 l = normalize(SunDir.xyz);
float3 h = normalize(v+l+float3(0.00001,0.00001,0.00001));
float nl = saturate(dot(n,l));
float vh = saturate(dot(n,h));
float rim = pow(1.0-saturate(dot(n,v)),4.0)*nl;
float broad = pow(vh, 12.0)*nl;
float2 p = UV*clamp(Tiling,0.25,32.0);
float2 cell = floor(p*154.0);
float chance = frac(sin(dot(cell,float2(127.1,311.7)))*43758.5453);
float pixFootprint = max(fwidth(p.x*154.0),fwidth(p.y*154.0));
float glitterMask = smoothstep(0.9965,0.9998,chance);
float antialias = saturate(1.0 - pixFootprint*0.42);
float glint = glitterMask*pow(vh,18.0)*antialias*nl;
float sand = 1.0-step(0.5,Mode);
float3 tint = lerp(float3(0.36,0.55,0.73),float3(1.0,0.72,0.32),sand);
float crust = saturate(Crust);
float snowFactor = lerp(0.10,0.28,crust);
float intensity = lerp(snowFactor,1.0,sand);
float glow = (broad*saturate(Sheen)*0.22
    + rim*saturate(Sheen)*0.075
    + glint*saturate(Glitter)*0.42)*intensity*q*sun;
return tint * min(glow,0.65);
"""


def validate():
    if not ROOT.startswith("/Game/TSTSS/Review/") or len(set(SURFACES)) != 2:
        raise ValueError("Must use unique noncanonical review path")
    combined = COLOR_HLSL + NORMAL_HLSL + HIGHLIGHT_HLSL
    if any(bad in combined for bad in ("WorldPositionOffset", "SceneDepth",
                                       "Time *", "#include", "Texture2DSample")):
        raise ValueError("Optical study cannot modify geometry or import sources")
    return {
        "authority": ART_AUTHORITY,
        "root": ROOT,
        "surfaces": list(SURFACES),
        "native_render": NATIVE_RENDER,
        "shader_sha256": hashlib.sha256(combined.encode("utf8")).hexdigest(),
        "production_terrain_edited": False,
        "weather_simulation": False,
        "footprint_system": False,
        "material_inputs": [
            "UV", "Mode", "Tiling", "Crust", "Sheen", "Glitter",
            "Quality", "SunStrength", "SunDir", "NormalWS", "ViewDir",
        ],
    }


def preflight(u):
    if u.EditorAssetLibrary.does_directory_exist(ROOT):
        raise RuntimeError("Review destination already occupied; refusing overwrite")
    if (u.EditorLoadingAndSavingUtils.get_dirty_map_packages()
            or u.EditorLoadingAndSavingUtils.get_dirty_content_packages()):
        raise RuntimeError("Unreal Editor has unsaved assets or maps")
    shapes = {
        k: u.load_asset(f"/Engine/BasicShapes/{k}.{k}") for k in ("Plane", "Sphere")
    }
    if not all(shapes.values()):
        raise RuntimeError("Review basic-shape mesh missing")
    return shapes


def require_connection(result, label):
    if not result:
        raise RuntimeError("Could not connect material node: " + label)


def require_compilation(errors):
    if errors is None or errors:
        raise RuntimeError("UE shader compilation unverified/failed: " + str(errors))


def create_surface(u, mode, name):
    edit = u.MaterialEditingLibrary
    asset_tools = u.AssetToolsHelpers.get_asset_tools()
    mat = asset_tools.create_asset("M_" + name, ROOT, u.Material, u.MaterialFactoryNew())
    if not mat:
        raise RuntimeError("Material creation failed for " + name)

    def node(kind, **properties):
        item = edit.create_material_expression(mat, getattr(u, "MaterialExpression" + kind))
        if not item:
            raise RuntimeError("Material expression creation failed: " + kind)
        for key,value in properties.items():
            item.set_editor_property(key, value)
        return item

    def custom(code, output, inputs, description):
        expr = node("Custom", code=code, output_type=output, description=description)
        vals = []
        for inp in inputs:
            slot = u.CustomInput()
            slot.set_editor_property("input_name",inp)
            vals.append(slot)
        expr.set_editor_property("inputs",vals)
        return expr

    sources = {
        "UV": node("TextureCoordinate"),
        "Mode": node("Constant", r=float(mode)),
        "ViewDir": node("CameraVectorWS"),
        "NormalWS": node("VertexNormalWS"),
        "SunDir": node("VectorParameter", parameter_name="ReviewSunDirectionWS",
                       default_value=u.LinearColor(0.33,0.48,0.81,1.0)),
    }
    for name_,value in (
        ("Tiling",1.0),("Crust",0.55),("Sheen",0.75),("Glitter",0.45),
        ("Quality",1.0),("SunStrength",0.75),
    ):
        sources[name_] = node("ScalarParameter",
                              parameter_name=name_,default_value=value)

    def feed(expr,keys):
        for key in keys:
            require_connection(
                edit.connect_material_expressions(sources[key],"",expr,key),key)

    color = custom(COLOR_HLSL,u.CustomMaterialOutputType.CMOT_FLOAT4,
                   ("UV","Mode","Tiling","Crust"),"Original granular albedo/roughness")
    feed(color,("UV","Mode","Tiling","Crust"))
    rgb=node("ComponentMask",r=True,g=True,b=True,a=False)
    rough=node("ComponentMask",r=False,g=False,b=False,a=True)
    # UE MaterialEditingLibrary treats an empty input name as the first pin.
    # Do not assume a translated/variant ComponentMask pin is named 'Input'.
    require_connection(edit.connect_material_expressions(color,"",rgb,""),"color")
    require_connection(edit.connect_material_expressions(color,"",rough,""),"roughness")
    require_connection(
        edit.connect_material_property(rgb,"",u.MaterialProperty.MP_BASE_COLOR),
        "base color")
    require_connection(
        edit.connect_material_property(rough,"",u.MaterialProperty.MP_ROUGHNESS),
        "roughness")

    normal = custom(NORMAL_HLSL,u.CustomMaterialOutputType.CMOT_FLOAT3,
                    ("UV","Mode","Tiling","Crust"),"Original wind ripple normals")
    feed(normal,("UV","Mode","Tiling","Crust"))
    require_connection(
        edit.connect_material_property(normal,"",u.MaterialProperty.MP_NORMAL),
        "normal")

    light = custom(HIGHLIGHT_HLSL,u.CustomMaterialOutputType.CMOT_FLOAT3,
                   ("UV","Mode","Tiling","Crust","Sheen","Glitter","Quality",
                    "SunStrength","SunDir","NormalWS","ViewDir"),
                   "Original bounded highlight; NOT physical sparkle simulation")
    feed(light,("UV","Mode","Tiling","Crust","Sheen","Glitter","Quality",
                "SunStrength","SunDir","NormalWS","ViewDir"))
    require_connection(
        edit.connect_material_property(light,"",u.MaterialProperty.MP_EMISSIVE_COLOR),
        "bounded art-direction highlight")

    edit.layout_material_expressions(mat)
    require_compilation(edit.recompile_material(mat))
    if not u.EditorAssetLibrary.save_loaded_asset(mat):
        raise RuntimeError("Material save failed")
    inst = asset_tools.create_asset(
        "MI_" + name, ROOT, u.MaterialInstanceConstant, u.MaterialInstanceConstantFactoryNew())
    if not inst:
        raise RuntimeError("Review instance creation failed")
    edit.set_material_instance_parent(inst,mat)
    edit.update_material_instance(inst)
    if not u.EditorAssetLibrary.save_loaded_asset(inst):
        raise RuntimeError("Instance save failed")
    return inst


def build():
    try:
        import unreal as u
    except ImportError as exc:
        raise RuntimeError("--build requires Unreal Engine Editor Python") from exc
    if not hasattr(u,"MaterialEditingLibrary"):
        raise RuntimeError("--build requires Unreal Engine Editor Python")
    plan=validate()
    meshes=preflight(u)
    instances=[create_surface(u,i,name) for i,name in enumerate(SURFACES)]
    world=u.EditorLoadingAndSavingUtils.new_blank_map(False)
    if not world:
        raise RuntimeError("Could not create separate material review map")
    actors=u.get_editor_subsystem(u.EditorActorSubsystem)

    def spawn(cls,label,position,rotation=(0,0,0)):
        actor=actors.spawn_actor_from_class(cls,u.Vector(*position),u.Rotator(*rotation))
        if actor is None:
            raise RuntimeError("Review actor spawn failed: "+label)
        actor.set_actor_label("NONCANONICAL_GRANULAR_V2_"+label)
        return actor

    for i,(name,instance) in enumerate(zip(SURFACES,instances)):
        x=(i-0.5)*900
        for geometry,pos,scale in (
            ("Plane",(x,0,0),(7.0,7.0,1.0)),
            ("Sphere",(x,190,95),(1.8,1.8,1.8)),
        ):
            actor=spawn(u.StaticMeshActor,name+"_"+geometry,pos)
            comp=actor.get_component_by_class(u.StaticMeshComponent)
            comp.set_static_mesh(meshes[geometry])
            comp.set_material(0,instance)
            comp.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
            actor.set_actor_scale3d(u.Vector(*scale))
    spawn(u.DirectionalLight,"Sun",(0,0,1500),(-42,-35,0))
    spawn(u.SkyLight,"SkyFill",(0,0,300))
    spawn(u.SkyAtmosphere,"Sky",(0,0,0))
    spawn(u.CineCameraActor,"Overview",(0,-2200,950),(-21,90,0))
    if not u.EditorLoadingAndSavingUtils.save_map(world,ROOT+"/GranularReview"):
        raise RuntimeError("Could not save unique granular review map")
    plan["native_shader_compilation"]="EDITOR_REPORTED_NO_ERRORS_NOT_GPU_ACCEPTANCE"
    plan["native_render"]="NOT_CAPTURED"
    u.log(json.dumps(plan,sort_keys=True))
    return plan


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate",action="store_true")
    group.add_argument("--build",action="store_true")
    args=parser.parse_args()
    print(json.dumps(build() if args.build else validate(),indent=2))
