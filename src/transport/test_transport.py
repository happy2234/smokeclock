from pathlib import Path

import pandas as pd


from .fire_clusters import cluster_fires
from .trajectory import score_fire_cluster
from src.data.open_meteo_client import fetch_weather


PROJECT_ROOT = Path(__file__).resolve().parents[2]

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

# Strongest fire cluster
cluster = clusters.iloc[0]

# Delhi
DELHI_LAT = 28.6139
DELHI_LON = 77.2090

weather = fetch_weather(
    latitude=DELHI_LAT,
    longitude=DELHI_LON,
    forecast_days=2,
)

transport = score_fire_cluster(
    cluster,
    DELHI_LAT,
    DELHI_LON,
    weather,
)

print("Selected fire cluster:")
print(cluster.to_string())

print("\nTransport analysis:")
print(
    transport[
        [
            "time",
            "distance_km",
            "bearing_to_target",
            "wind_speed_kmh",
            "wind_direction_from",
            "transport_alignment",
            "eta_hours",
            "boundary_layer_height_m",
        ]
    ].head(24).to_string(index=False)
)
