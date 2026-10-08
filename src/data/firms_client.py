import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


FIRMS_MAP_KEY = os.getenv("FIRMS_MAP_KEY")

if not FIRMS_MAP_KEY:
    raise RuntimeError(
        "FIRMS_MAP_KEY is missing. Add it to ~/smokeclock/.env"
    )


BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"


def fetch_fires(
    west: float,
    south: float,
    east: float,
    north: float,
    source: str = "VIIRS_NOAA21_NRT",
    days: int = 1,
) -> pd.DataFrame:
    """
    Download FIRMS fire detections for a geographic bounding box.

    Parameters
    ----------
    west, south, east, north:
        Bounding box coordinates.
    source:
        FIRMS satellite/product source.
    days:
        Number of recent days to request (1-5).

    Returns
    -------
    pandas.DataFrame
        FIRMS fire detections.
    """

    if not 1 <= days <= 5:
        raise ValueError("FIRMS API allows 1-5 days per area request.")

    area = f"{west},{south},{east},{north}"

    url = f"{BASE_URL}/{FIRMS_MAP_KEY}/{source}/{area}/{days}"

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    # FIRMS returns CSV
    from io import StringIO

    return pd.read_csv(StringIO(response.text))


if __name__ == "__main__":
    # Punjab + Haryana + Delhi-NCR test region
    df = fetch_fires(
        west=73.5,
        south=27.5,
        east=78.5,
        north=32.5,
        source="VIIRS_NOAA21_NRT",
        days=1,
    )

    print(f"Downloaded {len(df):,} fire detections")

    if not df.empty:
        print("\nColumns:")
        print(df.columns.tolist())

        print("\nFirst 5 detections:")
        print(df.head().to_string(index=False))
