# First Wake coastal harbor environment V1 — 2026-11-04

**Authority:** ORIGINAL SOURCE CONSTRUCTION / NOT NATIVE-STAGED / NOT ART-APPROVED / NOT PLAYABLE-VERIFIED. Draft branch only. No merge, protected-main change, SaveGame edit, or Starbourne unlock.

## Purpose and dependencies
First environment-construction pass for the Unreal 5.8.4 vertical slice, **built on the actual 34-actor native asset assembly** from #752 and the physical RAM graphical-review guard from #756, rather than an unrelated diorama.

- Parent: /Game/TSTSS/Review/Scenes/FirstWake_AssetAssembly_20261104_REVIEW_V3
- Target: /Game/TSTSS/Review/Scenes/FirstWake_HarborEnvironment_20261104_REVIEW_V1
- Verified parent binary SHA-256: 54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5

The inherited scene has 24 Prelude actors (seven First Wake milestones and one PlayerStart) and 10 static ship/cast review actors, including noncanonical Aureate Wake proxy geometry and static Ender/Ionia. The new scenery must not alter those systems.

## Authoring snapshot
The reproducible Python source at unreal/Tools/build_first_wake_harbor_environment.py defines **47** no-collision scenery actors and eight original plain PBR material roles:
- Quay retaining wall, stone pier, boarding gangplank, offshore water plane;
- Customs building, Ionia's office frontage, harmonic-engineering workshop, drydock shed, canvas awning, and coastal signal tower;
- Seven sets of bollards, lamp posts and amber lanterns, plus six cargo stacks;
- Distant headlands and inland ridgelines, native SkyAtmosphere, ExponentialHeightFog and a horizon-oriented review camera.

Material roles: quay stone, harbor plaster, warm roof, patinated metal, canvas, coastal rock, sea teal and amber signal glass. The authoring script constructs actual native Unreal Material graphs **only when** an Editor stage is run. Engine-free source tests and manifests produce no saved Unreal materials or level.

All new review props are no-collision and visually outside the existing y=-400..+400 cm interaction corridor. Ocean visual is strictly **not buoyancy or physical sea contact**. This version has no finished masonry meshes, surface waves, foam, real weather, LOD, real collision/navmesh, gameplay ocean or approved canon architecture.

## Art direction and native sky risk
Highest priority remains believable scale, curvature, lighting, intentional framing, atmospheric depth and readable contrast. The departure should contrast warm stone/brass with cool teal sea and a real coastal horizon. Built-in primitive proxies are *not* cinematic finish art.

The prior SkySphere experimental rendering (#705) had black sky with blue ocean. This new script requests native SkyAtmosphere and links the existing single sun. It is a **source-level change of approach**, not proof the black-sky issue has been fixed; a genuine warmed-up native screenshot is mandatory.

Journey-inspired sand/snow (#753) are a **separate original-material review** and remain native-render HOLD. No proprietary artwork, code, or textures should be copied.

## Actual workstation work completed
- Created isolated worktree at C:\TSTSS_EnvironmentHarbor_20261104 from review P0 branch #756 at fc5f3c78f569ab783ce02f9f7751135e17cb1214.
- Copied *without overwrite* private ship/cast review assets and the exact V3 native parent map from the earlier isolated asset-assembly workspace. Parent-map digest matches the documented source.
- All copied native binaries remain untracked, private and unmerged. Do not add them to GitHub commits.
- Initial source-only verification: 13/13 tests PASS, Python compile PASS, validate-plan PASS.

## Execution and acceptance gates — NOT YET RUN
1. Preserve the user's current Unreal Editor. Refuse a competing Editor/Live Coding process. Require current clean tracked source; exact copied parent World SHA; no SaveGames; at least 5 GiB free physical RAM and 14 GiB free disk for isolated NullRHI map stage. For graphical D3D11/PIE review require at least **6.5 GiB physical free RAM**.
2. Run Python build script inside actual UE 5.8.4 Editor only with explicitly guarded resource/concurrency checks, creating the NEW destination map (never overwrite). Require saved map, native stage receipt, and original configs/map unchanged. Engine-free validation does not count.
3. Reload in a separate native Unreal process and independently confirm all 34 old actors, seven milestones, original PlayerStart, 47 no-collision scenery meshes, atmosphere, fog, camera, eight saved materials, and no Starbourne actor.
4. Capture real D3D11 fixed harbor hero + player-eye cameras. Inspect horizon percentage, black sky, sun direction, water/shore seam, scale, material clipping, Ender/Ionia visibility, ship-wing sight lines and frame timing. Add D3D12 only if resources allow.
5. Actual PIE WASD/mouse, E/J, F5/F9 traversal through seven stops and isolated save. No approval until creator side-by-side review.

## Remaining environments for the first slice
| Area | Status now | Next work |
| --- | --- | --- |
| Harbor / hiring / workshop | Source-authored harbor V1, native staging pending | Detailed architecture, polished PBR materials and native walk-through |
| Aureate Wake deck / ship surroundings | Existing noncanonical ship components and sky proposal | Crew-scale sightlines, dome/wing clearance, art acceptance |
| Flight / emergency descent | Sky/ocean backdrop proposed, physical ocean unproven | Clouds, depth, physical splashdown integration |
| Shoreline after Splashdown / Lyra | Not built in this pass | Original rocky coastline, sand, shallow water, interaction trigger |

**HOLD:** No new map saved in Unreal, no GPU image, material compilation, native readback, PIE, artistic sign-off or packaged build has been performed for this environment branch. Existing RAM measured ~4.96 GiB free with Unreal Editor active. Do not close user processes or bypass the resource gate.
