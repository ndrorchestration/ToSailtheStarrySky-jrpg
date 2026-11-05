# First Wake review: rebind marker collision after successful F9 restore

**Source-only draft review**, stacked upon water witness [#777](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/777) at `fc79092dc5006f4b4b3f06e55dcbbe6abe0be536`.

## Genuine native reproduction (parent source)
In a new isolated Unreal 5.8.4 D3D11 PIE source checkout at `83cd089f54cc5c1a3f16d80036b9bf64bd3d1152`:
- Actual W/E accepted FlyerDiscovery (objective became `Speak with Captain Ionia`).
- Pressing F5 wrote exactly **2,043 bytes** to project-local `Saved/SaveGames/tstss_prelude_pie_quick.sav`, SHA-256 `4066ab12ae388ab1d7a2b6de8c0c25bdb526cd0f4c4b0fd34bc3abf93940d0ab`.
- Real W/E accepted IoniaHiring (objective became `Board the Aureate Wake`); F9 then returned the objective to `Speak with Captain Ionia`. A new real E ray produced `E_MISS`, consistent with the previously consumed Ionia review marker still ignoring Visibility/Pawn collisions.
- Own Editor exited cleanly. Same save hash survived restart. A **new** PIE session and an attempted F9 followed by real W/E **accepted FlyerDiscovery again**, proving the prior save was not adopted. This cross-session denial is **intentional** in current `bPIEReviewQuickSlotOwned` protection; automatic Continue is not implemented.
- Private exact source/map/save/log custody receipts: `C:\TSTSS_SaveResumePIE_20261105\TSTSS_FirstWakeSplashdownSandbox_20261103\unreal\Saved\SaveAudit\session1_f5_f9_20261105.json` and `session2_f9_restart_denied_20261105.json`. Originals, source configs and all user saves preserved.

## Corrective boundary
After a **successful** `FirstWakeState->Restore`, in **editor-only PIE** only, iterate actual review milestones and reconcile precisely the `ECC_Visibility` and `ECC_Pawn` channel responses:
- Completed story markers remain `Ignore` so they do not obstruct progression;
- Incomplete story markers restore `Block`, making them interactable again following an older quicksave;
- Inspection markers use *saved inspection-mask bits*, not only the overall beat;
- No sea-contact/flotation marker may bypass the physics-only state authority;
- Production/unrelated actors and non-PIE worlds retain their previous collision;
- An invalid/corrupt/failed load changes **nothing**.

**This patch does not introduce Continue**, lift the stale save ownership guard, store pawn position, modify save schema, grant progress, or change production saves/maps.

## Evidence still required
1. 100% Python source suite and exact native Unreal Windows Editor build.
2. 29/29 native automations, including transient PIE actor negatives, previous story completed markers, partial inspections, failed out-of-order actions and production actor preservation.
3. New disposable exact-head PIE run with actual F5 after Flyer, Ionia hire, F9, then Ionia re-interaction **accepted** and boarding reachable without a forced sidestep.
4. Separate user-explicit, provenance-bound Continue implementation after restart, and long-term save location/party/ship restoration, must remain independent mandatory P0 gates.
5. Protect all SaveGames and previous evidence. Keep PR draft/unmerged, Starbourne locked and art noncanonical.
