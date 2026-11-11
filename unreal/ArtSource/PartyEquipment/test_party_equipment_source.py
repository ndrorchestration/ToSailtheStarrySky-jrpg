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
  self.assertEqual(i["sha256"],
     "0ceb1955bcc8053dc306f564bbe3a6647b36a3d9aa09f49fcff5752e7d89e307")
  self.assertTrue(1.70 < i["bounds_m"][1][1]-i["bounds_m"][1][0] < 1.75)
if __name__=="__main__":unittest.main()
