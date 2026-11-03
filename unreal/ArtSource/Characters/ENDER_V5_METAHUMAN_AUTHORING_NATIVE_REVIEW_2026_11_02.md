# Ender V5 — MetaHuman facial-authoring feasibility (native, review only)

**Date:** November 2, 2026 US/Eastern (UE log records November 3 UTC). **Milestone: native MetaHuman *authoring foundation* PASS; likeness and production readiness HOLD.** Reversible branch stacked on [Ender V4 facial-topology PR #718](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/718) at exact parent `acdd771d8fcbcf6762fcf8d07810589737521243`.

## Why this change instead of another procedural face

The V4 screenshots prove that tweaks to disconnected procedural eye, nose, ear and hair primitives are failing to achieve the artistic direction. The latest approved October 30 cast and earlier approved Ender full-body sheet show a youthful 22-year-old, expressive bright green eyes, goggles, tousled hair, practical olive/cream equipment, and a naturalistic JRPG identity. Hair color is contested between the dark/green-looking group reference and an earlier auburn/copper reference; neither is silently promoted. Maintain **Reson > Aepex > Ender > Ionia > Lyra** without claiming numeric character heights. The Five Lights and story are out of scope for this visual engineering slice.

Epic's UE 5.8 MetaHuman Creator supports a character asset and Python-accessible face landmark editing. It is a more suitable future human-face editing basis than repeatedly reshaping toy-like source primitives; **this experiment does not claim the new asset looks like Ender**.

Official sources:
- [Creating a MetaHuman Character](https://dev.epicgames.com/documentation/en-us/metahuman/creating-a-character)
- [Python Scripting for MetaHuman Creator](https://dev.epicgames.com/documentation/metahuman/python-scripting-for-metahuman-creator)
- [Getting Started / Optional MetaHuman Creator Core Data](https://dev.epicgames.com/documentation/en-us/metahuman/getting-started-with-metahuman-creator)
- [MetaHuman Creator From Custom Mesh limitations](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-from-custom-mesh-tool-in-unreal-engine)

## Verified native result (not inferred from Linux CI)

Authorized **neontic** Windows workstation, installed **Unreal 5.8.4** (native engine revision in receipt), fresh `C:\MH1\CastAllSandbox`. The isolated `CastAllSandbox.uproject` alone enables `MetaHumanCharacter`; original project and repository manifests remain unchanged. Python automation `Editor.Python.CastAllSandbox.test_ender_v5_metahuman_native` **Success, process exit code 0** using **NullRHI**, not a rendered screenshot or gameplay build. Strict script `probe_ender_v5_metahuman_native.py` guarded project name, disposable marker, enabled plugin and unmodified V2 review map SHA before doing anything. Then it created and saved a real **`MetaHumanCharacter` UObject asset**:

`/Game/ArtLookdev/Characters/EnderV5MetaHumanStudy/MHC_EnderV5_UnapprovedBase.MHC_EnderV5_UnapprovedBase`

The actual local binary package is `C:\MH1\CastAllSandbox\Content\ArtLookdev\Characters\EnderV5MetaHumanStudy\MHC_EnderV5_UnapprovedBase.uasset`; **757,405 bytes**, Unreal package signature `c1832a9e`, SHA-256 **`7d648da499e5756d845faeed221ac4584e51516d1274b766db41d908e1fb17bd`**. A genuine `MetaHumanCharacterEditorSubsystem` registered the candidate for editing, provided **79 editable face landmarks** (first example native XYZ `[-4.7842, 9.5674, 165.2554]`), then was deregistered. No face deltas, body shape parameters, skin textures, rig/assembly, import from V4, artist likeness decision, game asset replacement, live game build or native render occurred. Original reference review map SHA-256 unchanged: `025539f8717c6215a17dc8acff24ec7bd39b3d43129de4069a9418b3d8da3a2a`.

The independent verifier `verify_ender_v5_metahuman_probe.py` **exit 0** cross-checked the JSON receipt, real `.uasset` package bytes/hash/signature, original review-map SHA, exact sandbox .uproject plugin marker and original native Editor log's test Success + zero exit. The four focused engine-free negative-control tests **4/4 PASS**. They reject malformed approval claims, a forged log status, wrong asset paths, corrupted Unreal package and absent landmarks. **Engine-free CI checks evidence contracts only**; they do not stand in for the independently recorded real UE 5.8.4 automation.

Evidence committed to branch as sanitized text/JSON under `ReviewEvidence/2026-11-02/EnderV5MetaHuman/`. Do **not** commit or publish the raw MetaHuman UObject asset or engine core data. It remains isolated on the authorized workstation, and is currently only a *default MetaHuman base*, not an Ender representation.

## Native blockers / warnings — preserve distinction

- `LogMetaHumanCharacterEditor: MetaHuman Optional Content folder not found. MetaHuman Creator plugin initialized with limited features.`
- Texture synthesis data were absent; engine logged `skin editing will be disabled`. **Do not claim PBR authoring, skin texture baking or full MetaHuman preset/assembly capabilities are verified.**
- Native Editor warned `AssetCompile memory estimate is greater than available` (skeletal mesh compilation request); the actual script did successfully complete without a rig. Hardware has approximately 15.65 GB physical RAM and about 4.22 GB free at a later check. Memory headroom must be evaluated before heavier feature initialization. This warning is not itself a native test failure.
- No additional software installed and no content downloaded. **Only MetaHumanCharacter plugin was toggled inside the disposable clone.** Plugin dependencies were satisfied by the existing Unreal installation, but the optional Core Data package is absent.
- The V4 GLB is too schematic for reliable automated MetaHuman fitting: do not auto-conform it and claim approved identity, especially given Epic's documented limitations for stylized source meshes. Keep it only as separate historical source/visual baseline.

## Next reversible production-quality slice (not executed)

1. Register the creator-approved Ender 2D face references to an **artist-reviewed** explicit landmark/angle sheet; resolve style targets, hair conflict and intended likeness before changing MetaHuman face coordinates.
2. In a *new disposable clone*, use the already proven `MetaHumanCharacterEditorSubsystem` to move only selected, documented facial landmarks from a human-reviewed sculpt plan, preserving original MetaHuman base. Maintain unrigged face-edit state; no skin or rig promises.
3. Before high-quality skin or cinematic pipeline, arrange the **official MetaHuman Creator Core Data** via Unreal Engine installation options *only after explicit authorization*. Do not install by default; no paid assets or downloads were used.
4. Capture real matched native closeups after high-quality content and materials are actually available, separately verify render pixels and facial deformation, seek creator art signoff, then rig/assemble/integrate in a different milestone.
5. Never merge this review branch, promote art, change main/default .uproject plugin state, or replace the existing playable character without explicit authority.

**Outcome:** `METAHUMAN_NATIVE_AUTHORING_BASE=PASS`; `FACIAL_LANDMARK_API=79`; `OPTIONAL_CORE_DATA=MISSING`; `SKIN_AUTHORING=BLOCKED`; `ART_LIKENESS=NOT_REVIEWED`; `RIG/ASSEMBLY/RENDER/PLAYABLE=NOT_TESTED`; `CANON/PROMOTION=HOLD`.
