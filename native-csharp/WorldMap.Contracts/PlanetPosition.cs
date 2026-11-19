using System;

namespace StarrySky.WorldMap.Contracts;

/// <summary>
/// Engine-neutral spherical coordinate contract; never binds a canonical planet
/// radius, shore, location, ship or story route. Latitude/longitude in degrees,
/// altitude in kilometres. Longitude is normalized to [-180, 180).
/// </summary>
public readonly record struct PlanetPosition
{
    public double LatitudeDegrees { get; }
    public double LongitudeDegrees { get; }
    public double AltitudeKm { get; }

    public PlanetPosition(double latitudeDegrees, double longitudeDegrees, double altitudeKm = 0)
    {
        if (!double.IsFinite(latitudeDegrees) || latitudeDegrees < -90 || latitudeDegrees > 90)
            throw new ArgumentOutOfRangeException(nameof(latitudeDegrees));
        if (!double.IsFinite(longitudeDegrees))
            throw new ArgumentOutOfRangeException(nameof(longitudeDegrees));
        if (!double.IsFinite(altitudeKm) || altitudeKm < 0)
            throw new ArgumentOutOfRangeException(nameof(altitudeKm));

        LatitudeDegrees = latitudeDegrees;
        // Modulo is safe here after finite checks and does not change latitude.
        var wrapped = (longitudeDegrees % 360.0 + 540.0) % 360.0 - 180.0;
        LongitudeDegrees = Math.Abs(latitudeDegrees) == 90.0 ? 0.0 : wrapped;
        AltitudeKm = altitudeKm;
    }
}
