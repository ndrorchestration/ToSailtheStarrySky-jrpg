# First Wake vertical slice — joined state and water verification (2026-11-03)

**Status: IMPLEMENTED IN ISOLATED DRAFT SOURCE; NOT NATIVE-VERIFIED, PLAYABLE-VERIFIED, OR MERGED.**

## Authority and bounded scope

- Active target: Unreal Engine 5.8.4 C++/Blueprints. The Godot/browser material is historical.
- Baseline: draft PR #713 at `f7b58df09bafc8eec04e463c9a2e82cbff7606e3` with the seven-actor V2 Prelude map, objective cues, interaction reach and P01–P13 PIE acceptance protocol.
- Selectively reconciled, not merged: PR #717 water quickload reset, PR #726 Windows/MSVC water behavior checker, and PR #730 interaction-to-Splashdown native automation and source contract. All source PRs remain separate and unmerged.
- Intended journey: discover Ionia's flyer -> hire Ionia -> board Aureate Wake -> inspect Lift, Pressure and Reserve -> authorize launch -> require physical sea contact and 2 seconds of stable flotation -> begin Chapter 1 Act 1 at Splashdown -> inspect empty reserve -> return to berth.
- This joins API-level state/integration proof, NOT a single approved cinematic/playable 3D level. Lyra is not recruited early; Ionia joins first. No new combat authority, production ship art, save schema, Starbourne unlock or canonical ending/reveal.

## Actual integrated changes

1. Successful `UTSTSSFirstWakeState::Restore` advances a transient generation even when restoring the same story beat; failed restores do not.
2. `UTSTSSWaterLandingGate::Observe` invalidates stale wet-contact/settling evidence on generation change; fresh continuous stable contact must accumulate again. No interaction actor can forge `SeaContact` or `FlotationConfirmed`.
3. New `TSTSS.FirstWake.InteractionToSplashdown` native C++ automation test uses a transient milestone actor, the actual story and water APIs, synthetic water observations and an in-memory version-2 save payload. It does not touch player saves or measure buoyancy.
4. The strict native report registry now requires **26 unique named tests** instead of this branch's inherited 25. Source registration is not native execution.
5. GitHub source preflight includes both the water-rewind compiled stand-in/mutation check and the 7-case integration authority contract.

## Evidence executed on neontic

- Reversible worktree: `C:\TSTSS_FirstWake_VerticalSliceIntegration_20261103`, created from the exact baseline above; original worktrees and protected main unchanged.
- Source integration authority suite: **7/7 PASS**.
- Unreal Tools Python tests: **177/177 PASS** at integration commit `43e0b8d93e1ecfa7796cdc845d39bb248bf57606` (before the MSVC-only runner enhancement); rerun after any further edits.
- Native registry source accounting: **26 registered required names across 15 C++ test files — PASS (source only)**.
- Windows VS2022 `vcvars64.bat` source-extracted **production water C++ behavior**: **310 assertions PASS**; deliberate removal of restore-generation guard compiles but fails the designated same-beat test. This is not an Unreal build or physical water test.
- The authorized device had `UnrealEditor.exe` and `LiveCodingConsole.exe` active during inspection. No competing native UBT, Editor automation or map commandlet was launched; neither application was stopped.

## 2026-11-03 continuation — join newer objective HUD without native claim

- The parent draft #713 advanced beyond the original integration baseline. Its exact fetched head for this reconciliation was `2ee5d4e08e89aff1b66a44af419913c8b005d29a`. This isolated branch integrates that parent history; the only textual conflict was in `.github/workflows/unreal-source-preflight.yml`, resolved by preserving **both** the water-rewind harness and the newly added objective-HUD source/harness checks.
- The review-only `ATSTSSFirstWakeReviewHUD` now comes from the parent: objective text and Lift/Pressure/Reserve lamp states refresh from live story state; limited viewport layouts are covered by source tests. The HUD hides after the Chapter 1 boundary and under shipping builds. This is an implementation/source-harness claim, **not** a visual Unreal/PIE acceptance claim.
- The HUD's source-extracted C++ compiler runner gained a reversible Windows MSVC `cl.exe` fallback (with separate temporary `.obj`/`.exe` paths), preserving the GCC/Clang route on hosted CI. Invoked through VS2022 `vcvars64.bat` on `neontic`, the actual `DrawHUD` method passed **21 non-shipping and 1 shipping portable assertions** using API stand-ins, without launching Unreal or touching project saves. This does not prove actual game rendering.
- The integrated source-only Python suite passed **205/205** tests on the merged working tree before adding the runner fallback; final post-merge committed SHA source checks must be reread independently. The previous 26 required native names remain registered, NOT engine-executed.

## 2026-11-03 physical water-adapter review continuation

The authorized UE 5.8.4 Windows machine still has a separate active Unreal Editor/Live Coding session. A real `Verify-Unreal.ps1 -SkipTests` preflight against exact previous branch SHA `19192d00af765dd4e12febb73f2873d299ce69d5` **correctly refused native compilation before creating evidence**; ignored evidence directories stayed 0 before and after, and the tracked worktree was clean. It would be misleading to claim 26/26 native execution.

To advance the *real water source handoff* without interfering with that session, this review adds `unreal/Tools/check_first_wake_physical_adapter_compiled.py`. It extracts **the actual production `ATSTSSWaterContactAdapter::Tick` C++ method**, compiles it against narrow actor/hull/water API doubles, and exercises 13 behavior assertions on the authorized Windows VS2022 MSVC toolchain. Assertions cover a simulated-physics hull requirement, water actor tagging, lower-bound waterline geometry, real overlap forwarding, actual sampled vertical velocity, NaN and invalid-draft denial, default-off vs opt-in provisional buoyancy force, and player-story rebinding. **13 checks PASS**.

Three deliberately unsafe code mutations **compiled but failed at the intended behavioral assertions**: removing `Hull->IsSimulatingPhysics()`, removing the water-volume tag, and removing the true hull-bottom-below-surface requirement. This test now runs in hosted Unreal source preflight. It does **not** simulate UE physics, create a water volume, save an Editor map, run PIE, measure two real seconds of immersion, or grant Splashdown. The existing adapter is still not shown as successfully placed/configured in a traversable real level.

**Next physical scene acceptance:** in a separate, disposable Unreal map, place a properly collidable simulated hull and bounded tagged water volume, verify the hull really overlaps below the surface, sample `GetPhysicsLinearVelocity().Z`, measure continuous low-speed contact against the unchanged two-second gate, and capture no-contact/fast-impact/occlusion/quickload negatives. Keep cinematic hull art and chapter unlock independent from this greybox proof.

## 2026-11-03 full restart water-evidence fix (draft only)

A separate **actual production source defect** was identified in the joined First Wake code. `UTSTSSFirstWakeState::Restore()` advanced the transient `RestoreGeneration` used by `UTSTSSWaterLandingGate` to discard stale settling/sea-contact evidence, but `UTSTSSFirstWakeState::Reset()` did **not**. When a same-object Story/Gate pair was fully reset and progressed through a fresh Prelude before the adapter's next tick, the old gate could retain `bContactRecorded` and the prior stable-contact timer. It could then fail to reacquire actual `SeaContact` on the new launch or count stale duration.

**Small reversible fix:** `Reset()` now increments the *existing transient* `RestoreGeneration`. No saved game schema or gameplay beat enum changed. The existing native water restore automation test now exercises the real old-contact -> full Reset -> flyer/Ionia/boarding/three inspections/signoff/launch -> new contact sequence **without calling `Gate->Reset()`**. It requires the new timeline to genuinely reacquire `SeaContact` and to accumulate a full **two fresh stable seconds** before flotation.

In this isolated review patch, Windows MSVC successfully compiled the **actual state/gate C++ and two existing repository automation test bodies** against API doubles: **341 assertions PASS**, up from 310 in the prior baseline. Two separate deliberately unsafe mutations compiled and **failed at their specific behavior assertions**: removing the same-beat Restore-generation guard, or removing Reset's new generation increment. This remains **portable C++ evidence, not a native Unreal build/PIE/water simulation**. Existing 26 registered native test names are unchanged.

## Outstanding hard gates

| Gate | Status |
|---|---|
| 26/26 UE 5.8.4 native automation at exact joined head | NOT TESTED |
| Native Win64 Editor UBT/UHT at exact joined head | NOT TESTED |
| Real seven-actor V2 map native admission at joined head | NOT TESTED |
| P01–P13 player-in-Editor keyboard/movement/line trace and F5/F9 | NOT TESTED |
| Actual hull/water overlap, flotation, camera and seamless Splashdown | NOT TESTED |
| Film-quality Ender/Ionia/ship visuals and creator art approval | NOT AUTHORIZED |
| Packaged player build, release, merge into protected main | NOT AUTHORIZED |

**Next smallest reversible acceptance:** when the running Editor/Live Coding sessions are independently idle, use a fresh clean disposable worktree and `unreal/Tools/Verify-Unreal.ps1` with the exact branch SHA and installed UE 5.8.4. Require genuine UBT/UHT success, **26 distinct Success entries** in the real native JSON, clean-source postflight and immutable receipts; then separately run the source-locked native map QA and P01–P13 PIE. Keep actual player saves and tracked config credentials out of test evidence. All art remains review-only, and Starbourne stays fail-closed.
