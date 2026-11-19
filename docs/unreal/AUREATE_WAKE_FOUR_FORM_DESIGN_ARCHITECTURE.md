# Aureate Wake — Four-Form Design Architecture (Unreal 5.8)

**Status:** DESIGN SPECIFICATION / PROPOSED ENGINEERING; CREATOR VISUAL ACCEPTANCE PENDING. Do not reinterpret speculative mechanisms as established canon.

## Core identity
A single continuous vessel with stable keel, inhabited central fuselage, recognizable elegant bow, geodesic glass bridge, forward open deck, and gold/brass + luminous resonance architecture. Maintain comparable spatial layout and genuine crew access in all forms. The ship responds evocatively to crew synergy; avoid reducing it to a generic transforming spacecraft.

## Four modes (all canonical as traversal capabilities)
| Mode | Configuration design direction | Engineering questions to prove |
| --- | --- | --- |
| 01 SKYBORNE | Wide wing membrane span, vertical lift glow, open deck observation, active aerial stabilization | Wing articulation, propulsion, drag, docking, weather, breathing conditions |
| 02 SEABORNE | Exposed seaworthy hull, stabilizing folded or elevated wing elements, protected propulsion, recognizable deck | Displacement/buoyancy, center of gravity, splashdown loads, watertight below-deck doors |
| 03 SUBMERSIBLE | Pressure-safe bridge envelope, flush/stowed wing mechanism, protected intakes, underwater beacons | Pressure hull versus decorative shell, geodesic glazing rating, life support, ballast, sealing routes |
| 04 MOON BRIDGE | Hidden celestial transformation; existing signature architecture reconfigures with auroral/resonant field structures | Full-moon + auroral approach + rare alignment activation, sustained pressure micro-environment, ascent/descent, lunar landing |

Moon Bridge is a **hidden traversal mode**, not default combat magic or an ordinary selectable flight form. Preserve mystery. Avoid assigning fixed wing positions, hull dimensions, mechanisms, engine fuel solutions or exact Moon Bridge appearance without creator approval.

## Transformation continuity rules
1. Maintain one persistent structural skeleton and coordinate frame; component transforms are derived from a shared rig and stable hardpoint IDs.
2. No teleporting internal rooms or unexplained change in walkable topology. Seal and test relevant portals as environment changes.
3. Use staged transitions: warning / mechanism unlock / articulation / seal or buoyancy check / propulsion switch / control handoff / new-mode stable.
4. Record independent safety gates. Sky↔Sea needs flotation confirmation. Sea↔Submersible needs pressure-seal and life-support confirmation. Sky↔Moon Bridge requires celestial clue and location state.
5. Interrupted transforms must fail to a documented recoverable state where physically plausible; no automatic scene jump to a certified completed configuration.
6. Use form-specific material parameter collections, lighting, audio and camera beats, but preserve ship identity and recognizable silhouettes.

## Unreal architecture proposal (not yet implemented)
- `AAureateWakeVessel`: stable actor, structural component hierarchy, bridge and interior attachment points.
- `EAureateWakeMode`: Skyborne, Seaborne, Submersible, MoonBridge; separate `Transitioning` state.
- `UAureateWakeTransformationComponent`: time-parameterized rig state and guard checks; transactional mode entry.
- `DA_AureateWakeModes`: authored per-form constraints/animation/audio/material references (Data Assets).
- Optional `Niagara` ambience: lift glow, spray, caustics, auroral resonance, with independent visual gates.
- Three review cameras: side orthographic silhouette, 3/4 hero shot and bridge/interior continuity.

## Art direction / acceptance deliverables
- Orthographic 4-form side/top/front sheets at the **same scale** and reference origin.
- Four cinematic 3/4 hero renders of the same asset family (not four unrelated ships).
- Annotated moving-part exploded diagram and crew-access map.
- Per-transition storyboard and Unreal native preview captures.
- Quantified silhouette landmark consistency, no self-intersections, no clipping deck/bridge, explicit sealing state.
- Creator visually approves each form *and* transformation separately.

## Canon and project boundaries
First Wake actual opening uses Skyborne and Seaborne; its sea landing must remain meaningful. Submersible and Moon Bridge are later progression. Do not mark any generated visual as canonical without creator approval. Current Unreal foundation is draft PR #608; SpriteCook starter material remains concept-only in draft PR #609. No claim of native Unreal model, animation or validated four-form rig is made here.

## Creator-confirmed fourth-form lock — October 30, 2026
The Moon Bridge form is **satellite-like**, with the ship's existing wings rotating/reconfiguring into a **radial solar-sail arrangement** around the recognizable central hull and geodesic bridge. This is creator-specified visual canon, not speculative styling. Preserve continuity of hinge points, structure and wing identities between atmospheric and radial modes. The exact wing count, deployed diameter, membrane geometry, motion and physical propulsion remain design questions, not settled canon. Review matched-scale front/side/top silhouettes and animated transition for overlaps, crew safety and readability. The resemblance to solar sails does not establish that solar radiation pressure powers this traversal mode.

## Creator design refinements — hydrofoil, wing visibility, Orbiter metamaterial
**Mode 02 Seaborne:** specify visible deployable hydrofoils extending beneath the hull, with load paths and clearance that let the vessel rise and glide over water. Hydrofoil use is an intended design direction; foil sizing, takeoff velocity and water handling are not yet simulated.

**Mode 03 Submersible:** retain all four wings, folded/rotated into compact hull-side positions but **still visibly readable** as wings. Do not erase them into a smooth submarine body. Show mounting hinges, small membrane outlines and fairings; check pressure-safe articulation and clearances.

**Mode 04 ORBITER (renamed from Moon Bridge):** four and only four equal-sized dragonfly-descended wings deployed **up, down, left and right**, radial cross arrangement around the still-forward-facing bridge and hull. Each wing is a futuristic iridescent metamaterial sail with visibly layered photovoltaic collection structures and light-sail optical membranes. Include dragonfly-like veining, prismatic gleam and subtle chromatic iridescence; avoid generic rigid rectangular solar panels. The solar-panel/light-sail dual capability is **fictional design canon** for the game, not a claim that a currently available material performs both at these parameters. Retain the Moon Bridge as the *hidden traversal path* name only until any separate path renaming decision.

**Art QA:** verify four primary wings in Skyborne, their visible transitions through Sea/Submersible, and precisely four equal radial sails in Orbiter. Check frontal-bridge heading, relative scale, hinge continuity, hydrofoil deployed/stowed geometry, no self-clipping and a smooth visual identity across four views. Concept sheets remain subject to creator acceptance.
