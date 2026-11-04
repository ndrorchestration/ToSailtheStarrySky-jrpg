#!/usr/bin/env python3
"""Pure-stdlib, exact-source Skybourne camera/horizon composition contract.

This creates a *proposal* for a private Unreal 5.8.4 review map and camera.
It does not touch Unreal assets, approve ship art or fake GPU rendering.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

AUTHORITY="NONCANONICAL_V4_HORIZON_LOOKDEV_ONLY"
BASE_MAP="/Game/TSTSS/Review/Scenes/AureateCinematicV4_Skybourne_Hero_20261103_FullEditor"
REVIEW_MAP="/Game/TSTSS/Review/Scenes/AureateV4_Skybourne_HorizonAtmosphere_ReviewV1"
SOURCE_MAP_SHA="16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40"
FRAME=(1280,720)
HFOV_DEGREES=42.0
OLD_CAMERA=(1050.0,840.0,560.0)
OLD_TARGET=(0.0,0.0,40.0)
HERO_CAMERA=(900.0,1100.0,190.0)
HERO_TARGET=(0.0,0.0,80.0)
OCEAN_Z=-165.0  # Review reference only; not an approved sea level or physics surface.
HERO_LABEL="V4_NONCANONICAL_CAMERA_HORIZON_HERO_REVIEWV1"

def finite_vector(v):
    return len(v)==3 and all(math.isfinite(x) for x in v)

def frame_geometry(position,target,hfov=HFOV_DEGREES,frame=FRAME):
    """Angles are Euclidean local-level approximations, not globe horizon proof."""
    if not finite_vector(position) or not finite_vector(target):
        raise ValueError("Camera/target must contain three finite coordinates")
    width,height=frame
    if not (width>0 and height>0 and 1.0<hfov<120.0):
        raise ValueError("Invalid camera FOV or frame")
    dx=target[0]-position[0]
    dy=target[1]-position[1]
    dz=target[2]-position[2]
    horizontal=math.hypot(dx,dy)
    if horizontal<0.01:
        raise ValueError("Camera must have a meaningful horizontal viewing direction")
    vfov=math.degrees(2*math.atan(math.tan(math.radians(hfov)/2)*height/width))
    pitch=math.degrees(math.atan2(dz,horizontal))
    top=pitch+vfov/2
    bottom=pitch-vfov/2
    # Frame proportion estimate assumes rectilinear projection and the horizon
    # near zero elevation; does not include a real planet's curved horizon.
    fraction=max(0.0,min(1.0,top/vfov))
    return {"horizontal_fov_degrees":round(hfov,5),
            "vertical_fov_degrees":round(vfov,5),
            "camera_pitch_degrees":round(pitch,5),
            "top_ray_elevation_degrees":round(top,5),
            "bottom_ray_elevation_degrees":round(bottom,5),
            "approx_visible_sky_fraction":round(fraction,5),
            "local_horizon_intersects_frame":bool(bottom<0<top)}

def plan():
    previous=frame_geometry(OLD_CAMERA,OLD_TARGET)
    proposal=frame_geometry(HERO_CAMERA,HERO_TARGET)
    assert previous["top_ray_elevation_degrees"]<0, "Original comparison changed; re-audit"
    assert proposal["local_horizon_intersects_frame"], "Pilot view lost the local horizon"
    assert 0.25 <= proposal["approx_visible_sky_fraction"] <= 0.4, "Pilot sky fraction out of review bounds"
    return {
      "status":AUTHORITY,
      "engine_review_target":"Unreal Engine 5.8.4 / D3D11",
      "frame_dimensions":list(FRAME),
      "scene_base":BASE_MAP,"new_scene":REVIEW_MAP,
      "scene_source_sha256":SOURCE_MAP_SHA,
      "original_camera":{"location_cm":list(OLD_CAMERA),"target_cm":list(OLD_TARGET),
                         "geometry":previous,"must_remain_unchanged":True},
      "proposed_camera":{"actor_label":HERO_LABEL,"location_cm":list(HERO_CAMERA),
                         "target_cm":list(HERO_TARGET),
                         "horizontal_fov_degrees":HFOV_DEGREES,"geometry":proposal},
      "environment_proposal":{
        "sky":"UNREAL_SKY_ATMOSPHERE_ACTOR_NOT_A_BITMAP_BILLBOARD",
        "sun":"EXISTING_REVIEW_DIRECTIONAL_LIGHT_ATMOSPHERE_SUN_INDEX_0",
        "ambient":"UNREAL_SKYLIGHT",
        "haze":"LOW_DENSITY_EXPONENTIAL_HEIGHT_FOG_DIAGNOSTIC",
        "water":"PROVISIONAL_PBR_OCEAN_PLANE_WITH_NO_COLLISION_NO_BUOYANCY",
        "provisional_ocean_z_cm":OCEAN_Z,
        "human_scale":"170_CM_PROVISIONAL_UNIDENTIFIED_SILHOUETTE_NOT_CANON",
        "no_weather_or_physical_wave_simulation":True
      },
      "gates":[
        "NATIVE_NEW_MAP_ACTORS_AND_CAMERA_FOV_NOT_VERIFIED",
        "NATIVE_D3D11_PIXEL_CAPTURE_NOT_VERIFIED",
        "SKY_ATMOSPHERE_EXPOSURE_AND_MATERIAL_NOT_VERIFIED",
        "SAVED_MAP_ORIGINAL_SHA_MUST_REMAIN_UNCHANGED",
        "APPROVED_HULL_AND_GEODESIC_GLASS_DOME_NOT_IMPLEMENTED",
        "HORIZON_AND_GAMEPLAY_VISUAL_ACCEPTANCE_NOT_ESTABLISHED",
        "STARBOURNE_PLAYER_UNLOCK_REMAINS_CLOSED"
      ],
      "approvals":{"production_art":False,"playable":False,"release":False,
                   "starbourne_player_unlock":False},
      "description":"Proposal only. No player-map, Story, SaveGame, physics, UE install or existing four-form review-map mutations."
    }

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,help="Unique offline JSON evidence path, outside repo")
    parser.add_argument("--check",action="store_true",help="Check an existing immutable plan")
    args=parser.parse_args(argv)
    data=plan()
    blob=(json.dumps(data,sort_keys=True,indent=2)+"\n").encode("utf8")
    if args.check:
        if args.output is None or not args.output.is_file() or args.output.read_bytes()!=blob:
            parser.error("Plan does not match exact deterministic bytes")
    elif args.output:
        with args.output.open("xb") as stream:stream.write(blob)
    print(json.dumps({"authority":AUTHORITY,
                      "plan_sha256":hashlib.sha256(blob).hexdigest(),
                      "old_sky_fraction":data["original_camera"]["geometry"]["approx_visible_sky_fraction"],
                      "pilot_sky_fraction":data["proposed_camera"]["geometry"]["approx_visible_sky_fraction"],
                      "native_rendered":False},sort_keys=True))

if __name__=="__main__":
    main()
