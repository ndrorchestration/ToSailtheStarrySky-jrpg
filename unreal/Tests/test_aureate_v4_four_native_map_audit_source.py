"""Safety audit of read-only UE four-scene checker and host runner (source only)."""
import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"Tools"
class FourMapAuditSource(unittest.TestCase):
    def read(self,file):
        p=TOOLS/file
        s=p.read_text(encoding="utf8")
        ast.parse(s,filename=str(p))
        return s

    def test_engine_scene_sha_bound_on_all_forms(self):
        s=self.read("audit_aureate_v4_four_native_maps_readonly.py")
        for form in ("Skybourne","Seabourne","Submersible","Starbourne"):
            self.assertIn(form,s)
        for sha in ("16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40",
                    "b0b0587783197b2eff4a3e820fb49a52ac70edbbc9519a8cdbceee470edc955a",
                    "815e235aae6abef0e9a816bd8c9d01a13b4441bd81538763d2424e799e925f35",
                    "953bb2aaca0db194bdd871229cdb13245c59ceab19cf0f8cbc44a802c01e0e00"):
            self.assertIn(sha,s)
        self.assertIn("checksum(file)==MAP_SHA[form]",s)

    def test_shared_bridge_quarters_and_four_wing_identities(self):
        s=self.read("audit_aureate_v4_four_native_maps_readonly.py")
        for text in ("FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD",
                     "CENTRAL_LIVING_QUARTERS_PROXY","FORWARD_GLASS_GEODESIC_BRIDGE_PROXY",
                     "SHARED_PEARL_HULL_PROXY"):
            self.assertIn(text,s)
        self.assertIn("shared_core_matches_across_forms",s)
        self.assertIn("get_all_level_actors()",s)
        self.assertIn("FOUR_MAP_READONLY_NATIVE_AUDIT_PASS",s)

    def test_marine_and_private_starbourne_negative_controls(self):
        s=self.read("audit_aureate_v4_four_native_maps_readonly.py")
        self.assertIn("HYDROFOIL_",s)
        self.assertIn("SUBMERSIBLE_V4_LIGHT_RAIL",s)
        self.assertIn("PRIVATE_STATIC_STARB_SAIL_ID_",s)
        self.assertIn("starbourne_player_unlocked",s)
        self.assertIn("bridge_quarters_rotation_proven",s)

    def test_no_ue_scene_write_or_actor_mutation(self):
        s=self.read("audit_aureate_v4_four_native_maps_readonly.py")
        for banned in ("save_current_level(", "spawn_actor_from_class(", "destroy_actor(",
                       "set_actor_location(", "set_actor_rotation(", "RequestForm(",
                       "unreal.AssetToolsHelpers.get_asset_tools()"):
            self.assertNotIn(banned,s)

    def test_resource_guard_and_only_owned_process(self):
        s=self.read("run_aureate_v4_four_map_native_readonly_audit.py")
        for text in ("-ExecutePythonScript=","-NullRHI","ram_gib()<4.2",
                     "14*1024**3","process.terminate()","process.kill()"):
            self.assertIn(text,s)
        self.assertNotIn("Stop-Process",s)
        self.assertNotIn("taskkill",s)

if __name__=="__main__":unittest.main()
