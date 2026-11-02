# Aureate Wake — Skybourne atmosphere + ocean lookdev review (November 1, 2026)

**Status: RESEARCH / VISUAL HOLD.** Reversible noncanonical UE 5.8.4 scene development, not playable environment, approved art, simulated water, Starbourne authority, or release.

## Why this slice

The [native Aureate Wake image review](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/692) and [UV-repaired wing screenshot](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/700) proved real Unreal 5.8.4 preview rendering, but the all-black environment prevented useful atmosphere/ocean material judgment. Other parallel drafts already cover hydrofoils, wing-root fairings and the coupled rotating bridge/living quarters; this avoids modifying them.

## Source and test boundary

- `unreal/Tools/author_aureate_sky_sea_review.py`: deterministic standard-library generator for a 512×256 equirectangular blue-to-warm-horizon sky and a 512×512 blue-teal wave-textured ocean. A SHA-256 manifest declares provenance and exactly one noncanonical scene and asset folder. Files refuse a nonempty output directory.
- `unreal/Tests/test_author_aureate_sky_sea_review.py`: **5/5 tests passed on the authorized Windows source checkout**, verifying exact PNG dimensions, deterministic repeated bytes, shader-relevant color variation, status, and refuse-to-overwrite.
- `unreal/Tools/stage_aureate_sky_sea_native_review.py`: explicit opt-in **Unreal Editor Python only**, with external source/receipt environment variables. Verifies manifest SHA and noncanonical Orbiter lock, refuses existing assets/map, imports only to `/Game/TSTSS/Review/Environment/SkySeaV1`, duplicates historical `/Game/TSTSS/Review/Scenes/AureateWakeSkyborne_WingUVRepairV3` to a new private `AureateWakeSkyborne_SkySeaReviewV1` map. Creates a two-sided emissive sky material, an ocean material with texture and specified roughness, a collision-free sphere and plane at z=-165cm. Existing ship actor remains one instance with four wings and Starbourne/Orbiter requests denied.
- Native UE 5.8.4 `-run=pythonscript` on the local isolated #700 review checkout **completed with exit 0 and 0 reported errors/warnings**; exact JSON receipt confirmed textures, material actors, saved new map, wing count 4, and denied Orbiter request. **Only .uasset review files locally**, not in production or committed to this source PR.

## Visual QA — do not mistake load for quality

First genuine offscreen 1280×720 D3D12 screenshot of the new map showed **the ocean plane as gray and the background black**, not the intended blue/teal color. This **FAILS visual acceptance** despite successful asset import, material graph connections and scene save. Native read-only Editor inspection verified the ocean material is connected to Base Color/Roughness and the sky is two-sided/unlit with a texture driving Emissive; material graph existence does *not* prove finished D3D12 shading. This may involve shader-readiness at early screenshot frame, material rendering or sky-geometry issues; precise root cause **not established**. Do not promote screenshots as proof of an effective atmosphere upgrade.

**Next verification:** reproduce screenshot with a delayed shader-ready capture (rather than the immediate frame-5 HighResShot), inspect actual material compilation and game runtime visibility, confirm blue sky/sea in two independent genuine D3D12 frames, and compare a consistent camera baseline. If still gray/black, diagnose and repair material pipeline in a new isolated candidate. No gameplay ocean, buoyancy, weather, approval, Starbourne unlock, or public release.

## Repro commands (Windows; paths are examples)

```powershell
python unreal/Tools/author_aureate_sky_sea_review.py --output-dir C:\review\AureateSkySeaV1
python -m unittest discover -s unreal/Tests -p test_author_aureate_sky_sea_review.py -v
$env:TSTSS_AUREATE_SKY_SEA_SOURCE_DIR = "C:\review\AureateSkySeaV1"
$env:TSTSS_AUREATE_SKY_SEA_RECEIPT = "C:\review\AureateSkySeaReceipt.json"
# Run the staging script only from a native, isolated Unreal Editor Python session.
```

**Scope authority:** creator-approved original Aureate Wake art is unchanged; official form names are Skybourne, Seabourne, Submersible, Starbourne. This source slice preserves historical serialized enum identifiers and all safe/unsafe form gates. No merges, releases or art promotion.
