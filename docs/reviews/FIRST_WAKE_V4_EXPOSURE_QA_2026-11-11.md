# First Wake V4 — exposure failure and corrected rotation evidence

**Status:** REVIEW-ONLY, NOT APPROVED, NOT ROUTED, NOT MERGED.
**Authoring commit:** `134e9c93c022e6191cf130cdf2037eca2e31d093`
**Map:** `/Game/TSTSS/Review/FirstWake_PreludeInteraction_V4_VisualReview`
**Native map SHA-256:** `ac3b2f8d2e65cb65c7f0e3191d48d4495ea174e6c688d22b95fdca912697575d`
**Original V2 SHA-256 unchanged:** `4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80`

Native authoring exited 0 and saved the V4 map (72,305 bytes). UE 5.8.4 native readback verified the flyer sign rotation as `pitch=0,yaw=180,roll=0`, and the sun key rotation as `pitch=-43,yaw=138,roll=0`. This confirms that explicit named Rotator fields repaired the V3 misorientation.

**Visual QA FAIL:** A real D3D11 standalone render revealed a severely overexposed white world. The frame did not establish readable signs, topology or atmospheric depth. Runtime-only CVar tests `r.EyeAdaptationQuality=0`, `r.SkyAtmosphere=0`, and `r.Fog=0` did not restore a correctly exposed scene. The original harbor-day sunlight value of 75,000 lux was not tolerable under this review project's current exposure configuration; this is a working hypothesis, not a final calibrated diagnosis.

[Standalone V4 exposure failure](assets/firstwake_v4_whiteout.png)

**Next isolated change:** Stage V5 from source V2 (not from the defective V4 map) with conservative daylight intensity, lower ambient fill and explicit exposure compensation. Revalidate screenshot and sign readability before changing any title route. Keep production maps, saves, story gates and roster unchanged.
