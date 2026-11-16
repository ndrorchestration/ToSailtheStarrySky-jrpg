"""Fail-closed checkout identity for the nonshipping bridge review tools."""
import re

INTEGRATION_BASE = "41feda70fce06da2749861333c56a13626888e6f"
ORIGINAL = ("TSTSS_840_OpticalReach_20261115",
            "review/ue58-optical-bridge-reach-probe-20261115")
INTEGRATED = ("TSTSS_843_OpticalIntegrated_20261115",
              "review/ue58-optical-integration-stage-20261115")


def validate_checkout(root_name, branch, actual_head, expected_head, has_integration_base):
    """Verify identity; ancestry must be checked using Git by the caller."""
    identity = (root_name, branch)
    if identity not in (ORIGINAL, INTEGRATED):
        raise RuntimeError("HOLD: unauthorized checkout or branch")
    if not re.fullmatch(r"[0-9a-f]{40}", actual_head or ""):
        raise RuntimeError("HOLD: invalid actual commit")
    if actual_head != expected_head:
        raise RuntimeError("HOLD: checkout SHA mismatch")
    if identity == INTEGRATED and has_integration_base is not True:
        raise RuntimeError("HOLD: integrated checkout lacks telemetry base")
