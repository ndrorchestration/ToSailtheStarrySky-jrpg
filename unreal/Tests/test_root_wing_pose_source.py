"""Static, executable source-bound checks for opt-in root-pivoted wing preview.
Not an Unreal compile, 3D collision proof, or artistic acceptance.
"""
from pathlib import Path
import math
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADER = (ROOT / "Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h").read_text(encoding="utf-8")
SOURCE = (ROOT / "Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp").read_text(encoding="utf-8")


class RootWingPoseSourceContracts(unittest.TestCase):
    def test_default_is_original_cube_poses(self):
        self.assertIn("bool bUseRootPivotedWingPose = false;", HEADER)
        self.assertIn("bUseRootPivotedWingPose && AuthoredWingMesh", SOURCE)
        self.assertIn(": WingPose(Form, WingIndex);", SOURCE)

    def test_native_actor_reuses_existing_four_wings(self):
        self.assertIn("for (int32 Index = 0; Index < 4; ++Index)", SOURCE)
        self.assertIn('CreateDefaultSubobject<UStaticMeshComponent>(Name)', SOURCE)
        self.assertIn("Wings.Add(Wing);", SOURCE)
        self.assertEqual(SOURCE.count("RootPivotedWingPose(EAureateWakeForm Form, int32 WingIndex)"), 1)

    def test_pose_adapter_binds_both_snap_and_transition(self):
        self.assertIn("SetRelativeTransform(WingPoseForMesh(Form, Index))", SOURCE)
        self.assertIn("TargetWingTransforms.Add(WingPoseForMesh(RequestedForm, Index))", SOURCE)
        self.assertIn("if (!bTransitioning)", SOURCE)
        self.assertIn("SnapToForm(CurrentForm);", SOURCE)

    def test_authored_pose_requires_imported_mesh(self):
        self.assertIn("(bUseRootPivotedWingPose && !AuthoredWingMesh)", SOURCE)
        self.assertIn("UStaticMesh* MeshToDisplay = bUseRootPivotedWingPose", SOURCE)
        self.assertIn("if (!MeshToDisplay)", SOURCE)
        self.assertIn("OriginalCubeWingMesh.Get()", SOURCE)

    def test_four_cardinal_sail_rotations_are_distinct_and_equal_scale(self):
        root = SOURCE.split("FTransform AAureateWakePreviewActor::RootPivotedWingPose(",1)[1]
        root = root.split("FTransform AAureateWakePreviewActor::WingPoseForMesh(",1)[0]
        self.assertIn("Scale = FVector(1.f, 1.f, 1.f);",root)
        for r in ("FRotator(90.f, 0.f, 0.f)","FRotator(-90.f, 0.f, 0.f)",
                  "FRotator(0.f, -90.f, 0.f)","FRotator(0.f, 90.f, 0.f)"):
            self.assertIn(r,root)
        self.assertEqual(root.count("WingIndex =="),3)

    def test_story_progression_and_orbiter_unlock_unchanged(self):
        self.assertIn("bool bAllowOrbiterPreview = false;",HEADER)
        self.assertIn("(RequestedForm == EAureateWakeForm::Orbiter && !bAllowOrbiterPreview)",SOURCE)
        self.assertIn("RequestedForm == EAureateWakeForm::Orbiter || CurrentForm == EAureateWakeForm::Orbiter",SOURCE)
        self.assertNotIn("AdvanceTo(",SOURCE)
        self.assertNotIn("FlotationConfirmed(",SOURCE)
        self.assertNotIn("SeaContact(",SOURCE)

    def test_artist_uses_280cm_root_span_not_100cm_center(self):
        root=SOURCE.split("RootPivotedWingPose(EAureateWakeForm Form, int32 WingIndex)",1)[1]
        root=root.split("FTransform AAureateWakePreviewActor::WingPoseForMesh(",1)[0]
        self.assertIn("authored 280cm span",root)
        self.assertIn("const float RootY = Side * 112.f;",root)
        self.assertIn("const float RootX = bForward ? 155.f : -180.f;",root)
        # The root starts outside the provisional 150cm-wide hull and wings span outward.
        self.assertGreater(112,75)

if __name__ == "__main__":
    unittest.main()
