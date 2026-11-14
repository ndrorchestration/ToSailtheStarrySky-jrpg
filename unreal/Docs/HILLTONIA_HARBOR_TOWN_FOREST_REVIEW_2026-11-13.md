# Hilltonia — Harbor, Town and Deciduous Woodland (Unreal review v0.1)

**Authority:** New creator-selected place name *Hilltonia*, adjoining First Wake Harbor. This is an additive **geographic and gameplay review proposal**, not a promotion of final world geography, NPCs, mission content or AAA-quality visuals. Reference branch: `review/ue58-hilltonia-harbor-forest-20261113`.

## Geography and scale

Hilltonia is a **small northern-temperate coastal town**, set in a working **mid-northern-hemisphere latitude band analogous to approximately 40–50° N**. Its exact latitude, planetary longitude, calendar seasons and relation to global navigation lanes are **not yet canonically fixed**. Keep this distinct from Earth coordinates. The coastline meets a sheltered harbor; a deciduous forest lies on the landward, gently rising slopes. The Aureate Wake's First Wake starts at the waterfront, not at an isolated mystery fuel depot.

**Local-axis draft:** First Wake V5 dock runs approximately X=-3750 to +2550 cm, Y=-700 to +700 cm (top Z=0); +Y is seaward, -Y is landward. Hilltonia's main street travels west from the landward end of the harbor dock toward X~-9000 cm. A short northern woodland road branches toward Y~-3380 cm. The initial connector remains level at Z=0 for reliable gameplay. Farther green ridges are scene-only silhouettes pending actual landscape/topography work.

## Town character and story utility

Hilltonia is an ordinary, lived-in small town with approximately six visible house proxies, a larger community hall/inn-like building, a market green and a harbor-to-town approach road. Stone footings, timber frames, steep rain-shedding roofs, small workshops, stores and mixed orchard/woodland edges communicate north-temperate settlement life. A coherent local cast, town economy, occupations, lore and quest chain still require creator approval; a generic supply and repair economy is **not evidence of the rare harmonic components** Ender will eventually seek.

The adjoining forest should eventually support **oak, maple, beech and birch** where biome and soil conditions are suitable, with seasonal leaf-color changes, mist, birds, undergrowth, wind and leaf litter. The initial green spherical canopies are **review placeholders**, not species-approved trees. Winter snow and shoulder-season rain are possible future weather modes, not verified in this build.

## Connection / gameplay topology

1. **Harbor pier / seven-milestone Prelude:** unchanged original native map and interactions; source markers remain on Y=0 from X=-2200 to +1175 cm.
2. **Town threshold:** westward road begins at X=-3650 cm and overlaps the existing X=-3750 cm dock-floor edge. It is approximately 7.8 m wide, with ten 6.2 m overlapping collision sections. This is a genuine additional walkable route, not a menu teleport or quest shortcut.
3. **Hilltonia street and square:** westward to X=-9050 cm, flanked by six timber house proxies and a larger hall. No buildings are enterable, and NPCs are not yet integrated.
4. **Deciduous forest road:** an approximately 3.6 m-wide lane branches at X=-7350 cm and continues toward negative Y; tree trunks leave a clearing around the path. Its far endpoint is an unfinished wooded edge, not a quest zone or authored world transition.
5. **Beyond the forest:** hills and deciduous canopy silhouettes hint at the adjoining biome. No usable cross-map road, adjacent world-cell streaming or navmesh is established in v0.1.

**Terrain correction from first live render:** The initial native screenshot showed houses appearing suspended above the original ocean plane. The revised candidate adds two contiguous, WorldStatic prototype land/soil shelves under the village, both at Z=-10 cm above the old water plane and below the road top. These mask water under the houses, preserve a seaward shore edge, support the woodland junction, and remain review-only blockout terrain rather than a true Unreal Landscape. Recheck by GPU screenshot and physical walking before visual or traversal approval.

**Physics/authority:** The existing dock remains the source of seven ordered E interactions. The new town road/woodland lane and exterior house/trunk collision are tagged WorldStatic; remaining architecture, ridges and leaf crowns are decorative. The original docking, ship-form, water-observer, flotation, save and Starbourne gates are not changed. Town extension is spawned **only at runtime** in the exact standalone Unreal V5 review package, using native material assets already in the project; no .umap or .uasset is saved or overwritten.

## Evidence ledger — November 13, 2026

- **Native engine evidence for terrain+town commit `37c5335d`:** Unreal 5.8.4 Win64 Editor compiled, and 38/38 real native automation tests passed, with clean exact-head receipt retained on Neontic. The three native screenshots showing town street, ground and forest-edge proxies are **review only**, not creator-approved.
- **Source-only follow-up `2b8cb26c`:** new `test_hilltonia_route_geometry.py` computes five-point 35-cm-footprint support every 20 cm along the planned harbor → village street → forest approach → harbor return, approximately 185 m and 929 sampled points. It also rejects missing main-road segments, missing forest segments, obstructing props, missing soil, wrong ground elevation, and weakened review-map authority. This is **planar source-geometry evidence only**, not a real Unreal walking/physics pass.
- **Current exact-head acceptance:** new commits after the native receipt require their own source/CI verification; previous native results cannot be misrepresented as exact-head native verification of a later source or documentation commit. Neontic was offline during the source-only follow-up.
- **Unresolved runtime coverage:** actual pawn location and collision traces at the dock/road seam, town turnaround, forest turnoff and return; marker/quest noninterference; screenshot matching and terrain grading; the separate VS02 interior camera/lighting issue.

## Read-only live traversal telemetry — November 13, 2026

**Source-only addition pending exact-head native recompilation:** the V5 standalone review pawn now emits bounded `TSTSS_HILLTONIA_ROUTE_WAYPOINT` events on entering named checkpoints and `TSTSS_HILLTONIA_ROUTE_SAMPLE` heartbeats every two seconds while in the Hilltonia landward region. Each logged value comes from the real pawn's `GetActorLocation()`, `UCharacterMovementComponent::IsMovingOnGround()` and pre-existing five-point downward `HasSupportedReviewFooting()` world-static line traces. The telemetry does **not** grant any First Wake beat, modify movement or save data, change levels, or run in shipping. The final waypoint order is harbor seam → town street → square → **far-west town end** → square → woodland approach → forest edge → woodland approach → square → town street → harbor seam.

In a **new isolated review session**, first admit exact-head UE 5.8.4 Win64 build + required native automation with `Verify-Unreal.ps1` and its hash-bound receipt. Confirm the game starts in V5 Prelude, then physically walk the route in both directions. Evaluate a copied runtime log with:

```powershell
python unreal/Tools/check_hilltonia_runtime_route.py --log unreal/Saved/Logs/ToSailTheStarrySky.log
```

The evaluator requires correct checkpoint chronology, at least eight live location heartbeats, grounded and supported footprint at every logged sample, a plausible movement speed, at least 15,000 cm measured traversal, a minimum duration and no fall-return event. It rejects unsupported, out-of-order, insufficient or teleport-like records. **Even a positive report is only `REVIEW_ROUTE_LOG_CONSISTENT_NOT_NATIVE_ATTESTATION`**, never creator/cinematic approval or a substitute for an independently verified exact-SHA native receipt. Match in-game camera screenshots at the dock seam, town west end, forest edge and return; inspect the genuine quay-to-ground visual seam and collision.

**GitHub source regression at instrumentation commit `b196070a1279fc0084a19e23814a263c4e508db6`:** 662 Python tests completed successfully under the hosted Linux preflight; all three CI workflows passed. Neontic was **offline** during this source-only implementation, so no UE C++ compile, actual native route log, screenshots or playthrough evidence exists yet for that commit. Do not propagate prior native 38/38 evidence from `37c5335d` to the new exact HEAD.

## Player wayfinding — November 14, 2026 (source-only)

Four fixed, noncolliding **review signboards** now identify the Hilltonia entrance, the deciduous woodland turnoff, the forest-to-town return, and the western town-to-harbor return. They are world-space text proxies with the current review palette, not final carved signage or a HUD quest system. Placement on the verge is checked by `test_hilltonia_wayfinding.py` using the actual source coordinates and a 35 cm pawn-footprint clearance; they cannot advance narrative milestones or block travel. Confirm actual reading direction, legibility, scale and environmental framing against native Unreal captures before accepting them.

The wooded route remains a review-only spatial extension. No NPC interactions, forest zone transition, navmesh or canonical planet coordinates are established by these markers, and they must not substitute for testing physical walking to Hilltonia and back.

## Required acceptance and design gaps

- Engine-free spatial-contract checks and native 5.8.4 Win64 compilation, followed by exact-SHA native automation.
- Native **WASD** traversal from existing pier across the join into Hilltonia, collision and fall-recovery checks, forest junction, and **return to harbor** without bypassing the seven plot milestones.
- Native 1280×720 screenshots from **dock looking inland**, town street, village square, and woodland approach. Assess house scale, sign legibility, road direction, sky exposure, forest silhouette density, culling, performance and continuity.
- Keep town spatial approval independent from the existing **VS02 Aureate interiors camera/lighting failure**.
- Future actual Landscape heightfields, foliage asset selection, species palette, seasonal variants, named NPCs, harbor audio crossfade, navmesh, clock/weather coupling, LOD/HISM and biome streaming require separate implementation/evidence.
- Do not claim Hilltonia is a production-approved open-world city or that the full First Wake flight-to-shoreline vertical slice is complete.

**Status:** draft #829 is source-authored and has a verified earlier Unreal native build/test receipt. The full harbor-to-town-to-forest route remains a **source-geometry pass only** pending physical Unreal gameplay and visual approval.
