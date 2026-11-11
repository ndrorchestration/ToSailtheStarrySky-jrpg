# TSTSS vertical slice — three-member equipment asset packet (2026-11-10)

## Plot authority and scope

- **First Wake / before splashdown:** Ender and Captain Ionia are the only available party members.
- **After the splashdown and Lyra's actual recruitment:** Lyra becomes available with her authored loadout.
- **Reson and Aepex are not playable or available in this vertical slice.** No default item ownership, equipment grant, or character-selection access is created for them.
- The broader five-member cast canon and Five Lights identities are not changed. This packet is limited to the early-game vertical slice.
- Ender's native profession is Harmonic Resonance Engineer; creator-selected slice combat job is Resonator. These identity/class gates are separate from equipment. No spell, class, mastery or Five Lights unlock follows from an item.

## Source 3D models (14 review-only GLB meshes)

| Member | Weapon | Armor / clothing | Accessory | Non-equippable scene/tool prop |
| --- | --- | --- | --- | --- |
| **Ender** | Original centered-leather-wrap, double-brass-ferrule fighting staff (preserved reviewed mesh; SHA-256 `0ceb1955…`) | Engineer's vest shell | Sealed aviator goggles | Harmonic calibration tool case |
| **Ionia** | Captain's saber (provisional) | Captain's coat shell | Earth compass | Chart case |
| **Lyra** | Water focus (provisional) | Travel coat shell | Water pendant | Healer's satchel |
| **Shared** | — | — | — | Restorative vial and resonance capacitor, decorative/quest props only |

The authoring generator `unreal/ArtSource/PartyEquipment/generate_party_equipment.py` creates individual meter-scale, Y-up glTF2 binary GLBs with separate material primitives, vertex normals, and glTF metallic/roughness PBR definitions. Every model has a SHA-256, dimensions, slot, owner, stage, and noncanonical state in `party_equipment_manifest.review.json`.

This is **authored low-to-mid complexity static 3D geometry** for editor inspection, blockout, proportions and loadout testing; it is **not** final AAA sculpting, cloth simulation, photogrammetric texturing, LODs, collisions, animation, IK sockets, approved rigging, or production character likeness. Armor/coats are standalone torso-shell preview models, not approved body-fitting wearables. The goggles require sealed facial-fit confirmation. All generated art is **creator_approved=false**.

## Review-only C++ equipment ledger wiring

The new `FTSTSSPartySliceReviewEquipment` stage gate returns only Ender and Ionia in `FirstWake`, and Ender, Ionia, Lyra in `AfterSplashdown`. It constructs explicitly requested in-memory test gear with weapon, armor, accessory slots and passes it to the existing `FTSTSSReviewEquipment::TryEquip` ownership/slot validation. The fixture does not mint persistent inventory, grant loot, update SaveGame, or spawn assets automatically.

- Opening fixture: **2 owners, 6 equipped instances**.
- Post-splashdown fixture: **3 owners, 9 equipped instances**.
- Prototype-only stat bonuses (not approved balance): Ender staff +3 ATK, vest +3 DEF, goggles +1 DEF; Ionia saber +2 ATK, coat +3 DEF, compass +1 DEF; Lyra focus +1 ATK, coat +2 DEF, pendant +1 DEF.
- Non-equippable props have no combat or consumable authority.
- The new mandatory native automation `TSTSS.Equipment.PartySliceStageGate` checks valid and invalid ownership, stage progression, excluded protagonists, atomicity, and use of the existing battle-start stat/weapon-class projection. It is not an in-game party UI or a runtime unlock.

## Reproduction and evidence levels

Source-only:
```powershell
python unreal/ArtSource/PartyEquipment/test_party_equipment_source.py -v
python unreal/Tools/test_automation_registry.py
python unreal/Tools/check_automation_registry.py
```

Static native import script: `unreal/ArtSource/PartyEquipment/native_import_party_equipment.py`. It only writes under `/Game/TSTSS/Review/PartyEquipment` and emits `Saved/PartyEquipmentReview/native_import_report.json`. The exact project path is guarded. Native asset import, asset-editor viewport review, socket/grip measurement, tested collision and native C++ automation must each have their **own evidence** before being claimed.

The Unreal 5.8 Editor build attempt on this worktree encountered `Unable to build while Live Coding is active` because another Editor session was running. Source test successes do not establish native compilation.

## Next admission gates

1. Imported static mesh `.uasset` source SHA and UE world-scale bounds checked (separate native import receipt).
2. Exact-head UE 5.8.4 UBT/UHT/MSVC build, mandatory native automation registration and pass including `TSTSS.Equipment.PartySliceStageGate`.
3. Disposable review level where Ender, Ionia and post-splashdown Lyra can be visually equipped; explicit mesh sockets, rig, skin/clipping, animated grips and equip/unequip verified.
4. Character creative approval for all provisional items, material texture polish, fit and lookdev.
5. Integrate through actual recruitment state, 3-active party UI, owned inventory and player-controlled gameplay; keep Lyra gated and Reson/Aepex excluded.

**Do not merge or represent this as approved, playable or release-ready without the missing evidence.**
