# Unreal water contact adapter (prototype)

New `ATSTSSWaterContactAdapter` implements observation wiring to `UTSTSSWaterLandingGate`. This is not the final Aureate Wake model or buoyancy simulation.

Setup in the *native* level:
1. Set a properly licensed hull mesh and physics collision to `Hull`, enable Simulate Physics and Generate Overlap Events.
2. Make a water-contact volume with collidable overlap geometry, actor tag `TSTSSWaterVolume`; configure collision channels so hull overlap events are actually generated.
3. Bind an owned, living `UTSTSSFirstWakeState` to `BindStory` (e.g. from the player story controller) before flight. An unbound story cannot advance.
4. Capture actual hull/world collision-overlap and `GetPhysicsLinearVelocity().Z` at the correct physics/update cadence. Tick-based observation is a provisional adapter; adjust to fixed physics substeps if stability varies with frame rate.
5. The 2-second stable-contact threshold and 25 cm/s vertical speed threshold are uncalibrated. This adapter **does not create buoyancy forces**, so a sinking hull cannot count as correct seaworthiness merely because a scripted water plane renders.
6. Required tests: enter/exit overlaps, ignored tagged actors without real overlap, overlapping false positives (e.g. water volume above the surface), vertical velocity, substeps, collision-channel mismatch, resumed saves and high-speed impact.
7. SeaContact and FlotationConfirmed are not triggered by generic milestone actors; audit any other direct calls to `AdvanceTo` before claiming anti-bypass guarantees.

Evidence gate: exact SHA native Windows compile and a recorded physics-backed sea landing with hull waterline / contact logs and creator scene review. Do not close CH1-05 based on these source files.

## Buoyancy prototype (October 31)
The adapter now has opt-in (`bEnablePrototypeBuoyancy=false` by default) force-based vertical buoyancy. For a genuinely overlapping tagged volume, it estimates a water-surface elevation from the volume's upper world-space bound and an immersed fraction using a configurable draft. It applies `Mass * (max_buoyant_acceleration * immersion - damping * vertical_velocity)` through `UStaticMeshComponent::AddForce`, subject to positive mass and finite numeric inputs.

**Explicit limitations:** This is not fluid volume displacement, Unreal Water plugin integration, calibrated hydrostatics, pitch/roll stabilization, wave sampling, or certified seaworthiness. The top of an arbitrary bounding box may not be the water surface; volume authoring must ensure the level matches. The actor still needs to be placed, provided a licensed collidable hull asset, configured for true physics/overlap and run in Unreal. No Unreal compilation, runtime splashdown, frame capture, creator art approval, or installer is claimed.

**Potential upstream pulls:** Godot #547's real contact/sustained flotation test vectors; ship identity constraints from `docs/WORLD_SHIP_VISUAL_DIRECTION.md` (compact articulated dragonfly body, veined wings, rootwood/brass, habitable bridge); #551's installer safeguards; Chapter One checklist CH1-05/17/18/19. Pull *requirements and tests*, not Godot physics APIs, historical low-fidelity model art, or assets without clear redistribution rights.

## First Wake single-player wiring update
The water actor now attempts to find the first local `ATSTSSExplorerCharacter` and bind to its `UTSTSSFirstWakeState` in BeginPlay. If player BeginPlay has not yet initialized that object, the adapter retries while unbound on Tick, then stops doing the lookup after successful binding. `bAutoBindPlayerStory` is author-configurable and may be disabled for explicit ownership or multiplayer. This is runtime source wiring, not proof that an Unreal level has been authored or run.

The player's interaction ray additionally requires the physical player-to-hit distance to be within `InteractionDistance`; distant camera booms cannot grant interaction from beyond the character's range.

Native PIE acceptance must test actor initialization order, a respawn/repossess while an old character still exists, water volume settings and overlap, three inspections, launch, sea contact, save/load, camera collision, and the no-physics-abuse regression. Auto-binding does not solve player replacement/respawn; use explicit rebinding if that occurs.

## Possession/restart handling update
The auto-bound adapter now compares the currently possessed local player story with the bound story on Tick and calls `BindStory` only when the reference changes. Rebinding resets the landing gate, including after player loss, replacing the earlier retry-only approach that could retain a stale story after respawn. This costs a local player lookup each tick while auto-bind is enabled; disable auto-bind and explicitly bind on possession changes for a larger production world. The current single-player behavior still requires native PIE tests of possession, save/load, destruction, and actor ordering.
