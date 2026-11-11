# TSTSS — First Wake equipment menu (review-only)

## Scope and plot boundary

This is a developer-controlled, opt-in **interactive equipment review panel** for the opening vertical slice. It is not production inventory, does not mint items from loot tables, does not save equipment, does not grant abilities, and does not automatically recruit any character. The exact roster remains **Ender and Captain Ionia** during the First Wake and **Lyra only after a separate, explicit recruitment event**. The current First Wake story/save state does not contain such an event. Therefore **Lyra remains locked** even after the ship splashes down.

## User interaction

- In a non-shipping First Wake playable review, press **G** to open the field-equipment review menu. The menu is not available while the title screen has hidden the game HUD.
- Select Ender or Ionia's **weapon, armor, or accessory** buttons to equip/unequip their already-owned review items. Each operation goes through the existing atomic, owner-checked equipment ledger. The menu updates immediately and does not touch SaveGame.
- Lyra's three equipment buttons are disabled and marked **LOCKED** until the plot supplies a distinct recruitment receipt. No player-facing button creates that receipt.
- Select **RETURN TO VOYAGE** (or G when gameplay input still receives it) to close the panel; game input and cursor handling are restored.
- The review menu preserves choices while it is open/reopened within its owner session; the First Wake-to-splashdown story stage may advance without generating new items.

## Technical implementation

- `UTSTSSPartyGearMenuReviewWidget` creates native UMG hierarchy at runtime with three character sections, explicit lock labels and nine per-slot buttons.
- `TryApplyReviewToggle` rejects unknown owner, unavailable stage, invalid slot, duplicate same-state requests, ambiguous item ownership and equipment not already in the fixture. It writes to output only on successful ledger swap.
- The default First Wake pawn handles **G** only in non-shipping builds. It obtains `FirstWake` or `AfterSplashdown` strictly from `UTSTSSFirstWakeState::IsChapterOneActOne()`. It does not expose `LyraRecruited` or call any story mutators. The panel is opt-in and does not replace the opening title screen or the First Wake HUD.
- This menu presents ledger state only; **it is not yet synchronized to skeleton/socket-mounted animated equipment**. The separate 3D review component already handles static mesh swap and socket admission.

## Testing and outstanding gates

- The existing mandatory `TSTSS.Equipment.PartySliceStageGate` native test now also exercises pure UMG review toggle policy, successful atomic unequip/re-equip, forbidden Lyra before recruitment, excluded characters, invalid slots, duplicate operations and output preservation.
- Engine-free source tests verify the G-key mapping, runtime story-stage derivation, source UI gates and denial paths.
- Native UMG runtime widget visibility, mouse focus, button clicks, cinematic layout and D3D12 screenshots require actual target-project PIE review (compile and source-only checks are not visual evidence).
- Final three-character rigging, fit and animation, persistent inventory ownership and player combat integration remain separate tasks. No current changes are authorized for merge or art promotion.
