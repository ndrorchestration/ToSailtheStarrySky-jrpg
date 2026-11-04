"""Static safety/regression contract for separate coupled native pivot pilot."""
import ast
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"Tools"

class NativeCoupledPivotSource(unittest.TestCase):
    def source(self,name):
        p=TOOLS/name
        self.assertTrue(p.is_file())
        t=p.read_text(encoding="utf8")
        ast.parse(t,filename=str(p))
        return t

    def test_attaches_both_children_to_same_pivot_and_retains_hull(self):
        s=self.source("stage_aureate_v4_coupled_habitation_native_pilot.py")
        self.assertIn('bridge.attach_to_actor(pivot',s)
        self.assertIn('quarters.attach_to_actor(pivot',s)
        self.assertIn("get_attach_parent_actor()==pivot",s)
        self.assertIn('near(h0,v3(hull.get_actor_location()))',s)

    def test_real_rotation_preserves_distance_and_rolls_back_before_save(self):
        s=self.source("stage_aureate_v4_coupled_habitation_native_pilot.py")
        self.assertIn("Rotator(0,17.5,0)",s)
        self.assertIn('abs(distance(b1,q1)-d0)<.01',s)
        self.assertIn("Rotator(0,0,0)",s)
        self.assertLess(s.index("Rotator(0,0,0),False"),s.index("levels.save_current_level()"))
        self.assertIn("review_angle_restored",s)

    def test_new_sandbox_map_sha_gate_and_no_production_writes(self):
        s=self.source("stage_aureate_v4_coupled_habitation_native_pilot.py")
        self.assertIn("AUREATE_CINEMATIC_V4_REVIEW_ONLY",s)
        self.assertIn("16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40",s)
        self.assertIn("if OUT.exists():raise FileExistsError",s)
        self.assertIn("not lib.does_asset_exist(MAP)",s)
        self.assertIn("SOURCE_MAP",s)
        self.assertIn('req(digest(SOURCE_MAP)==SOURCE_SHA',s)

    def test_native_pilot_no_collision_or_story_approval(self):
        s=self.source("stage_aureate_v4_coupled_habitation_native_pilot.py")
        self.assertIn('"physical_clearance_proven":False',s)
        self.assertIn('"creator_pose_approved":False',s)
        self.assertIn('"starbourne_player_unlock":False',s)
        self.assertIn("set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)",s)
        self.assertNotIn("RequestForm(",s)

    def test_runner_uses_full_editor_with_strict_resource_guards(self):
        s=self.source("run_aureate_v4_coupled_habitation_native_pilot.py")
        for word in ("-ExecutePythonScript=","-NullRHI","ram_gib()<4.2",
                     "14*1024**3","proc.terminate()","proc.kill()",
                     "AureateCinematicV4Sandbox","NATIVE_COUPLED_PIVOT_PASS"):
            self.assertIn(word,s)
        self.assertNotIn("taskkill",s)
        self.assertNotIn("Stop-Process",s)

if __name__=="__main__":unittest.main()
