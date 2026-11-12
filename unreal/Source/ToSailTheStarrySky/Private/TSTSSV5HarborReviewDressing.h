#pragma once
// Decorative, unsaved First Wake V5 lookdev. No Actor UCLASS, story,
// equipment, saves, physics gates or production map edits.
class UWorld;
class UMaterialInterface;

namespace TSTSSV5HarborReviewDressing
{
#if WITH_EDITOR
// Requires the exact local, standalone V5 review package and a complete
// previously imported material palette. No partial asset or scene placement.
bool Apply(UWorld* World, UMaterialInterface* Timber,
           UMaterialInterface* Stone, UMaterialInterface* Brass,
           UMaterialInterface* Aether);
#endif
}
