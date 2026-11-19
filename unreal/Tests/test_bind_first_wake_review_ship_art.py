"""Offline and mocked Unreal Editor preflights; NOT a native Unreal scene test."""
from __future__ import annotations

from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Tools"))
import bind_first_wake_review_ship_art as binding

WING=binding.WING_DIR+"AureateWake_Wing_Lookdev"
ROOT_ASSET=binding.SUPPORT_DIR+"AureateWake_RootSupport_Lookdev"


class FakeMesh:
    pass


class FakeShip:
    def __init__(self):
        self.attrs={"allow_orbiter_preview":False,"authored_wing_mesh":None,
                    "authored_root_support_mesh":None,"use_root_pivoted_wing_pose":False}
        self.refreshes=0
        self.raise_next=False

    def get_actor_label(self,create_if_none=False):
        return binding.SHIP_LABEL
    def get_wing_count(self):return 4
    def get_root_support_count(self):return 4
    def get_hydrofoil_count(self):return 2
    def is_transitioning(self):return False
    def get_current_form(self):return "AureateWakeForm.SKYBORNE"
    def get_editor_property(self,name):
        if name not in self.attrs:raise AttributeError(name)
        return self.attrs[name]
    def set_editor_property(self,name,value):
        if self.raise_next and name=="authored_root_support_mesh":
            self.raise_next=False
            raise RuntimeError("Simulated Editor setter error")
        self.attrs[name]=value
    def refresh_wing_meshes(self):self.refreshes+=1
    def refresh_root_supports(self):self.refreshes+=1


def fake_unreal(ship, *, world=binding.MAP, assets=True, other_actors=None):
    class Editor:
        pass
    class Actors:
        pass
    def subsystem(cls):
        if cls is Editor:
            return types.SimpleNamespace(get_editor_world=lambda:
                   types.SimpleNamespace(get_path_name=lambda: world+".FirstWake_Benchmark_V1"))
        return types.SimpleNamespace(get_all_level_actors=lambda:
               [ship]+list(other_actors or []))
    def load_asset(path):
        return FakeMesh() if assets and path in (WING,ROOT_ASSET) else None
    return types.SimpleNamespace(
        UnrealEditorSubsystem=Editor,EditorActorSubsystem=Actors,
        StaticMesh=FakeMesh,AureateWakePreviewActor=FakeShip,
        get_editor_subsystem=subsystem,load_asset=load_asset
    )


class ReviewShipBindContracts(unittest.TestCase):
    def test_only_explicit_review_folders(self):
        self.assertEqual(binding.validate_plan(WING,ROOT_ASSET)["expected_wings"],4)
        for alt in ("/Game/TSTSS/Production/Ship/Wing",
                    binding.WING_DIR+"../Stolen",
                    binding.WING_DIR+"Wing-Unsafe",
                    binding.WING_DIR+"Wing/Other", ""):
            with self.subTest(path=alt),self.assertRaises(binding.ShipReviewHold):
                binding.validate_plan(alt,ROOT_ASSET)
        with self.assertRaises(binding.ShipReviewHold):
            binding.validate_plan(WING,WING)

    def test_non_unreal_host_cannot_bind(self):
        with patch.dict(sys.modules,{"unreal":None}):
            with self.assertRaisesRegex(binding.ShipReviewHold,"Unreal Editor Python"):
                binding.bind_in_editor(binding.validate_plan(WING,ROOT_ASSET))

    def test_successful_editor_mock_changes_only_isolated_actor(self):
        ship=FakeShip()
        with patch.dict(sys.modules,{"unreal":fake_unreal(ship)}):
            result=binding.bind_in_editor(binding.validate_plan(WING,ROOT_ASSET))
        self.assertEqual(result["result"],"REVIEW_ACTOR_BOUND_UNSAVED")
        self.assertTrue(result["requires_manual_save"])
        self.assertIsInstance(ship.attrs["authored_wing_mesh"],FakeMesh)
        self.assertIsInstance(ship.attrs["authored_root_support_mesh"],FakeMesh)
        self.assertTrue(ship.attrs["use_root_pivoted_wing_pose"])
        self.assertEqual(ship.refreshes,2)
        self.assertFalse(ship.attrs["allow_orbiter_preview"])

    def test_refuses_non_review_world(self):
        ship=FakeShip()
        with patch.dict(sys.modules,{"unreal":fake_unreal(ship,world="/Game/TSTSS/Chapter01")}):
            with self.assertRaisesRegex(binding.ShipReviewHold,"outside"):
                binding.bind_in_editor(binding.validate_plan(WING,ROOT_ASSET))
        self.assertEqual(ship.refreshes,0)

    def test_refuses_missing_or_wrong_actor(self):
        ship=FakeShip()
        ship.get_actor_label=lambda *_:"OtherActor"
        with patch.dict(sys.modules,{"unreal":fake_unreal(ship)}):
            with self.assertRaisesRegex(binding.ShipReviewHold,"exactly one"):
                binding.bind_in_editor(binding.validate_plan(WING,ROOT_ASSET))
        self.assertEqual(ship.refreshes,0)

    def test_refuses_existing_asset_and_orbiter(self):
        for changed,value,fragment in (
            ("authored_wing_mesh",FakeMesh(),"Existing"),
            ("allow_orbiter_preview",True,"Orbiter"),
            ("use_root_pivoted_wing_pose",True,"Existing")):
            ship=FakeShip()
            ship.attrs[changed]=value
            with self.subTest(property=changed),patch.dict(sys.modules,{"unreal":fake_unreal(ship)}):
                with self.assertRaisesRegex(binding.ShipReviewHold,fragment):
                    binding.bind_in_editor(binding.validate_plan(WING,ROOT_ASSET))
            self.assertEqual(ship.refreshes,0)

    def test_refuses_nonexistent_static_mesh(self):
        ship=FakeShip()
        with patch.dict(sys.modules,{"unreal":fake_unreal(ship,assets=False)}):
            with self.assertRaisesRegex(binding.ShipReviewHold,"two distinct"):
                binding.bind_in_editor(binding.validate_plan(WING,ROOT_ASSET))
        self.assertEqual(ship.refreshes,0)

    def test_failure_rolls_back_original_properties(self):
        ship=FakeShip()
        ship.raise_next=True
        with patch.dict(sys.modules,{"unreal":fake_unreal(ship)}):
            with self.assertRaisesRegex(binding.ShipReviewHold,"restored"):
                binding.bind_in_editor(binding.validate_plan(WING,ROOT_ASSET))
        self.assertIsNone(ship.attrs["authored_wing_mesh"])
        self.assertIsNone(ship.attrs["authored_root_support_mesh"])
        self.assertFalse(ship.attrs["use_root_pivoted_wing_pose"])

    def test_tool_never_saves_or_spawns_gameplay(self):
        source=(ROOT/"Tools"/"bind_first_wake_review_ship_art.py").read_text()
        for unsafe in ("save_current_level(", "save_map(", "spawn_actor_from_class(",
                       "RequestForm(", "AdvanceTo(", "SeaContact(", "FlotationConfirmed("):
            self.assertNotIn(unsafe,source)
        self.assertIn("get_all_level_actors()",source)
        self.assertIn("get_editor_world()",source)
        self.assertIn("get_path_name()",source)


if __name__=="__main__":
    unittest.main()
