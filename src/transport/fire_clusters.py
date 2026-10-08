from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


EARTH_RADIUS_KM = 6371.0088


def cluster_fires(
    fires: pd.DataFrame,
    radius_km: float = 15.0,
    min_samples: int = 2,
) -> pd.DataFrame:
    """
    Cluster nearby FIRMS fire detections using DBSCAN.

    Distance is measured using the haversine metric.

    Parameters
    ----------
    fires:
        FIRMS detections containing latitude, longitude and FRP.
    radius_km:
        Maximum distance between nearby detections in a cluster.
    min_samples:
        Minimum number of detections required to form a cluster.

    Returns
    -------
    pandas.DataFrame
        One row per fire cluster.
    """

    required = {"latitude", "longitude", "frp"}

    missing = required - set(fires.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data = fires.dropna(
        subset=["latitude", "longitude", "frp"]
    ).copy()

    if data.empty:
        return pd.DataFrame()

    coordinates = np.radians(
        data[["latitude", "longitude"]].to_numpy()
    )

    model = DBSCAN(
        eps=radius_km / EARTH_RADIUS_KM,
        min_samples=min_samples,
        metric="haversine",
    )

    labels = model.fit_predict(coordinates)
    data["cluster_id"] = labels

    clusters = []

    for cluster_id, group in data.groupby("cluster_id"):

        # -1 is DBSCAN noise.
        # Keep it as an individual source rather than throwing it away.
        if cluster_id == -1:
            for _, row in group.iterrows():
                clusters.append(
                    {
                        "cluster_id": f"noise_{row.name}",
                        "latitude": row["latitude"],
                        "longitude": row["longitude"],
                        "fire_count": 1,
                        "total_frp": row["frp"],
                        "max_frp": row["frp"],
                        "frp_weighted": False,
                    }
                )
            continue

        weights = group["frp"].clip(lower=0.01).to_numpy()

        latitude = np.average(
            group["latitude"].to_numpy(),
            weights=weights,
        )

        longitude = np.average(
            group["longitude"].to_numpy(),
            weights=weights,
        )

        clusters.append(
            {
                "cluster_id": int(cluster_id),
                "latitude": latitude,
                "longitude": longitude,
                "fire_count": len(group),
                "total_frp": group["frp"].sum(),
                "max_frp": group["frp"].max(),
                "frp_weighted": True,
            }
        )

    result = pd.DataFrame(clusters)

    if not result.empty:
        result = result.sort_values(
            "total_frp",
            ascending=False,
        ).reset_index(drop=True)

    return result


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parents[2]

    input_file = (
        project_root
        / "data"
        / "raw"
        / "firms"
        / "fires_latest.csv"
    )

    output_dir = (
        project_root
        / "data"
        / "processed"
        / "firms"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    fires = pd.read_csv(input_file)

    clusters = cluster_fires(
        fires,
        radius_km=15,
        min_samples=2,
    )

    output_file = output_dir / "fire_clusters_latest.csv"

    clusters.to_csv(output_file, index=False)

    print(f"Input detections: {len(fires):,}")
    print(f"Fire clusters:    {len(clusters):,}")
    print()
    print(clusters.to_string(index=False))
