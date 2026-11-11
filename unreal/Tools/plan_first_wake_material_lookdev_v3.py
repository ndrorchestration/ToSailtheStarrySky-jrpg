"""First Wake V3 PBR material + architectural detail derivative of 115-actor World.

Review-only: original collision and milestones retained, no PIE or art approval.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import generate_first_wake_pbr_textures_v3 as pbr

ROOT_NAME = "TSTSS_VSliceLookdev_20261111"
BASE_LEVEL = "/Game/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1"
DEST_LEVEL = "/Game/TSTSS/Review/Scenes/FirstWake_MaterialLookdev_20261111_REVIEW_V3"
BASE_PATH = "Content/TSTSS/Review/Scenes/FirstWake_SliceObjects_20261110_REVIEW_V1.umap"
DEST_PATH = "Content/TSTSS/Review/Scenes/FirstWake_MaterialLookdev_20261111_REVIEW_V3.umap"
BASE_SHA = "837e537ab91339f56af006782c8e7dba9ac981d36eb800eb3b2a10c97661bbbc"
ORIGINAL_PATH = "Content/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3.umap"
ORIGINAL_SHA = "54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5"
MATERIAL_DIR = "/Game/TSTSS/Review/Environment/FirstWakeMaterialLookdevV3"
TEXTURE_DIR = MATERIAL_DIR + "/Textures"
RECEIPT = "Saved/FirstWakeMaterialLookdevV3/native_stage.json"
PREFIX = "TSTSS_MATERIAL_LOOKDEV_V3_"
ORIGINAL_HERO = "TSTSS_ENV_HARBOR_V1_CoastalHeroCamera"
MILESTONES=("FlyerDiscovery","IoniaHiring","AureateBoarding","LiftStation",
            "PressureStation","ReserveStation","EngineeringApproval")
FLOOR_LABEL="TSTSS_PRELUDE_REVIEW_Harbor_TraversalFloor"
HERO_LOCATION = (-2750, -3600, 850)
HERO_TARGET = (-1450, -1530, 350)
PIER_LOCATION = (-1900, -300, 650)
PIER_TARGET = (-850, 1200, -50)
MATERIALS = {
    "warm_stone_trim": ((0.72, 0.59, 0.46), 0.79),
    "blue_green_glass": ((0.095, 0.31, 0.37), 0.14),
    "dark_copper": ((0.21, 0.12, 0.085), 0.38),
    "sea_foam": ((0.61, 0.84, 0.78), 0.27),
    "ochre_canvas": ((0.68, 0.37, 0.20), 0.86),
    "quay_stone": ((0.27, 0.33, 0.36), 0.81),
    "harbor_plaster": ((0.62, 0.57, 0.49), 0.85),
    "warm_roof": ((0.52, 0.24, 0.18), 0.88),
    "dock_timber": ((0.37, 0.25, 0.17), 0.88),
    "patina_metal": ((0.17, 0.41, 0.41), 0.51),
}

@dataclass(frozen=True)
class Detail:
    name: str
    mesh: str
    xyz: tuple[float, float, float]
    scale: tuple[float, float, float]
    role: str

def make_details() -> tuple[Detail, ...]:
    details = []
    def add(name, mesh, xyz, scale, role):
        details.append(Detail(name, mesh, tuple(xyz), tuple(scale), role))
    facades = (
        ("Customs", -3200, -1550, 660, 600, 400, (-3370, -3200, -3030)),
        ("IoniaOffice", -1450, -1530, 560, 580, 340, (-1610, -1450, -1290)),
        ("Engineering", 250, -1580, 760, 850, 420, (0, 250, 500)),
        ("Drydock", 1275, -1500, 420, 480, 320, (1150, 1275, 1400)),
    )
    for label, cx, cy, height, width, depth, xs in facades:
        face = cy - depth / 2 - 13
        add(label + "_DoorRecess", "Cube", (cx, face, 130), (1.27, .18, 2.60), "dark_copper")
        add(label + "_DoorPanel", "Cube", (cx, face - 13, 125), (1.03, .13, 2.40), "blue_green_glass")
        add(label + "_DoorLintel", "Cube", (cx, face - 15, 266), (1.6, .25, .22), "warm_stone_trim")
        for j, x in enumerate(xs):
            z = min(height - 155, 360)
            add(label + f"_WindowFrame_{j+1}", "Cube", (x, face, z), (1.14, .16, 1.42), "dark_copper")
            add(label + f"_WindowPane_{j+1}", "Cube", (x, face - 12, z), (.89, .07, 1.18), "blue_green_glass")
            add(label + f"_WindowCrossbar_{j+1}", "Cube", (x, face - 18, z), (.90, .09, .065), "warm_stone_trim")
        add(label + "_Cornice", "Cube", (cx, face + 20, height - 38),
            ((width + 55) / 100, .35, .22), "warm_stone_trim")
        for side, x in (("West", cx - width/2 + 14), ("East", cx + width/2 - 14)):
            add(label + "_CornerTrim" + side, "Cube", (x, face + 23, height/2),
                (.22, .25, height / 100), "warm_stone_trim")
        add(label + "_RoofGild", "Cube", (cx, cy, height + 112),
            ((width - 40)/100, .18, .12), "dark_copper")
    # Dockside railing and mooring architectural details, all visual-only.
    for ix, xpos in enumerate((-1190, -510)):
        for iy, ypos in enumerate((1230, 1430, 1630, 1830)):
            add(f"PierBannister_{ix}_{iy}", "Cylinder", (xpos, ypos, 104),
                (.17, .17, 2.1), "dark_copper")
        add(f"PierRail_{ix}", "Cube", (xpos, 1530, 206),
            (.20, 6.5, .16), "warm_stone_trim")
    # Harbor shoreline foam is a visual layer, not an ocean simulation.
    for idx, (x,y,sx,sy) in enumerate((
            (-1450, 985, 35, .24), (1200, 985, 18, .25),
            (-850, 1175, 7.4, .24), (-850, 1935, 7.4, .27)), 1):
        add(f"QuayEdgeFoam_{idx}", "Cube", (x, y, -4), (sx, sy, .045), "sea_foam")
    for idx, (x, y, z) in enumerate((
            (-2320,-1190,375),(-2210,-1190,375),
            (-500,-1110,300),(-300,-1110,300),
            (600,-1180,350),(800,-1180,350)), 1):
        add(f"MarketSailPanel_{idx}", "Cube", (x, y, z), (1.45, .045, 1.15), "ochre_canvas")
    return tuple(details)

DETAILS = make_details()

def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def validate_plan():
    import math
    if len(DETAILS) < 65:
        raise ValueError("Insufficient original harbor lookdev details")
    if len({x.name for x in DETAILS}) != len(DETAILS):
        raise ValueError("Duplicate lookdev actor labels")
    if {x.role for x in DETAILS} - set(MATERIALS) or set(MATERIALS) != set(pbr.ROLES):
        raise ValueError("Incorrect lookdev material inventory")
    for item in DETAILS:
        if item.mesh not in {"Cube","Cylinder"}:
            raise ValueError("Unsupported review mesh")
        if not all(math.isfinite(x) for x in (*item.xyz, *item.scale)):
            raise ValueError("Nonfinite geometry")
        if min(item.scale) <= 0:
            raise ValueError("Negative or zero geometry scale")
        if abs(item.xyz[1]) - 50 * item.scale[1] < 400:
            raise ValueError("Review geometry intrudes into player corridor: " + item.name)
    return {
        "status": "SOURCE_FIRSTWAKE_PBR_LOOKDEV_NOT_NATIVE",
        "from_sha": BASE_SHA, "destination": DEST_LEVEL,
        "pbr_source_textures":len(pbr.ROLES)*len(pbr.CHANNELS),
        "preserve_seven_story_interactions":True,
        "collision_floor_surface_only":True,
        "runtime_developer_labels_retained":True,
        "expected_original_actors": 115,
        "new_visual_only_details": len(DETAILS),
        "new_materials": sorted(MATERIALS),
        "hero_camera_reframed": False, "original_camera_untouched": True,
        "new_pier_camera": True,
        "collision": "NoCollision", "pie_verified": False,
        "art_approved": False, "starbourne_unlocked": False,
    }


if __name__=="__main__":
    import json
    print(json.dumps(validate_plan(),indent=2,sort_keys=True))
