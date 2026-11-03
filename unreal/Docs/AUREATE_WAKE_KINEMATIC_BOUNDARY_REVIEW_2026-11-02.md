# Aureate Wake — four-wing kinematic boundary review

**Status:** Review-only test change; noncanonical; no runtime behavior, physics, art, save data, or gameplay authority changed. The expanded native test remains registered under the existing required name but has not been compiled or executed at this branch's candidate head.

## Exact review lineage

This child review starts from draft [PR #695](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/695), head `a1c0b09030bba15c2bb2c8c83c171c4a553d05f7`, whose base is `review/ue58-aureate-ordinary-forms-20261101` at `77ee249f8a0d734eab165dcafcd16870f12f07a7`. PR #695 is OPEN/DRAFT. This branch does not modify that parent branch, protected `main`, or the separate integrated authority/First Wake line (#713 and #717).

## Why this first slice is intentionally narrow

The existing `AAureateWakePreviewActor` is a geometric review actor. Its four `DragonflyWing_1` … `DragonflyWing_4` components are persistent, have collision disabled, and are not intended to simulate physics. The actor's header explicitly excludes sail thrust/navigation; there is no aerodynamic force application in this actor. This review adds a regression guard only; it does not implement the requested aerodynamic model or turn illustrative simulation values into game physics.

The existing required automation `TSTSS.Ship.PreviewFormsAndOrbiterHold` now checks that exactly the same four named wing component instances remain present, `NoCollision`, and not simulating physics in their source pose, at transition start and midpoint, at each ordinary-form endpoint, and through all six directed routes among the existing ordinary-form preview states. It also checks an authored-wing preview transition and confirms that the Starbourne/legacy Orbiter request remains rejected. The test name and registry are unchanged; no new runtime mode, fifth wing, or physics authority is added.

Player-facing configuration names are **Skybourne, Seabourne, Submersible, and Starbourne**. Existing serialized/internal C++ enum identifiers **Skyborne, Seaborne, Submersible, and Orbiter** are intentionally preserved; any such spellings in test diagnostics refer to internal identifiers, not player-facing labels. Starbourne remains gated and its four-wing visual study does not authorize a fifth wing or unlock a transition.

## Authority reconciliation and limits

The current Notion Operational Control Center and Documentation Authority & Reconciliation records designate Unreal Engine 5.8.4 as the active forward-development track. GitHub draft #713 contains the authority reconciliation; current draft #717 is a separate First Wake follow-up. The exact PR #695 ancestry used here still carries a root `AGENTS.md` that says Godot 4.7.2 is active. That file-level conflict is recorded, not silently rewritten in this bounded review. This PR remains explicitly stacked on #695 and must not be mistaken for integration into #713/#717 or as a fresh native verification of those branches.

The Starbourne-to-Skyborne force CSV uses illustrative inputs (including assumed mass, density path, effective coefficient-area products, and left/right lag). It is not measured ship data, a validated flight model, or an approved load envelope. This change adds **no** `AddForce`/torque path, control authority, coefficient defaults, new physics component, gameplay integration, or Starbourne unlock. Seabourne/hydrodynamic behavior remains a separate medium/system and is not inferred from this test.

## Verification contract

- The existing `TSTSS.Ship.PreviewFormsAndOrbiterHold` registration remains in `unreal/Tools/Verify-Unreal.ps1` as a required named native automation.
- The repository's source registration checker confirms test-name registration only; that is not a native compile or execution result.
- Exact-head UE 5.8.4 Editor build, all required native automation results, final clean-tree check, and any visual acceptance remain pending. Prior PR #695 native receipts are tied to their earlier SHA and do not transfer to this changed candidate.
- A source-only or hosted pass must not be described as native proof, aerodynamic validation, or creator art approval.

## Next gate

Before expanding implementation, select and reconcile against the current intended integration base; do not assume that this #695 child is already part of #713/#717. Then run exact-head source checks and an authorized UE 5.8.4 native build/automation with a clean-tree check. Only after actual authored geometry, per-wing coordinate frames, environment inputs, and reviewed aerodynamic data are available should a separate proposal define a force/control interface. Keep any future model disabled and distinct from Submersible hydrodynamics until reviewed; do not use the current assumption-based CSV as production parameters.
