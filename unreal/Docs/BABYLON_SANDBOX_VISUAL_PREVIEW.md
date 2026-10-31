# Babylon.js Sandbox — Aureate Wake rapid visual inspection

Browser viewer: https://sandbox.babylonjs.com/?from=3dviewer

Babylon Sandbox supports OBJ and glTF/GLB as well as material and animation inspection. Use it as an optional **pre-Unreal reviewer**, not as proof of Unreal runtime readiness.

1. Generate the wing OBJ and matching MTL via `python unreal/Tools/generate_dragonfly_wing.py --output /tmp/AureateWake_DragonflyWing_Prototype.obj`.
2. Open Sandbox and drop/select the **OBJ and MTL together**. With future GLB export, prefer self-contained GLB for materials/animations.
3. Inspect both membrane faces, normal orientation, silhouette, sharp edge outlines and clipping. Compare wing root +X convention before importing into Unreal.
4. For the four-form vessel, export a separate coherent assembly per form or an animated GLB and inspect wing count = 4, Orbiter cross = up/down/port/starboard, forward-facing bridge, Seaborne hydrofoils and slightly exposed Submersible wings.
5. Capture screenshots, exact input file hashes, viewer date and any defects as **browser preview evidence**. Do not call it a compiled UE acceptance result.
6. Complete Windows Unreal 5.8 compile, native asset import, in-engine render + material/animation capture and creator acceptance as separate release gates.

Reference: https://github.com/BabylonJS/Documentation/blob/master/content/toolsAndResources/sandbox.md
