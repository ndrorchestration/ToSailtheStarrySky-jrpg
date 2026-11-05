"""Pure-Python guards for noncanonical First Wake Prelude review staging."""
import ast
from pathlib import Path
import tempfile
import unittest
import build_first_wake_prelude_interaction as first


class PreludeReviewLayoutTests(unittest.TestCase):
    def test_first_three_story_events_and_engineering_order(self):
        plan = first.validate_plan()
        self.assertEqual(plan["status"], "REVIEW_ONLY_TRAVERSABLE_PRELUDE_NO_GAMEPLAY_PROOF")
        self.assertEqual([s["milestone"] for s in plan["stops"] if s["milestone"]],
                         ["FlyerDiscovered", "IoniaHired", "BoardedAureateWake",
                          "EngineeringChecked"])

    def test_three_distinct_inspections_before_engineering_approval(self):
        plan = first.validate_plan()
        stations = [i for i,s in enumerate(plan["stops"]) if s["inspection"]]
        self.assertEqual([plan["stops"][i]["inspection"] for i in stations],
                         ["Lift", "Pressure", "Reserve"])
        self.assertTrue(all(i < len(plan["stops"]) - 1 for i in stations))

    def test_no_fake_splashdown_recruitment_or_orbiter(self):
        plan=first.validate_plan()
        for flag in ("water_physics_events_issued","launch_progression_issued",
                     "canon_cast_art_present","automatic_party_recruitment",
                     "orbiter_unlocked","production_map_modified",
                     "approved_gameplay"):
            self.assertIs(plan[flag],False)
        self.assertEqual(plan["map"], "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2")
        names=" ".join(s["label"] for s in plan["stops"]).lower()
        for prohibited in ("lyra","talen","reson","aepex","orbiter","splashdown"):
            self.assertNotIn(prohibited,names)

    def test_player_spawn_and_increasing_route_x(self):
        starts=[s.x for s in first.STOPS]
        self.assertTrue(all(a < b for a,b in zip(starts,starts[1:])))
        self.assertLess(first.PLAYER_SPAWN[0],starts[0])
        self.assertGreater(starts[0]-first.PLAYER_SPAWN[0], 250)

    def test_only_explicit_disposable_project_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            good=Path(tmp)/first.REVIEW_ONLY_PROJECT_PARENT/"unreal"
            good.mkdir(parents=True)
            self.assertEqual(first.assert_disposable_project(str(good)),good.resolve())
            for bad in (Path(tmp)/"production"/"unreal", Path(tmp)/"unreal", good.parent):
                with self.subTest(bad=bad),self.assertRaises(RuntimeError):
                    first.assert_disposable_project(str(bad))

    def test_wrong_order_fails_closed_without_mutation(self):
        old=first.STOPS
        try:
            first.STOPS=tuple(reversed(old))
            with self.assertRaises(ValueError):
                first.validate_plan()
        finally:
            first.STOPS=old

    def test_missing_engineering_stop_fails_closed(self):
        old=first.STOPS
        try:
            first.STOPS=old[:-1]
            with self.assertRaises(ValueError):
                first.validate_plan()
        finally:
            first.STOPS=old

    def test_physics_story_beats_do_not_enter_authoring_plan(self):
        source=Path(first.__file__).read_text(encoding="utf-8")
        self.assertNotIn("advance_water_beat",source.lower())
        self.assertIn("Ocean_VISUAL_ONLY_NO_BUOYANCY",source)
        self.assertIn("set_collision_enabled",source)
        self.assertIn('set_collision_profile_name("BlockAll" if collision else "NoCollision")',source)
        self.assertIn("save_map(world, REVIEW_MAP)",source)

    def test_no_overwrite_existing_map_or_savegame(self):
        source=Path(first.__file__).read_text(encoding="utf-8")
        self.assertIn("does_asset_exist(REVIEW_MAP)",source)
        self.assertIn("get_dirty_map_packages()",source)
        self.assertIn("Review staging receipt exists: refuse overwrite",source)
        for forbidden in ("SaveGameToSlot","LoadGameFromSlot",
                          "EditorAssetLibrary.delete_asset","destroy_actor("):
            self.assertNotIn(forbidden,source)

    def test_rotators_have_named_axes(self):
        tree=ast.parse(Path(first.__file__).read_text(encoding="utf-8"))
        calls=[node for node in ast.walk(tree)
               if isinstance(node,ast.Call) and
               isinstance(node.func,ast.Attribute) and
               node.func.attr=="Rotator"]
        self.assertGreaterEqual(len(calls),2)
        for call in calls:
            self.assertEqual(call.args,[])
            self.assertEqual({k.arg for k in call.keywords},{"pitch","yaw","roll"})

if __name__=="__main__":
    unittest.main()
