import os
from io import StringIO

import pandas as pd
import requests
from dotenv import load_dotenv


BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

# Punjab + Haryana + nearby upwind region.
DEFAULT_BBOX = (73.5, 28.0, 77.5, 32.5)


def fetch_historical_fires(
    start_date: str,
    end_date: str,
    bbox: tuple[float, float, float, float] = DEFAULT_BBOX,
    satellite: str = "VIIRS_SNPP_SP",
) -> pd.DataFrame:
    """Fetch historical VIIRS fire detections from NASA FIRMS.

    bbox format:
        (west, south, east, north)
    """

    load_dotenv(dotenv_path=".env")

    key = os.getenv("FIRMS_MAP_KEY")
    if not key:
        raise RuntimeError("FIRMS_MAP_KEY is not configured")

    west, south, east, north = bbox
    bbox_string = f"{west},{south},{east},{north}"

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    frames = []

    # FIRMS area API allows at most 5 days per request.
    current = start

    while current <= end:
        chunk_end = min(current + pd.Timedelta(days=4), end)
        day_range = (chunk_end - current).days + 1

        url = (
            f"{BASE_URL}/{key}/{satellite}/"
            f"{bbox_string}/{day_range}/{current:%Y-%m-%d}"
        )

        response = requests.get(url, timeout=60)
        response.raise_for_status()

        if response.text.strip():
            chunk = pd.read_csv(StringIO(response.text))

            if not chunk.empty:
                frames.append(chunk)

        current = chunk_end + pd.Timedelta(days=1)

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)

    # FIRMS acq_time is HHMM in UTC.
    df["acq_time"] = df["acq_time"].astype(str).str.zfill(4)

    df["datetime"] = pd.to_datetime(
        df["acq_date"].astype(str)
        + " "
        + df["acq_time"].str[:2]
        + ":"
        + df["acq_time"].str[2:]
        ,
        utc=True,
    )

    return (
        df.sort_values("datetime")
        .reset_index(drop=True)
    )
