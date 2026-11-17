# First Wake — Unreal vs browser quest-state authority reconciliation

**Date:** 2026-11-17
**Status:** SOURCE AUDIT / REVIEW ONLY / NO CROSS-RUNTIME ADAPTER ACCEPTANCE
**Compared heads:** Unreal review `9ae71aa5d6e910d82017240150870be3950ea939`; protected-main browser quest tranche `37d8918dea717de0a5e89aee34727a4c52463b52`.

## Source ownership and discrepancy

| Topic | Latest protected main (browser / NW.js) | Current creator-approved Unreal vertical slice | Disposition |
|---|---|---|---|
| Quest-state owner | `modules/quest-defs.js`, `modules/quest-state.js`, `modules/first-wake-quest-adapter.js`; schema v1 / quest QST-A1-001 | `UTSTSSFirstWakeState` progression; review-only C++ state, boarding ticket, three inspection bits | Separate runtime authorities; do not convert one state code to the other |
| Opening | Browser `modules/first-wake-opening.js` stages dock, berth, Talen, Lyra's household and `lyra_join` before `first_wake_card` | Ender starts in Greenwood; read Ionia's Hilltonia flyer, explicitly accept, meet Ionia, separately board ship | Browser chronology conflicts with currently approved Unreal scene placement |
| Engineering | Browser quest states OPENING → WRONG_SONG_NOTICED → PRACTICAL_RESPONSE → CHAPTER_CARD → COMPLETE | C++ review must earn LIFT/Pressure/Reserve plus separate signoff inside the Aureate Wake before launch | No valid 1:1 state mapping currently established |
| Lyra | Browser `lyra_join` scene precedes its First Wake chapter card | Lyra joins **after** physical offshore splashdown and crew regroup, never before first flight | **HOLD** any cross-runtime scene/quest mirroring until redesigned |
| Recovery | Browser first-wake adapter records provisional Wrong Song evidence; it cannot authorize an Unreal physical landing | Actual hull-water contact and stable float, then plot-locked Seabourne; no convenient legacy Denith shanty transition | Separate verified physics and narrative requirements |
| Starbourne | Browser definitions include separate auroral crew/route controls | Starbourne fail-closed; Reson and Aepex unavailable in this vertical slice | Must stay locked regardless of proposals |

## Reconciliation decision

1. **Do not copy the browser quest-state modules into Unreal or overwrite the protected-main JS tranche.** The browser files are genuinely present on protected main; importing them into this older review branch without integrating main would create an unnecessary duplicate snapshot and falsely imply semantic parity.
2. The [creator-locked First Wake route](FIRST_WAKE_CREATOR_LOCKED_HILLTONIA_TO_OFFSHORE_SPLASHDOWN_2026-11-16.md) is the authoritative **design requirement** for the Unreal slice. This does not certify production readiness.
3. This branch's current creator-route [log-contract verifier](../../unreal/Tools/verify_first_wake_hilltonia_water.py) adapts PR #849's **physics validation logic** to require Hilltonia flyer read and acceptance, dockside Ionia/ship E interactions, earned shipboard E×4, source-locked scene travel to sea, and two-sided stable immersion. It returns **LOG CONTRACT PASS / NATIVE NOT AUTHENTICATED**, never an Unreal gameplay or real ship-hull approval. PR #849's original seven dock-marker script remains historical evidence on its own draft branch.
4. Before any merged browser/UE quest abstraction, design an explicit **schema-versioned, non-authoritative translator** with strict negative cases for premature Lyra, early signoff, duplicate accepts, no earned boarding ticket, wrong save generation, Starbourne unlock, and direct denial of false native proof. Do not silently map wrong-song evidence to ship-system faults.
5. The missing native work remains primary: UHT/UBT exact-head compilation, two end-to-end third-person PIE playthroughs, actual engineering interior and intercom, physical contact with an Aureate hull, save/load, camera/art review, and creator approval.

**Git custody:** reviewed main HEAD `37d8918` has 12 commits not present in the prior review lineage. A direct branch merge is out of scope; the older review branch is hundreds of commits ahead and the shallow Neontic clone cannot be used to infer branch ancestry. Use server-side comparisons to plan any future integration. Protected main remains unchanged.
