"""Source-only integration regression: preserve First Wake and Aureate Wake authority.

These checks prove presence of known controls in this integrated source tree.
They are NOT engine compilation, runtime physics, mesh imports or visual approval.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Source" / "ToSailTheStarrySky" / "Private"
PUBLIC = ROOT / "Source" / "ToSailTheStarrySky" / "Public"
TOOLS = ROOT / "Tools"


def code(path):
    return path.read_text(encoding="utf-8")


class ShipFoundationIntegrationAuthority(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.story = code(SOURCE / "TSTSSFirstWakeState.cpp")
        cls.gate = code(SOURCE / "TSTSSWaterLandingGate.cpp")
        cls.contact = code(SOURCE / "TSTSSWaterContactAdapter.cpp")
        cls.observer = code(SOURCE / "AureateWakeWaterObserverComponent.cpp")
        cls.observer_header = code(PUBLIC / "AureateWakeWaterObserverComponent.h")
        cls.ship = code(SOURCE / "AureateWakePreviewActor.cpp")
        cls.header = code(PUBLIC / "AureateWakePreviewActor.h")
        cls.importer = code(TOOLS / "import_aureate_wing_review.py")
        cls.support = code(TOOLS / "import_aureate_root_support_review.py")

    def test_new_foundation_water_beats_still_reject_generic_calls(self):
        self.assertIn("bool UTSTSSFirstWakeState::AdvanceWaterBeat(", self.story)
        self.assertIn("RequestedBeat == ETSTSSFirstWakeBeat::SeaContact ||", self.story)
        self.assertIn("RequestedBeat == ETSTSSFirstWakeBeat::FlotationConfirmed) return false;", self.story)
        self.assertIn("if (RequestedBeat == ETSTSSFirstWakeBeat::EngineeringChecked && !AreInspectionsComplete())", self.story)
        self.assertIn("bool UTSTSSFirstWakeState::Restore(", self.story)
        self.assertIn("SavedInspectionMask != 0x07", self.story)

    def test_existing_water_gate_is_still_sole_story_transition_api(self):
        self.assertIn("Story->AdvanceWaterBeat(ETSTSSFirstWakeBeat::SeaContact)", self.gate)
        self.assertIn("Story->AdvanceWaterBeat(ETSTSSFirstWakeBeat::FlotationConfirmed)", self.gate)
        self.assertIn("StableContactSeconds < 2.f", self.gate)
        self.assertIn("FMath::Abs(HullVerticalSpeedCms) > 25.f", self.gate)
        self.assertNotIn("Story->AdvanceTo(", self.gate)

    def test_latest_foundation_requires_surface_intersection_not_tag_only(self):
        self.assertIn("const bool bBelowSurface", self.contact)
        self.assertIn("const bool bActualImmersion = bBelowSurface && Submersion > 0.01f;", self.contact)
        self.assertIn("Gate->Observe(DeltaSeconds, bActualImmersion, VerticalSpeed, Story);", self.contact)
        self.assertIn("Hull->IsSimulatingPhysics()", self.contact)
        self.assertNotIn("Gate->Observe(DeltaSeconds, bInWater,", self.contact)

    def test_ship_observer_uses_newer_acceptance_guard_not_older_overlap(self):
        self.assertIn("GetPhysicsLinearVelocity()", self.observer)
        self.assertIn("GetComponentVelocity()", self.observer)
        self.assertIn("IsSimulatingPhysics()", self.observer)
        self.assertIn("bEnableStoryWaterObservation = false;", self.observer_header)
        self.assertIn("if (!bEnableStoryWaterObservation)", self.observer)
        self.assertIn("HasMeasuredHullWaterlineIntersection(", self.observer)
        self.assertIn("PhysicalHull->GetComponentBounds(", self.observer)
        self.assertIn("WaterCollision->GetComponentBounds(", self.observer)
        self.assertLess(self.observer.index("HasMeasuredHullWaterlineIntersection("),
                        self.observer.index("LandingGate->Observe("))
        self.assertIn("const bool bContactAccepted =", self.observer)
        self.assertIn("bContactAccepted && bTouchingWater", self.observer)
        self.assertLess(self.observer.index("LandingGate->Observe("), self.observer.index("VisualShip->RequestForm("))
        self.assertNotIn("Story->AdvanceTo(", self.observer)

    def test_four_wings_four_supports_and_two_hydrofoils(self):
        self.assertIn("Wings.Add(Wing);", self.ship)
        self.assertIn("WingRootSupports.Add(Support);", self.ship)
        self.assertIn("Hydrofoils.Add(Foil);", self.ship)
        self.assertIn("GetWingCount() const { return Wings.Num(); }", self.header)
        self.assertIn("GetRootSupportCount() const { return WingRootSupports.Num(); }", self.header)
        self.assertIn("GetHydrofoilCount() const { return Hydrofoils.Num(); }", self.header)
        self.assertIn("SetCollisionEnabled(ECollisionEnabled::NoCollision)", self.ship)

    def test_review_art_not_auto_pushed_into_gameplay(self):
        self.assertIn("bool bUseRootPivotedWingPose = false;", self.header)
        self.assertIn("bool bAllowOrbiterPreview = false;", self.header)
        self.assertIn("OriginalCubeWingMesh.Get()", self.ship)
        self.assertIn("RequestedForm == EAureateWakeForm::Orbiter || CurrentForm == EAureateWakeForm::Orbiter", self.ship)
        for importer in (self.importer, self.support):
            self.assertIn("/Review/", importer)
            self.assertIn("set_editor_property('replace_existing',False)", "".join(importer.replace('"', "'").split()))
            self.assertNotIn("spawn_actor_from_class(", importer)
            self.assertNotIn("SeaContact(", importer)

    def test_first_wake_benchmark_is_explicitly_review_only(self):
        benchmark = code(TOOLS / "build_first_wake_benchmark.py")
        self.assertIn("REVIEW_ONLY_NO_GAMEPLAY_OR_WATER_AUTHORITY", benchmark)
        self.assertIn("EditorAssetLibrary.does_asset_exist(MAP_PATH)", benchmark)
        self.assertIn("bAllowOrbiterPreview", self.header)
        self.assertNotIn("Story->AdvanceTo(", benchmark)

    def test_preserve_separate_physics_wiring_authority(self):
        # Two prototype observation pathways must never become proof by mere
        # overlap. Only the trusted water gate can mutate the story beats.
        self.assertEqual(self.observer.count("LandingGate->Observe("), 1)
        self.assertEqual(self.contact.count("Gate->Observe("), 1)
        self.assertNotIn("FlotationConfirmed(", self.ship)
        self.assertNotIn("AdvanceWaterBeat(", self.ship)
        self.assertNotIn("AdvanceWaterBeat(", self.observer)
        self.assertNotIn("AdvanceWaterBeat(", self.contact)


if __name__ == "__main__":
    unittest.main()
