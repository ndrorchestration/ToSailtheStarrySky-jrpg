"""Read-only SHA-locked Unreal 5.8 directional source inventory for Ender.

This does not import, retarget, export, modify or authorize any animation.
Record one unique JSON receipt inside Saved/MigrationEvidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "unreal/Saved/MigrationEvidence"
TEMPLATES = Path(r"C:\Program Files\Epic Games\UE_5.8\Templates\TemplateResources\High\Characters\Content\Mannequins\Anims\Unarmed")
# Engine-origin source files verified on Neontic, Nov 23 2026 (NOT GASP provenance).
EXPECTED = {
    "Walk/MF_Unarmed_Walk_Bwd.uasset": (606821, "ae0c2ee1c1178fd1b9493f6c327e52d10a3d6bbde29eae54dcb07c13a27dcf46"),
    "Walk/MF_Unarmed_Walk_Left.uasset": (486552, "81500e4fcdd9ae9aa6433e652e67dea8f9dd9fa7b9ef1714e29f6ab0a1bb9d97"),
    "Walk/MF_Unarmed_Walk_Right.uasset": (491934, "f5922b4e632351353224b32f719af97e85512ab4f6553b15315cf14ad04f675f"),
    "Jog/MF_Unarmed_Jog_Bwd.uasset": (483265, "1f6e9448f0e0737f506d9e8f11b8d661d6d65c818f0e3160938f1e24082b16c3"),
    "Jog/MF_Unarmed_Jog_Left.uasset": (487864, "f7842445f0c2b2f8d3cd9d43b9f58bc3ea888adeb1e161398b492097358431bd"),
    "Jog/MF_Unarmed_Jog_Right.uasset": (521907, "208f642310d9627d12a5125889b480e051a1f1fc5397a10b83975903a0c59aea"),
}


def require(condition, token):
    if not condition:
        raise RuntimeError("HOLD_ENDER_DIRECTION_SOURCE_" + token)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    require(bool(re.fullmatch(r"[0-9a-f]{40}", args.expected_head)), "INVALID_HEAD")
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()
    status = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                            capture_output=True, text=True, check=True).stdout.strip()
    require(sha == args.expected_head and not status, "SOURCE_CHANGED")
    receipt = Path(args.receipt).resolve()
    require(receipt.parent == EVIDENCE.resolve() and
            not receipt.exists() and receipt.suffix == ".json", "RECEIPT_PATH")
    require(TEMPLATES.is_dir(), "NO_NATIVE_TEMPLATE_DIRECTORY")
    rows = []
    for subpath, (length, digest) in EXPECTED.items():
        path = TEMPLATES / subpath
        require(path.is_file() and path.stat().st_size == length, "SIZE_" + path.stem)
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == digest, "HASH_" + path.stem)
        rows.append({"unreal_template_relative_path": subpath,
                     "bytes": length, "sha256": digest,
                     "engine_install_origin": "UE_5.8/Templates/TemplateResources/High"})
    payload = {
        "status": "SOURCE_DIRECTIONAL_INVENTORY_PASS_NOT_RETARGETED",
        "source_sha": sha,
        "files": rows,
        "candidate_count": len(rows),
        "source_package": "Unreal Engine 5.8 installed mannequin template",
        "game_animation_sample_origin": "NOT_ESTABLISHED",
        "target_152_bone_skeleton_compatibility": "NOT_TESTED",
        "private_ik_retarget_result": "NOT_EXECUTED",
        "gameplay_animation_or_license_release_authority": "NOT_ESTABLISHED",
        "source_copied_or_modified": False,
    }
    receipt.write_text(json.dumps(payload, indent=2), encoding="utf8")
    print("ENDER_DIRECTION_TEMPLATE_INVENTORY_PASS " + str(receipt))


if __name__ == "__main__":
    main()
