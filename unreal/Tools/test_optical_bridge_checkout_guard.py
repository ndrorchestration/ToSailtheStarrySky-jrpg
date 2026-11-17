"""Checkout admission tests; these do not constitute Unreal evidence."""
import importlib.util
import unittest
from pathlib import Path

PATH = Path(__file__).with_name("optical_bridge_checkout_guard.py")
BASE = "41feda70fce06da2749861333c56a13626888e6f"
HEAD = "a" * 40


class CheckoutGuardTests(unittest.TestCase):
    def test_guard_exists(self):
        self.assertTrue(PATH.is_file(), "integration checkout guard is missing")

    @unittest.skipUnless(PATH.is_file(), "guard not implemented")
    def test_integrated_and_original_checkouts_and_rejections(self):
        spec = importlib.util.spec_from_file_location("guard", PATH)
        guard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guard)
        validate = guard.validate_checkout
        original = ("TSTSS_840_OpticalReach_20261115", "review/ue58-optical-bridge-reach-probe-20261115")
        integrated = ("TSTSS_843_OpticalIntegrated_20261115", "review/ue58-optical-integration-stage-20261115")
        validate(*original, HEAD, HEAD, False)
        validate(*integrated, HEAD, HEAD, True)
        for root, branch, actual, expected, ancestry in [
            (*integrated, HEAD, HEAD, False),
            (*integrated, HEAD, "b" * 40, True),
            (*integrated, HEAD, "", True),
            (*integrated, "abc", "abc", True),
            (original[0], integrated[1], HEAD, HEAD, True),
            (integrated[0], original[1], HEAD, HEAD, True),
            ("arbitrary", integrated[1], HEAD, HEAD, True),
        ]:
            with self.subTest(root=root, branch=branch, expected=expected, ancestry=ancestry):
                with self.assertRaises(RuntimeError):
                    validate(root, branch, actual, expected, ancestry)


if __name__ == "__main__":
    unittest.main()
