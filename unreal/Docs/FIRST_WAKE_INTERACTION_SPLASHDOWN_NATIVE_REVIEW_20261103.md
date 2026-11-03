# First Wake interaction → Splashdown: Unreal native integration experiment

**Status:** REVIEW ONLY / DRAFT / NOT AUTHORITATIVE GAMEPLAY. Source branch `review/ue58-firstwake-interaction-splashdown-20261103`, pinned parent `4b85f0d1d7b8870f09d72420871abf4553e3dfbf` (UE migration foundation). Do not merge or claim a playable level from this source alone.

## Purpose

Verify the *existing* Unreal API chain together, rather than checking First Wake order, generic milestone actors, water gate, and save payload in separate tests. This proposed native integration test exercises a real `ATSTSSMilestoneActor` instance in a **transient test world**, a `UTSTSSFirstWakeState`, a `UTSTSSWaterLandingGate`, and the existing v2 `UTSTSSSaveGame` *in memory*.

Scope of proposed C++ automation test: `TSTSS.FirstWake.InteractionToSplashdown`.

1. Ender cannot board or hire Ionia before viewing the flyer. Flyer → Ionia hired → boarded Aureate Wake proceeds in that order, with duplicate flyer refused.
2. Native interaction actor enforces three inspections (lift, pressure, reserve), with duplicate or partial signoff refused, before engineering clear and first launch.
3. Generic milestone interactions **cannot forge SeaContact or FlotationConfirmed**. The story stays Prelude on launch or impact alone.
4. `UTSTSSWaterLandingGate::Observe` is fed **synthetic** contact/vertical-speed samples: impact records SeaContact but cannot start Chapter 1; insufficient stable time and a contact gap cannot promote the story; 21 × 0.1 second synthetic low-speed contact samples can advance to FlotationConfirmed.
5. Only sustained flotation causes the existing derived `IsChapterOneActOne()` view to become true, after which reserve-inspection and berth-recovery milestones become available.
6. The resulting save-state payload is structurally validated, restored into a separate in-memory story object, retains Chapter 1, then Reset returns to Prelude. **No file-based save slot is written or overwritten.**

## Explicit evidence distinction

| Claim | Status until new native report |
| --- | --- |
| Source for ordered API integration assertions | AUTHORED, unmerged |
| Engine-free source contract & adversarial source-mutation checks | Pending/then record precise result |
| Actual UE 5.8.4 Editor Win64 C++ compile of *this* head | NOT VERIFIED |
| Actual `TSTSS.FirstWake.InteractionToSplashdown` automation execution | NOT EXECUTED |
| Real physics overlap, buoyancy, water surface, hull contact | NOT TESTED — input is synthetic |
| Actual PIE movement, camera interaction and a traversable dock/ship | NOT TESTED |
| First Wake cinematic scenes, Ender/Ionia visual fidelity, animation and cinematography | NOT TESTED |
| Real disk save/load, engine-integrated inventory and party roster | NOT TESTED by this test (separate existing suites) |
| Final art approval, canon promotion or release authorization | NOT AUTHORIZED |

The test registers in `unreal/Tools/Verify-Unreal.ps1` so a future real native JSON report must include it exactly once as SUCCESS before a comprehensive PASS claim. Source-level CI is intentionally not an Unreal compile. These tests **do not** import draft PR #643 Ender art or assert any visual signoff.

## Next review slice

Only when the workstation's RAM/commit headroom is sufficient, no competing Editor/build conflicts exist, and a clean *exact-head* checkout is available, run the UE 5.8.4 Win64 Editor build and named native automation with a unique JSON evidence directory. Separately build an isolated playable dock-to-Aureate Wake greybox, wire Ender interactions and actual water overlap, then check input, camera, state/scene, full-float boundary and save restoration in PIE. No gameplay promotion until those separate proofs exist.


## Parallel integration relationship: PR #713 (discovered 2026-11-03)

[Draft PR #713](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/713) already owns a broader **seven-actor V2 Prelude review map**, source-locked Editor map admission, a 23-case executable in-memory map-checker behavior suite and a staged PIE matrix P01–P13. It is on a **different unmerged branch lineage**, and its previous **25/25 native automation** success is bound to source `52e13aedaa8bda900cece849b54eae570179c838`, not this PR or its newer map-checker head.

**This PR #730 is intentionally narrower and nonduplicative:** it specifically exercises native C++ milestone actor calls, first-flight state, synthetic physical water-gate observations, Chapter 1 derived state and in-memory save restoration *within one proposed automation test*. It **does not** replace PR #713's map admission/PIE path or the fuller 25-test registry. Its foundation branch has 13 required native tests, including this new one; this is **not** a claim that the current integrated project has only 13 tests.

**Integration handoff:** do not merge or retarget across stacks automatically. In a later explicitly reviewed isolated integration branch, reconcile the single `TSTSS.FirstWake.InteractionToSplashdown` native source and its required `Verify-Unreal.ps1` entry against #713's exact-head 25-name registry, carry over one engine-free contract check, rebuild and obtain one genuine exact-head full native JSON report. Only then consider real V2 Prelude map PIE plus measured water overlap and approved art.
