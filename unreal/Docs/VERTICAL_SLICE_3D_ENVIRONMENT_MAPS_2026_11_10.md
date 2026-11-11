# First Wake — 3D environment map staging (Unreal 5.8)

**Status:** review-only environmental implementation; no art, gameplay, map or release approval.
**Owner:** P0 Prelude → Splashdown issue #754.
**Source base:** #788 at d9548f449e3dd5fd50b19bb04b7bc93ad599b58a.
**Worktree:** C:\TSTSS_VSlice_Environments_20261110 (isolated).
**Builder:** unreal/Tools/build_vertical_slice_environment_maps.py.

## Ordered environments

| ID | Level | Visual and gameplay purpose | Boundary |
|---|---|---|---|
| VS01 | DenithHarbor | Harbor quay, buildings, flyer/Ionia/boarding | Preserves real seven-stop Prelude review map |
| VS02 | AureateInteriors | Front deck, bridge dome silhouette, engine and inspections | Ship geometry is NOT approved art |
| VS03 | FirstWakeSky | Cloud banks, atmosphere, auroral route cue | No actual flight pawn |
| VS04 | SplashdownSea | Ocean and native physical-water-adapter lab | Water contact unverified in this new map |
| VS05 | DenithFuelShanty | Tide-worn pier, fuel stop and nearby settlement | No inventory grant |
| VS06 | SplashdownShore | Sand coast, basalt cliffs, tidal rocks and canopy | Lyra introduction staging, no early recruitment |

All maps are new and distinct under /Game/TSTSS/Review/VerticalSlice, in centimeter-scale Unreal geometry. PBR materials, cinematic camera compositions, sunlight, skylight and atmospheric actors form a visual blockout, not an approved cinematic render. PlayerStart/floor collision exists only where on-foot travel is appropriate.

## Runtime connection dependencies — NOT implemented

1. VS01 to VS02: Ionia hired and ship boarded.
2. VS02 to VS03: three engineering checks signed off and launch authorized.
3. VS03 to VS04: physical sky-to-sea transition and real hull contact.
4. VS04 to VS05: directly observed stable flotation and progression.
5. VS05 to VS06: post-contact shore exploration; Lyra only after canonical gate.

Do not add map opening shortcuts which bypass story gates. No Starbourne or cross-session save migration work is authorized by this environment branch.

## Source and native verification

Source plan: py -3 unreal/Tools/build_vertical_slice_environment_maps.py --plan

Unit tests: py -3 -m unittest discover -s unreal/Tools -p test_vertical_slice_environment_maps.py -v

Native editor commandlet requires an exact HEAD, clean sandbox, correct Unreal module and free-memory/disk resource admission. Example invocation from worktree root:

    $env:TSTSS_VSLICE_EXPECTED_HEAD = (git rev-parse HEAD)
    & 'C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe' '.\unreal\ToSailTheStarrySky.uproject' -run=pythonscript -script='.\unreal\Tools\build_vertical_slice_environment_maps.py --build' -unattended -nop4 -nullrhi -nosplash -log

The builder refuses prior target packages, dirty source, out-of-sandbox paths, unapproved HEAD, or an absent immutable Prelude map. Do not retry after partial native output without inspecting and preserving its artifacts.

## Production-readiness checklist

- [ ] Six native map packages saved, SHA-256 inventoried and reopened.
- [ ] Native maps' material references, lights, camera and collision checked.
- [ ] Original Prelude/map, config and existing SaveGames unchanged.
- [ ] Matching-head UE 5.8.4 native build, required native tests and no source regression.
- [ ] Real player-controlled progression between all six areas and physical sea landing.
- [ ] Consistent progression/save state and no early party recruitment.
- [ ] Authentic GPU screenshots/video, lighting/curvature/performance/readability QA.
- [ ] Approved ship and cast 3D meshes integrated with the review geometry safely.
- [ ] Creator aesthetic acceptance and uncoached player acceptance.

No merge, production art promotion, release, globe implementation or Starbourne change is implied.
