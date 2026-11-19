"""Unreal Editor Python: create a four-wing-compatible veined dragonfly mesh and preview material.
Run in an UE 5.8 editor with Python Editor Script Plugin and Modeling Tools Editor Mode enabled.
This creates REVIEW PROTOTYPES; inspect resulting assets and render before use.
"""
import math
import unreal

ROOT = "/Game/TSTSS/Art/Prototype/AureateWake"
unreal.EditorAssetLibrary.make_directory(ROOT)
# Source surface exported as OBJ through a deterministic local intermediate.
# Unreal FBX/OBJ importer support depends on editor plugins; this script is intentionally
# a validation-first import aid, not a claim of creating engine assets automatically.
unreal.log("Aureate Wake authoring plan: run tools/unreal/generate_dragonfly_wing.py externally, then import the generated OBJ.")
unreal.log("Assign the imported wing mesh to AuthoredWingMesh on the actor Blueprint; build material using the documented parameters.")
