import os
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
from dotenv import load_dotenv


BASE_URL = "https://api.openaq.org/v3"


def _get_api_key() -> str:
    load_dotenv()

    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAQ_API_KEY is not configured in .env"
        )

    return api_key


def _headers() -> dict:
    return {
        "X-API-Key": _get_api_key(),
        "Accept": "application/json",
    }

def find_delhi_locations(
    limit: int = 100,
) -> pd.DataFrame:
    """
    Find PM2.5 monitoring locations around Delhi.

    Uses OpenAQ's geospatial point-radius query.
    """

    response = requests.get(
        f"{BASE_URL}/locations",
        headers=_headers(),
        params={
            "coordinates": "28.6139,77.2090",
            "radius": 25000,
            "parameters_id": 2,
            "limit": limit,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    rows = []

    for location in data.get("results", []):
        coordinates = location.get(
            "coordinates",
            {},
        )

        rows.append(
            {
                "id": location.get("id"),
                "name": location.get("name"),
                "locality": location.get("locality"),
                "country": (
                    location.get("country", {})
                    .get("name")
                ),
                "latitude": coordinates.get(
                    "latitude"
                ),
                "longitude": coordinates.get(
                    "longitude"
                ),
            }
        )

    return pd.DataFrame(rows)



def fetch_pm25_hours(
    location_id: int,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Fetch hourly PM2.5 data for a location from OpenAQ."""

    # OpenAQ v3 exposes measurements through sensors.
    sensors_response = requests.get(
        f"{BASE_URL}/locations/{location_id}/sensors",
        headers=_headers(),
        params={
            "limit": 100,
        },
        timeout=60,
    )
    sensors_response.raise_for_status()

    sensors = sensors_response.json().get("results", [])

    pm25_sensors = [
        sensor
        for sensor in sensors
        if sensor.get("parameter", {}).get("name") == "pm25"
    ]

    if not pm25_sensors:
        return pd.DataFrame(
            columns=[
                "datetime",
                "pm25",
                "sensor_id",
                "location_id",
            ]
        )

    frames = []

    for sensor in pm25_sensors:
        sensor_id = sensor["id"]

        response = requests.get(
            f"{BASE_URL}/sensors/{sensor_id}/hours",
            headers=_headers(),
            params={
                "datetime_from": f"{start_date}T00:00:00Z",
                "datetime_to": f"{end_date}T23:59:59Z",
                "limit": 1000,
            },
            timeout=60,
        )
        response.raise_for_status()

        results = response.json().get("results", [])

        for row in results:
            period = row.get("period", {})
            dt_from = period.get("datetimeFrom", {}).get("utc")

            if dt_from is None:
                continue

            frames.append(
                {
                    "datetime": pd.to_datetime(dt_from, utc=True),
                    "pm25": row.get("value"),
                    "sensor_id": sensor_id,
                    "location_id": location_id,
                }
            )

    if not frames:
        return pd.DataFrame(
            columns=[
                "datetime",
                "pm25",
                "sensor_id",
                "location_id",
            ]
        )

    df = pd.DataFrame(frames)

    return (
        df
        .dropna(subset=["pm25"])
        .sort_values("datetime")
        .reset_index(drop=True)
    )
