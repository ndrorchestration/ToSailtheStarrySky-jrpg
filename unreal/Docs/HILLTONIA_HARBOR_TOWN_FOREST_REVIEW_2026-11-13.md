# Hilltonia — Harbor, Town and Deciduous Woodland (Unreal review v0.1)

**Authority:** New creator-selected place name *Hilltonia*, adjoining First Wake Harbor. This is an additive **geographic and gameplay review proposal**, not a promotion of final world geography, NPCs, mission content or AAA-quality visuals. Reference branch: \`review/ue58-hilltonia-harbor-forest-20261113\`.

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

## Required acceptance and design gaps

- Engine-free spatial-contract checks and native 5.8.4 Win64 compilation, followed by exact-SHA native automation.
- Native **WASD** traversal from existing pier across the join into Hilltonia, collision and fall-recovery checks, forest junction, and **return to harbor** without bypassing the seven plot milestones.
- Native 1280×720 screenshots from **dock looking inland**, town street, village square, and woodland approach. Assess house scale, sign legibility, road direction, sky exposure, forest silhouette density, culling, performance and continuity.
- Keep town spatial approval independent from the existing **VS02 Aureate interiors camera/lighting failure**.
- Future actual Landscape heightfields, foliage asset selection, species palette, seasonal variants, named NPCs, harbor audio crossfade, navmesh, clock/weather coupling, LOD/HISM and biome streaming require separate implementation/evidence.
- Do not claim Hilltonia is a production-approved open-world city or that the full First Wake flight-to-shoreline vertical slice is complete.

**Current state at creation:** source-authored **review candidate**; native run, physics/collision experience and visual creator approval remain unknown until evidenced.
