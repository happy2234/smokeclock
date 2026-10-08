
from pathlib import Path

import pandas as pd

from .fire_clusters import cluster_fires
from .trajectory import score_fire_cluster
from src.data.open_meteo_client import fetch_weather


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

    weather = fetch_weather(
        latitude=DELHI_LAT,
        longitude=DELHI_LON,
        forecast_days=2,
    )

    results = []

    for _, cluster in clusters.iterrows():

        transport = score_fire_cluster(
            cluster,
            DELHI_LAT,
            DELHI_LON,
            weather,
        )

        # Prototype analysis window.
        future = transport.iloc[:18].copy()

        aligned = future[
            future["transport_alignment"] > 0
        ]

        if aligned.empty:
            max_alignment = 0.0
            best_eta = None
        else:
            best = aligned.loc[
                aligned["transport_alignment"].idxmax()
            ]

            max_alignment = float(
                best["transport_alignment"]
            )

            best_eta = best["eta_hours"]

        distance_km = float(
            future["distance_km"].iloc[0]
        )

        # Simple prototype transport score.
        #
        # This is NOT the final SmokeClock exposure model.
        score = (
            float(cluster["total_frp"])
            * max_alignment
            / max(distance_km, 1.0)
        )

        results.append(
            {
                "cluster_id": cluster["cluster_id"],
                "latitude": cluster["latitude"],
                "longitude": cluster["longitude"],
                "fire_count": cluster["fire_count"],
                "total_frp": cluster["total_frp"],
                "distance_km": distance_km,
                "max_alignment": max_alignment,
                "best_eta_hours": best_eta,
                "transport_score": score,
            }
        )

    ranking = pd.DataFrame(results)

    ranking = ranking.sort_values(
        "transport_score",
        ascending=False,
    ).reset_index(drop=True)

    print()
    print("SmokeClock — Delhi Transport Ranking")
    print("=" * 80)

    print(
        ranking.to_string(
            index=False,
            float_format=lambda x: f"{x:.2f}",
        )
    )


if __name__ == "__main__":
    main()
