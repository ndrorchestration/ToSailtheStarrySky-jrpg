"""Source-level fail-closed integration checks for the explicit First Wake C-key view.

This verifies authoring constraints, not native PIE camera/controls evidence.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp"
HEADER = ROOT / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h"
INPUT = ROOT / "Config/DefaultInput.ini"

RULES = {
    "pie_only": 'World->WorldType != EWorldType::PIE',
    "explicit_binding": 'BindAction(TEXT("EngineFocusPreview"), IE_Pressed',
    "bound_to_toggle": '&ATSTSSExplorerCharacter::ToggleEngineFocusPreview)',
    "unique_gauge": 'InstrumentCount != 1',
    "unique_atmosphere": 'AtmosphereCount != 1',
    "real_gauge": 'TEXT("TSTSS_VS_REVIEW_InstrumentCore_LIFT")',
    "proximity": 'GetActorLocation(), Instrument->GetActorLocation()) > 450.f',
    "player_camera_owner": 'PC->GetViewTarget() != this',
    "existing_movement_guard": 'PC->IsMoveInputIgnored()',
    "existing_look_guard": 'PC->IsLookInputIgnored()',
    "actual_story": 'FirstWakeState, Atmosphere, ETSTSSPresentationMoment::EngineInspection',
    "optical_permission": '!Intent.bAllowCinematicFocus',
    "rack_permission": '!Intent.bAllowFocusRack',
    "deep_focus_denial": 'Intent.bRequireDeepFocus',
    "authorized_shot": 'FName(TEXT("FW03_Engine_Inspection"))',
    "review_user_opt_in": 'Coordinator->SetReviewEnabled(true);',
    "existing_cinematic_owner_guard": 'if (bWasEnabled && Coordinator->GetCurrentIntent().bEligible)',
    "preview_camera_only": 'World->SpawnActor<ACineCameraActor>',
    "lens": 'Cine->SetCurrentFocalLength(65.f);',
    "aperture": 'Cine->SetCurrentAperture(2.8f);',
    "manual_focus": 'Settings.FocusMethod = ECameraFocusMethod::Manual;',
    "limited_duration": 'EngineFocusPreviewStartedSeconds + 4.0',
    "blend_entry_grace": 'FPlatformTime::Seconds() - EngineFocusPreviewStartedSeconds > 0.75',
    "no_owner_disable": 'if (!Current.bEligible',
    "only_cleanup_when_opened": 'else if (bHadPreview)',
    "discoverable_prompt": 'Engine inspection: press C near the LIFT instrument for a 4s focus view',
    "visual_return": 'PC->SetViewTargetWithBlend(this, 0.3f,',
    "cancel_pending_entry_blend": 'PC->SetViewTargetWithBlend(this, 0.f);',
    "do_not_steal_external_view": 'PC->GetViewTarget() == this',
    "input_restore_move": 'PC->SetIgnoreMoveInput(false);',
    "input_restore_look": 'PC->SetIgnoreLookInput(false);',
    "camera_cleanup": 'Camera->SetLifeSpan(0.6f);',
    "coordinator_cleanup": 'Coordinator->SetReviewEnabled(false);',
    "timer": '&ATSTSSExplorerCharacter::VerifyEngineFocusPreview',
    "end_play_cleanup": 'RestoreEngineFocusPreview();',
}


def check_contract(cpp: str, header: str, config: str) -> None:
    if config.count('+ActionMappings=(ActionName="EngineFocusPreview",Key=C)') != 1:
        raise ValueError("missing or duplicate explicit PIE C input")
    if config.count('+ActionMappings=(ActionName="Interact",Key=E)') != 1:
        raise ValueError("normal E interaction must be unchanged")
    if "void ToggleEngineFocusPreview();" not in header:
        raise ValueError("player focus action not declared")
    if "virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;" not in header:
        raise ValueError("end play restore not registered")
    if "void ATSTSSExplorerCharacter::ToggleEngineFocusPreview()" not in cpp:
        raise ValueError("no player view preview implementation")
    if cpp.count('BindAction(TEXT("EngineFocusPreview"), IE_Pressed') != 1:
        raise ValueError("input preview binding missing/duplicated")
    bind = cpp.index('BindAction(TEXT("EngineFocusPreview"), IE_Pressed')
    pie_scope = cpp.rfind('if (InputWorld && InputWorld->WorldType == EWorldType::PIE)', 0, bind)
    if pie_scope < 0 or cpp.rfind('#endif', pie_scope, bind) > pie_scope:
        raise ValueError("C binding escaped explicit PIE-only block")
    for label, token in RULES.items():
        if token not in cpp:
            raise ValueError("missing fail-closed source rule: " + label)
    if "GetCurrentIntent().bEligible" not in cpp:
        raise ValueError("stale authoritative moment must expire preview")
    if 'GetCurrentIntent().ShotId !=' not in cpp:
        raise ValueError("camera expires when coordinator switches shot")
    if 'TryActivate(FirstWakeState)' not in cpp:
        raise ValueError("normal milestone activation unexpectedly removed")
    section = cpp.split("void ATSTSSExplorerCharacter::ToggleEngineFocusPreview()", 1)[1].split(
        "void ATSTSSExplorerCharacter::VerifyEngineFocusPreview()", 1
    )[0]
    for unsafe in ("TryActivate(", "SaveFirstWake(", "LoadFirstWake(",
                   "OpenLevel(", "SetActorLocation(", "PlaySound",
                   "DestroyActor(", "Starbourne", "LyraIntroduction"):
        if unsafe in section:
            raise ValueError("camera action writes unrelated game state: " + unsafe)
    if 'Coordinator->TryPublishMoment(' not in section:
        raise ValueError("presentation source-of-truth bypassed")
    # A shared coordinator can already be presenting a different active shot.
    # The explicit camera review is never permitted to preempt that owner.
    guard = section.index('if (bWasEnabled && Coordinator->GetCurrentIntent().bEligible)')
    publication = section.index('Coordinator->TryPublishMoment(')
    if guard >= publication:
        raise ValueError("existing coordinator shot guard occurs after publication")


class FirstWakePlayerFocusPreviewSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp = CPP.read_text(encoding="utf-8")
        cls.header = HEADER.read_text(encoding="utf-8")
        cls.config = INPUT.read_text(encoding="utf-8")

    def test_source_authored_preview_policy(self):
        check_contract(self.cpp, self.header, self.config)

    def test_c_key_missing_fails(self):
        with self.assertRaisesRegex(ValueError, "explicit PIE C input"):
            check_contract(self.cpp, self.header,
                           self.config.replace('ActionName="EngineFocusPreview"', 'ActionName="Other"'))

    def test_e_key_must_remain(self):
        with self.assertRaisesRegex(ValueError, "normal E interaction"):
            check_contract(self.cpp, self.header,
                           self.config.replace('ActionName="Interact",Key=E', 'ActionName="Interact",Key=F'))

    def test_wrong_story_event_fails(self):
        with self.assertRaisesRegex(ValueError, "actual_story"):
            check_contract(self.cpp.replace('FirstWakeState, Atmosphere, ETSTSSPresentationMoment::EngineInspection',
                                            'FirstWakeState, Atmosphere, ETSTSSPresentationMoment::NightSkyWonder'),
                           self.header, self.config)

    def test_unowned_player_camera_fails(self):
        with self.assertRaisesRegex(ValueError, "player_camera_owner"):
            check_contract(self.cpp.replace('PC->GetViewTarget() != this',
                                            'false /* removed owner check */'),
                           self.header, self.config)

    def test_missing_unique_world_owner_fails(self):
        with self.assertRaisesRegex(ValueError, "unique_atmosphere"):
            check_contract(self.cpp.replace("AtmosphereCount != 1", "AtmosphereCount < 1"),
                           self.header, self.config)

    def test_missing_actual_gauge_fails(self):
        with self.assertRaisesRegex(ValueError, "real_gauge"):
            check_contract(self.cpp.replace('TEXT("TSTSS_VS_REVIEW_InstrumentCore_LIFT")',
                                            'TEXT("UntestedGauge")'), self.header, self.config)

    def test_cinematic_owner_guard_cannot_be_removed(self):
        edited = self.cpp.replace(
            'if (bWasEnabled && Coordinator->GetCurrentIntent().bEligible)',
            'if (false /* preempt any other cinematic shot */)')
        with self.assertRaisesRegex(ValueError, "existing_cinematic_owner_guard"):
            check_contract(edited, self.header, self.config)

    def test_owner_check_must_precede_publication(self):
        source = self.cpp
        guard_line = 'if (bWasEnabled && Coordinator->GetCurrentIntent().bEligible)'
        guard = source.index(guard_line)
        publish = source.index('const FTSTSSPresentationIntent Intent = Coordinator->TryPublishMoment(')
        self.assertLess(guard, publish)
        # This remains an editor-only, explicit interaction—not part of E.
        self.assertIn('Engine view held: another cinematic shot already owns presentation',
                      source[guard:publish])

    def test_missing_optical_permission_fails(self):
        with self.assertRaisesRegex(ValueError, "optical_permission"):
            check_contract(self.cpp.replace('!Intent.bAllowCinematicFocus',
                                            'false /* bypass */'), self.header, self.config)

    def test_lens_drift_fails(self):
        with self.assertRaisesRegex(ValueError, "lens"):
            check_contract(self.cpp.replace("Cine->SetCurrentFocalLength(65.f);",
                                            "Cine->SetCurrentFocalLength(135.f);"),
                           self.header, self.config)

    def test_missing_restoration_fails(self):
        with self.assertRaisesRegex(ValueError, "input_restore_move"):
            check_contract(self.cpp.replace("PC->SetIgnoreMoveInput(false);",
                                            "/* movement remains blocked */"), self.header, self.config)

    def test_manual_cancel_pending_blend_restores_pawn(self):
        edited = self.cpp.replace(
            'PC->SetViewTargetWithBlend(this, 0.f);',
            '/* pending camera blend is never explicitly canceled */')
        with self.assertRaisesRegex(ValueError, "cancel_pending_entry_blend"):
            check_contract(edited, self.header, self.config)

    def test_external_camera_owner_cannot_be_overwritten(self):
        # Both valid cases are explicit: the preview owns the active camera,
        # or the pawn is still active while its preview entry blend is pending.
        restore = self.cpp.split(
            "void ATSTSSExplorerCharacter::RestoreEngineFocusPreview()", 1)[1]
        self.assertIn("PC->GetViewTarget() == Camera", restore)
        self.assertIn("PC->GetViewTarget() == this", restore)
        self.assertNotIn("PC->SetViewTargetWithBlend(this, 0.f);\n        }\n        else", restore)

    def test_lifespan_cleanup_fails(self):
        with self.assertRaisesRegex(ValueError, "camera_cleanup"):
            check_contract(self.cpp.replace("Camera->SetLifeSpan(0.6f);",
                                            "/* preview camera left live */"),
                           self.header, self.config)

    def test_entry_blend_grace_cannot_be_removed(self):
        edited = self.cpp.replace(
            'FPlatformTime::Seconds() - EngineFocusPreviewStartedSeconds > 0.75',
            'false /* ignores camera switch while blending */')
        with self.assertRaisesRegex(ValueError, "blend_entry_grace"):
            check_contract(edited, self.header, self.config)

    def test_exit_must_not_revoke_unowned_coordinator_state(self):
        edited = self.cpp.replace('else if (bHadPreview)',
                                  'else /* invalidates even without camera */')
        with self.assertRaisesRegex(ValueError, "only_cleanup_when_opened"):
            check_contract(edited, self.header, self.config)

    def test_persistent_gameplay_mutation_fails(self):
        insertion = "    SaveFirstWake(TEXT(\"unsafe_auto_save\"));\n"
        marker = "    // Explicit review-only camera cut; never an E-interaction consequence."
        with self.assertRaisesRegex(ValueError, "writes unrelated game state"):
            check_contract(self.cpp.replace(marker, marker + "\n" + insertion),
                           self.header, self.config)


if __name__ == "__main__":
    unittest.main()
