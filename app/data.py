import pandas as pd

from app.config import FEATURES_24H_PATH


def load_data() -> pd.DataFrame:
    """Load the 24-hour historical feature dataset."""
    df = pd.read_csv(FEATURES_24H_PATH)
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df.sort_values("datetime").reset_index(drop=True)


def split_chronological(
    df: pd.DataFrame,
    train_fraction: float = 0.75,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split historical data chronologically for replay evaluation."""
    split_index = int(len(df) * train_fraction)
    train = df.iloc[:split_index].copy()
    test = df.iloc[split_index:].copy()
    return train, test


def replay_prediction(
    df: pd.DataFrame,
    test_index: int,
):
    """Train M3 only on earlier observations and predict one held-out row."""
    from src.models.forecast import predict, train_forecast

    train, test = split_chronological(df)

    if test_index < 0 or test_index >= len(test):
        raise IndexError("test_index is outside the replay test period")

    model = train_forecast(train)
    row = test.iloc[[test_index]]

    prediction = float(predict(model, row)[0])
    observed = float(row["target_pm25"].iloc[0])

    return {
        "datetime": row["datetime"].iloc[0],
        "prediction": prediction,
        "observed": observed,
    }



