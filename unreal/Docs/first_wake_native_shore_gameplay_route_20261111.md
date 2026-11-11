# First Wake integrated 3D review route (not production approved)

The First Wake C++ player now has an opt-in, review-only scene route through **existing saved Unreal maps**, ending in the native 43-actor composited shore scene. The source Prelude and six environment maps remain immutable. This is not the final six-map authored story path, and no PIE end-to-end acceptance has occurred yet.

## Player route

1. Use `powershell -ExecutionPolicy Bypass -File unreal/Tools/Launch-TSTSS-FirstWakeShoreReview.ps1` from the repository root. The launcher opens the native Prelude in standalone review mode with the opening New Game overlay; for PIE instead open `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2` directly.
2. On the Prelude, use WASD, mouse and E to discover Ionia's flyer, accept her hiring, board the ship and inspect the lift/pressure/reserve systems. After the engineering signoff, **K explicitly launches**, advancing the real story state to Launched and loading the existing `VS03_FirstWakeSky` review level.
3. In `VS03_FirstWakeSky`, **K** goes to `VS04_SplashdownSea`. These scene levels currently have no PlayerStart or flight controls, so the review pawn uses a temporary flying observer position; this is **not** final Aureate Wake flight gameplay.
4. In `VS04_SplashdownSea`, the existing native physical-water adapter must observe actual hull-water contact and stable flotation. Pressing K before FlotationConfirmed is refused. When the physics gate really reaches FlotationConfirmed, **K** continues to `VS05_DenithFuelShanty`.
5. At the shanty, an additive runtime **E** interaction marked EMPTY RESERVES is generated near the PlayerStart only for a successful, story-bound arrival. It advances EmptyReserveInspected, never supplies fuel or items. Then **K** loads `/Game/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review`.
6. Shore arrival uses the existing PlayerStart and preserves the validated First Wake state and inspection mask through a one-use GameInstance subsystem. There is no automatic Lyra recruitment. The shore's static Ender/Ionia/Lyra gear props, three enemy silhouettes and nine spell VFX are **not yet gameplay-equippable items, enemy encounters or ability unlocks**.

K only works in the named source map with the exact authorized story beat and a present destination map. A prematurely pressed key, unrelated world, lack of physical landing, stale pending ticket, or wrong destination is rejected. The subsystem carries no permanent SaveGame data.

## Current evidence and incomplete acceptance

- New C++ automation test: `TSTSS.VerticalSlice.NativeSceneRouteStoryGate` covers the authorized four scene boundaries and denial cases. This source is not marked PASS until compiled and executed natively.
- The existing source suite and UE Win64 compiler must be rerun against the final source commit; source-only checks cannot prove the OpenLevel route or native water landing.
- Remaining interactive gate: New Game -> input -> engineering -> sky -> physics-driven sea landing -> fuel interaction -> composited shore pawn control, with logs and a fresh lit D3D12 screenshot.
- Automated white captures are inconclusive. No visuals, combat, gear, spell progression, ship flight or Chapter 1 scenes have been approved.
- Ender and Ionia precede splashdown; Lyra's subsequent actual recruitment remains future work. Reson and Aepex are unavailable; Starbourne stays locked.

PR remains draft, protected main unchanged. Do not promote source maps/assets, drop resource guards or claim full AAA slice completion without native and creator review evidence.
