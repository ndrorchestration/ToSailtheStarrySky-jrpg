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

The authoring generator `unreal/ArtSource/PartyEquipment/generate_party_equipment.py` creates individual meter-scale, Y-up glTF2 binary GLBs with separate material primitives, vertex normals, and glTF metallic/roughness PBR definitions. Every model has a SHA-256, dimensions, slot, owner, stage, and noncanonical state in `party_equipment_manifest.review.json`. The preserved original staff GLB is independently retained in `Sources/` with a required SHA-256; a clean-room regeneration from this tracked source was executed and reproduced **all 14 GLB hashes plus the exact manifest bytes**.

This is **authored low-to-mid complexity static 3D geometry** for editor inspection, blockout, proportions and loadout testing; it is **not** final AAA sculpting, cloth simulation, photogrammetric texturing, LODs, collisions, animation, IK sockets, approved rigging, or production character likeness. Armor/coats are standalone torso-shell preview models, not approved body-fitting wearables. The goggles require sealed facial-fit confirmation. All generated art is **creator_approved=false**.

## Review-only C++ equipment ledger wiring

The review stage gate admits Ender and Ionia in FirstWake and AfterSplashdown. Lyra is admitted ONLY at the separate LyraRecruited stage, never on splashdown alone.

- Opening fixture: **2 owners, 6 equipped instances**.
- After-Lyra-recruitment fixture: **3 owners, 9 equipped instances**. Immediate post-splashdown (before recruitment) remains two owners and six equipped instances.
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

Native static import script: `unreal/ArtSource/PartyEquipment/native_import_party_equipment.py`. Its direct target-project route is explicitly guarded; during the concurrent Live Coding blocker, a separate **Unreal 5.8.4 content-only sandbox** at `C:\TSTSS_PartyEquipmentContentQA_20261110` was used by copying the script and replacing only the expected isolated root and external source manifest path. The script imported all **14 of 14** reviewed static meshes at `/Game/TSTSS/Review/PartyEquipment`, validated their real Unreal dimensions/material slots, and emitted status `NATIVE_STATIC_MESH_IMPORT_PASS_REVIEW_ONLY`. Its unaltered report is tracked as `unreal/Docs/PartyEquipment_NativeStaticImport_2026_11_10.report.json`.

The 84 native `.uasset` files (14 meshes plus generated material assets; 6,463,462 bytes) were then copied into this branch's **otherwise empty, isolated** `unreal/Content/TSTSS/Review/PartyEquipment` directory; all 84 source-vs-target hashes matched. Native assets were created by genuine UE 5.8.4 static import, not an invented `uasset` conversion. The C++ target project has **not** loaded or PIE-tested these assets: **content-only sandbox native import is narrower than a successful game-target integration.**

A content-only native **showroom** level was then authored via `native_build_gallery_review.py` and **saved** at `/Game/TSTSS/Review/PartyEquipment/TSTSS_ThreePartyGearGallery_REVIEW`: 14 StaticMesh actors (four per party member plus two shared props), 14 review pedestals, key/fill light actors and owner/item actor labels. The source `.umap` was SHA-256 matched to the isolated target worktree copy. Native headless report status `NATIVE_REVIEW_GALLERY_MAP_PASS_NO_VISUAL_PROOF` is tracked in `unreal/Docs/PartyEquipment_NativeGallery_2026_11_10.report.json`. This is **NOT** a character rig-fitting level or proof of visual quality, hand sockets, pickup interactions, recruitment story binding, real UI, combat activation, or gameplay.

The initial target C++ build was blocked by an active Live Coding session. A subsequent isolated Windows UE 5.8.4 UBT/UHT build succeeded. Full native automation execution, rig fitting and visual acceptance remain separate gates.

## Next admission gates

1. Open the copied `.uasset` meshes and the saved gallery map in the **actual C++ game project**, inspect visuals with D3D12 RHI and capture real rendered screenshots; source-only/native content sandbox results are not target-gameproof.
2. Exact-head UE 5.8.4 UBT/UHT/MSVC build, mandatory native automation registration and pass including `TSTSS.Equipment.PartySliceStageGate`.
3. Add a separate gameplay review level where Ender, Ionia and post-splashdown Lyra can be actually equipped; verify explicit mesh sockets, rig, skin/clipping, animated grips and equip/unequip.
4. Character creative approval for all provisional items, material texture polish, fit and lookdev.
5. Integrate through actual recruitment state, 3-active party UI, owned inventory and player-controlled gameplay; keep Lyra gated and Reson/Aepex excluded.

**Do not merge or represent this as approved, playable or release-ready without the missing evidence.**

## Continued integration ? separate recruitment and native mount interfaces

The authored GLB manifest retains post_splashdown as an ASSET CHRONOLOGY TAG, not evidence that Lyra was recruited. It now includes lyra_unlock_requires: LyraRecruited, and an explicit review_availability_gate on each entry. Regeneration must reproduce the manifest fields and all 14 existing GLB hashes.

The developer-review-only UTSTSSPartyGearReviewMountComponent is a Blueprint-callable bridge between the atomic gear ledger and three caller-owned native UStaticMeshComponent mounts (weapon, armor, accessory). The caller authors the physical mount placements. The component rejects excluded characters, Lyra before explicit review recruitment, duplicate/foreign-owner components, missing native assets and failed ledger swaps before mutating the view. TrySetReviewSlotEquipped swaps both the transient ledger and native mounted mesh. It does not mint items, advance the plot, unlock abilities or persist SaveGame.

No skeletal rig or socket names are presumed: exact weapon grips, cloth and goggles attachment points must be supplied and visually verified on the actual approved character rigs. This component does not force loose torso-shell study meshes onto an unapproved player body.

The existing mandatory TSTSS.Equipment.PartySliceStageGate Editor automation has been extended to cover splashdown versus recruitment, native loading of the nine wearable mesh packages and a disposable actor-based mount / equip / unequip / denied-access test. These new assertions must be executed under UE 5.8.4 and reported SUCCESS before dynamic behavior is called verified. Seven engine-free checks independently cover geometry, source provenance, stage gating, asset allowlists and Unreal import path consistency.

Remaining: exact-head native test report; owner and story-state wiring to a player UI; actual skeleton/socket fit and cinematics; D3D12 screenshots; animation; combat; explicit creator art approval. This review-only component is not a shipping gameplay feature.

## Socket-ready integration checkpoint (2026-11-11 UTC)

A second review-only entry point now accepts an explicit real SkeletalMeshComponent and three existing distinct sockets (weapon, armor, accessory). It checks actual skeletal mesh presence, same-actor ownership, registered views, socket existence and available character stage before parenting; it refuses static-only character candidates. Actor attachment state is captured for rollback if a native attach fails. The mandatory UE equipment automation has three new negative cases denying absent rigs and duplicate socket names. A UE 5.8.4 Win64 Editor build **succeeded** for these source changes; exact-head test execution is still a separate receipt.

Source audit of available prior Ender/Ionia/Lyra cast candidate GLBs found 0 skins and 0 animations for all three. Consequently this adapter cannot yet be claimed as final character fitting, nor as playable equipment. Detailed status: PARTY_EQUIPMENT_RIG_READINESS_2026_11_10.md.

An earlier clean-head strict native verification attempt executed 30/30 named tests successfully but did not satisfy its source-custody invariant because UE auto-wrote tracked config. The config changes were restored; a rerun then failed the mandatory free-disk preflight. The native test report is preserved as a diagnostic, not an accepted strict gate: PartyEquipment_ThirtyNativeTests_Diagnostic_2026_11_10.report.json.
