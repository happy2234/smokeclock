from math import asin, atan2, cos, degrees, radians, sin, sqrt

import pandas as pd


EARTH_RADIUS_KM = 6371.0088


def haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Great-circle distance between two coordinates."""

    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))


def bearing_degrees(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Initial bearing from point 1 to point 2.

    0° = north
    90° = east
    180° = south
    270° = west
    """

    lat1, lat2 = radians(lat1), radians(lat2)
    dlon = radians(lon2 - lon1)

    x = sin(dlon) * cos(lat2)

    y = (
        cos(lat1) * sin(lat2)
        - sin(lat1) * cos(lat2) * cos(dlon)
    )

    return (degrees(atan2(x, y)) + 360) % 360


def angular_difference(a: float, b: float) -> float:
    """Smallest absolute difference between two directions."""

    return abs((a - b + 180) % 360 - 180)


def wind_alignment(
    source_to_target_bearing: float,
    wind_direction_from: float,
) -> float:
    """
    Calculate how strongly wind carries air from source toward target.

    Meteorological wind direction describes where the wind comes FROM,
    while transport follows the opposite direction.

    Returns:
        1.0  = perfectly aligned
        0.0  = perpendicular
       -1.0  = directly opposing
    """

    transport_direction = (wind_direction_from + 180) % 360

    difference = angular_difference(
        source_to_target_bearing,
        transport_direction,
    )

    return cos(radians(difference))


def estimate_eta_hours(
    distance_km: float,
    wind_speed_kmh: float,
    alignment: float,
) -> float | None:
    """
    Estimate travel time for an air parcel.

    This is intentionally a simple prototype, not a dispersion model.
    """

    effective_speed = wind_speed_kmh * max(alignment, 0.0)

    if effective_speed <= 0:
        return None

    return distance_km / effective_speed


def score_fire_cluster(
    cluster: pd.Series,
    target_lat: float,
    target_lon: float,
    weather: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate transport relevance of one fire cluster
    for a target location.
    """

    distance = haversine_km(
        cluster["latitude"],
        cluster["longitude"],
        target_lat,
        target_lon,
    )

    bearing = bearing_degrees(
        cluster["latitude"],
        cluster["longitude"],
        target_lat,
        target_lon,
    )

    rows = []

    for _, weather_row in weather.iterrows():

        wind_speed_kmh = weather_row["wind_speed_10m"] * 3.6

        alignment = wind_alignment(
            bearing,
            weather_row["wind_direction_10m"],
        )

        eta = estimate_eta_hours(
            distance,
            wind_speed_kmh,
            alignment,
        )

        rows.append(
            {
                "time": weather_row["time"],
                "distance_km": distance,
                "bearing_to_target": bearing,
                "wind_speed_kmh": wind_speed_kmh,
                "wind_direction_from": weather_row[
                    "wind_direction_10m"
                ],
                "transport_alignment": alignment,
                "eta_hours": eta,
                "boundary_layer_height_m": weather_row[
                    "boundary_layer_height"
                ],
            }
        )

    return pd.DataFrame(rows)
