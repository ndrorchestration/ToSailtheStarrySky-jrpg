# First Wake — third-person interaction ray correction (Unreal 5.8.4)

**2026-11-01 · Review-only.** Stacked on independently bounded V2 Prelude/SaveGame test [PR #703](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/703), which itself stacks on native V2 [PR #694](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/694). The authored V2 `.umap`, storyboard, starter stats, ocean contact and all production assets remain untouched.

## Reproduced source geometry defect

`ATSTSSExplorerCharacter`'s default third-person spring arm is **360 cm**, while its interaction radius is **300 cm**. The original code traced from `FollowCamera` only **300 cm**. In the unobstructed, zero-pitch harbor geometry, an actor merely 190 cm in front of Ender lies about **550 cm from the camera**. The ray ends 60 cm *behind the player*, so hitting a forward milestone can be impossible even when the actor is inside its intended 300 cm player-centered range.

## Reversible fix

`TSTSSInteractionReach::GetCameraTraceLength` computes `Distance(CameraLocation, PawnLocation) + PlayerReach`; the controller still traces from the actual camera, using its existing facing direction. **Independent** `IsInsidePlayerReach` constrains successful activation by actual `Distance(PawnLocation, Hit.ImpactPoint) <= PlayerReach`. Negative, zero, NaN, Inf or invalid camera/pawn coordinates fail closed before making a trace. Camera collision, obstructed marker visibility and off-axis aim still naturally block E, and no actor or milestone can be activated solely because the camera is farther away.

The change does not increase the player's intended reach, replace Unreal's visibility trace, change onboarding event order, auto-complete engineering checks, unlock Orbit, grant combat magic or alter save slots.

## Automated QA

- One native C++ automation test `TSTSS.FirstWake.InteractionCameraBoomReach` compares an actual default-like camera offset (360), player reach (300), target forward (190), and reject/accept boundary/NaN cases. The engine's strict `Verify-Unreal.ps1` suite increases from **23 to 24 required tests**.
- Four source-only Python regression checks cover source geometric reproduction, call-site use, player-limit preservation, and native test/registry presence. CI source preflight runs them on the exact PR head.
- **Native Game and Editor builds, 24 named automation tests, actual keyboard E interaction and player-controlled traversal require new exact-head proof.** Earlier PR #685's 23/23 pass does not transfer to this new C++ branch.

## Production readiness gates

1. When the other Unreal Editor's Live Coding mode is no longer active, compile the exact branch in an isolated Windows UE 5.8.4 project; do not bypass the global build guard or terminate a parallel Editor.
2. Run 24/24 native automation tests and inspect each result in the exported JSON. Preserve failure evidence.
3. Launch the V2 harbor review map, verify that E interacts with a front marker from 100–250 cm but not from over 300 cm, with unobstructed and obstructed camera angles. Test movement, signage, save/load and empty sky camera separately. A source/native geometry test is **not** proof of keyboard/PIE.
4. Confirm First Wake progression and save roundtrip remain faithful and the decorative ocean cannot fake a physics landing. Then obtain creator gameplay/art review before merging.

**Status: source design and tests authored; native test/runtime verification pending.** Draft only.
