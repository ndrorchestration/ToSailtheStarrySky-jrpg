# Aureate Wake — Central Rotating Bridge and Living-Quarters Design Constraint

**Creator direction: 2026-11-01. Documentation-only review. No approved animation, location coordinates or mechanical solution yet.**

## Creator-established design intent

The **geodesic-dome bridge and the living quarters directly beneath it** are one significant, centrally situated section of the Aureate Wake. Because this assembly is central enough within the vessel, **it may rotate about a central pivot as the vessel transforms between configurations**.

Treat the bridge and living quarters as a *coupled spatial assembly*, rather than animating only the transparent dome or assuming the bridge must always remain rigidly aligned with the outer hull. Preserve the four-wing dragonfly heritage and the geodesic glass bridge. Do not relocate the living quarters to a different part of the ship without creator review.

**Important distinction:** This establishes a **permitted/desired transformation design option**, *not* a final mandate that the assembly must rotate in every transition. The creator has not yet fixed the pivot, orientation angle, mechanism, center of rotation, handedness, axis, rotation speed, interior camera behavior or whether any one form uses a different default bridge facing. Those are engineering proposals needing visual testing.

## Relationship to established form and visual canon

Player-facing configurations are **Skybourne, Seabourne, Submersible, Starbourne**. The serialized/internal Unreal identifiers (`Skyborne`, `Seaborne`, `Submersible`, `Orbiter`) must remain stable until a separately reviewed migration. Starbourne remains story/progression-gated, including the prohibited direct interpolation pathways; do **not** activate or build a bypass through this feature.

The creator-approved four-form ship illustration remains the **artistic authority**. The four dragonfly-derived wings remain visible (or intentionally tucked in Submersible), Seabourne retains the hydrofoils and struts, Starbourne uses its four cardinal light/solar sails, and the bridge remains visually identifiable and navigationally sensible. Earlier descriptions of the bridge as “forward-facing” should be reconciled through its **orientation when deployed**, rather than assuming a permanently rigid, forward-offset component or silently relocating it.

## Current code discrepancy — not a decision to modify source

In the unmerged preview-actor lineage, `ForwardBridge` is attached directly to `VesselRoot` and set to relative translation `FVector(240, 0, 95)`. The V2 glass bridge GLB was tested against that **provisional** placement. This is a static review implementation, **not** a verified central rotating bridge/habitation assembly; it neither models the living quarters below nor proves that a gimbaled module fits the existing hull.

Prior exact-head wing/hull clearance receipts, screenshots and hydrofoil-strut test results **cannot** be generalized to a newly repositioned or rotating bridge/living-quarters unit. Those would require fresh exact-source and native Unreal verification.

## Proposed engineering slice (not yet canonical implementation)

1. In an **isolated Unreal 5.8 review actor**, define a dedicated `BridgeHabitationPivot` `USceneComponent` near an *artistically evaluated* center of the bridge-plus-quarters assembly, separate from wing hinge roots. Attach a `BridgeDome` component and an explicit **HabitationDeck/LivingQuarters envelope** as children, preserving their relative geometry and shared rotation. Keep the existing preview actor unchanged until the prototype passes.
2. Parameterize a **form-specific target orientation** and interpolate through an optional, controlled rotation during ordinary-mode transitions. Any stabilization against gravity/acceleration is a proposal requiring design testing; Submersible pressure seals and Starbourne zero-g orientation are independent constraints.
3. Prove that the pivot and moving envelope remain free of the hull, four wing roots/support details, hydrofoils, radial sails, crew movement paths and exterior deck through each transition. Validate **continuous/swept** collision, not only discrete endpoint AABBs. Treat intended mounting contacts separately from accidental penetration.
4. Include visible/physical passageway handling between the rotating habitation module and stationary hull. Assess connection seals, power/air circulation, living-quarters livability, accessible interior navigation, character/camera transitions, and save/load of the form and bridge rotation. Don't imply pressure protection works just because a material is translucent.
5. Capture before/after and mid-transition **native Unreal** images/short reviews from matched camera angles for Skybourne, Seabourne and Submersible. Include the bridge dome **and living quarters beneath**, not dome-only animation. Starbourne visual work may remain an isolated locked-gate preview; do not authorize its gameplay transition.
6. Present the smallest successful reversible prototype to the creator for approval **before** replacing model assets, relocating the bridge, changing the approved four-form silhouettes or merging into protected main.

## Acceptance / governance

**Design intent:** creator stated, recorded here.

**Mechanism:** **PROPOSED — NOT IMPLEMENTED OR ART APPROVED.**

**Tests:** no native rotating bridge/habitation build, animation, collision report or screenshot is claimed by this documentation.

**Prior review status:** V2 root-support variant in draft #701 remains a noncanonical support-clearance experiment with attachment integrity HOLD. A future pivot prototype must not override that hold or inherit clearance evidence without rechecking the new moving bodies.

Never merge, promote generated 3D art, unlock Starbourne or release publicly without user authorization.
