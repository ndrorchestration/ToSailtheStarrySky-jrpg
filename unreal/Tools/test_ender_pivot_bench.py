"""Static fail-closed checks for short private Ender rotation benchmark."""
import ast
from pathlib import Path
import unittest

SRC=(Path(__file__).parent/"bench_ender_turns.py").read_text(encoding="utf8")
NODE=ast.parse(SRC)


class EnderPivotBenchTests(unittest.TestCase):
    def test_script_parses_with_distinct_phases(self):
        names=[node.name for node in NODE.body if isinstance(node,ast.FunctionDef)]
        self.assertIn("main",names)
        for label in ("walk_start","walk_stop","sprint_start","sprint_stop",
                      "right_90","reverse_180","final_stop"):
            with self.subTest(label=label):
                self.assertIn('"'+label+'"',SRC)

    def test_strict_exact_pid_focus(self):
        for s in ("GetForegroundWindow","UnrealWindow","ToSailTheStarrySky",
                  "actual == pid","owned_foreground(pid)",
                  "WINDOW_FOCUSED_OS_INJECTED_NOT_HUMAN","KEY_RELEASE_"):
            with self.subTest(value=s):
                self.assertIn(s,SRC)
        self.assertIn('"-offset_x", str(rectangle.left)', SRC)
        self.assertIn('"-offset_y", str(rectangle.top)', SRC)
        self.assertIn('"-video_size", str(width) + "x" + str(height)', SRC)
        self.assertIn("width -= width % 2", SRC)
        self.assertIn("height -= height % 2", SRC)
        self.assertIn('"CAPTURE_NOT_ENTIRELY_ON_PRIMARY_SCREEN"', SRC)
        self.assertIn('"-i", "desktop"', SRC)
        self.assertIn('unique >= 70', SRC)
        self.assertIn('HOLD_STALE_OR_TOO_SHORT_VIDEO', SRC)

    def test_no_external_input_or_hidden_simulated_state(self):
        for bad in ("SetActorLocation","set_actor_location","set_world_location",
                    "CheatManager","SaveGame","-ExecCmds","git push","git merge",
                    "reset --hard","-Force","-y\","):
            with self.subTest(value=bad):
                self.assertNotIn(bad,SRC)

    def test_distinct_baseline_and_blend_assertions(self):
        for s in ("args.variant == \"blend\"","args.variant == \"legacy\"",
                  "TSTSS_ENDER_PRIVATE_BLENDSPACE_BOUND",
                  "TSTSS_ENDER_PIE_ANIM_REQUESTED",
                  "TSTSS_ENDER_PRIVATE_BLENDSPACE_BAND",
                  "TSTSS_ENDER_FACING_SAMPLE",
                  "TSTSS_ENDER_FOOT_SAMPLE"):
            with self.subTest(value=s):
                self.assertIn(s,SRC)

    def test_host_exit_and_asset_guards(self):
        for s in ("child_exit_code","assets_unchanged","source_clean",
                  "HOLD_ENDER_PIVOT_","SOURCE","FRESH_EVIDENCE",
                  "frame_count","fluidity_and_art_acceptance"):
            with self.subTest(value=s):
                self.assertIn(s,SRC)


if __name__=="__main__":
    unittest.main()
