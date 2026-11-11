# TSTSS — Unified RPG menu and Aureate Wake console (2026-11-11)

## Intent and menu information architecture
An integrated, nonshipping native UMG review menu now wraps the earlier equipment panel. **M** opens the menu at Party / Status. **G** opens the same menu at Equipment. The left navigation includes Party/Status, Items, Equipment, Magic/Spells, Skills/Arts, Jobs/Growth, Formation, Journal, Aureate Wake, and System.

The Aureate Wake has seven independently navigable subsections: Status, Engineering, Configurations, Crew, Navigation, Upgrades, Cargo. These are true clickable UMG menu navigation buttons, but **ship configuration, repair, cargo transfer, upgrade and crew assignment actions are not implemented or authorized** by this review. Styling is provisional: dark deep-teal console with warm brass headings, not signed-off cinematic quality.

## Authority and data fidelity
| Area | Current review source | Can change state? | Additional required system |
|---|---|---|---|
| Equipment | Transient, owned-by-character review gear ledger | Yes, equip/unequip within review fixture only | Persistent inventory + skeletal mounts + player character gameplay integration |
| Items | Read-only reviewed ownership ledger (six opening gear pieces) | No | Real item inventory/consumable/crafting system |
| Party / Status | Approved affinity definitions, First Wake party gate | No | Live character HP/MP/stats/XP progression |
| Magic / Spells | Affinity and existing action schema only | No | Explicitly admitted, learned spell data; available MP and requirements |
| Skills / Arts | Existing skill/data table contract | No | Runtime learned status, proficiency and cooldown state |
| Jobs / Growth | Existing job-class contract | No | Unlocked job catalog, XP, skill policy and sanctioned selection |
| Formation | First Wake stage gate | No | Actual combat party ownership, legal recruitment and battle layout |
| Journal | Actual First Wake objective and milestone state | No | Quest log, bestiary, codex, map and tracked quest records |
| System | Existing F5/F6/F9 bindings and safety descriptions | No | Audio/video/accessibility/gamepad settings and approved save UI |
| Ship status | Actual First Wake engineering inspection bits; unavailable elsewhere | No | Live hull/power/fuel/altitude/crew telemetry |
| Ship configurations | Canonical design list only | **Never** in this review | Real authorized config transition + animation, physics and narrative gates |
| Ship crew, cargo, route, upgrades | Canonical role/feature design notes | No | Individual ship subsystems and serialized progression |

Data absence must remain explicit, never replaced by invented numerical health, fuel or mastery.

## Canon locks
- Ender and Captain Ionia are First Wake characters. Lyra remains locked at splashdown until a separate recruitment event. Reson and Aepex are not in the playable slice.
- Ender Spirit; Ionia Earth; Lyra Water; Reson Fire; Aepex Air. These narrative affinities are not spell unlock permissions.
- Skyborne, Seaborne, Submersible and Starbourne are named configurations, but the menu **does not possess any transformation authority** for any of them. Starbourne additionally requires the full five-member crew *and* the Aureate Wake plus plot/celestial requirements.
- Ship engineering inspection flags are read from the existing, authoritative First Wake story object; they are not hull-condition, lift-output or reserve-performance gauges.
- No menu operation writes SaveGame, advances the First Wake, awards classes/spells/gear, recruits a character, alters vessel form, or promotes draft art.

## Implementation and input safety
- UTSTSSPartyGearMenuReviewWidget expands from a one-page review to a ten-page native UMG interface and seven ship subpages; widget tree is generated and navigation is wired to dynamic UButton delegates.
- ATSTSSExplorerCharacter binds M (ReviewRPGMenu) and G (ReviewEquipment) **only** in PIE or Game nonshipping worlds, and binds the same widget to the actual First Wake state for read-only journal/engineering display. Both menus share one transient review gear ledger.
- The gameplay pawn rejects movement, camera look, interaction and quick save/load while this menu is open. Closing restores the existing game input mode; no global pause is toggled. The opening/title HUD concealment prevents the menu appearing over that title.
- The existing portable First Wake input-binding compiler harness is extended for M and G; PIE F6 and normal Game F5 exclusivity remain intact. A valid story quickload may rewind splashdown to First Wake; the menu displays either stage without granting Lyra.
- Native equipment automation extends an existing mandatory test with explicit refusal to execute any ship mode via this menu; native test registration remains 30 identities.

## Remaining full acceptance
- Actual Windows Unreal PIE interactive visual proof for both M and G, ten top-level pages, seven ship pages, button operation/focus/cursor, G toggling and M closing, title-screen exclusion, and correct page bounds at 1280x720 and 1920x1080.
- Verify equipment changes remain after switching tabs and cannot persist to save, and that both M and G are not active in Editor or null world.
- Verify story inspection flags update correctly when returning to the ship page, but do not show fictional ship instrument readings.
- Bind real gameplay inventory/skills/jobs/party progression, ship controls, crew assignments and upgrade resources **only after** exact source-of-truth owners exist. Ship configuration and Starbourne authority remain separate protected gates.
- Creator art review for cinematic materials, iconography, HUD typography, sound cues, controller/gamepad focus and accessibility, plus native D3D12 captures.

**Review-only / draft / no merge.**

## Native and portable acceptance updates

At implementation head 40aba94c6ab9db57f9417a4a9110afdd593c1f75, Windows UE 5.8.4 Win64 Editor build and the complete strict source-locked 30/30 native automation suite passed; checkout remained clean and original DefaultEngine.ini / DefaultInput.ini hashes were unchanged. Local retained receipt: unreal/Saved/MigrationEvidence/40aba94c6ab9-20261111T154137603Z-bd0d8071 (not a D3D12 visual/PIE acceptance).

Hosted source preflight discovered a portable test-doubles mismatch: the older F5/F9 handler compilation harness did not model the new EquipmentReviewMenu open-state predicate. The repair adds a menu-visibility double and proves actual QuickSave/QuickLoad C++ method bodies refuse operations while the RPG menu is open, without changing production gameplay guards. Windows MSVC ran 16 successful cases and rejected mutations bypassing the menu guard, the stale PIE save-ownership restriction, and both Shift+F5 protections. These portable results do not claim real disk writes or PIE UX proof. Revalidate full hosted CI and exact-head native status after any repair commit.

## Verified version-2 saved roster display (November 11 continuation)

The Status page may now optionally display **actual, validated HP / maximum HP, resource / maximum resource, Attack and Defense from the most recently successful First Wake SaveGame v2 load**. The runtime pawn retains a transient reference only when UTSTSSPersistence::LoadProgress has accepted the save and the story restore succeeded. Display projection then independently verifies the exact supported schema, structural validity, nonempty roster, stage match, and story beat/inspection-mask match, and requires every saved character ID to be available in the current First Wake stage. Lyra cannot appear before separate recruitment, including when a structurally valid historical save already contains Lyra. Reson/Aepex remain excluded from this slice. An old, incompatible or out-of-stage snapshot leaves the menu without saved stat values; the UI does not synthesize character HP or MP.

**Provenance:** These are explicitly labelled LAST-LOADED SAVE values, never live battle state or current HP/MP. Resource is generic in the current combat schema, not assumed to be MP. Level, XP, job and mastery are absent from SaveGame v2 and must not be invented.

Additional equipment UI affordances now distinguish actual reviewed item names, EQUIPPED vs OWNED/NOT EQUIPPED inventory slots and status-page reviewed gear bonuses. Provisional equipment bonuses are shown separately from saved combat attributes; they do not change saved or live battle stats.

The existing mandatory TSTSS.Equipment.PartySliceStageGate native automation has been extended to require a compatible actual UTSTSSSaveGame v2 object, positive safe snapshot projection, transactional output preservation, and negative cases for splashdown mismatches, unrecruited Lyra, unrelated recruitment status, future schema and malformed HP. This is source/native business-logic verification, NOT actual live combat telemetry or cinematic menu screenshot acceptance.

## Native UMG lifecycle finding (nonpromotion)

Exploratory test-only attempts to instantiate the in-game UMG menu through a headless Editor/NullRHI commandlet were **not accepted** as UI evidence. Direct NewObject initialization had no visual root; a disposable Editor PlayerController was correctly denied as non-local; a synthetic LocalPlayerContext did not initialize the root. These attempts were *never* treated as production/render/PIE passes. The exploratory headless widget-construction assertions were excluded from the existing 30-test native integrity suite because that suite has no real PIE local-player session. Existing native game logic, story, equipment and newly added saved-roster negative tests remain mandatory. The missing acceptance step is a **real, locally controlled PIE session** testing M/G, tab switching, keyboard/gamepad focus, cursor capture/close, active ship inspection state, saved-roster labels, equipment toggles, and screenshots. Do not promote the menu art or gameplay on source/NullRHI results alone.


## Native D3D12 game-client approval captures ? 2026-11-11

This review branch was launched **as an actual Win64 Unreal Engine 5.8.4 -game runtime** at /Game/TSTSS/Review/FirstWake_PreludeInteraction_V2, with M / G real input and mouse interactions. On Neontic, runtime LogRHI explicitly selected D3D12 with SM5 (Intel Iris Xe). Native game window client pixels were captured at 1280x720, not simulated or generated. The source-locked evidence package lives under unreal/Docs/ReviewEvidence/UnifiedMenu_20261111/, including six unretouched native PNGs, a four-screen montage derived solely from those frames, and SHA-256 manifest.

Verified visually/interactively: M opens status, sidebar and ship subpages switch, Ender owned review gear can be equipped/unequipped, Lyra remains unavailable, Starbourne unselectable, engineering reflects story inspection bits, full-review overlay hides and restores its own HUD and engine debug text. All currently active menu controls are nonshipping review artifacts. This is **approval evidence for navigation and draft UI styling**, NOT evidence of final 3D character fitting, ship rendering, persistent inventory or combat/skill unlocks. The underlying First Wake study scene has separate outstanding unbuilt lighting / cinematic quality; transparent data limitations were retained.

All 30 native test identities remain registered. Visual proof and controller/PIE acceptance are distinct; a separate full strict native suite at the final exact commit is still a gate.
