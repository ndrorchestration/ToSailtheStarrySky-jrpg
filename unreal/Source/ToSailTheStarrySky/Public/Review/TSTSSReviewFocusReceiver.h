#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CineCameraSettings.h"
#include "Review/TSTSSPresentationCoordinatorSubsystem.h"
#include "TimerManager.h"
#include "TSTSSReviewFocusReceiver.generated.h"

class ACineCameraActor;
class UCineCameraComponent;

/**
 * Opt-in review-only lens owner for an independently staged engine room camera.
 * NEVER activates the player's view, changes map/story/physics/weather,
 * spawns any actors, edits Post Process Volumes, or emits audio.
 *
 * OFF by default. Only works with an explicitly assigned camera whose
 * label starts TSTSS_BOKEH_ENGINE_REVIEW_ in an Unreal PIE world.
 */
UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSReviewFocusReceiver : public AActor
{
    GENERATED_BODY()

public:
    ATSTSSReviewFocusReceiver();

    UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category="TSTSS|Bokeh|Review")
    bool bExplicitReviewOptIn = false;

    UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category="TSTSS|Bokeh|Review")
    TObjectPtr<ACineCameraActor> StagedReviewCamera = nullptr;

    /** Existing source-authored engine/gauge proxy; NEVER the player pawn. */
    UPROPERTY(EditInstanceOnly, BlueprintReadOnly, Category="TSTSS|Bokeh|Review")
    TObjectPtr<AActor> AuthoredEngineFocusAnchor = nullptr;

    /** Called only by an intentional review scene action, never the E pawn adapter. */
    UFUNCTION(BlueprintCallable, Category="TSTSS|Bokeh|Review")
    bool RequestAuthoredEngineFocus(ETSTSSPresentationMoment Moment);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Bokeh|Review")
    void RestoreReviewCamera();

    UFUNCTION(BlueprintPure, Category="TSTSS|Bokeh|Review")
    bool HasAppliedReviewLens() const { return bHasSavedLens; }

    /** Stateless policy used by the existing locked automation-test identity. */
    static bool IsFocusCueApplicable(const FTSTSSPresentationIntent& Intent,
                                      ETSTSSPresentationMoment Moment,
                                      bool bExplicitlyEnabled, bool bPIE);

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UFUNCTION()
    void ReceivePresentationIntent(const FTSTSSPresentationIntent& Intent);

    bool IsAuthenticReviewCamera() const;
    bool ApplyBoundedLens(const FTSTSSPresentationIntent& Intent);
    void VerifyActiveSource();

    TWeakObjectPtr<UTSTSSPresentationCoordinatorSubsystem> BoundCoordinator;
    FCameraFocusSettings OriginalFocus;
    float OriginalFocalLength = 0.0f;
    float OriginalAperture = 0.0f;
    bool bHasSavedLens = false;
    FTimerHandle FocusGuardTimer;
};
