"""D3D11 sky lighting review custody; cosmetic-only, never source of water/story proof."""
import unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
CPP=(R/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
SKY=CPP.split("void ATSTSSExplorerCharacter::BeginPrivateSkyStormReview()",1)[1].split(
    "void ATSTSSExplorerCharacter::PrivateStormSecureLift()",1)[0]
DIRECTOR=(R/"Source/ToSailTheStarrySky/Private/TSTSSAtmosphereDirector.cpp").read_text(encoding="utf8")
BUILD=(R/"Tools/build_vertical_slice_environment_maps.py").read_text(encoding="utf8")

class LightingCustody(unittest.TestCase):
    def test_existing_map_sun_is_authored(self):
        self.assertIn('spawn(unreal.DirectionalLight, "SunKey"',BUILD)
        self.assertIn('spawn(unreal.SkyLight, "SkyAmbient"',BUILD)
        self.assertIn("CreateDefaultSubobject<UDirectionalLightComponent>",DIRECTOR)
        self.assertIn("CreateDefaultSubobject<USkyLightComponent>",DIRECTOR)

    def test_exact_private_storm_scope_is_retained(self):
        self.assertIn("if (!IsPrivateSkyStormReviewWorld() || bPrivateSkyStormStarted)",SKY)
        self.assertIn("TSTSSPrivateSkyStormResponseReview",CPP)
        self.assertIn('IsPrivateSkyStormReviewWorld()',CPP)

    def test_only_transient_director_components_can_be_suppressed(self):
        for token in ('TActorIterator<ADirectionalLight>','bSpawned && bAuthoredSunExists',
                      'Atmosphere->GetComponents<ULightComponentBase>(PrivateLights)',
                      'Atmosphere->GetComponents<USkyAtmosphereComponent>(PrivateSkies)',
                      'Light->SetVisibility(false)', 'Sky->SetVisibility(false)',
                      'original_lights_untouched=1'):
            self.assertIn(token,SKY)
        self.assertNotIn("It->SetVisibility",SKY)
        self.assertNotIn("It->Destroy",SKY)
        self.assertNotIn('GetComponents<ULightComponentBase>(World',SKY)

    def test_weather_story_physics_unchanged(self):
        for x in ('Atmosphere->RequestWeather(ETSTSSWeather::Storm, 2.5f)',
                  'Atmosphere->RequestTimeOfDay(19.0f, 3.0f)',
                  'TSTSS_PRIVATE_SKY_STORM_START beat=4 mask=7'):
            self.assertIn(x,SKY)
        for x in ('AdvanceTo(', 'OpenLevel(', 'SaveGame(', 'SetActorLocation(',
                  'TeleportTo(', 'SetSimulatePhysics(', 'SetActorTransform(',
                  'SetWorldLocation(', 'SetIntensity('):
            self.assertNotIn(x,SKY)

if __name__=="__main__":unittest.main()
