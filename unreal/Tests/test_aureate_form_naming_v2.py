"""Canon-level display naming and old Unreal enum compatibility guards."""
import json
import re
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"ArtSource"/"ShipReview"
HEADER=ROOT/"Source"/"ToSailTheStarrySky"/"Public"/"AureateWakePreviewActor.h"
CPP=ROOT/"Source"/"ToSailTheStarrySky"/"Private"/"AureateWakePreviewActor.cpp"
NAMES=ART/"aureate_wake_canonical_form_names_v2.json"
HISTORIC=ART/"aureate_wake_approved_art_contract.json"

class ShipFormNamingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(NAMES.read_text(encoding="utf-8"))
        cls.history=json.loads(HISTORIC.read_text(encoding="utf-8"))
        cls.header=HEADER.read_text(encoding="utf-8")
        cls.cpp=CPP.read_text(encoding="utf-8")

    def test_exact_new_player_display_names_in_approved_order(self):
        required=["Skybourne","Seabourne","Submersible","Starbourne"]
        self.assertEqual(self.data["canonical_display_order"],required)
        self.assertEqual([f["display_name"] for f in self.data["forms"]],required)
        self.assertEqual(len(set(required)),4)

    def test_backward_compatible_native_enum_ordinals(self):
        historical=self.history["canonical_consistency"]["forms"]
        self.assertEqual(historical,["Skyborne","Seaborne","Submersible","Orbiter"])
        self.assertEqual([f["internal_enum"] for f in self.data["forms"]],historical)
        block=self.header.split("enum class EAureateWakeForm : uint8",1)[1].split("};",1)[0]
        members=re.findall(r'(?m)^\s*(\w+)\s+UMETA\(DisplayName="([^"]+)"\)\s*,?',block)
        self.assertEqual(members,list(zip(historical,self.data["canonical_display_order"])))
        self.assertTrue(self.data["guardrails"]["enum_ordinals_preserved"])
        self.assertFalse(self.data["guardrails"]["serialization_migration_required"])

    def test_every_legacy_name_resolves_to_one_new_form(self):
        for f in self.data["forms"]:
            for name in f["legacy_names"]:
                self.assertNotEqual(name,f["display_name"])
        self.assertEqual(self.data["forms"][3]["legacy_names"],
                         ["Orbiter","Orbital","Orbital form"])
        self.assertEqual([f["internal_enum"] for f in self.data["forms"] if f["first_wake_available"]],
                         self.history["story_lock"]["first_wake_allows"])

    def test_starbourne_and_moon_bridge_gates_still_fail_closed(self):
        g=self.data["guardrails"]
        for k in ("starbourne_story_locked","moon_bridge_locked",
                  "physical_clearance_hold_unchanged","moon_bridge_lunar_gates_unchanged"):
            self.assertTrue(g[k],k)
        self.assertFalse(g["debug_orbiter_preview_opt_in_default"])
        self.assertFalse(g["gameplay_unlocked"])
        self.assertIn("bool bAllowOrbiterPreview = false;",self.header)
        self.assertIn("!bAllowOrbiterPreview",self.cpp)
        self.assertIn("EAureateWakeForm::Orbiter",self.cpp)
        self.assertNotIn("EAureateWakeForm::Starbourne",self.cpp)

    def test_story_visuals_same_four_wings_and_radial_sails(self):
        v=self.data["canonical_visual_requirements"]
        self.assertEqual(v["principal_wings"],4)
        self.assertEqual(v["starbourne_radial_sails"],4)
        self.assertTrue(v["starbourne_equal_sail_size"])
        self.assertEqual(v["starbourne_sail_positions"],
                         ["top","bottom","port","starboard"])
        self.assertTrue(v["forward_facing_bridge_persists"])

    def test_historical_visual_reference_untouched_by_naming(self):
        self.assertEqual(self.data["prior_visual_reference_sha256"],
                         self.history["approved_image"]["sha256"])
        self.assertEqual(self.history["authority"],"CREATOR_APPROVED_VISUAL_REFERENCE")
        self.assertEqual(self.history["model_acceptance"],"NOT_YET_ESTABLISHED")
        self.assertFalse(self.data["guardrails"]["model_art_approval_granted"])
        self.assertEqual(self.history["story_lock"]["orbiter_locked"],True)

    def test_native_reflected_display_labels_have_registered_unreal_automation(self):
        filename=ROOT/"Source"/"ToSailTheStarrySky"/"Private"/"Tests"/"AureateWakeCanonicalFormNamesTests.cpp"
        self.assertTrue(filename.is_file())
        native=filename.read_text(encoding="utf-8")
        self.assertIn("TSTSS.AureateWake.Canon.FormDisplayNames",native)
        self.assertIn("StaticEnum<EAureateWakeForm>()",native)
        self.assertIn("GetDisplayNameTextByValue(Value)",native)
        self.assertIn("GetNameStringByValue(Value)",native)
        self.assertIn("TestFalse(TEXT(\"Starbourne debug preview remains gated off by default\"),",native)
        for internal,display in zip(
            ["Skyborne","Seaborne","Submersible","Orbiter"],
            ["Skybourne","Seabourne","Submersible","Starbourne"]
        ):
            self.assertIn('EAureateWakeForm::'+internal,native)
            self.assertIn('TEXT("'+display+'")',native)

    def test_no_new_gameplay_or_forced_form_change(self):
        self.assertNotIn("bAllowOrbiterPreview = true",self.header)
        self.assertNotIn("EAureateWakeForm::Starbourne",self.header)
        self.assertNotIn("EAureateWakeForm::Skybourne",self.header)
        self.assertNotIn("EAureateWakeForm::Seabourne",self.header)

if __name__=="__main__":
    unittest.main()
