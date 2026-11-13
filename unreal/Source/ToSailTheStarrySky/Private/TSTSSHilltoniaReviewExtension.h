#pragma once
// Hilltonia's temperate small-town approach: unsaved, review-only spatial
// extension adjoining the inland end of the First Wake V5 harbor. The town
// geography is proposed lookdev, not a final world-coordinate canon claim.
// No story progression, ship authority, save data or production maps change.

class UWorld;
class UMaterialInterface;

namespace TSTSSHilltoniaReviewExtension
{
#if WITH_EDITOR
// A genuine WorldStatic road outside the seven-marker harbor corridor,
// flanked by decorative town and deciduous forest. No gameplay shortcuts.
// Returns false on a wrong map, a duplicate actor, or missing materials.
bool Apply(UWorld* World, UMaterialInterface* Timber,
           UMaterialInterface* Stone, UMaterialInterface* Brass,
           UMaterialInterface* Canopy);
#endif
}
