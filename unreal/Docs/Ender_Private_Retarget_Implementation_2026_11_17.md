# Ender — private Manny → Genesis 9 IK retargeting execution gate

**Authority:** engineering REVIEW / NOT CANON / draft PR #853 / no merge. This is an engineering plan and gated editor script, **not a native execution receipt**. Last native playable control proof applies to `cc7548b` and the user's confirmed Shift sprint, not automatically to subsequent script-only heads.

## Grounded local inputs

The independent project worktree is `C:\TSTSS_CivicIntegration_20261116\unreal`. The target is an unapproved **152-bone private Genesis9 review mesh** with its linked Skeleton and review-only Blueprint. Five official UE 5.8 template source assets were copied locally under `Content/Mannequins`, excluding each exact `.uasset` in local Git `info/exclude` and verifying SHA-256 byte identity: Manny mesh, Manny Skeleton, `MM_Idle`, `MF_Unarmed_Walk_Fwd`, `MF_Unarmed_Jog_Fwd`. Retain these as read-only local development inputs. Do not copy into GitHub, Google Drive, shipped builds, screenshots shown as approved Ender art, or other projects.

The source and destination skeletons have different bone conventions (Manny uses `upperarm_l`, `ball_l`; Genesis9 uses `l_upperarm`, `l_toes`). Their compatibility **has not yet been proven natively**, nor are the three source motions confirmed in-place after retargeting. In particular, `MF_Unarmed_Jog_Fwd` is a jog *candidate*, not an approved sprint clip.

## Phase 1 — native read-only intake (mandatory)

1. Confirm Neontic online, no user-owned Unreal process active, and source worktree on the live draft PR head with a clean *tracked* status. Respect an operating reserve: **at least 6.5 GiB RAM free and 16.5 GiB disk free** to start; watchdog floors are 2.5 GiB RAM and 14.3 GiB disk while Unreal is running, monitored throughout; do not kill user apps or bypass the reserve. Use a disposable editor subprocess, not the user's playable window.
2. Protect the existing `DefaultEngine.ini`, `DefaultInput.ini`, `.uproject`, private assets and V5 map by exact hashes and read-only attributes where possible. Existing UE editor boot has auto-rewritten tracked INIs on a prior run; restore only backed-up, source-identical bytes after verifying no outside owner changed them. Never blanket reset.
3. In UE 5.8.4, invoke `python unreal/Tools/run_ender_private_retarget_native.py --audit` from the repo root. The host runner starts the read-only audit in its own guarded `UnrealEditor-Cmd.exe -nullrhi` process. It refuses to start if another Unreal process belongs to the user, records the exact source head, protects INI/uproject bytes, and watches resource floors. No asset/level save. The script checks project/engine, verified native gameplay ancestor and **current Git HEAD**, 7 exact asset fingerprints, two different Skeletons, three `AnimSequence` classes with source Skeleton parity and root-motion-disabled flags, six proposed bone chains with actual native `SkeletalMesh.get_bone_parent` ancestry traversal (rejects missing, unrelated or cyclic paths), and IK Rig editor availability.
4. Read `Saved/MigrationEvidence/EnderRetargetPrivate/prerequisite_report.json`. Only `NATIVE_RETARGET_INPUTS_VALIDATED_NOT_RETARGETED` on the **same current Git HEAD** qualifies. Any `HOLD_` means stop, inspect the narrow failure, and correct the source/rig assumption rather than inventing compatibility. Native report is *prerequisite evidence only*, not animation success.

## Phase 2 — private IK authoring (explicitly opt-in, separate process)

1. With no Unreal process already running and resources reverified, back up the local `.git/info/exclude`, then locally add the exact noncanonical path `/unreal/Content/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/`. Verify `git check-ignore` for the expected .uassets. This is local-only; **do not change tracked `.gitignore`**. Confirm that no generated outputs already exist.
2. A second guarded native editor session may opt in by setting `TSTSS_PRIVATE_IK_CREATE=1` only in the launching PowerShell session and invoking `python unreal/Tools/run_ender_private_retarget_native.py --create-rigs`. Otherwise the authoring script refuses to create anything. The host requires **>=6.5 GiB free RAM and >=16.5 GiB disk before launch** and writes a short-lived unique-run startup-gate receipt. The builder must match this gate's run ID, a fresh (within six hours) successful native report **on the identical current Git HEAD**, a known-good ancestor, 7 rehashed input assets, no existing generated outputs, safe **in-editor** floors (>=2.5 GiB RAM and >=14.3 GiB disk), and exact project path/version. The host re-verifies native report and output files; stale reports fail closed.
3. The generated *review-only* outputs (only if the preceding gates pass) are `IK_Manny_EnderReview_NONCANONICAL`, `IK_Genesis9_EnderReview_NONCANONICAL`, and `RTG_MannyToEnder_NONCANONICAL`. The code constructs manual Spine/Head/left-right arm/left-right leg chains after native ancestry checks, sets pelvis as retarget root, adds UE5.8 default operation stack, and maps corresponding chains. It creates **no AnimSequence** and does not edit the Ender player pawn, save maps, or override animation ownership.
4. Inspect `Saved/MigrationEvidence/EnderRetargetPrivate/rig_build_receipt.json`. A `PRIVATE_IK_RIGS_CREATED_REVIEW_ONLY_NO_ANIMATION` record must be cross-checked against all three actual private assets, their paths, chain maps, and clean tracked Git state. The host records each attempt under `Saved/MigrationEvidence/EnderRetargetPrivate/HostReceipts/<run_id>/`; a stale receipt or changed protected config produces HOLD, never success. On partial-failure HOLD, do not automatically delete unknown generated assets; classify and reconcile first. Later merges/releases remain unauthorized.

### Exact native commands (only with Neontic online and resources safe)

From a separate PowerShell terminal after the current PR head is fetched into the clean local review branch:

```powershell
cd C:\TSTSS_CivicIntegration_20261116
python unreal\Tools\run_ender_private_retarget_native.py --audit
# Read the native report and host receipt; stop immediately on HOLD.
# Only after the audit passes, three rig output paths are locally Git-ignored
# and no generated rig assets exist:
$env:TSTSS_PRIVATE_IK_CREATE = "1"
try {
    python unreal\Tools\run_ender_private_retarget_native.py --create-rigs
} finally {
    Remove-Item Env:\TSTSS_PRIVATE_IK_CREATE -ErrorAction SilentlyContinue
}
```

Never run while a user's Unreal Editor or playtest is active. Do not reset changed INIs or delete private assets on a HOLD. Rig creation does not establish rendered motion.
## Phase 3 — motion import and playable quality (NOT YET IMPLEMENTED)

After retargeter correctness and retarget pose alignment are **natively** checked: use Unreal's IK Retarget Batch Operation to generate **three** noncanonical Ender Skeleton-compatible, in-place locomotion loops in an otherwise empty excluded review folder; never overwrite existing clips. Measure root displacement and verify pose mapping at hips/knees/feet, correct gait cadence at 260 cm/s walk versus 600 cm/s Shift sprint, orientation, grounded capsule motion and no double-root-motion. Assign source-locked clips to the **existing private BP** under the editor-only opt-in flag, not to a second gameplay pawn, and ensure animation-owner / existing-AnimBlueprint guards remain active. Record native PIE movement transitions, gameplay interactions, screenshots (Lit and unlit diagnostics), clipping/head-goggles-staff alignment, stable foot contact and Ender's reference likeness.

**Acceptance remains:** real rendered idle/walk/run (not simply capsule velocity), no break to flyer modal, Ionia/ship target, C++ source or Shift sprint, 38/38 native automation on the exact source SHA, privacy/licensing review, and creator art signoff. Do not infer approval from source tests or successful IK asset creation.

## Verified references

- [Epic Unreal 5.8: Retargeting bipeds with IK Rig](https://dev.epicgames.com/documentation/unreal-engine/retargeting-bipeds-with-ik-rig-in-unreal-engine)
- [Epic Unreal 5.8: Python IK Rig construction](https://dev.epicgames.com/documentation/unreal-engine/using-python-to-create-and-edit-ik-rigs-in-unreal-engine)
- [Epic Unreal 5.8: Python IK Retargeter construction](https://dev.epicgames.com/documentation/unreal-engine/using-python-to-create-and-edit-ik-retargeter-assets-in-unreal-engine)
- [Epic Unreal 5.8: Default retarget operation stack](https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/IKRetarget/AddDefaultOps)
- [Epic Unreal 5.8: Batch retarget operation](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/IKRetargetBatchOperation)
