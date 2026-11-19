# First Wake approved-cast GLB intake — review-only

**Status:** implemented offline validator, native UE 5.8 asset import **not executed**.  
**Source:** [PR #622](https://github.com/ndrorchestration/ToSailtheStarrySky-jrpg/pull/622). Parent PRs #610 and #608 remain draft/unmerged.

## Purpose

Carry the **October 30, 2026 creator-approved full-cast visual** forward without inventing new faces, blindly adopting outdated sheets or replacing gameplay art with unrelated stock characters.

The first scene needs **Ender and Ionia**. In particular, Ionia's current lock is **long curly blonde hair** (Captain updo acceptable), which supersedes the older shoulder-length text in `docs/CHARACTER_AND_ART_AUTHORITY.md`. Preserve Ender's young facial likeness, green eyes, short copper/auburn hair and full-length staff with longitudinally centered wrapping and brass ferrules. No gender, age, costume, facial detail or crew-order changes are authorized by this tool. Refer to canon/visual bible and the newer locked cast artwork; do not assume that the image alone produces a rig.

## Source custody

The user's canonical October 30 full-cast image was not recovered as a local, original full-resolution file in this tooling environment. **No image hash, model file, rig or animations are invented.** Staged external model files must be creator-correct and provenance-recorded before use. Never commit the actual cast source or rig data to the public GitHub repository without a separate source/rights/release review.

Use a **private folder outside the Git repository**, for example `C:\TSTSS_Private_Cast\`:

- `approved_cast.png` — original approved full-cast visual (PNG or JPEG).
- `ender_candidate.glb` — creator-directed modeled, UV-mapped, skinned Ender with animation.
- `ionia_candidate.glb` — creator-directed modeled, UV-mapped, skinned Ionia with animation.
- `intake.json` — a local manifest with real SHA-256 values; do not include it in commits.

**Illustrative schema only** (replace ALL values with actual source filenames and real hashes; invalid placeholders fail closed):

```json
{
  "schema": "tstss-first-wake-cast-candidate-v1",
  "creator_reference": {
    "decision": "creator-visual-reference-2026-10-30",
    "path": "approved_cast.png",
    "sha256": "<64-lowercase-hex-of-original-file>"
  },
  "characters": [
    {
      "id": "ender",
      "model_path": "ender_candidate.glb",
      "model_sha256": "<64-lowercase-hex-of-actual-glb>"
    },
    {
      "id": "ionia",
      "model_path": "ionia_candidate.glb",
      "model_sha256": "<64-lowercase-hex-of-actual-glb>"
    }
  ]
}
```

For local hashes use:

```powershell
Get-FileHash C:\TSTSS_Private_Cast\approved_cast.png -Algorithm SHA256
Get-FileHash C:\TSTSS_Private_Cast\ender_candidate.glb -Algorithm SHA256
Get-FileHash C:\TSTSS_Private_Cast\ionia_candidate.glb -Algorithm SHA256
```

## Offline validation (does not import)

```powershell
py -3.11 unreal\Tools\validate_cast_glb.py --manifest C:\TSTSS_Private_Cast\intake.json --source-root C:\TSTSS_Private_Cast --require-both
py -3.11 -m unittest discover -s unreal\Tests -p "test_cast_glb_intake.py" -v
```

The validator checks the original picture's cryptographic hash and recognizable image header; GLB container structure, embedded data, 20+ named rig joints including a head joint, skinned geometry with normals, UVs and weights, at least one animation and materials. It rejects directory escapes and wrong crew identities. **This is a coarse file-structure gate, not the official glTF Validator nor a proof of character likeness, topology, morph targets, functioning Unreal retargeting or lifelike animation.**

A manifest that says `creator-visual-reference-2026-10-30` is an assertion, NOT proof of an actual creator approval for a derived model; creator acceptance and source-rights evidence remain separate gates.

## Optional Unreal Editor import (not tested)

Open Unreal 5.8, enable the Python Editor Script Plugin and Interchange plugins, and use **a clean isolated project/checkout**. Do **not** import into production characters, default maps or the main branch.

Execute the tool from Unreal Python with the same `--manifest` / `--source-root` arguments and `--import-review`, e.g. in the Python console:

```python
import sys
sys.argv = ["validate_cast_glb.py", "--manifest", r"C:\TSTSS_Private_Cast\intake.json", "--source-root", r"C:\TSTSS_Private_Cast", "--require-both", "--import-review"]
exec(compile(open(r"PATH_TO_REPO\unreal\Tools\validate_cast_glb.py", encoding="utf-8").read(), "validate_cast_glb.py", "exec"))
```

The script demands an empty `/Game/TSTSS/Review/CastCandidates/Ender` and `.../Ionia` destination, sets `replace_existing=False`, and surfaces Interchange options to the operator. **Native import plugin/pipeline behavior is unverified.** If import fails or creates only partial assets, stop and inspect the candidate folder; never rerun over existing results. Engine import and model quality are distinct gates.

### Art direction handoff

For each hero, request from a real modeler or validated art tool:

1. Creator-correct front/side/back likeness sheet and expression references from the approved source, not newly invented designs.
2. Scale/axis documentation, separate hair/outfit/eyes and appropriate topology, facial controls or blendshape plan, and material/texture sources.
3. Editable source (Blender preferred), skinned .glb export, animation clips (idle, walk, turn, gesture), bone naming and import/retarget notes.
4. Native UE editor close/mid/far shots at 1920×1080, side-by-side against original image. Check Ionia hair volume and silhouette, Ender staff length/grip, skin/hair shading, feet, hands, eyes and anatomy.
5. Scene insertion at the benchmark's existing approved-art import slots only after asset rights, exact source hashes and creator signoff.

## Acceptance and implementation boundary

- **IN SOURCE:** validator and draft Editor import path; host Python tests.
- **NOT PRESENT:** approved original image bytes, Ender/Ionia rigged GLBs, native Unreal import results, completed animations, production-ready materials, gameplay character actor integration.
- **NOT AUTHORIZED:** changes to Ionia-first recruitment, save authority, combat, Five Lights as automatic spells, First Wake SeaContact/flotation story gates, protected main merge, public release.
- **NEXT PROOF:** recover approved original source, prepare one actual GLB, verify its hash/rig, import and capture the real actor in the First Wake visual stage.

Epic Interchange glTF/GLB is the intended import route; texture/skin/animation handling must be checked on exact Unreal 5.8 installation: https://dev.epicgames.com/documentation/unreal-engine/interchange-import-reference-in-unreal-engine
