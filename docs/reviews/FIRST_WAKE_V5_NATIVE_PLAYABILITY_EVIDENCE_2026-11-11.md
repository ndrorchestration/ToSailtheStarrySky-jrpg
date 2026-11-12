# First Wake V5 native playability evidence — isolated review

**Authority:** Native standalone **review** evidence, not canon art approval, production release, or full vertical-slice acceptance.
**Worktree:** `C:\TSTSS_DockOpening_20261111`
**Branch:** `review/ue58-opening-and-dock-rescue-20261111`
**Exact tested code commit:** `31eb52266b719cfd968df15330029b5190d71a95`
**Target engine:** Unreal Engine 5.8.4, Windows Development / D3D11.
**Title:** `/Game/TSTSS/Review/Opening/L_FirstWake_TitleReview`
**Play map:** `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview`
**V5 .umap SHA-256:** `ff2b5c1423a370c4ac318b9b241088d8f20fec5eee993c998c2a5ed335cbb299`

## Verified in real Unreal process

1. **Native Editor compile PASS**, exit `0` at `31eb522`; receipt `unreal/Saved/OpeningDockReview/ubt_focus_31eb522.exit` and `.log`.
2. **Standalone title click-through PASS.** Windows game process opened the title, a scoped real UI click selected New Game. The UE log recorded `TSTSS_REVIEW_NEW_GAME_ROUTE route=/Game/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview input_mode=game_only progress_reset_by_fresh_map=1`, then `Load map complete` under `TSTSSGameMode`.
3. **W movement PASS.** Holding W for approximately 820 ms visibly advanced the scene camera and nearby marker relative to the earlier screenshot. This followed a narrow input-mode repair that removes the title widget, hides the cursor and sets `FInputModeGameOnly` before OpenLevel.
4. **E interaction PASS.** Pressing E in reach of the first flyer milestone advanced the live HUD objective from **Find Ionia's flyer** to **Speak with Captain Ionia**. In-game screenshot below is direct Windows frame evidence. This is the **first** milestone only, not the entire seven-stop progression.
5. **Review-map fall-recovery PASS.** Holding D moved the pawn off the collision floor and downward; native log recorded `TSTSS_REVIEW_FALL_RETURN map=FirstWake_PreludeInteraction_V5_VisualReview from=V(X=-2485.18, Y=1326.90, Z=-401.30) to=V(X=-2348.71, Y=620.83, Z=90.15) story_unchanged=1`. Subsequent screen retained **Speak with Captain Ionia**, consistent with recovery not advancing the story. The physical fall recovery is scoped only to named review maps, not sea scenes or production.
6. **Compiled gate evidence from prior exact code revision** `53e2aff54b2f78e9f1aad1deeeaf22361d91f32e`: Unreal native two tests `TSTSS.FirstWake.ReviewDockReturnBoundaries` and `TSTSS.FirstWake.ReviewObjectivesAreReadOnly` both PASS, exit `0`; 63 source tests PASS, 16 portable actual-header C++ decision cases PASS. Current UI-only fix did not alter those native decision functions; focused and related source tests also PASS.

## Native screenshots

- [W movement from title-to-V5](assets/firstwake_v5_movement_confirmed.png)
- [First E milestone objective advanced](assets/firstwake_v5_first_e_confirmed.png)
- [After falling off map and returning to walkway](assets/firstwake_v5_edge_recovery.png)

All images are **review evidence**, not approved game art. Some signs appear reversed when viewed from their backs in the recovery screenshot; V5 signfront orientation was otherwise corrected. The visual result remains very bright and lacks final ship, character, surface, sound and environmental quality.

## Remaining acceptance gates

- Complete Ionia hiring, boarding, three independent engineering checks and signoff through actual inputs.
- Verify intentional gated flight/sea contact/flotation sequence and return to fuel-shanty/shore; no shortcuts.
- Verify gameplay interactions, party menus, equipment and Ender's magic in the same build, and capture source-locked native evidence.
- Validate death/fall safety on shore and dock environments, not solely the V5 review floor.
- Integrate final cinematic assets, music/sound rights-cleared sources, lighting/weather and topology; get creator visual approval.
- Do not promote Reson/Aepex into the opening party and do not unlock Starbourne. No merge or production startup-config change was performed.
