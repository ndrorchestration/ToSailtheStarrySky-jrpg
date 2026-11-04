# Aureate Wake — APPROVED visual reference (creator canon)

**CANONICAL NAME UPDATE — November 1, 2026:** The creator has renamed the four configurations **Skybourne, Seabourne, Submersible, and Starbourne**, respectively. The earlier labels *Skyborne*, *Seaborne*, and *Orbiter* in the historical image and engineering records are now legacy labels. See [the authoritative name and backward-compatibility contract](AUREATE_WAKE_CANONICAL_CONFIGURATION_NAMES_2026-11-01.md). This naming decision **does not replace the approved illustration, modify existing engine enum identifiers, or unlock Starbourne/Moon Bridge**.

**Decision:** Creator-approved reference for **all four ship configurations**, supplied directly in the TSTSS project conversation on **2026-11-01**. This is the visual source of truth for the Aureate Wake's design, not a screenshot of an implemented engine asset.

| Original art integrity | Value |
| --- | --- |
| Original filename | \`Aureate Wake_ Four Configurations.png\` |
| Dimensions | **1536 × 1024 px** |
| Original image SHA-256 | \`03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13\` |
| Original file size | **3,837,524 bytes** |
| Approval source | Direct creator instruction: "**This is the approved art for implementation**" |
| Binary custody | The original PNG was uploaded to the 2026-11-01 project conversation. **This text-only PR does not contain or purport to replace those image bytes**. Before future source/reference-gallery promotion, attach the original unchanged PNG and verify the SHA above. |
| Authority | **Art direction approved.** Geometry, engineering solutions, model scale, rigging, material behavior, imported assets and gameplay remain subject to independent validation. |

## Design invariants — match these, do not casually reinterpret

**One recognizable physical vessel across all forms**, not four different ships: the same long forward-pointing ivory/white central hull, dark navy/blue mechanical inserts, warm gold/brass filigree and structural frames, blue/cyan luminous resonant components, cockpit and cabin glazing, wing roots, engine region and consistent crew spaces. Silhouette reads as a fast, elegant, dragonfly-inspired science-fantasy airship rather than a box, generic jet or ordinary sailing ship.

### Persistent architecture

- **Hull:** long pointed, swept ivory-and-gold bow with flowing integrated body panels, high-detail blue-black propulsion/engine nacelles and visible mechanical articulation; the existing flat rectangular cube in native PR #655 screenshots is a **blockout to replace**.
- **Bridge:** forward-facing **panoramic geodesic glass dome**, blue-clear glazed triangular sections, elegant gold-rib framing and usable crew/captain stations. Preserve location and crew space across all four forms. Dark opaque or solid cube bridges **do not meet approval**.
- **Deck:** recognizable open observation / forward deck segment and believable entry/crew circulation. Maintain a continuous human-scale central hull, internal pressure protection and consistent cockpit placement.
- **Wings:** **exactly four principal dragonfly-inspired wings** in all forms, with gold filigree/vein lattice and translucent blue-violet-cyan iridescent panels. Fore and aft pairs mirror intelligently; wing joint/locking assemblies are clearly readable. Do not mistake numerous fine wing ribs, mechanical struts, or smaller fins for extra main wings.
- **Color/material language:** pearl/ivory enamel; gold/brass metallic edges and filigree; blue to violet luminous transparent metamaterial; dark midnight-navy framework; blue resonance engines. Avoid monochrome turquoise/pure graphite proxy bodies as final results. The prior simplified review wing, hull and support meshes remain **noncanonical approximations** even if structural tests pass.
- **Proportions:** long fine bow, compact yet legible forward dome, dorsal mechanical and glazed sections, four generously extended wings in Skyborne, integrated hydrofoil geometry in Seaborne. No absolute metre dimensions are canon from this art sheet; existing **7.98 m hull** and **280 cm wing** proxy dimensions are temporary implementation coordinates and need crew-scale review.
- **Presentation:** physically based attractive glass/metal materials, legible detail from top/front/side and matching 3/4 hero views, soft amber vs cyan lighting, recognizable silhouette in every environment. Story/engineering credibility takes priority over arbitrary glow.

### I. Skyborne — atmospheric flight (visual priority 1)

Four articulated dragonfly wings **deployed visibly** for atmospheric navigation, harmonic levitation and docking. Gold-veined translucent wings should read from above and in the side silhouette. Pointed prow and glass bridge face forward. The approved art shows aerial sky/city/coastal travel; flight physics and levitation systems must be demonstrated independently, not inferred from the art.

### II. Seaborne — open-ocean and shoreline (priority 2)

Same hull, bridge and wings, with wings stabilized / folded to a marine-ready geometry while retaining identity. **Deployable hydrofoils** extend below the hull for credible water-gliding contact; visible foam/spray/wake are cinematic target only until native waterline and flotation simulation is measured. The ship must support a believable First Wake emergency sea landing rather than silently triggering narrative progression on a visual effect.

### III. Submersible — underwater exploration (priority 3)

Same bow/bridge/cabin assembly, **wings folded and rotated but still partly exposed and visibly identifiable**. Underwater lights and protected machinery, sealed bridge and pressure-safe crew space (to be engineered/tested), deep blue bioluminescent mood. This form is later-game; do not imply entry into it during First Wake.

### IV. Orbiter — celestial/lunar traversal (priority 4; STORY GATE)

A still-recognizable vessel, forward-facing bridge, **four equal-size radial translucent blue/violet/gold solar/light sails**, arranged **top, bottom, port, starboard** like a cardinal cross. Their iridescence/photovoltaic material language visibly descends from the four original dragonfly wings. Orbiter stays locked behind its existing narrative and clearance gates; **this art approval does not authorize gameplay unlocking it**, nor does it prove transition collision safety or Moon Bridge eligibility.

## Mechanisms explicitly illustrated (review before modifying rig)

1. Wing rotation about harmonic/structural pivot joints.
2. Articulation and fold changing deployment angle and available wing surface.
3. Positive environmental locking / stabilizing into an approved configuration.
4. A complete deployed form appropriate to its environment.
5. Hydrofoil deployment (Seaborne) and visible tuck/retained membrane (Submersible).
6. A single navigable, forward-facing crew bridge across all transformations.

## Acceptance matrix (not all checked)

| Independent gate | Current evidence at approval |
| --- | --- |
| Creator has selected authoritative visual reference | **APPROVED** — source image + explicit instruction |
| Previous source-side four-form actor architecture | Implemented as preview only; native PR #655 rendered Skyborne |
| Four visible primary wings, review glTF import | **Native Skyborne review passed** with approximate noncanonical wing art |
| Authored ivory/gold pointed hull matching reference | **NOT IMPLEMENTED / NOT APPROVED** (PR #664 noncanonical body candidate is dark graphite and simplified) |
| Panoramic habitable geodesic bridge matching reference | **NOT IMPLEMENTED / NOT APPROVED** (PR #664 dome is isolated source-side lookdev) |
| A coherent art-fidelity ship in **four** forms | **NOT VERIFIED** |
| Skyborne flight + Seaborne water transition | **Physics & visual acceptance NOT VERIFIED** |
| Seaborne functional hydrofoil and wake | **NOT VERIFIED** |
| Submersible sealing, partial wing visibility, pressure | **NOT VERIFIED** |
| Orbiter four equal radial sails | Preview concept/code only; **LOCKED**, no artistic/physics acceptance |
| Native Windows 5.8.x editor import of updated approved-fidelity art | **NOT VERIFIED** |
| Four-form matching-camera/orthographic art review | **NOT VERIFIED** (PR #655 images are simplified Skyborne only) |

## Implementation ordering / fidelity checklist

1. **Preserve this approved image as an immutable original.** Match by SHA, do not substitute generated concept art or the gray native capture for the approved reference.
2. **Establish shared geometry scale:** adult height and habitable bridge/deck footprints, hinge-to-hull clearance, original art proportions. Existing proxy centimetres are **not** final scale canon.
3. **Replace hull blockout:** ivory/gold swept tapered bow, rich layered blue-black engine fairings, wing-root structures, usable open deck; render the first 3/4 angle at the same approved art orientation.
4. **Replace bridge blockout:** forward geodesic blue-clear glazed canopy with readable interior, rib lattice and deck/bridge continuity.
5. **Authored wing detail:** gold veins/transparent iridescence, articulation and matching root fittings; ensure four and exactly four principal wings throughout, symmetrical where appropriate.
6. **Form-specific rigs:** full Skyborne deploy, Seaborne hinge+hydrofoil, visible Submersible tuck, four identical radial Orbiter sail cards without breaking persistent ship geometry.
7. **Native full-fidelity review:** import into isolated Unreal review paths, verify X-forward/Z-up and metre conversion, in-engine screen captures top/front/side/3/4 at consistent camera scale and actual materials, inspect frames for alignment with approved art.
8. **Independent simulation/QA:** swept transition clearance vs final hull/bridge, hydrodynamics/sea contact, pressure, crew circulation, performance, accessibility, and all existing progression locks. Never use a screenshot as evidence of physics.

### Change-control rule

This decision **supersedes provisional style in draft PR #664** wherever that provisional faceted graphite hull or isolated glass shell differs from the approved sheet. Keep that source-side candidate as an optional procedural learning asset if useful, but **do not promote it to final art**. The approved visual source must be evaluated independently of engineering correctness. No merges, releases, or automatic Orbiter access are authorized by the art approval.

## November 3, 2026 — Starbourne private development clarification and V4 material intake

The approved art remains the **visual source**, not automatic authorization for procedural V4 game meshes. Creator authorization now explicitly allows **internal Starbourne visual/mechanical work** (private four equal radial sails, experimental materials, engineering and Unreal rendering). The **player/story reveal, SaveGame progression and lunar route remain gate-locked**. Do not interpret the older word Orbiter/locked as a ban on private developer work, or as a player unlock.

Draft [Aureate Cinematic V4 #732](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/732) imported five review GLBs as real UE 5.8.4 StaticMeshes with four material slots each. Its separate assembled-level attempt failed before actor creation and produced **no approved cinematic image**. See [native evidence](AUREATE_CINEMATIC_V4_NATIVE_IMPORT_EVIDENCE_2026_11_03.md) and [dependency plan](AUREATE_V4_DEPENDENCIES_AND_ACCELERATION_2026_11_03.md). Final proportions, glass, bridge+quarters pivot, water/shaders, continuous clearance and game art remain held.

## November 3 — Native Skybourne V4 assembly acceptance boundary

The new [Skybourne native scene evidence](AUREATE_V4_NATIVE_SKYBOURNE_SCENE_EVIDENCE_2026_11_03.md) establishes one actually saved Unreal 5.8.4 *review* map with shared-hull/dome/quarters blockouts, four wing identities and imported V4 lace. It does **not** establish a faithful rendered version of this approved source art: the D3D11 PNG is pending and the review proxy bridge is not the final geodesic glass assembly. Maintain the original approved image authority. Starbourne private development remains authorized but the player story gate remains locked.

## November 3 — Four Unreal V4 review layouts are not approved final models

[Four-mode Unreal native layout evidence](AUREATE_V4_ALL_FOUR_NATIVE_REVIEW_MAPS_2026_11_03.md) now records four real saved UE5.8.4 scene maps. These remain provisional hull/dome/quarters/wings/foils/light/sail assemblies, not faithful D3D11 renders of the original approved art. The approved PNG stays unchanged and continues to control aesthetic choices and geometric proportions. No physical proof of central rotating quarters or playable Starbourne is implied.

## November 3 — Central habitation coupling is feasible, not final art

A separate native Unreal 5.8.4 review test has now attached the bridge and quarters proxies to one common pivot, rotated them temporarily through 17.5 degrees, verified rigid distance and restored the pose. The original approved visual proportions, actual geodesic construction, crew gravity, dynamic clearance and final art remain unverified; this mechanical proof does not supersede the approved reference artwork. The V4 GPU Skybourne image is still not available. See AUREATE_V4_NATIVE_MAP_AUDIT_AND_HABITATION_PIVOT_2026_11_03.md. Starbourne stays developer-only until story authorization.
