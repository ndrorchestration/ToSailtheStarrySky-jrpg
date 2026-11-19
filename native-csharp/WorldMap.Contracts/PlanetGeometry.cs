using System;

namespace StarrySky.WorldMap.Contracts;

/// <summary>
/// Pure spherical-navigation functions. They make no claims about the actual
/// size, geography, gravity, weather, collision or art of the game planet.
/// Every radius must be provided explicitly by the caller (km).
/// </summary>
public static class PlanetGeometry
{
    private const double ToRadians = Math.PI / 180.0;
    private const double ToDegrees = 180.0 / Math.PI;

    public static double RequireRadius(double radiusKm)
    {
        if (!double.IsFinite(radiusKm) || radiusKm <= 0)
            throw new ArgumentOutOfRangeException(nameof(radiusKm));
        return radiusKm;
    }

    public static double AngularSeparationRadians(PlanetPosition a, PlanetPosition b)
    {
        double lat1 = a.LatitudeDegrees * ToRadians;
        double lat2 = b.LatitudeDegrees * ToRadians;
        double deltaLat = lat2 - lat1;
        double deltaLon = (b.LongitudeDegrees - a.LongitudeDegrees) * ToRadians;
        double x = Math.Pow(Math.Sin(deltaLat / 2.0), 2)
            + Math.Cos(lat1) * Math.Cos(lat2)
            * Math.Pow(Math.Sin(deltaLon / 2.0), 2);
        return 2.0 * Math.Asin(Math.Sqrt(Math.Clamp(x, 0.0, 1.0)));
    }

    public static double SurfaceDistanceKm(PlanetPosition a, PlanetPosition b, double radiusKm)
        => RequireRadius(radiusKm) * AngularSeparationRadians(a, b);

    public static double HorizonAngleRadians(double altitudeKm, double radiusKm)
    {
        RequireRadius(radiusKm);
        if (!double.IsFinite(altitudeKm) || altitudeKm < 0)
            throw new ArgumentOutOfRangeException(nameof(altitudeKm));
        return Math.Acos(Math.Clamp(radiusKm / (radiusKm + altitudeKm), 0.0, 1.0));
    }

    /// <summary>Distance along a spherical surface to the geometric horizon.</summary>
    public static double HorizonSurfaceDistanceKm(double altitudeKm, double radiusKm)
        => RequireRadius(radiusKm) * HorizonAngleRadians(altitudeKm, radiusKm);

    /// <summary>
    /// An intentionally geometry-only line-of-sight gate. It does not model
    /// refractive effects, elevation, buildings, weather or terrain relief.
    /// </summary>
    public static bool HasGeometricLineOfSight(PlanetPosition observer, PlanetPosition target, double radiusKm)
    {
        double limit = HorizonAngleRadians(observer.AltitudeKm, radiusKm)
            + HorizonAngleRadians(target.AltitudeKm, radiusKm);
        return AngularSeparationRadians(observer, target) <= Math.Min(Math.PI, limit) + 1e-12;
    }

    /// <summary>
    /// Returns false rather than inventing a heading for coincident or
    /// antipodal points. Bearing is clockwise from true north.
    /// </summary>
    public static bool TryInitialBearingDegrees(PlanetPosition a, PlanetPosition b, out double degrees)
    {
        double lat1 = a.LatitudeDegrees * ToRadians;
        double lat2 = b.LatitudeDegrees * ToRadians;
        double deltaLon = (b.LongitudeDegrees - a.LongitudeDegrees) * ToRadians;
        double east = Math.Sin(deltaLon) * Math.Cos(lat2);
        double north = Math.Cos(lat1) * Math.Sin(lat2)
            - Math.Sin(lat1) * Math.Cos(lat2) * Math.Cos(deltaLon);
        if (Math.Sqrt(east * east + north * north) < 1e-11)
        {
            degrees = 0;
            return false;
        }
        degrees = (Math.Atan2(east, north) * ToDegrees + 360) % 360;
        return true;
    }

    public static PlanetPosition Destination(PlanetPosition start, double bearingDegrees,
        double distanceKm, double radiusKm)
    {
        RequireRadius(radiusKm);
        if (!double.IsFinite(bearingDegrees))
            throw new ArgumentOutOfRangeException(nameof(bearingDegrees));
        if (!double.IsFinite(distanceKm) || distanceKm < 0 || distanceKm > Math.PI * radiusKm)
            throw new ArgumentOutOfRangeException(nameof(distanceKm));
        if (distanceKm == 0)
            return start;
        double arc = distanceKm / radiusKm;
        double theta = bearingDegrees * ToRadians;
        double lat1 = start.LatitudeDegrees * ToRadians;
        double lon1 = start.LongitudeDegrees * ToRadians;

        double sinLat2 = Math.Sin(lat1) * Math.Cos(arc)
            + Math.Cos(lat1) * Math.Sin(arc) * Math.Cos(theta);
        double lat2 = Math.Asin(Math.Clamp(sinLat2, -1.0, 1.0));
        double lon2 = lon1 + Math.Atan2(
            Math.Sin(theta) * Math.Sin(arc) * Math.Cos(lat1),
            Math.Cos(arc) - Math.Sin(lat1) * Math.Sin(lat2));
        return new PlanetPosition(lat2 * ToDegrees, lon2 * ToDegrees, start.AltitudeKm);
    }
}
