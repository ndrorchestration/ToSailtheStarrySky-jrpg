"""No real or approved PNGs committed. Synthetic source/reference rejection tests."""
import copy
import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from verify_ender_v5_private_face_candidates import verify_private_candidate, PREFERENCES

ROOT=Path(__file__).resolve().parent
POLICY=json.loads((ROOT/"ender_v5_reference_priority.json").read_text(encoding="utf-8"))

def chunk(typ,data):
    return struct.pack(">I",len(data))+typ+data+struct.pack(">I",zlib.crc32(typ+data)&0xffffffff)

def synthetic_png(width,height):
    signature=b"\x89PNG\r\n\x1a\n"
    ihdr=struct.pack(">IIBBBBB",width,height,8,2,0,0,0)
    pixels=b"".join(b"\x00"+bytes([125,143,167])*width for _ in range(height))
    return signature+chunk(b"IHDR",ihdr)+chunk(b"IDAT",zlib.compress(pixels))+chunk(b"IEND",b"")

class PrivateProposalQATests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)
        self.policy=copy.deepcopy(POLICY)
        self.proposal={
          "project":"To Sail the Starry Sky",
          "status":"CANDIDATE_2D_MARKS_NOT_REVIEWED",
          "landmark_names":"image-left/right, not anatomical handedness",
          "coordinate_system":"0-based original image pixels; x right, y down",
          "references":[],
          "guardrails":{
            "source_image_file_publicly_committed":False,
            "secondary_recent_shipdeck_photo_used_for_landmarks":False,
            "metahuman_3d_index_assigned":False,
            "creator_landmark_approval":False,
            "facial_sculpt_changed":False,
            "hair_color_resolved":False,
            "character_art_promoted":False,
          }
        }
        for i,(key,pref) in enumerate(PREFERENCES.items()):
            r=self.policy["earlier_face_reference_candidates"][i]
            blob=synthetic_png(320,320)
            (self.root/r["name"]).write_bytes(blob)
            sha=hashlib.sha256(blob).hexdigest()
            r["sha256"]=sha
            self.proposal["references"].append({
                "key":key,"file":r["name"],"sha256":sha,
                "dimensions":[320,320],"crop":[25,25,300,300],
                "preference":pref,
                "points":{
                    "eye_image_left":[110,115],
                    "eye_image_right":[170,122],
                    "nose_tip":[143,160],
                    "chin_point":[144,228],
                }
            })

    def check(self):
        return verify_private_candidate(self.proposal,self.root,self.policy)

    def test_three_sources_four_marks_no_approval(self):
        result=self.check()
        self.assertEqual(result["status"],"PRIVATE_2D_SOURCES_AND_CANDIDATE_GEOMETRY_VALID_ARTIST_HOLD")
        self.assertEqual(result["candidate_marks"],12)
        self.assertFalse(result["creator_face_selection_approved"])
        self.assertFalse(result["metahuman_index_mapping_approved"])
        self.assertTrue(all(not x["actual_point_coordinates_emitted"] for x in result["checks"]))

    def test_impostor_image_sha_rejected(self):
        r=self.proposal["references"][0]
        source=self.root/r["file"]
        b=bytearray(source.read_bytes());b[-8]^=0x01
        source.write_bytes(bytes(b))
        with self.assertRaisesRegex(ValueError,"SHA"):
            self.check()

    def test_selected_reference_or_secondary_authority_rejected(self):
        self.proposal["guardrails"]["secondary_recent_shipdeck_photo_used_for_landmarks"]=True
        with self.assertRaisesRegex(ValueError,"False approval"):
            self.check()
        self.proposal["guardrails"]["secondary_recent_shipdeck_photo_used_for_landmarks"]=False
        self.policy["creator_priority"]="MOST_RECENT_CAST"
        with self.assertRaises(ValueError):
            self.check()

    def test_fake_native_index_and_creator_review_rejected(self):
        self.proposal["guardrails"]["metahuman_3d_index_assigned"]=True
        with self.assertRaisesRegex(ValueError,"False approval"):
            self.check()
        self.proposal["guardrails"]["metahuman_3d_index_assigned"]=False
        self.proposal["status"]="ARTIST_APPROVED"
        with self.assertRaisesRegex(ValueError,"promoted"):
            self.check()

    def test_points_outside_crop_and_handedness_rejected(self):
        pts=self.proposal["references"][1]["points"]
        pts["nose_tip"]=[999,161]
        with self.assertRaisesRegex(ValueError,"outside"):
            self.check()
        pts["nose_tip"]=[143,160]
        pts["eye_image_left"]=[190,115]
        with self.assertRaisesRegex(ValueError,"eye order"):
            self.check()

    def test_malformed_crop_nose_chin_order_and_paths_rejected(self):
        r=self.proposal["references"][1]
        r["points"]["chin_point"]=[144,148]
        with self.assertRaisesRegex(ValueError,"vertical order"):
            self.check()
        r["points"]["chin_point"]=[144,228]
        r["crop"]=[25,25,800,300]
        with self.assertRaisesRegex(ValueError,"Crop"):
            self.check()
        r["crop"]=[25,25,300,300]
        r["dimensions"]=[123,320]
        with self.assertRaisesRegex(ValueError,"dimensions"):
            self.check()

    def test_no_raw_reference_data_in_public_policy(self):
        for entry in POLICY["proposal_points"]:
            self.assertIsNone(entry["image_x_px"])
            self.assertIsNone(entry["image_y_px"])
            self.assertIsNone(entry["native_index"])
            self.assertFalse(entry["artist_verified"])

if __name__=="__main__":
    unittest.main()
