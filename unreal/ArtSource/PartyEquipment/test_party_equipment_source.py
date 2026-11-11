"""Source-only fail-closed checks for the EXACT authored review party assets.
Run: python unreal/ArtSource/PartyEquipment/test_party_equipment_source.py
Does not require Unreal; does not prove engine import or gameplay.
"""
import hashlib, json, struct, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
EXPECTED={
 "Ender":{"weapon","armor","accessory","utility"},
 "Ionia":{"weapon","armor","accessory","utility"},
 "Lyra":{"weapon","armor","accessory","utility"},
 "Shared":{"prop"}
}
class TestPartyEquipmentSource(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=json.loads((HERE/"party_equipment_manifest.review.json").read_text())
 def test_party_gate(self):
  m=self.manifest
  self.assertEqual(m["available_party"],["Ender","Ionia"])
  self.assertEqual(m["joins_post_splashdown"],["Lyra"])
  self.assertEqual(m["lyra_unlock_requires"],"LyraRecruited")
  self.assertEqual(m["excluded_party"],["Reson","Aepex"])
  self.assertFalse(m["automatic_item_grants"])
  self.assertFalse(m["creator_approved"])
 def test_inventory_is_three_party_only(self):
  entries=self.manifest["entries"]
  self.assertEqual(len(entries),14)
  self.assertEqual(len({i["id"] for i in entries}),14)
  for owner,slots in EXPECTED.items():
   got={i["slot"] for i in entries if i["owner"]==owner}
   self.assertEqual(got,slots,owner)
  for i in entries:
   self.assertNotIn(i["owner"],("Reson","Aepex"))
   self.assertEqual(i["review_availability_gate"],"LyraRecruited" if i["owner"]=="Lyra"
                    else "FirstWake" if i["owner"] in ("Ender","Ionia") else "scene_prop_only")
   self.assertEqual(i["stage"],"post_splashdown" if i["owner"]=="Lyra"
                    or i["id"]=="Shared.RestorativeVial" else "prelude")
   self.assertFalse(i["runtime_equippable"])
   self.assertFalse(i["creator_approved"])
   self.assertFalse(i["rig_attached"])
   self.assertFalse(i["collision_tested"])
 def test_geometry_hash_bounds_materials(self):
  for i in self.manifest["entries"]:
   with self.subTest(id=i["id"]):
    p=HERE/i["relative_path"]
    b=p.read_bytes()
    self.assertEqual(hashlib.sha256(b).hexdigest(),i["sha256"])
    self.assertEqual(b[:4],b"glTF")
    self.assertEqual(struct.unpack_from("<II",b,4),(2,len(b)))
    n,t=struct.unpack_from("<I4s",b,12)
    self.assertEqual(t,b"JSON")
    d=json.loads(b[20:20+n])
    self.assertFalse(d.get("skins"))
    self.assertFalse(d.get("animations"))
    self.assertFalse(d["extras"]["creator_approved"])
    self.assertEqual(len(d["meshes"]),1)
    self.assertGreaterEqual(len(d["meshes"][0]["primitives"]),1)
    for p in d["meshes"][0]["primitives"]:
     acc=d["accessors"][p["attributes"]["POSITION"]]
     self.assertEqual(len(acc["min"]),3)
     self.assertTrue(all(0.001 < i["bounds_m"][j][1]-i["bounds_m"][j][0] < 3
                  for j in range(3)))
 def test_ender_staff_provenance(self):
  i=next(x for x in self.manifest["entries"] if x["id"]=="Ender.ResonanceStaff")
  self.assertTrue(i["reused_prior_review_staff"])
  original=HERE/"Sources"/"Ender_DoubleFerrule_CenteredWrap_Staff_V1_NONCANONICAL.glb"
  self.assertEqual(hashlib.sha256(original.read_bytes()).hexdigest(),i["sha256"])
  self.assertEqual(i["sha256"],
     "0ceb1955bcc8053dc306f564bbe3a6647b36a3d9aa09f49fcff5752e7d89e307")
  self.assertTrue(1.70 < i["bounds_m"][1][1]-i["bounds_m"][1][0] < 1.75)

 def test_splashdown_does_not_equal_recruitment(self):
  root=HERE.parents[1]/"Source"/"ToSailTheStarrySky"
  header=(root/"Public"/"TSTSSPartySliceReviewEquipment.h").read_text(encoding="utf-8-sig")
  impl=(root/"Private"/"TSTSSPartySliceReviewEquipment.cpp").read_text(encoding="utf-8-sig")
  tests=(root/"Private"/"Tests"/"TSTSSPartySliceEquipmentTests.cpp").read_text(encoding="utf-8-sig")
  self.assertIn("AfterSplashdown",header)
  self.assertIn("LyraRecruited",header)
  self.assertIn('CharacterId == TEXT("Lyra")',impl)
  self.assertIn("Stage == ETSTSSPartySliceReviewStage::LyraRecruited",impl)
  self.assertIn("splashdown is not proof Lyra has joined",tests)
  self.assertIn("splashdown alone grants no Lyra equipment",tests)
  self.assertIn('After.EquippedByCharacter.Num(), 3',tests)
 def test_review_mount_is_allowlisted_and_nonpersistent(self):
  root=HERE.parents[1]/"Source"/"ToSailTheStarrySky"
  h=(root/"Public"/"TSTSSPartyGearReviewMountComponent.h").read_text(encoding="utf-8-sig")
  impl=(root/"Private"/"TSTSSPartyGearReviewMountComponent.cpp").read_text(encoding="utf-8-sig")
  self.assertIn("TryInitializeReviewDisplay",h)
  self.assertIn("TrySetReviewSlotEquipped",h)
  self.assertIn("TryAttachToSkeletalSocketsReview",h)
  self.assertIn("Rig->GetSkeletalMeshAsset()",impl)
  self.assertIn("Rig->DoesSocketExist(Sockets[Index])",impl)
  self.assertIn("FAttachmentTransformRules::SnapToTargetNotIncludingScale",impl)
  self.assertIn("PreviousTransforms[Index]",impl)
  self.assertIn("FTSTSSReviewEquipment::TryEquip(",impl)
  self.assertIn("IsMemberAvailable(Stage, CharacterId)",impl)
  self.assertIn("IsOwnedMount(GetOwner(), WeaponMount)",impl)
  self.assertIn("WeaponMount == ArmorMount",impl)
  self.assertIn("ReviewState = MoveTemp(Candidate)",impl)
  self.assertNotIn("SaveGame",impl)
  for i in self.manifest["entries"]:
   if i["slot"] in {"weapon","armor","accessory"}:
    self.assertIn('TEXT("'+i["id"].split(".")[1]+'")',impl,i["id"])
 def test_native_path_contract_for_review_mount(self):
  report=HERE.parents[1]/"Docs"/"PartyEquipment_NativeStaticImport_2026_11_10.report.json"
  entries=json.loads(report.read_text(encoding="utf-8"))["entries"]
  for i in entries:
   if i["owner"]=="Shared":continue
   owner,suffix=i["id"].split(".")
   asset=owner+"_"+suffix+"_REVIEW"
   expected="/Game/TSTSS/Review/PartyEquipment/"+owner+"/"+asset+"/StaticMeshes/"+asset+"."+asset
   self.assertEqual(i["mesh_path"],expected,i["id"])

 def test_ingame_review_menu_has_g_key_and_never_auto_recruits_lyra(self):
  unreal=HERE.parents[1]
  h=(unreal/"Source"/"ToSailTheStarrySky"/"Public"/"TSTSSPartyGearMenuReviewWidget.h").read_text(encoding="utf-8-sig")
  impl=(unreal/"Source"/"ToSailTheStarrySky"/"Private"/"TSTSSPartyGearMenuReviewWidget.cpp").read_text(encoding="utf-8-sig")
  pawn=(unreal/"Source"/"ToSailTheStarrySky"/"Private"/"TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8-sig")
  test=(unreal/"Source"/"ToSailTheStarrySky"/"Private"/"Tests"/"TSTSSPartySliceEquipmentTests.cpp").read_text(encoding="utf-8-sig")
  cfg=(unreal/"Config"/"DefaultInput.ini").read_text(encoding="utf-8-sig")
  self.assertIn('+ActionMappings=(ActionName="ReviewEquipment",Key=G)',cfg)
  self.assertIn("TryApplyReviewToggle",h)
  self.assertIn("FTSTSSReviewEquipment::TryEquip(",impl)
  self.assertIn("FTSTSSPartySliceReviewEquipment::IsMemberAvailable(",impl)
  self.assertIn("if (!Desired.IsNone()) return false;",impl)
  self.assertIn("TryBeginEquipmentReview",impl)
  self.assertIn("TryRefreshStoryStageReview",impl)
  self.assertIn("TryRefreshStoryStageReview(CurrentStage)",pawn)
  self.assertIn("const bool bWasPreviewStage",impl)
  self.assertIn("const bool bIsPreviewStage",impl)
  self.assertIn("RequestedStage == ETSTSSPartySliceReviewStage::FirstWake",impl)
  self.assertIn("RequestedStage == ETSTSSPartySliceReviewStage::AfterSplashdown",impl)
  self.assertIn("Stage",h)
  self.assertIn("FirstWakeState->IsChapterOneActOne()",pawn)
  self.assertIn("ETSTSSPartySliceReviewStage::AfterSplashdown",pawn)
  self.assertNotIn("ETSTSSPartySliceReviewStage::LyraRecruited",pawn)
  self.assertIn("cannot equip Lyra gear at splashdown",test)
  self.assertIn("review UI re-equips originally owned staff",test)
  self.assertIn("PC->SetInputMode(Mode)",pawn)
  self.assertIn("CloseReview",impl)
  self.assertIn("Save->IsStructurallyValid()",impl)
  self.assertIn("Save->PartyRoster",impl)
  self.assertNotIn("SaveProgress(",impl)
  self.assertNotIn("SaveGameToSlot(",impl)

 def test_unified_rpg_and_ship_console_contract(self):
  unreal=HERE.parents[1]
  cpp=(unreal/"Source"/"ToSailTheStarrySky"/"Private"/"TSTSSPartyGearMenuReviewWidget.cpp").read_text(encoding="utf-8")
  head=(unreal/"Source"/"ToSailTheStarrySky"/"Public"/"TSTSSPartyGearMenuReviewWidget.h").read_text(encoding="utf-8")
  pawn=(unreal/"Source"/"ToSailTheStarrySky"/"Private"/"TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
  test=(unreal/"Source"/"ToSailTheStarrySky"/"Private"/"Tests"/"TSTSSPartySliceEquipmentTests.cpp").read_text(encoding="utf-8")
  config=(unreal/"Config"/"DefaultInput.ini").read_text(encoding="utf-8")
  self.assertIn('+ActionMappings=(ActionName="ReviewRPGMenu",Key=M)',config)
  for page in ("Status","Inventory","Equipment","Magic","Skills","Jobs","Formation","Journal","Ship","System"):
   self.assertIn(page,head)
  for page in ("Overview","Engineering","Configurations","Crew","Navigation","Upgrades","Cargo"):
   self.assertIn(page,head)
  self.assertIn("IsShipConfigurationSelectableForReview",cpp)
  self.assertIn("ship menu may not execute an unauthorised mode change",test)
  self.assertIn("StoryReviewState->GetInspectionMask()",cpp)
  self.assertIn("StoryReviewState->GetReviewObjectiveText()",cpp)
  self.assertIn("ReviewState.OwnedInstances.GetKeys(Names)",cpp)
  self.assertIn("FTSTSSCombatData::ApprovedAffinity",cpp)
  self.assertIn("FTSTSSPartySliceReviewEquipment::IsMemberAvailable",cpp)
  self.assertIn("TogglePartyMenuReview",pawn)
  self.assertIn("TryBindFirstWakeStoryForReview",pawn)
  self.assertNotIn("ETSTSSPartySliceReviewStage::LyraRecruited",pawn)
  self.assertNotIn("AdvanceTo(",cpp)
  self.assertNotIn("SaveProgress(",cpp)

 def test_saved_party_status_displays_provenance_without_recruitment(self):
  unreal=HERE.parents[1]
  cpp=(unreal/"Source"/"ToSailTheStarrySky"/"Private"/"TSTSSPartyGearMenuReviewWidget.cpp").read_text(encoding="utf-8")
  pawn=(unreal/"Source"/"ToSailTheStarrySky"/"Private"/"TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
  test=(unreal/"Source"/"ToSailTheStarrySky"/"Private"/"Tests"/"TSTSSPartySliceEquipmentTests.cpp").read_text(encoding="utf-8")
  self.assertIn("TryProjectValidatedSavedRosterForReview",cpp)
  self.assertIn("bSavedAfterSplashdown",cpp)
  self.assertIn("FTSTSSPartySliceReviewEquipment::IsMemberAvailable",cpp)
  self.assertIn("GetCurrentBeat() != Save->FirstWakeBeat",cpp)
  self.assertIn("GetInspectionMask() != Save->InspectionMask",cpp)
  self.assertIn("SAVED HP %d/%d | RESOURCE %d/%d",cpp)
  self.assertIn("NOT live combat stats",cpp)
  self.assertIn("LastLoadedSaveSnapshotForReview",pawn)
  self.assertIn("TryBindLoadedSaveRosterForReview(",pawn)
  self.assertIn("no Lyra from saved roster at mere splashdown",test)
  self.assertIn("malformed HP cannot be shown as verified stats",test)
  self.assertNotIn("SaveProgress(",cpp)

if __name__=="__main__":unittest.main()
