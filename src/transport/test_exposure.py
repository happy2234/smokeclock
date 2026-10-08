from pathlib import Path

import pandas as pd

from .fire_clusters import cluster_fires
from .trajectory_engine import (
    calculate_exposure,
    interpolate_path,
)
from src.data.open_meteo_client import (
    fetch_weather_points,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DELHI_LAT = 28.6139
DELHI_LON = 77.2090


def main():

    fires_file = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "firms"
        / "fires_latest.csv"
    )

    fires = pd.read_csv(fires_file)

    clusters = cluster_fires(
        fires,
        radius_km=15,
        min_samples=2,
    )

    cluster = clusters.iloc[0]

    path = interpolate_path(
        cluster["latitude"],
        cluster["longitude"],
        DELHI_LAT,
        DELHI_LON,
        points=12,
    )

    print("Trajectory sampling points:")
    for i, point in enumerate(path):
        print(
            f"{i:02d}: "
            f"lat={point[0]:.4f}, "
            f"lon={point[1]:.4f}"
        )

    print("\nFetching weather fields...")

    weather = fetch_weather_points(
        path,
        forecast_days=2,
    )

    print(
        f"Weather points retrieved: {len(weather)}"
    )

    exposure = calculate_exposure(
        cluster=cluster,
        weather_points=weather,
        target_lat=DELHI_LAT,
        target_lon=DELHI_LON,
    )

    print("\nTransport exposure:")
    print(
        exposure.head(24).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
