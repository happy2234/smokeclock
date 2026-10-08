from math import cos, radians
from typing import List, Tuple

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

    u = speed_kmh * np.sin(direction_to)
    v = speed_kmh * np.cos(direction_to)

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
    ) * cos(radians((source_lat + target_lat) / 2))

    distance = np.hypot(dlat, dlon)

    if distance == 0:
        return 1.0

    target_x = dlon / distance
    target_y = dlat / distance

    u, v = wind_to_uv(
        wind_speed_kmh,
        wind_direction_from,
    )

    wind_norm = np.hypot(u, v)

    if wind_norm == 0:
        return 0.0

    wind_x = u / wind_norm
    wind_y = v / wind_norm

    return float(
        np.clip(
            target_x * wind_x + target_y * wind_y,
            -1.0,
            1.0,
        )
    )


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

    for timestamp_index in range(
        len(next(iter(weather_points.values())))
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

            row = weather.iloc[timestamp_index]

            alignment = transport_alignment(
                cluster["latitude"],
                cluster["longitude"],
                target_lat,
                target_lon,
                row["wind_speed_10m"] * 3.6,
                row["wind_direction_10m"],
            )

            if alignment <= 0:
                continue

            # Larger boundary layer = more dilution.
            blh = max(
                float(row["boundary_layer_height"]),
                100.0,
            )

            dilution = 1.0 / np.sqrt(blh)

            segment_exposure = (
                float(cluster["total_frp"])
                * alignment
                * dilution
            )

            total_exposure += segment_exposure
            weighted_alignment += alignment
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
                "time": next(
                    iter(weather_points.values())
                ).iloc[timestamp_index]["time"],
                "transport_exposure": total_exposure,
                "mean_alignment": mean_alignment,
                "valid_segments": valid_segments,
            }
        )

    return pd.DataFrame(rows)
