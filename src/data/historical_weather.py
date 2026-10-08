import pandas as pd
import requests


BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

DELHI_LAT = 28.6139
DELHI_LON = 77.2090


def fetch_historical_weather(
    start_date: str,
    end_date: str,
    latitude: float = DELHI_LAT,
    longitude: float = DELHI_LON,
) -> pd.DataFrame:
    """Fetch hourly historical weather data from Open-Meteo."""

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "wind_direction_10m",
                "boundary_layer_height",
            ]
        ),
        "timezone": "Asia/Kolkata",
        "wind_speed_unit": "ms",
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()

    hourly = data["hourly"]

    df = pd.DataFrame(
        {
            "datetime": pd.to_datetime(hourly["time"]),
            "temperature_2m": hourly["temperature_2m"],
            "relative_humidity_2m": hourly["relative_humidity_2m"],
            "wind_speed_10m": hourly["wind_speed_10m"],
            "wind_direction_10m": hourly["wind_direction_10m"],
            "boundary_layer_height": hourly["boundary_layer_height"],
        }
    )

    df["datetime"] = df["datetime"].dt.tz_localize("Asia/Kolkata")

    return df.sort_values("datetime").reset_index(drop=True)
