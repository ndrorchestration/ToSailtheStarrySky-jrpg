# First Wake shoreline gameplay route (native review, not production approved)

This additive route makes the saved 3D shoreline map reachable through the First Wake player's normal input, without changing the main/default entry map, original Prelude, save schema, or any content authority. It is a **review-only playable travel handoff**; the source level still contains static gear, nine VFX demonstrations and three enemy silhouettes, not equipped items, unlocked magic or actual combat encounters.

## How to enter

1. Launch with `powershell -ExecutionPolicy Bypass -File unreal/Tools/Launch-TSTSS-FirstWakeShoreReview.ps1` from the repository root, or open `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2` in PIE.
2. On standalone review launch, choose **New Game** to leave the optional opening overlay. Walk and interact with First Wake markers using **WASD, mouse, E**.
3. Complete three engineering inspections, launch, establish actual physics-backed sea contact and stable flotation, then inspect the empty reserves. **K** becomes available to visit the native scene `/Game/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review`. Press **J** to see the hint; premature K attempts are refused.
4. The level transition carries the existing First Wake story beat and inspection mask in a **one-use, memory-only GameInstance subsystem**. It does not copy files to SaveGames or change save-slot ownership. Only a validated source map and qualifying milestone can issue the ticket; the destination consumes it once. The existing PlayerStart on shore remains the spawn.
5. Ender and Ionia belong to the pre-splashdown progression, and Lyra's eventual post-splashdown recruitment is still a separate **unimplemented** gameplay event. Reson and Aepex do not join the slice. Starbourne stays locked.

## Verification gates

- A source-only predicate unit test checks no entry before hiring/launch, sea contact, stable flotation and reserve inspection; the wrong source map is refused.
- Native Unreal 5.8.4 Editor build and the targeted gate must be rerun at the new committed SHA; no previous 35/35 evidence automatically covers the changes.
- Interactive PIE/standalone must verify user click -> Prelude control -> real sea contact -> reserve inspection -> K -> 3D shore pawn spawn and state preservation. There is no automatic launch/sea travel across all six levels yet.
- The previously white automated render captures remain **inconclusive**; an interactive Lit viewport, geometry placement, exposure, and creator approval are required before visual acceptance.
- Any failure of Unreal map loading, input, packaging, collision or physics is **not** gameplay completion.

No changes to protected main or automatic production promotion are allowed by this review path.
