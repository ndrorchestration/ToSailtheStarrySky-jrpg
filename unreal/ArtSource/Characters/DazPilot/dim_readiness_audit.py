#!/usr/bin/env python3
"""Read-only Daz Install Manager (DIM) readiness and asset provenance preflight.

Only the known Daz product IDs are reported, never account data, personal paths,
installed product inventory, email, serials or imported mesh/texture bytes.
This does not launch Daz, install plugins, export models or establish a license.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

KNOWN = {
    "86958": "Genesis 9 Starter Essentials",
    "72003": "Daz to Unreal Bridge",
}
DEFAULT_MANIFESTS = Path("C:/Users/Public/Documents/DAZ 3D/InstallManager/ManifestFiles")
MAX_MANIFESTS = 20000
MAX_MANIFEST_BYTES = 2 * 1024 * 1024
STATUS = "READ_ONLY_DIM_INSTALL_MANIFEST_PROBE_NOT_LICENSE_VERIFICATION"


def sku_from_manifest(raw: bytes) -> str | None:
    """Read only the whitelisted ProductStoreIDX; never persist private XML."""
    root = ET.fromstring(raw)
    if root.tag != "DAZInstallManifest":
        return None
    for node in root.iter("ProductStoreIDX"):
        item = node.attrib.get("VALUE", "").strip()
        match = re.fullmatch(r"(0*[0-9]+)(?:-[0-9]+)?", item)
        if match:
            return str(int(match.group(1)))
    return None


def inspect(manifest_dir: Path, studio_exe: Path | None = None) -> dict:
    found = {sku: False for sku in KNOWN}
    scanned = 0
    malformed = 0
    oversize = 0
    path_exists = manifest_dir.is_dir()
    if path_exists:
        # The DIM archive can contain private account/order metadata. We
        # deliberately ignore it and do not report individual manifest paths.
        manifests = sorted(manifest_dir.glob("*.dsx"))
        if len(manifests) > MAX_MANIFESTS:
            raise ValueError("DIM manifest count exceeds bounded read-only audit")
        for path in manifests:
            if path.is_symlink() or not path.is_file():
                continue
            scanned += 1
            if path.stat().st_size > MAX_MANIFEST_BYTES:
                oversize += 1
                continue
            try:
                sku = sku_from_manifest(path.read_bytes())
            except (ET.ParseError, OSError, UnicodeError, ValueError):
                malformed += 1
                continue
            if sku in found:
                found[sku] = True

    studio_state = ("NOT_CHECKED" if studio_exe is None else
                    "PRESENT" if studio_exe.is_file() and
                    studio_exe.suffix.casefold() == ".exe" else "NOT_FOUND")
    ready = studio_state == "PRESENT" and found["86958"]
    return {
        "state": STATUS,
        "manifest_directory": "FOUND" if path_exists else "NOT_FOUND",
        "manifest_file_count": scanned,
        "malformed_manifest_count": malformed,
        "oversize_manifest_count": oversize,
        "daz_studio_executable": studio_state,
        "products": {
            sku: {"known_name": title,
                  "dim_installed_manifest_observed": present,
                  "daz_scene_load_verified": False}
            for sku, (title, present) in
            ((sku, (KNOWN[sku], found[sku])) for sku in KNOWN)
        },
        "daz_only_reference_preflight": "CANDIDATE" if ready else "INCOMPLETE",
        "interactive_license_verified": False,
        "unreal_3d_asset_export_authorized": False,
        "ue58_bridge_compatibility_verified": False,
        "daz_native_figure_load_verified": False,
        "daz_or_unreal_application_launched": False,
        "gameplay_or_production_content_modified": False,
        "art_creator_approved": False,
        "provenance_notice": (
            "A DIM install manifest is not proof the corresponding Daz preset loads, "
            "a grant of game-interactive rights, or UE5.8 compatibility. "
            "Do not export licensed Daz 3D assets into interactive TSTSS."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-dir", type=Path, default=DEFAULT_MANIFESTS,
                        help="DIM ManifestFiles folder; never scanned recursively")
    parser.add_argument("--studio-exe", type=Path, default=None,
                        help="Optional installed Daz Studio executable; existence only")
    parser.add_argument("--receipt", type=Path, default=None,
                        help="Write a NEW public-safe, privacy-redacted JSON report")
    args = parser.parse_args(argv)
    result = inspect(args.manifest_dir, args.studio_exe)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        # One-time output, no overwriting or writing inside DIM manifests.
        if args.manifest_dir.resolve() == args.receipt.resolve().parent:
            parser.error("Do not write evidence into DIM's install-manifest folder")
        with args.receipt.open("x", encoding="utf-8") as stream:
            stream.write(payload)
    sys.stdout.write(payload)


if __name__ == "__main__":
    main()
