# Ender — original dark-copper hair in Unreal (2026-11-04)

**Review only / static look-development / NOT canonical, not wearable-fitted, not rigged, not complete.** Stacked on the live Ender V5 review branch at `9c6d711dad1a177092f628318de16605c24b7192`, *not* protected `main` or the playable Ender pawn. All work performed in a new isolated Git worktree and disposable `MH5/CastAllSandbox` UE 5.8.4 project.

## Creator art and intended design

The established earlier `Ender: Solarpunk RPG Character Sheet.png` and earlier character reference board show a young adult Ender, **bright green eyes, short tousled dark-copper/auburn hair with an asymmetric swept fringe**, and aviator goggles positioned above the eyes. These art images remain in the creator's **private Library**; they are deliberately *not copied to GitHub*. The newer group artwork may show greener hair; never infer creator resolution or alter existing approved artwork from a script. Realism means believable curvature, scale and lighting; cinema means framing, atmospheric depth and readable contrast.

**Do not confuse this authored procedural mesh with a MetaHuman Groom, professional hair cards, final facial likeness, or gameplay hair integration.** Daz/Genesis, MetaHuman Creator Core Data, and artistic review remain separate possibilities. Daz Store geometry is not admitted to a game without any necessary interactive-use rights.

## Original new V1 generated asset and genuine native proof

- `Candidates/Ender_DarkCopper_LayeredHair_V1_NONCANONICAL.glb`, SHA-256 `01bb9f400454d633c5e887cd47a12fd1af34e5bbf6b7c05ab6a5929b0a6db562`, 1,066,716 bytes, **43,634 triangles**, five PBR material primitives. 267 separate authored parts: scalp cap, 190 crown locks, 23 fringe locks, 30 side locks, 24 nape locks. Generated entirely in source-controlled Python with no copyrighted texture/reference pixels. Host regeneration against a new output directory was **byte-for-byte identical**.
- Source geometry check `verify_ender_copper_hair_v1.py` PASS: glTF buffer and accessor integrity, source hash, geometry bounds 23.030 × 24.337 × 18.718 cm in source axes, finite positions/normals and nondegenerate triangles. Review-only flags enforced.
- A **genuine UE5.8.4 NullRHI native import** in disposable MH5 completed `NATIVE_ENDER_HAIR_STATIC_IMPORT_PASS_FIT_AND_ART_HOLD`. One new StaticMesh, five material slots, actual converted Unreal bounds X=23.0297/Y=18.7177/Z=24.3367 cm. Source MetaHuman and review map retained their exact previous SHA-256.
- A **genuine UE5.8.4 D3D11 render** placed the imported original V1 hair StaticMesh on the actual transient V5 MetaHuman face with independently imported sealed-aviator V2 goggles and 10%-power studio light rig. The real engine 480 × 320 PNG core SHA-256 is `fc3e70b005c9c6f4af419de9a91a1d6d077811969f0b816ec8fe72467f68bdcc`. Its native receipt status is `NATIVE_ENDER_COPPER_HAIR_V1_AND_GOGGLES_V2_GPU_PASS_ART_HOLD`. Exact private PNG and raw native receipt remain on NEONTIC.
- **Visual QA FAIL** even though rendering was technically successful: material looked straw/pale, strands formed rope-like/wicker masses, fringe and sides were not framing Ender's face, crown cropped out of camera; goggles were detached, and scalp fit was not proven. These are reasons to *reject V1 visually*, not to approve it.

## V2 correction, built without altering V1

`CandidatesV2/Ender_DarkCopper_LayeredHair_V2_NONCANONICAL.glb` is an independent, immutable original source candidate. SHA `0da20d3b34e3fdf6171476db1736d2e2607987c71403272207e428f18c8ca9cd`; 701,104 bytes, **28,544 triangles**, five darker matte copper/chestnut material sections, 196 authored parts. Relative to V1, it reduces crown locks from 190 to 104, widens/flattens tufts, lowers/lengthens fringe and side hair, darkens the palette and tapers strand clumps. This is a technical revision and not yet an artistic success. Independent V2 source validator passed. Separate V2 generation also reproduced the original V2 GLB **byte-for-byte** on NEONTIC.

A distinct **actual UE 5.8.4 native V2 StaticMesh import has passed**, preserving exact original MetaHuman, level and V1 source hashes. V2 native import receipt status: `NATIVE_ENDER_HAIR_V2_STATIC_IMPORT_PASS_FIT_AND_ART_HOLD`; converted bounds X=23.0270/Y=18.4382/Z=24.9912 cm; five material slots. This validates static asset intake, not a rig or artistic likeness.

**V2 native beauty shot:** `native_capture_ender_hair_v2_v2_goggles_20261104.py` is source-prepared with its own unique output path, lower hair center `z=169.7 cm` and independently framed camera. It must only run when no other user's Unreal session is active and adequate RAM exists. Until its genuine GPU PNG and independent visual inspection are complete, keep `V2_VISUAL_ACCEPTANCE=HOLD`. Do not infer the image exists from the executable script alone.

## Native skeletal readback limitation

Read-only UE 5.8.4 `native_probe_v5_head_bounds_20261104.py` confirmed the real MetaHuman transient `Face`/`Body` skeletal preview components and named `head`/face-root bone locations without altering source assets. However, the attempted `get_component_bounds()` API was **unavailable** on Unreal's `DebugSkelMeshComponent` in this configuration. Therefore no actual skull surface, hairline contact, eye clearance or scalp intersection was proven. The hair location remains an **approximate source/visual trial** and must not be treated as physical fit.

## Source, evidence and acceptance guardrails

- Original V5 MetaHuman UAsset SHA: `2bb581a27aee55b0352f52227a3afe2c6d01a529b63c8dc661cbe8f4edbb2e3d`.
- Original V2 review map SHA: `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`.
- Original **sealed goggles V2** source GLB SHA on host: `5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb`. This is the semantically regenerated, on-host binary, *not byte-parity with the original separately packaged asset*. V1 thin spectacle-like glasses remain rejected.
- Five PBR hair materials and 6/6 engine-free source/tampering/anti-approval tests PASS. Native import and genuine V1 GPU capture are *separate* proofs. GitHub CI cannot render Unreal or check the private screenshot pixels.
- No protected-main merge, production actor/SaveGame change, facial mesh sculpt, MetaHuman source edit, level save, V2 goggles replacement, animation-ready hair groom, creator acceptance or new licensing assumption.

**Ender's character is only done when** the approved face silhouette/expression is matched in genuine native multi-angle images, dark-copper hair and sealed goggles physically/visually fit, staff/clothes/grip are accurately modeled, body/face skeletons and hair attachment work in runtime animation, the actor is connected to a playable First Wake encounter, and creator-approved camera/material/character acceptance is recorded with source-locked native evidence. A fixed-camera V1/V2 hair visual comparison must precede any promotion, and more professional grooming may replace these procedural candidates entirely.

This documentation is a bounded evidence log, not a claim of finished playable Ender.
