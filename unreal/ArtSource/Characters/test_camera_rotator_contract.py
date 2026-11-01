"""Regression guard for the upside-down Unreal camera bug.

UE Python Rotator positional construction does not use pitch,yaw,roll order.
Require named roll/pitch/yaw for every authored camera and light rotation.
"""
import ast
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name("capture_cast_render_review.py")

class NativeCameraRotationContract(unittest.TestCase):
    def test_every_unreal_rotator_uses_keyword_angles(self):
        root=ast.parse(SOURCE.read_text(encoding="utf-8-sig"))
        rotations=[
            x for x in ast.walk(root)
            if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute)
            and x.func.attr=="Rotator" and isinstance(x.func.value,ast.Name)
            and x.func.value.id=="unreal"
        ]
        self.assertGreaterEqual(len(rotations),3)
        for node in rotations:
            self.assertEqual(node.args,[],f"Rotator at line {node.lineno} uses unsafe positional angles")
            self.assertEqual({k.arg for k in node.keywords},{"pitch","yaw","roll"})

    def test_review_script_has_native_front_axis_and_no_source_save(self):
        text=SOURCE.read_text(encoding="utf-8-sig")
        self.assertIn('("Ender_front", cam("Ender_front", (0, -40, 102), -90, 44)',text)
        self.assertIn('if label == "Five_cast_lineup":',text)
        self.assertNotIn("save_current_level(",text)
        self.assertNotIn("replace_existing=True",text)

if __name__=="__main__":
    unittest.main()
