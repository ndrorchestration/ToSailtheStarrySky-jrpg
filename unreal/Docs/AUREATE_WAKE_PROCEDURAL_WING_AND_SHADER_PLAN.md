# Aureate Wake — Procedural Wing & Iridescent Orbiter Material Prototype

**Stage:** geometric OBJ generator committed; Unreal import, rendering and material asset creation NOT verified.

Run `python unreal/Tools/generate_dragonfly_wing.py --output /path/AureateWake_DragonflyWing_Prototype.obj` in Python 3. This outputs a closed two-sided tapered dragonfly-inspired **plain wing shell**, centered at local +X from its root. The generator does not yet create actual raised veins, detailed UVs, normals, or a skeletal articulation rig. It must not be described as final cinematic art. The optional Unreal Python helper provides guidance only; it does not create a material asset automatically.

**Proposed Unreal shader graph** (must be manually authored and validated):
1. Build `M_AureateWakeWing`, Surface, Default Lit / Two Sided; start with an opaque test, then evaluate thin translucent materials separately for performance.
2. Add scalar `OrbiterSailBlend` (0..1), Fresnel with view-angle-dependent secondary color, fine fractal vein mask using mesh UVs, and controlled metallic/roughness interpolation.
3. Atmospheric side: blue/teal iridescent semi-transparent dragonfly membrane with brass spars. Orbiter side: layered pearlescent photovoltaic cells with light-sail reflective film. The fictional metamaterial is a **narrative visual**, not a real-world physics claim.
4. Clamp emissive output; assess temporal shimmer/TAA, back-facing transparency, nighttime readability and cinematic composition at 1080p and 4K.
5. Keep four exactly equal wing objects in Orbiter, aligned up/down/port/starboard, and the bridge facing forward.

**Hard stop gates:** inspect OBJ integrity, build static mesh with appropriate normals and UVs, validate shell/manifold and shading, native UE 5.8 Windows compile, native screenshots, and creator approval. Neither the Python generator nor C++ bindings establishes a completed working engine material.
