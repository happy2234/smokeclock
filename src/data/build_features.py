from pathlib import Path
import argparse

import numpy as np
import pandas as pd

from src.transport.fire_clusters import cluster_fires_by_hour
from src.transport.trajectory import (
    bearing_degrees,
    haversine_km,
    wind_alignment,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DELHI_LAT = 28.6139
DELHI_LON = 77.2090


def load_pm25(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["datetime"] = (
        pd.to_datetime(df["datetime"], utc=True)
        .dt.tz_convert("Asia/Kolkata")
        .dt.floor("h")
    )

    return (
        df[["datetime", "pm25"]]
        .dropna(subset=["pm25"])
        .groupby("datetime", as_index=False)["pm25"]
        .mean()
        .sort_values("datetime")
    )


def load_weather(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True,
    ).dt.tz_convert("Asia/Kolkata").dt.floor("h")

    return df.sort_values("datetime").reset_index(drop=True)


def load_fires(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["datetime"] = pd.to_datetime(
        df["datetime"],
        utc=True,
    )

    return df


def build_fire_features(
    fires: pd.DataFrame,
    weather: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build hourly fire and transport features.

    Each fire cluster is scored using the wind observed when the
    fire was detected. The resulting transport relevance is then
    carried forward as a causally available rolling feature.

    This is a transport relevance index, not atmospheric concentration.
    """

    clusters = cluster_fires_by_hour(
        fires,
        radius_km=15.0,
        min_samples=2,
    )

    if clusters.empty:
        return pd.DataFrame(columns=[
            "datetime",
            "fire_count",
            "fire_frp",
            "transport_exposure_6h",
            "transport_exposure_24h",
            "transport_exposure_48h",
            "transport_exposure_72h",
        ])

    weather_lookup = weather.set_index("datetime")
    rows = []

    for _, cluster in clusters.iterrows():
        fire_time = cluster["datetime"]

        if fire_time not in weather_lookup.index:
            continue

        weather_row = weather_lookup.loc[fire_time]

        distance = haversine_km(
            cluster["latitude"],
            cluster["longitude"],
            DELHI_LAT,
            DELHI_LON,
        )

        bearing = bearing_degrees(
            cluster["latitude"],
            cluster["longitude"],
            DELHI_LAT,
            DELHI_LON,
        )

        alignment = wind_alignment(
            bearing,
            float(weather_row["wind_direction_10m"]),
        )

        wind_speed_kmh = float(
            weather_row["wind_speed_10m"]
        ) * 3.6

        if wind_speed_kmh > 0 and alignment > 0:
            travel_hours = distance / (
                wind_speed_kmh * alignment
            )
        else:
            travel_hours = np.nan

        # Spatial transport relevance.
        spatial_weight = (
            max(alignment, 0.0)
            / max(distance, 1.0)
        )

        # Convert estimated travel time into a broad,
        # causally available atmospheric-memory weight.
        #
        # This is a modeling heuristic, not a physical
        # dispersion calculation.
        if np.isfinite(travel_hours):
            time_weight = np.exp(
                -0.5 * ((travel_hours - 48.0) / 48.0) ** 2
            )
        else:
            time_weight = 0.0

        exposure = (
            float(cluster["total_frp"])
            * spatial_weight
            * time_weight
        )

        rows.append({
            "datetime": fire_time,
            "fire_count": int(cluster["fire_count"]),
            "fire_frp": float(cluster["total_frp"]),
            "transport_exposure": exposure,
        })

    if not rows:
        return pd.DataFrame(columns=[
            "datetime",
            "fire_count",
            "fire_frp",
            "transport_exposure_6h",
            "transport_exposure_24h",
            "transport_exposure_48h",
            "transport_exposure_72h",
        ])

    hourly = (
        pd.DataFrame(rows)
        .groupby("datetime", as_index=False)
        .agg(
            fire_count=("fire_count", "sum"),
            fire_frp=("fire_frp", "sum"),
            transport_exposure=("transport_exposure", "sum"),
        )
    )

    # Reindex onto every historical hour so rolling windows
    # include hours without detected fires.
    full_hours = pd.DataFrame({
        "datetime": weather["datetime"].sort_values().unique()
    })

    hourly = (
        full_hours
        .merge(hourly, on="datetime", how="left")
        .fillna({
            "fire_count": 0,
            "fire_frp": 0.0,
            "transport_exposure": 0.0,
        })
        .sort_values("datetime")
        .reset_index(drop=True)
    )

    # Only use present and past fire information.
    # No future fire observation can enter a prediction.
    hourly = hourly.set_index("datetime")

    for window, name in [
        (6, "transport_exposure_6h"),
        (24, "transport_exposure_24h"),
        (48, "transport_exposure_48h"),
        (72, "transport_exposure_72h"),
    ]:
        hourly[name] = (
            hourly["transport_exposure"]
            .rolling(
                window=window,
                min_periods=1,
            )
            .sum()
        )

    return (
        hourly
        .reset_index()
        [[
            "datetime",
            "fire_count",
            "fire_frp",
            "transport_exposure_6h",
            "transport_exposure_24h",
            "transport_exposure_48h",
            "transport_exposure_72h",
        ]]
    )

def build_features(
    pm25: pd.DataFrame,
    weather: pd.DataFrame,
    fire_features: pd.DataFrame,
    horizon_hours: int = 6,
) -> pd.DataFrame:
    """
    Build a leakage-safe hourly prediction dataset.

    At time t, features use information available at or before t.
    The target is PM2.5 at t + horizon_hours.
    """

    df = weather.merge(
        pm25,
        on="datetime",
        how="inner",
    )

    df = df.merge(
        fire_features,
        on="datetime",
        how="left",
    )

    fire_columns = [
        "fire_count",
        "fire_frp",
        "transport_exposure_6h",
        "transport_exposure_24h",
        "transport_exposure_48h",
        "transport_exposure_72h",
    ]

    df[fire_columns] = df[fire_columns].fillna(0.0)

    # Lagged PM2.5 features.
    df["pm25_lag_1h"] = df["pm25"].shift(1)
    df["pm25_lag_3h"] = df["pm25"].shift(3)
    df["pm25_lag_6h"] = df["pm25"].shift(6)

    # Future target.
    df["target_pm25"] = df["pm25"].shift(-horizon_hours)

    return (
        df.dropna(
            subset=[
                "pm25_lag_6h",
                "target_pm25",
            ]
        )
        .sort_values("datetime")
        .reset_index(drop=True)
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--horizon",
        type=int,
        choices=[6, 12, 24],
        default=6,
        help="Forecast horizon in hours",
    )
    args = parser.parse_args()

    pm25_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "openaq"
        / "october_2025.csv"
    )

    weather_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "weather"
        / "october_2025.csv"
    )

    fires_path = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "firms"
        / "october_2025.csv"
    )

    output_path = (
        PROJECT_ROOT
        / "data"
        / "processed"
        / "features"
        / f"october_2025_{args.horizon}h.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pm25 = load_pm25(pm25_path)
    weather = load_weather(weather_path)
    fires = load_fires(fires_path)

    fire_features = build_fire_features(
        fires,
        weather,
    )

    dataset = build_features(
        pm25,
        weather,
        fire_features,
        horizon_hours=args.horizon,
    )

    dataset.to_csv(
        output_path,
        index=False,
    )

    print(f"PM2.5 rows: {len(pm25):,}")
    print(f"Weather rows: {len(weather):,}")
    print(f"Fire detections: {len(fires):,}")
    print(f"Fire feature hours: {len(fire_features):,}")
    print(f"Feature rows: {len(dataset):,}")
    print(f"Saved: {output_path}")
    print()
    print(dataset.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
