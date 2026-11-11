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
