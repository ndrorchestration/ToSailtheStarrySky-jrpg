# First Wake surface textures / atmosphere and cinematic-lighting handoff

**Authority:** Review-only candidate. No canonical material or scene has been approved. No production map, story chronology, SaveGame, collision, ocean physics, or Starbourne permissions are changed.

## Scope and coverage

Source branch: `feat/ue58-firstwake-surface-textures-20261111` stacked on draft multipath PR #799 (`de0a6a185fae0c5c17300762d288fa753f39a203`).

The six native `/Game/TSTSS/Review/VerticalSlice/VS01…VS06` maps already exist. Their first-generation review surfaces were ten untextured PBR flat-color placeholder materials. This pass creates 30 original, deterministic 512×512 texture sources under `unreal/DataSource/Textures/FirstWakeSurfaceV1/`: for each of sand, stone, dark stone, timber, brass, ocean, aether, cloud, warm and green, there is a BaseColor sRGB, tangent-space Normal linear, and packed ORM linear map (red=ambient occlusion, green=roughness, blue=metallic). Tiling scales and per-family variation are explicit. All ten names are checked against the existing six-map authoring script's material inventory.

Generated patterns are **procedural review artwork**, not photogrammetry or approved production textures; do not claim cinematic/AAA-grade visuals from file generation alone. In particular, water, sky, translucent glass and volumetric cloud treatment require distinct dedicated shaders and native lookdev, not merely these opaque blockout texture maps.

## Isolated native staging

`unreal/Tools/first_wake_surface_textures.py --plan` is portable and read-only.
`--generate` deterministically emits the sources and SHA-256 receipt; it refuses to overwrite divergent material sources.
`--stage-native` is available **only** inside Unreal Python on the exact clean `C:\TSTSS_SurfacePass_20261111` worktree, only when `TSTSS_SURFACE_STAGE=1` and `TSTSS_SURFACE_EXPECTED_HEAD=<40-hex SHA>`. It refuses existing destinations, missing source maps, wrong checkout, missing/modified texture files and dirty maps/content.

The native stage imports 30 Texture2D assets with correct color-space/compression settings, creates ten connected PBR materials, duplicates all six existing maps into `/Game/TSTSS/Review/SurfacePassV1/`, remaps only actors with the review prefix and matching original material names, saves each duplicate, and writes an untracked native receipt with assignment counts. Original maps are not edited; failure is fail-closed, and partial outputs are never silently overwritten. No existing material or map is promoted.

## Lighting and weather relationship

The material staging is intentionally *additive* to the already implemented source work:
- [#796](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/796): 11 curated cinematic lighting looks, currently source-tested, not proven as GPU captures.
- [#798](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/798): seven native atmosphere/weather presets, transition control, sun/moon, sky, volumetric fog, aurora and camera-local precipitation, but not yet native/PIE-accepted on the integrated head.
- [#799](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/799): convergence source branch and 35-native-test fail-closed gate.

Do **not** add a second full sky/atmosphere director on top of the existing map's standalone lights; duplication would corrupt illumination and diagnostics. The next integration step is native source-locked build and validation of one unified atmosphere ownership path, then staged scene-specific lighting/look/weather combinations in duplicate review maps. Seven weather options are lookdev alternatives: snow/blizzard are optional biome review, not forced into the Denith prelude. The First Wake sea-contact and >=2.0-second observed pretransition flotation gate remain independent from spray/foam materials.

## Verification and visual acceptance

Source tests: `py -m unittest discover -s unreal/Tools -p test_first_wake_surface_textures.py -v`.
Full repository Python source tests must be run before promotion. Validate 30 source digests, all ten families, six map path separations, refusal cases, stage exact-head validation.

Native checks to perform **before any accepted visual claim**:
1. Win64 UE5.8.4 C++ Editor build and exact-commit required 35 real automation identities, preserving existing fail-closed gating.
2. Load the six *duplicated* maps; verify 30 imported textures, 10 material graphs and assignment counts; compare original map package SHA-256 before/after.
3. Render Lit GPU captures of harbor day/dusk/night, engineering, first ascent, storm descent, sea contact and shore aftermath. Inspect color texture detail, specular rolloff, tangent normals, contact shadows, exposure/contrast, Lumen waterline, volumetric fog, screen readability and camera-facing characters.
4. Check weather transitions under frame-time load, rain/snow visual legibility, accessibility low-motion settings and wet-surface response. Measure frame time and streaming memory on Neontic.
5. Capture player-input PIE and creator side-by-side review. Keep all PRs draft until native proof and art approval.

Status: `SOURCE_TEXTURES_CREATED` after generation; native assets, GPU screenshots, PIE, performance, final look and canonical approval remain **NOT_VERIFIED** until measured on this exact branch.
