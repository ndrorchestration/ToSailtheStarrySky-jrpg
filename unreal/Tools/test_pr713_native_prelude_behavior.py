"""Behavioral stand-ins for the actual Prelude V2 Editor map-checking function.

Calls verify_pr713_native_prelude_map.check_native() unchanged while replacing
*only* Unreal's Python bridge with isolated in-memory objects. This does not
launch UE, run gameplay, render a scene, or change a SaveGame. Both the
acceptance path and distinct fail-closed paths are exercised here.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import sys

import verify_pr713_native_prelude_map as qa


class Mesh:
    def __init__(self, collision="QueryAndPhysics", profile="BlockAll"):
        self.collision = collision
        self.profile = profile

    def get_collision_enabled(self):
        return self.collision

    def get_collision_profile_name(self):
        return self.profile


class Actor:
    def __init__(self, label, mesh=None, pos=(0, 0, 0)):
        self.label = label
        self.mesh = mesh
        self.pos = pos

    def get_actor_label(self):
        return self.label

    def get_component_by_class(self, cls):
        return self.mesh if isinstance(self.mesh, cls) else None

    def get_actor_location(self):
        return SimpleNamespace(x=self.pos[0], y=self.pos[1], z=self.pos[2])


class PlayerStart(Actor):
    pass


class StoryState:
    """Small deterministic double of the documented native C++ state machine."""

    def __init__(self):
        self.started = False
        self.stage = "Unstarted"
        self.mask = 0
        self.force_chapter = False
        self.initial_objective = "Find Ionia's flyer"

    def get_review_objective_text(self):
        if not self.started:
            return self.initial_objective
        if self.stage == "FlyerDiscovery":
            return "Speak with Captain Ionia"
        if self.stage == "IoniaHiring":
            return "Board the Aureate Wake"
        if self.stage == "AureateBoarding":
            for bit, label in (
                (1, "Inspect the levitation lift"),
                (2, "Inspect the pressure systems"),
                (4, "Inspect the reserve systems"),
            ):
                if not self.mask & bit:
                    return label
            return "Complete engineering signoff"
        if self.stage == "EngineeringApproval":
            return "Prepare for the First Wake launch"
        return "Unknown"

    def get_inspection_mask(self):
        return self.mask

    def is_chapter_one_act_one(self):
        return self.force_chapter


class Milestone(Actor):
    def __init__(self, label, name, station=False, mesh=None):
        super().__init__(label, mesh or Mesh())
        self.name = name
        self.station = station
        self.accept_illegal = False
        self.accept_duplicate = False
        self.force_failure = False

    def get_editor_property(self, name):
        if name == "is_inspection_station":
            return self.station
        raise AssertionError("Unexpected property requested: " + name)

    def try_activate(self, state):
        if self.force_failure:
            return False
        if self.name in ("LiftStation", "PressureStation", "ReserveStation"):
            if not state.started or state.stage != "AureateBoarding":
                return self.accept_illegal
            bit = {"LiftStation": 1, "PressureStation": 2, "ReserveStation": 4}[self.name]
            if state.mask & bit:
                return self.accept_duplicate
            state.mask |= bit
            return True
        if self.name == "FlyerDiscovery":
            if state.started:
                return self.accept_illegal
            state.started, state.stage = True, self.name
            return True
        predecessor = {
            "IoniaHiring": "FlyerDiscovery",
            "AureateBoarding": "IoniaHiring",
            "EngineeringApproval": "AureateBoarding",
        }[self.name]
        if not state.started or state.stage != predecessor:
            return self.accept_illegal
        if self.name == "EngineeringApproval" and state.mask != 7:
            return self.accept_illegal
        state.stage = self.name
        return True


class ModeDefault:
    def __init__(self):
        self.pawn_name = "TSTSSExplorerCharacter"

    def get_editor_property(self, prop):
        if prop != "default_pawn_class":
            raise AssertionError(prop)
        return self.pawn_name


class FakeEditor:
    def __init__(self):
        self.version = "5.8.4"
        self.map_ok = True
        self.subsystem_ok = True
        self.mode = ModeDefault()
        self.new_state = StoryState
        self.actors = []
        self.milestones = {}
        for label, _, station in qa.STOP_SPECS:
            name = qa.LABEL_PREFIX + label
            item = Milestone(name, label, bool(station))
            self.actors.append(item)
            self.milestones[label] = item
        self.actors.extend([
            PlayerStart(qa.LABEL_PREFIX + "PlayerStart_Ender_REVIEW_PROXY",
                        pos=(0, 0, 0)),
            Actor(qa.LABEL_PREFIX + "Harbor_TraversalFloor",
                  mesh=Mesh("QueryAndPhysics")),
            Actor(qa.LABEL_PREFIX + "Ocean_VISUAL_ONLY_NO_BUOYANCY",
                  mesh=Mesh("NoCollision", "NoCollision")),
        ])
        self.milestones["FlyerDiscovery"].pos = (200, 0, 0)

    def actor(self, suffix):
        return next(a for a in self.actors
                    if a.label == qa.LABEL_PREFIX + suffix)

    @contextmanager
    def native_bridge(self):
        owner = self

        class SystemLibrary:
            @staticmethod
            def get_engine_version():
                return owner.version

        class Loading:
            @staticmethod
            def load_map(map_name):
                if map_name != qa.MAP_PACKAGE:
                    raise AssertionError("Wrong map package used")
                return object() if owner.map_ok else None

        class EditorActorSubsystem:
            def get_all_level_actors(self):
                return owner.actors

        def get_editor_subsystem(cls):
            return cls() if owner.subsystem_ok else None

        def new_object(cls):
            return owner.new_state()

        fake = SimpleNamespace(
            SystemLibrary=SystemLibrary,
            EditorLoadingAndSavingUtils=Loading,
            EditorActorSubsystem=EditorActorSubsystem,
            TSTSSMilestoneActor=Milestone,
            StaticMeshComponent=Mesh,
            PlayerStart=PlayerStart,
            TSTSSGameMode=ModeDefault,
            TSTSSFirstWakeState=StoryState,
            CollisionEnabled=SimpleNamespace(NO_COLLISION="NoCollision",
                                              QUERY_AND_PHYSICS="QueryAndPhysics"),
            get_editor_subsystem=get_editor_subsystem,
            get_default_object=lambda cls: owner.mode,
            new_object=new_object,
        )
        with patch.dict(sys.modules, {"unreal": fake}):
            yield


class RealMapCheckerBehaviorTests(TestCase):
    def setUp(self):
        self.fake = FakeEditor()

    def run_checker(self):
        with self.fake.native_bridge():
            return qa.check_native(Path("/disposable/test/unreal"), {})

    def must_fail(self, expected):
        with self.assertRaisesRegex(RuntimeError, expected):
            self.run_checker()

    def test_valid_deterministic_seven_actor_story_review(self):
        report = self.run_checker()
        self.assertEqual(report["native_milestone_actor_count"], 7)
        self.assertEqual(report["engineering_inspection_mask"], 7)
        self.assertTrue(report["real_actor_ordered_story_acceptance"])
        self.assertEqual(report["spawn_to_flyer_actor_origin_cm"], 200.0)
        for field in ("actual_pie_player_input_tested",
                      "actual_savegame_disk_roundtrip_tested",
                      "native_collision_line_trace_tested",
                      "render_or_water_physics_approved",
                      "character_or_ship_art_approved",
                      "chapter_one_act_one"):
            self.assertFalse(report[field], field)

    def test_wrong_engine_patch_refused(self):
        self.fake.version = "5.8.5"
        self.must_fail("not UE 5.8.4")

    def test_missing_map_refused(self):
        self.fake.map_ok = False
        self.must_fail("cannot load")

    def test_editor_actor_subsystem_missing_refused(self):
        self.fake.subsystem_ok = False
        self.must_fail("subsystem unavailable")

    def test_duplicate_review_actor_label_refused(self):
        self.fake.actors.append(Actor(qa.LABEL_PREFIX + "FlyerDiscovery"))
        self.must_fail("duplicate V2 review actor label")

    def test_additional_native_milestone_refused(self):
        self.fake.actors.append(Milestone("OtherMilestone", "FlyerDiscovery"))
        self.must_fail("not exactly seven")

    def test_missing_milestone_refused(self):
        self.fake.actors.remove(self.fake.milestones["IoniaHiring"])
        self.must_fail("not exactly seven")

    def test_incorrect_station_tag_refused(self):
        self.fake.milestones["LiftStation"].station = False
        self.must_fail("inspection type mismatch")

    def test_untraceable_milestone_refused(self):
        self.fake.milestones["FlyerDiscovery"].mesh = Mesh("NoCollision")
        self.must_fail("not visibility/trace target")

    def test_missing_player_start_refused(self):
        self.fake.actors.remove(self.fake.actor("PlayerStart_Ender_REVIEW_PROXY"))
        self.must_fail("review spawn")

    def test_nonphysical_floor_refused(self):
        self.fake.actor("Harbor_TraversalFloor").mesh.collision = "NoCollision"
        self.must_fail("floor not physical")

    def test_ocean_with_collision_refused(self):
        self.fake.actor("Ocean_VISUAL_ONLY_NO_BUOYANCY").mesh.collision = "QueryAndPhysics"
        self.must_fail("ocean has unwanted collision")

    def test_ocean_nonempty_collision_profile_refused(self):
        self.fake.actor("Ocean_VISUAL_ONLY_NO_BUOYANCY").mesh.profile = "BlockAll"
        self.must_fail("NoCollision profile")

    def test_default_pawn_mismatch_refused(self):
        self.fake.mode.pawn_name = "WrongPlayerPawn"
        self.must_fail("default GameMode")

    def test_initial_objective_drift_refused(self):
        self.fake.new_state = lambda: self.make_initial_drift()
        self.must_fail("initial objective")

    @staticmethod
    def make_initial_drift():
        s = StoryState()
        s.initial_objective = "Skip ahead to Splashdown"
        return s

    def test_out_of_order_ionia_activation_refused(self):
        self.fake.milestones["IoniaHiring"].accept_illegal = True
        self.must_fail("out-of-order Ionia")

    def test_premature_engineering_signoff_refused(self):
        self.fake.milestones["EngineeringApproval"].accept_illegal = True
        self.must_fail("premature signoff")

    def test_valid_boarding_action_failure_refused(self):
        self.fake.milestones["AureateBoarding"].force_failure = True
        self.must_fail("valid native milestone refused")

    def test_engineering_signoff_cannot_bypass_inspections(self):
        # Illegal signoff must remain rejected after normal boarding, too.
        self.fake.milestones["EngineeringApproval"].accept_illegal = True
        self.must_fail("premature signoff")

    def test_inspection_replay_refused(self):
        self.fake.milestones["ReserveStation"].accept_duplicate = True
        self.must_fail("duplicate engineering station")

    def test_inspection_activation_failure_refused(self):
        self.fake.milestones["PressureStation"].force_failure = True
        self.must_fail("station activation failed")

    def test_signoff_failure_refused(self):
        self.fake.milestones["EngineeringApproval"].force_failure = True
        self.must_fail("signoff failed")

    def test_chapter_one_premature_progress_refused(self):
        def new_state():
            s = StoryState()
            s.force_chapter = True
            return s
        self.fake.new_state = new_state
        self.must_fail("incorrectly claims Splashdown")


if __name__ == "__main__":
    import unittest
    unittest.main()
