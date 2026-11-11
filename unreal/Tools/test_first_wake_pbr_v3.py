"""Source-only and adversarial PBR lookdev/native-control tests; no Unreal claims."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest import mock
import zlib
sys.path.insert(0,str(Path(__file__).resolve().parent))

import generate_first_wake_pbr_textures_v3 as pbr
import plan_first_wake_material_lookdev_v3 as plan
import stage_first_wake_pbr_native_v3 as stage
import intake_first_wake_pbr_native_v3 as intake
import first_wake_cinematic_sign_policy_v3 as sign
import run_first_wake_pbr_v3_native as host
import verify_first_wake_pbr_v3_native as native_verify
import run_first_wake_pbr_v3_readback as independent

class Actor:
    def __init__(self,label):
        self.label=label;self.hidden=False;self.touches=0
    def get_actor_label(self):return self.label
    def set_actor_hidden_in_game(self,flag):
        self.hidden=bool(flag);self.touches+=1
    def is_hidden(self):return self.hidden

class TextSign(Actor):pass

class TestFirstWakePBR(unittest.TestCase):
    def test_original_material_roles_and_channels(self):
        self.assertEqual(10,len(pbr.ROLES))
        self.assertEqual(set(pbr.ROLES),set(plan.MATERIALS))
        self.assertEqual(("BaseColor","Normal","Roughness"),pbr.CHANNELS)
        self.assertEqual(512,pbr.DIM)
        self.assertEqual(30,len(list(pbr.OUT.glob("TX_FWV3_*.png"))))
        self.assertTrue(all(0<=i<=255 for _,r,m,_,s in pbr.ROLES.values()
                            for i in (r,m)))
        self.assertFalse(any("licensed" in s for s in pbr.ROLES))

    def test_material_source_png_manifest_all_sha_and_signature(self):
        manifest=json.loads((pbr.OUT/"manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(30,len(manifest["textures"]))
        self.assertEqual("SOURCE_TEXTURES_NOT_NATIVE_RENDERED",manifest["status"])
        self.assertFalse(manifest["contains_licensed_assets"])
        for row in manifest["textures"]:
            path=pbr.OUT/row["name"]
            with self.subTest(file=row["name"]):
                payload=path.read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(),row["sha256"])
                self.assertEqual(len(payload),row["bytes"])
                self.assertTrue(payload.startswith(b"\x89PNG\r\n\x1a\n"))
                self.assertEqual((512,512),struct.unpack_from(">II",payload,16))
                self.assertIn(row["channel"],pbr.CHANNELS)
                self.assertGreater(len(payload),5000)
                self.assertEqual(pbr.chunk(b"PING",b"test")[-4:],
                                 struct.pack(">I",zlib.crc32(b"PINGtest")))

    def test_invalid_source_role_is_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"Unknown"):
            pbr.bytes_for_role("Starbourne")
        with self.assertRaises(ValueError):
            pbr.encode_png(b"too short",3)
        with self.assertRaises(ValueError):
            pbr.encode_png(b"no",4)
        self.assertEqual(pbr.hashed(12,46,15),pbr.hashed(12,46,15))

    def test_stage_authored_detail_and_map_invariants(self):
        report=plan.validate_plan()
        self.assertEqual(84,len(plan.DETAILS))
        self.assertEqual(115,report["expected_original_actors"])
        self.assertEqual(stage.plan.BASE_SHA,
                         "837e537ab91339f56af006782c8e7dba9ac981d36eb800eb3b2a10c97661bbbc")
        self.assertFalse(report["hero_camera_reframed"])
        self.assertTrue(report["original_camera_untouched"])
        self.assertEqual(len(set(d.name for d in plan.DETAILS)),len(plan.DETAILS))
        self.assertTrue(all(abs(d.xyz[1])-50*d.scale[1]>=400 for d in plan.DETAILS))
        self.assertEqual(115+84+1,200)

    def test_material_replacements_are_only_known_visual_structures(self):
        self.assertEqual("quay_stone",stage.REPLACEMENTS[stage.FLOOR])
        self.assertEqual(18,len(stage.REPLACEMENTS))
        self.assertTrue(set(stage.REPLACEMENTS.values())<=set(pbr.ROLES))
        self.assertTrue(all("SIGN_" not in label for label in stage.REPLACEMENTS))
        self.assertTrue(all(not any(x in label for x in stage.plan.MILESTONES)
                            for label in stage.REPLACEMENTS))
        self.assertNotIn("WaterBeyondHarbor"," ".join(stage.REPLACEMENTS))
        self.assertTrue(all("Starbourne" not in k for k in stage.REPLACEMENTS))

    def test_sign_inventory_requires_exact_seven_labels_and_story_actors(self):
        names=[sign.SIGN_PREFIX+s for s in sign.MILESTONES]
        names += [sign.MILESTONE_PREFIX+s for s in sign.MILESTONES]
        self.assertEqual(tuple(names[:7]),sign.sign_inventory(names))
        for corrupted in (names[:-1],names[:-7],names+[names[0]],
                          names+["TSTSS_PRELUDE_REVIEW_SIGN_Unknown"]):
            with self.subTest(size=len(corrupted)):
                with self.assertRaisesRegex(RuntimeError,"HOLD"):
                    sign.sign_inventory(corrupted)

    def test_cinematic_sign_only_transient_no_milestone_hidden(self):
        originals=[Actor(sign.MILESTONE_PREFIX+s) for s in sign.MILESTONES]
        signs=[TextSign(sign.SIGN_PREFIX+s) for s in sign.MILESTONES]
        unreal=type("Unreal",(object,),{"TextRenderActor":TextSign})
        response=sign.suppress_transient_only(originals+signs,unreal)
        self.assertEqual(7,len(response["sign_labels"]))
        self.assertEqual(0,response["interaction_actors_hidden"])
        self.assertTrue(all(s.hidden and s.touches==1 for s in signs))
        self.assertTrue(all(not a.hidden and a.touches==0 for a in originals))
        with self.assertRaisesRegex(RuntimeError,"not a native"):
            sign.suppress_transient_only(originals+[Actor(s.get_actor_label())
                                                     for s in signs],unreal)

    def test_native_stage_requires_explicit_opt_in_and_isolated_world(self):
        self.assertEqual("TSTSS_VSliceLookdev_20261111",plan.ROOT_NAME)
        self.assertEqual("TSTSS_FIRST_WAKE_PBR_V3_EXPLICIT",stage.OPT_IN)
        self.assertNotEqual(plan.DEST_LEVEL,plan.BASE_LEVEL)
        self.assertNotEqual(plan.DEST_PATH,plan.BASE_PATH)
        self.assertEqual(30,len(pbr.ROLES)*len(pbr.CHANNELS))
        self.assertEqual("NoCollision",plan.validate_plan()["collision"])
        path=Path(__file__).with_name("stage_first_wake_pbr_native_v3.py")
        code=path.read_text(encoding="utf-8")
        self.assertNotIn("destroy_actor",code)
        self.assertNotIn("set_actor_hidden_in_game",code)
        self.assertNotIn("save_game",code)
        self.assertIn("original_floor_collision_preserved",code)
        self.assertIn("original_interaction_markers_preserved",code)

    def test_private_paths_no_restricted_config_or_escape(self):
        for bad in ("../user","unreal/../../data","C:/Users/private",
                    "unreal/Content/Starbourne_Sail.uasset",
                    "unreal/Content/Submersible.uasset"):
            with self.subTest(path=bad),self.assertRaises(RuntimeError):
                intake.safe(bad)
        self.assertEqual(321,intake.EXPECTED_COUNT)
        self.assertEqual("f47656774d5bb0f163cef550eba09577e2ab8aef",intake.INPUT_HEAD)

    def test_native_uv_link_uses_documented_texture_sample_pin(self):
        code=Path(__file__).with_name("stage_first_wake_pbr_native_v3.py").read_text(encoding="utf-8")
        self.assertIn('edit.connect_material_expressions(coord,"",sample,"UVs")',code)
        self.assertNotIn('edit.connect_material_expressions(coord,"",sample,"Coordinates")',code)

    def test_only_safe_native_host_windows(self):
        with mock.patch.object(host.sys,"platform","linux"):
            with self.assertRaisesRegex(RuntimeError,"Windows"):
                host.preflight()
        self.assertGreaterEqual(host.MIN_RAM_GIB,5)
        self.assertGreaterEqual(host.MIN_DISK_GIB,14)
        self.assertLessEqual(host.MAX_SECONDS,450)

    def test_independent_readback_requires_exact_200_actors(self):
        labels=[stage.DETAIL_PREFIX+d.name for d in plan.DETAILS]
        labels.append(stage.DETAIL_PREFIX+"PierReviewCamera")
        labels += ["TSTSS_PRELUDE_REVIEW_"+x for x in plan.MILESTONES]
        labels += [stage.SIGN_PREFIX+x for x in plan.MILESTONES]
        labels += ["InheritedActor_"+str(i) for i in range(115-14)]
        self.assertEqual(200,len(labels))
        self.assertTrue(native_verify.exact_inventory(labels,labels[:85]))
        for wrong in (labels[:-1],labels+["Starbourne_LockedPreview"]):
            with self.assertRaisesRegex(RuntimeError,"HOLD"):
                native_verify.exact_inventory(wrong,labels[:85])

    def test_independent_host_rejects_false_stage_receipts(self):
        native={"status":"NATIVE_PBR_V3_MAP_SAVED_PENDING_INDEPENDENT_READBACK",
                "new_map_sha256":"map","parent_map_sha256":plan.BASE_SHA,
                "saved_actor_count":200,"new_actors":85,"native_material_assets":10,
                "native_texture_assets":30,"original_floor_collision_preserved":True,
                "original_interaction_markers_preserved":True}
        original={"status":"NATIVE_PBR_V3_MAP_SAVED_PENDING_INDEPENDENT_READBACK",
                  "new_map_sha256":"map","source_head":"head","native_exit_code":0}
        for key in ("source_head_preserved","parent_map_preserved",
                    "original_assembly_preserved","protected_configs_preserved"):
            original[key]=True
        self.assertTrue(independent.proof_check(original,native,"head","map"))
        for field,bad in (("saved_actor_count",199),("new_actors",84),
                          ("native_material_assets",9),("native_texture_assets",29),
                          ("original_floor_collision_preserved",False)):
            with self.subTest(field=field),self.assertRaisesRegex(RuntimeError,"HOLD"):
                independent.proof_check(original,dict(native,**{field:bad}),"head","map")
        with self.assertRaisesRegex(RuntimeError,"HOLD"):
            independent.proof_check(dict(original,native_exit_code=1),native,"head","map")

    def test_independent_receipt_rejects_false_pie_and_art(self):
        good={"status":native_verify.STATUS,
              "derived_world_sha256":"map","actors":200,
              "original_actors_inherited":115,"new_visual_only_mesh_actors":84,
              "new_camera_count":1,"materials_replaced_on_inherited_actors":18,
              "native_material_assets_reloaded":10,"native_texture_assets_reloaded":30,
              "preserved_interactions":list(plan.MILESTONES),
              "preserved_signs":[stage.SIGN_PREFIX+s for s in plan.MILESTONES],
              "original_floor_collision_verified":True,
              "original_floor_geometry_verified":True,
              "new_detail_collision_disabled":True,"gpu_render_verified":False,
              "pie_verified":False,"art_approved":False,
              "physics_splashdown_verified":False}
        self.assertTrue(independent.receipt_check(good,"map"))
        for key,bad in (("actors",199),("new_visual_only_mesh_actors",83),
                        ("native_texture_assets_reloaded",29),
                        ("pie_verified",True),("art_approved",True),
                        ("physics_splashdown_verified",True)):
            with self.subTest(key=key),self.assertRaisesRegex(RuntimeError,"HOLD"):
                independent.receipt_check(dict(good,**{key:bad}),"map")

    def test_png_semantic_pixels_independent_of_deflate_encoding(self):
        filename=pbr.OUT/"TX_FWV3_quay_stone_BaseColor.png"
        original=filename.read_bytes()
        raw,count=pbr.raw_png_pixels(original)
        self.assertEqual(3,count)
        self.assertEqual(512*512*3,len(raw))
        scan=b"".join(b"\x00"+raw[y*512*3:(y+1)*512*3]
                      for y in range(512))
        # Deliberately use a different zlib level: source PNG binary hashes
        # differ while image pixel data are still exactly identical.
        packed=(b"\x89PNG\r\n\x1a\n"+
                pbr.chunk(b"IHDR",struct.pack(">IIBBBBB",512,512,8,2,0,0,0))+
                pbr.chunk(b"IDAT",zlib.compress(scan,0))+
                pbr.chunk(b"IEND",b""))
        self.assertNotEqual(original,packed)
        self.assertEqual(raw,pbr.raw_png_pixels(packed)[0])
        damaged=bytearray(packed)
        damaged[50]^=1
        with self.assertRaisesRegex(RuntimeError,"CRC"):
            pbr.raw_png_pixels(damaged)

    def test_source_manifest_is_reproducibly_proven(self):
        # Expensive deterministic byte regeneration is done by --verify,
        # but this validation runs only once across the focused local suite.
        result=stage.validate_source()
        self.assertEqual("PBR_V3_SOURCE_PLAN_VALID_NOT_NATIVE",result["status"])
        self.assertEqual(85,result["expected_new_actor_count"])
        self.assertFalse(result["native_materials_imported"])
        self.assertFalse(result["gpu_visual_reviewed"])
        self.assertFalse(result["art_approved"])

if __name__=="__main__":
    unittest.main()
