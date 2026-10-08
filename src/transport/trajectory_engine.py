from math import cos, radians, sin
from typing import List, Tuple

from .trajectory import haversine_km

import numpy as np
import pandas as pd


def interpolate_path(
    source_lat: float,
    source_lon: float,
    target_lat: float,
    target_lon: float,
    points: int = 12,
) -> List[Tuple[float, float]]:
    """
    Create approximate geographic points between source and target.

    This is a sampling path, not yet a dynamically integrated trajectory.
    """

    latitudes = np.linspace(
        source_lat,
        target_lat,
        points,
    )

    longitudes = np.linspace(
        source_lon,
        target_lon,
        points,
    )

    return list(zip(latitudes, longitudes))


def wind_to_uv(
    speed_kmh: float,
    direction_from: float,
) -> tuple[float, float]:
    """
    Convert meteorological wind direction into transport vector.

    direction_from:
        Direction wind comes FROM.

    Returns:
        u = eastward component
        v = northward component
    """

    direction_to = radians(
        (direction_from + 180) % 360
    )

    u = speed_kmh * sin(direction_to)
    v = speed_kmh * cos(direction_to)

    return float(u), float(v)


def transport_alignment(
    source_lat: float,
    source_lon: float,
    target_lat: float,
    target_lon: float,
    wind_speed_kmh: float,
    wind_direction_from: float,
) -> float:
    """
    Calculate alignment between wind transport and
    source-to-target direction.
    """

    dlat = target_lat - source_lat

    # Correct longitude distance for latitude.
    dlon = (
        target_lon - source_lon
    ) * cos(
        radians(
            (source_lat + target_lat) / 2
        )
    )

    distance = np.hypot(
        dlat,
        dlon,
    )

    if distance == 0:
        return 1.0

    target_x = dlon / distance
    target_y = dlat / distance

    u, v = wind_to_uv(
        wind_speed_kmh,
        wind_direction_from,
    )

    wind_norm = np.hypot(
        u,
        v,
    )

    if wind_norm == 0:
        return 0.0

    wind_x = u / wind_norm
    wind_y = v / wind_norm

    return float(
        np.clip(
            target_x * wind_x
            + target_y * wind_y,
            -1.0,
            1.0,
        )
    )


def distance_decay(
    distance_km: float,
    scale_km: float = 250.0,
) -> float:
    """
    Smooth distance attenuation.

    This represents the decreasing influence of a fire
    source with increasing distance.

    It is a relative weighting, not a physical concentration.
    """

    distance_km = max(
        float(distance_km),
        0.0,
    )

    return float(
        np.exp(
            -distance_km / scale_km
        )
    )


def puff_spread(
    age_hours: float,
    initial_sigma_km: float = 5.0,
    growth_km_per_sqrt_hour: float = 12.0,
) -> float:
    """
    Approximate horizontal plume width.

    sigma grows approximately with sqrt(time).

    Returns sigma in km.
    """

    age_hours = max(
        float(age_hours),
        0.0,
    )

    return float(
        initial_sigma_km
        + growth_km_per_sqrt_hour
        * np.sqrt(age_hours)
    )


def gaussian_puff_weight(
    crosswind_distance_km: float,
    sigma_km: float,
) -> float:
    """
    Gaussian crosswind weighting.

    Maximum = 1 directly on the plume centerline.
    """

    sigma_km = max(
        float(sigma_km),
        0.1,
    )

    return float(
        np.exp(
            -0.5
            * (
                crosswind_distance_km
                / sigma_km
            ) ** 2
        )
    )


def crosswind_distance(
    source_lat: float,
    source_lon: float,
    point_lat: float,
    point_lon: float,
    wind_direction_from: float,
) -> float:
    """
    Estimate perpendicular distance between a sampled point
    and the wind transport centerline originating at the source.

    Returns distance in km.

    This is an approximate local-plane calculation suitable
    for the prototype exposure index.
    """

    mean_lat = radians(
        (source_lat + point_lat) / 2
    )

    dx = (
        point_lon - source_lon
    ) * 111.32 * cos(mean_lat)

    dy = (
        point_lat - source_lat
    ) * 111.32

    # Wind transport direction is opposite the
    # meteorological "from" direction.
    direction_to = radians(
        (wind_direction_from + 180) % 360
    )

    wind_x = sin(direction_to)
    wind_y = cos(direction_to)

    # Perpendicular unit vector.
    cross_x = -wind_y
    cross_y = wind_x

    distance = abs(
        dx * cross_x
        + dy * cross_y
    )

    return float(distance)


def calculate_exposure(
    cluster: pd.Series,
    weather_points: dict,
    target_lat: float,
    target_lon: float,
) -> pd.DataFrame:
    """
    Estimate transport-weighted exposure from one fire cluster.

    This is a prototype exposure index, NOT a physical
    atmospheric concentration model.
    """

    path = interpolate_path(
        source_lat=cluster["latitude"],
        source_lon=cluster["longitude"],
        target_lat=target_lat,
        target_lon=target_lon,
        points=12,
    )

    rows = []

    weather_reference = next(
        iter(weather_points.values())
    )

    for timestamp_index in range(
        len(weather_reference)
    ):

        total_exposure = 0.0
        weighted_alignment = 0.0
        valid_segments = 0

        for lat, lon in path:

            key = min(
                weather_points,
                key=lambda p: (
                    (p[0] - lat) ** 2
                    + (p[1] - lon) ** 2
                ),
            )

            weather = weather_points[key]

            row = weather.iloc[
                timestamp_index
            ]

            wind_speed_kmh = max(
                float(
                    row["wind_speed_10m"]
                ) * 3.6,
                1.0,
            )

            wind_direction_from = float(
                row["wind_direction_10m"]
            )

            alignment = transport_alignment(
                cluster["latitude"],
                cluster["longitude"],
                target_lat,
                target_lon,
                wind_speed_kmh,
                wind_direction_from,
            )

            # Wind pointing away from the target
            # should not contribute to exposure.
            if alignment <= 0:
                continue

            positive_alignment = float(
                alignment
            )

            # Larger boundary layer = more dilution.
            blh = max(
                float(
                    row["boundary_layer_height"]
                ),
                100.0,
            )

            dilution = (
                1.0
                / np.sqrt(blh)
            )

            distance_from_source = haversine_km(
                cluster["latitude"],
                cluster["longitude"],
                lat,
                lon,
            )

            decay = distance_decay(
                distance_from_source
            )

            # Approximate plume age using
            # distance / wind speed.
            age_hours = (
                distance_from_source
                / wind_speed_kmh
            )

            sigma_km = puff_spread(
                age_hours
            )

            # Calculate how far the sampled point is
            # from the wind-aligned plume centerline.
            crosswind_km = crosswind_distance(
                cluster["latitude"],
                cluster["longitude"],
                lat,
                lon,
                wind_direction_from,
            )

            puff_weight = gaussian_puff_weight(
                crosswind_km,
                sigma_km,
            )

            segment_exposure = (
                float(
                    cluster["total_frp"]
                )
                * positive_alignment
                * decay
                * puff_weight
                * dilution
            )

            total_exposure += (
                segment_exposure
            )

            weighted_alignment += (
                alignment
            )

            valid_segments += 1

        if valid_segments:
            mean_alignment = (
                weighted_alignment
                / valid_segments
            )
        else:
            mean_alignment = 0.0

        rows.append(
            {
                "time": weather_reference.iloc[
                    timestamp_index
                ]["time"],
                "transport_exposure": (
                    total_exposure
                ),
                "mean_alignment": (
                    mean_alignment
                ),
                "valid_segments": (
                    valid_segments
                ),
            }
        )

    return pd.DataFrame(rows)
