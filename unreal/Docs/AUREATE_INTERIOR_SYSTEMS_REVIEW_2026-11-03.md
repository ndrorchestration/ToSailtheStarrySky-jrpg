# Aureate Wake — Interior Systems and Structural Attachment Review

**Date:** November 3, 2026
**Status:** Unreal 5.8 review only; not canon art, habitable geometry, working life support, or release authority.
**Lineage:** stacked on review PR #706, preserving PR #702's coupled geodesic bridge + quarters pivot.

## New Unreal C++ review anchors

The reversible AAureateWakePreviewActor exposes four named collision-free scene attachment frames, for future authored interiors. These create **no furniture, doors, dynamic physics, crew AI, pressure barrier, or game progression**.

| Review frame | Parent | Position, centimeters | Status |
|---|---|---|---|
| BridgeHelmReviewAnchor | BridgeHabitationPivot | Legacy (240,0,95); opt-in central (0,0,80) | Provisional |
| QuartersDeckReviewAnchor | BridgeHabitationPivot | (0,0,-25) | Provisional |
| FixedEngineeringReviewAnchor | VesselRoot | Root origin, not yet placed | Unpositioned |
| FixedBoardingReviewAnchor | VesselRoot | Root origin, not yet placed | Unpositioned |

The bridge and quarters anchors rotate with their shared pivot; fixed engineering and boarding anchors remain attached to the hull. They deliberately do not inherit scale from the visual placeholder meshes. The review remains **off by default**, and opt-out restores the previous forward-bridge pose. All four wing components, two hydrofoils, six directed ordinary form routes and the Starbourne hold remain untouched.

## 24 internal ship-system proposals

The tracked non-runtime manifest is at **unreal/ReviewData/aureate_internals_review_v1.json**. It contains:

- **Bridge, four systems:** helm controls; star charts/auroral navigation; communications and sensors; navigation instruments.
- **Central quarters, six systems:** crew sleeping berths; galley/common room; sanitation; child-safe accommodation for Talen; cabin air distribution; emergency supplies.
- **Fixed engineering, twelve systems:** monitored power bus; harmonic levitation engine; four wing actuators; two hydrofoil deployers; Submersible ballast; pressure monitoring; air recirculation; water recovery; thermal management; fire detection; maintenance; future locked Starbourne light-sail support.
- **Boarding, two systems:** boarding interfaces and emergency egress.

Each entry is DESIGN_ONLY and gameplay_enabled=false. This is a construction dependency register and not an Unreal runtime component list. No story-energy resonance, ship-power mechanics, traversal rights or future mode is silently authorized.

## Interfaces between moving and fixed sections

1. **Bridge to quarters:** Same rotating pivot exists in the C++ preview, but there is no tested stair, hatch or occupiable interior.
2. **Quarters to engineering:** A rotating-to-fixed service collar, seals, pinch-point protection, power/air connections, and safe passage are all UNVERIFIED.
3. **Engineering to boarding:** A potential fixed-hull passage, with no proven walkable dimensions or emergency exit.

### Spatial mismatch requiring designer resolution

The current living-quarters proxy is **220 × 115 × 35 cm**, because Unreal BasicShapes/Cube is 100 cm and its C++ scale is (2.2, 1.15, 0.35). The 35 cm vertical extent cannot be treated as a crew cabin. The validator compares it to a **proposed 180 cm minimum screening height**, *not an official code/ergonomic standard*. The actual ship interior scale, number of beds, crew occupancy, child safety, hull taper, deck access, lift envelope and potential moving habitation collar remain undecided. Rescaling a cube alone is not a solution.

## Testable review contract

Run from the isolated branch root:

- python -B unreal/Tools/validate_aureate_internals_review.py
- python -B -m unittest discover -s unreal/Tools -p test_aureate_interior_systems_contract.py -v
- python -B -m unittest discover -s unreal/Tools -p test_*.py -q

The validator binds manifest modules and dependencies to **actual C++ attachment names and parents**, preview defaults, opt-in/out translation, physical proxy dimensions, source-nonfinite angle guards, and the Starbourne/Orbiter hold. It rejects fabricated implemented systems, duplicate/missing systems, dependency cycles, premature crew access, missing egress and false creator approval. Successful source validation intentionally returns **HOLD_UNBUILT_INTERNALS_AND_UNVERIFIED_PASSAGE**, not READY.

## Production stages

| Priority | Implementation | Required acceptance |
|---|---|---|
| I1 | Evaluate ship hull scale, geodesic dome height and real crew requirements | Whole-hull metric envelope and creator review |
| I2 | Author bridge, quarters, galley, bunks, engine bay, boarding and service greybox under the anchors | UE5.8.4 imported meshes, four-camera render, capsule clearance |
| I3 | Moving circular joint/collar and safe passage while habitation rotates | Swept six-route collision tests, no pressure/egress bypass |
| I4 | Modular ship system components: levitation engine, four-wing actuators, hydrofoil deployers, power, life support, Submersible ballast, pressure and alarms | Native fail-closed automation, actual physical tests |
| I5 | Playable crew traversal, Ionia at helm, Ender's engine repair, environmental storytelling | In-engine player input, objective and independent SaveGame tests |
| I6 | Approved final art and atmospheric ship effects | Creator inspection, native screenshots, lighting/performance/physics review |
| I7 | Starbourne light-sail/solar interior integration | Independent progression gate; locked until story authorization |

**Current new-head holds:** no Windows native UE build, native ship actor automation, continuous swept clearance, walkable crew path, real pressure proof, final cinematic art or launch approval established for this implementation.

See the separate AUREATE_CENTRAL_ROTATING_BRIDGE_HABITATION_DESIGN_2026-11-01.md for the original scope and unresolved rotating module constraints. Do not merge or promote this review without creator consent.

## Additional inherited wing QA blocker

The separate legacy suite at unreal/Tests currently fails during setUpClass of test_aureate_wing_clearance.OfflineEnvelope: it requests a per-primitive vertex budget of 900 while the immutable reviewed wing's venation primitive has 14,770 positions. Full-geometry budget enforcement correctly rejects that partial coverage. This test and wing reader were NOT modified by this interior branch. Reconcile the old suite against full-vertex mesh clearance and its expected sample count in a separate bounded review, not by disabling the fail-closed reader or claiming sampled wing/hull clearance.
