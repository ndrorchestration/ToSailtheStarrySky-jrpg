# Native observer setup and failure-case verification

Added `UAureateWakeWaterObserverComponent` in PR #610, reusing the existing `UTSTSSWaterLandingGate` in parent draft PR #608.

## Integration setup (not yet executed)
1. Put the observer on the ship gameplay actor or an explicitly managed physics observer actor.
2. Set `PhysicalHull` to an actual ship hull primitive with collision enabled and overlap events on, **not** the preview actor's non-colliding cube.
3. Set `WaterCollision` to an authored water volume component with overlap events enabled. Configure compatible collision channels and physically measured interaction.
4. Bind a live `UTSTSSFirstWakeState` owned by the active game/session and optionally `VisualShip` to `AAureateWakePreviewActor`.
5. Confirm actual component vertical velocity tracks ship motion; for a physics root and attached child this may require explicit measurement at the moving body. Static zero-speed contacts can falsely appear stable. Validate in the Unreal scene.
6. Observer is enabled only during `Launched` or `SeaContact`. It requests Seaborne visuals on real overlap, and independently sends the overlap and vertical-speed sample to `UTSTSSWaterLandingGate`.
7. Preserve First Wake ordering and save persistence. No mode change itself writes a story milestone.

## Required negative tests
- Unbound components → no story mutation.
- Preview cube without collision → no contact proof.
- Skyborne → manually request Seaborne midair → milestone unchanged.
- Hull overlap at high vertical speed → SeaContact can record but flotation must not.
- Loss of overlap before two settled seconds → stability timer resets.
- Stable water overlap and physically sampled speed at or below configured threshold for two seconds → gate may confirm flotation.
- No duplicate milestone after confirmed flotation; all forms preserve four wings.
- Reload while contacting water → test state restoration and gate reset; do not infer saved ship presentation from story automatically.
- Nonphysics tick gaps >0.25s must fail closed in gate. TickInterval is nominal, not a guarantee of bounded DeltaTime.

## Known limitations and blockers
The component checks Unreal collision overlap + component Z velocity. This is a useful engineering scaffold, **not independently authenticated physics evidence** against faulty collision configuration, scripted movement or bad velocity source. No realistic hydrodynamics, buoyancy solver, wave measurement, water-system plugin integration or UE native tests have been performed. The two source files have not been compiled here. Orbiter and Submersible remain outside First Wake authority. Do not merge or release until exact-head UE 5.8 compile, native scenario tests, Save/Load regression, visual acceptance and signed-off Windows build.
