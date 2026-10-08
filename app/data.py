import pandas as pd

from app.config import FEATURES_24H_PATH


def load_data() -> pd.DataFrame:
    """Load the 24-hour historical feature dataset."""
    df = pd.read_csv(FEATURES_24H_PATH)
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df


def latest_row() -> pd.Series:
    """Return the latest historical observation."""
    df = load_data()
    return df.iloc[-1]
