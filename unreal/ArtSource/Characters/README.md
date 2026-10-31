# TSTSS five-character 3D lookdev — provisional

This package contains five **original, static glTF 2.0 meshes** generated from `build_cast.py`: Ender, Ionia, Lyra, Reson and Aepex. They are a reusable silhouette and layout study. They are **not** photorealistic or cinematic production assets, are not rigged or animated, and have not been imported, compiled, lit, or rendered in Unreal. The PNGs are offline model inspections, never engine captures. The October 30 approved cast sheet stays private and is not redistributed here.

## Ender first

Ender.glb is the first review target: youthful slender build, green eyes and goggles, cream shirt, olive vest, satchel, full 1.84 m staff with midpoint wrap and brass ferrules. The approved cast sheet depicts dark green hair, while an older character dossier specifies dark copper/auburn. The candidate follows the newer approved image; confirm the final hair treatment against the original references before accepting a production model.

## Cast relationships

The five named files have relative heights Reson (1.93 m) > Aepex (1.85 m) > Ender (1.74 m) > Ionia (1.68 m) > Lyra (1.65 m). These numerical heights are lookdev choices, **not canon**. Ionia's blonde curls extend past the shoulders; Lyra keeps red hair. Reson has the broadest frame; Aepex is second tallest with an undercut and visible arm markings. Accessories are schematic and carry no final costume or role approval. The sheet's printed role text is inconsistent with the project's character authority and was not used as canon.

## Unreal 5.8 import and visual gate

1. On the authorized Windows machine, compile and open `unreal/ToSailTheStarrySky.uproject` from the migration branch. Preserve the playable Godot build and its saves.
2. In a **separate review level**, import `Ender.glb` through Content Browser into `/Game/ArtLookdev/Characters/Ender`. The Unreal 5.8 Interchange importer supports glTF static geometry. Keep the imported asset in a candidate folder and record import settings, conversion scale, material warnings and source SHA. glTF Y-up metres may require conversion to Unreal Z-up centimetres; inspect the resulting bounds before placing anything.
3. Place Ender as a static mesh actor beside a 180 cm calibration marker. Inspect front, back, profile and 3/4 views at gameplay and cinematic distances under neutral and scene lighting. Check the staff length, midpoint wrap, goggles, green eyes, costume silhouette, face shape and material response side by side with the actual approved references. Do not bind it to the playable pawn yet.
4. Repeat the same review for Ionia, Lyra, Reson and Aepex. Verify Ionia's long curly blonde silhouette and individual visual identities, plus naming and height order.
5. Replace this rough source geometry with authored high-fidelity sculpt, topology, UVs, textures, hair, fitted outfit and shared humanoid skeleton; then skin, animate, LOD, profile and capture native Unreal frames. Integrate an accepted Ender skeletal mesh into `ATSTSSExplorerCharacter` only after gait, camera, collision and save tests pass. Obtain creator visual approval before a canon or release claim.

To reproduce the candidate GLBs and their SHA-256 manifest: `python3 build_cast.py`. To produce the optional offline render: `python3 render_review.py` (Pillow required). The GLBs use only procedural geometry and flat PBR color factors; there are no third-party asset dependencies.

## Evidence status

- `IMPLEMENTED`: five original valid glTF 2.0 static character lookdev meshes and deterministic source generator.
- `OPEN`: Unreal import, Editor build, native render, skeleton/skin, animation, materials/texture quality, cinematic likeness, creator acceptance, integration into gameplay.
- `CREATOR CANON`: five identities and approved illustration direction; no generated GLB has been accepted as canonical game art.
