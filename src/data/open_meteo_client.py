from datetime import date, timedelta

import pandas as pd
import requests


BASE_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather(
    latitude: float,
    longitude: float,
    forecast_days: int = 2,
) -> pd.DataFrame:
    """
    Fetch hourly weather information from Open-Meteo.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "wind_direction_10m",
                "boundary_layer_height",
            ]
        ),
        "forecast_days": forecast_days,
        "timezone": "Asia/Kolkata",
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=60,
    )

    response.raise_for_status()

    payload = response.json()

    hourly = payload["hourly"]

    return pd.DataFrame(hourly)


if __name__ == "__main__":

    # Delhi
    df = fetch_weather(
        latitude=28.6139,
        longitude=77.2090,
        forecast_days=2,
    )

    print(f"Retrieved {len(df):,} hourly records")
    print()
    print(df.head(10).to_string(index=False))
