# Ender V3 head-landmark prototype — source + native Unreal evidence

2026-11-02 (US/Eastern). **REVIEW ONLY — CINEMATIC LIKENESS NOT APPROVED**. This work is stacked on [PR #715](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/715), itself stacked on [PR #663](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/663). No merge, release, gameplay pawn, battle animation, author-approved cast asset, or canonical game change.

## Canon reference and approval boundary

The creator-approved October 30 five-person cast imagery, the existing Ender appearance proof and [Notion Character Art Direction & Implementation Contract](https://app.notion.com/p/3e2f5bad238b8109b13ce1328d65910c) remain the authority. Preserve Ender (22), green eyes, forehead goggles with brass detailing, scholar/mechanic olive-and-cream layering, practical satchel and two-ended fighting staff with centered wrapping and brass ferrules. Party height ranking remains **Reson > Aepex > Ender > Ionia > Lyra**; model source lengths are not approved exact canonical heights.

**Reference conflict:** Earlier approved Ender full-body proof shows auburn/copper hair, while later character group imagery presents greenish hair. This V3 deliberately inherits the noncanonical green V2 palette. No automatic hair-color or face-likeness adoption is authorized. Facial 3D landmark coordinates are model-space study coordinates, NOT measured annotated features of the approved 2D art. Eyes, jaw, mouth, nose and goggles require artist-guided placement and approved likeness verification.

## What was independently built

- Derived immutable `FidelityCandidates/EnderV3/Ender_ender_head_landmark_v3.glb`; **source SHA-256 `0fb1b6e8de8d84ce751ce8bbb97b7ca78174e077acf64f60e127bd0ddb90c2de`**, **371,188 bytes**, **16,492 triangles**, **182 named parts**, **36 material sections**.
- New parametric orbital-socket recession, cheekbone plane, chin/jaw shaping and delicate lower-orbit crease; independent named head mesh and provisional source-space facial anchors.
- Replaces 54 V2 symmetric stiff hair ribbons with 62 asymmetrically swept ribbon sections (28 front + 16 temple + 18 nape). This is **not** groom-quality hair geometry/physics or UV-textured PBR.
- Retains V2 waistcoat/collar foundation, existing staff, proportions and accessories; original Ender, V1, V2 GLB SHA-256 values individually checked unchanged.
- Both source and asset are strictly separate from the production Unreal project, with an immutable-output refusal and explicit `art_approval=false`, `creator_approval=false`, `skin_or_rigged=false`, `gameplay_ready=false` in the source receipt.

## Verification performed, not inferred

**Engine-free:** `verify_ender_fidelity_v3.py` checked genuine glTF BIN/indexed triangles, surface orientation, norms, structural glTF integrity, named parts and predecessor hashes. The 6 generator/source tests and 3 native provenance/safety tests **9/9 PASS** locally. Confirmed local generator deterministic over two fresh output directories (not cross-host bitwise parity). The independent native report checker reads actual PNG files, not screenshot task success messages.

**Actual native UE5.8.4 on authorized Windows `neontic`:** New disposable `C:\E6\CastAllSandbox`. Native Unreal NullRHI StaticMesh import automation `Editor.Python.CastAllSandbox.test_ender_v3_import_native`: **Success / exit 0**, one native static mesh at `/Game/ArtLookdev/Characters/EnderLandmarksV3`. Staff-inclusive native Z extent **185.800003 cm** (scale check only), intake receipt matches exact candidate GLB. Then a separate real **D3D11 SM5** Editor Python automation `Editor.Python.CastAllSandbox.test_ender_v3_head_native`: **Success / exit 0**. It temporarily moves the saved V2 comparison actor out of view, spawns the V3 actor and three transient cameras, does NOT save a level. Independent `verify_ender_v3_native_captures.py` **exit 0 / `V3_NATIVE_SCREENSHOT_INTEGRITY_PASS_ART_HOLD`**, validated CRC/IDAT, 1280×720 image dimensions, distinct image hashes, visible center subject and authentic nested `Incoming.png` in the Editor screenshot reports:

- [Actual native front](ReviewCaptures/2026-11-02/EnderV3Head/v3_head_front.png): SHA-256 `8526d682ac5006b65b09a667f71cc75000b96950e63106507e4b4f9f8fba9149`; central foreground 0.4021.
- [Actual native three-quarter](ReviewCaptures/2026-11-02/EnderV3Head/v3_head_three_quarter.png): SHA-256 `abfc6b1e917fb0e603bb36b77db2835bbd6305fb3ce1785d9f57f5e936dde820`; central foreground 0.3427.
- [Actual native profile](ReviewCaptures/2026-11-02/EnderV3Head/v3_head_profile.png): SHA-256 `a399f95a6b3b8bdb23ca2a3b44f8818e1872736552c4c995ee98be0e6b28c7fc`; central foreground 0.2150.

All three are original UE D3D11 captures, **not** generated concept images, raster flips or art approval. Original saved V2 review map SHA-256 was verified before and after native rendering **unchanged**: `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`. Local evidence logs: `C:\E6\EnderV3Intake.log` and `C:\E6\EnderV3HeadCapture.log`. The actual frames are committed to this review branch; full native task receipt and Editor logs remain on the authorized workstation.

## Genuine artistic inspection — FAIL/HOLD

Inspecting front, three-quarter and profile images shows modest technical progress in hair asymmetry and detectable cheek/orbital shaping, **but Ender remains toy-like**. Principal unresolved blockers:

1. Eyes have large triangular/oval disconnected reads, thick sclera and uncertain natural orbital fit; eyelid and lashes require actual retopology/rig.
2. Nose is oversized and bulbous, ears appear oversized/flat, chin and jaw faceting is obvious. Face does not match the approved naturalistic young adult likeness.
3. Hair ribbons overlap stiffly like sheets, have flat material response and lack authentic strand layering or approved exact color.
4. Forehead goggles and staff geometry are recognizable but remain prototype materials and fixed hand pose; no realistic physical grip, fabric or skin.
5. Closeup shading is dark and low-detail on clothing. Actual authored PBR textures, physically plausible lighting, cloth thickness and skeletal-ready topology remain absent.

No production skinning, expression, animation, retargeting, interactive pawn, combat technique, LOD/performance budget, creator art approval or actual resemblance signoff occurred. **NATIVE TECHNICAL VERIFICATION PASS / CINEMATIC ART ACCEPTANCE FAIL-HOLD.**

## Smallest next reversible milestone (proposal)

**Artist-authored, reference-space facial retopology** in a separate V4 review candidate: establish an approved 2D/3D face landmark overlay from creator reference, sculpt face/eyelids/nose/ears/neck with anatomical topology, groom natural head hair with clearly unresolved palette variant, then produce equal-perspective native UE front/profile/three-quarter closeups alongside V3. Require visible improvement in adult facial anatomy and silhouette, true PBR material look, source hashes, valid static/skeletal intent, exact native import and screenshot proof, and explicit owner visual signoff. Do not automatically promote the V3 prototype or merge review chain.
