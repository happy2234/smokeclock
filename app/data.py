import pandas as pd

from app.config import FEATURES_24H_PATH
from src.models.forecast import predict, train_forecast


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


def train_replay_model(df: pd.DataFrame):
    """Train the replay model once on the historical training period."""
    train, _ = split_chronological(df)
    return train_forecast(train)


def replay_prediction(
    df: pd.DataFrame,
    test_index: int,
    model,
):
    """Predict one held-out row using an already-trained replay model."""
    _, test = split_chronological(df)

    if test_index < 0 or test_index >= len(test):
        raise IndexError("test_index is outside the replay test period")

    row = test.iloc[[test_index]]

    prediction = float(predict(model, row)[0])
    observed = float(row["target_pm25"].iloc[0])

    return {
        "datetime": row["datetime"].iloc[0],
        "prediction": prediction,
        "observed": observed,
    }


def replay_all(
    df: pd.DataFrame,
    model,
) -> pd.DataFrame:
    """Generate historical replay predictions using an existing model."""
    _, test = split_chronological(df)

    results = test[["datetime", "target_pm25"]].copy()
    results["predicted_pm25"] = predict(model, test)
    results["absolute_error"] = (
        results["predicted_pm25"] - results["target_pm25"]
    ).abs()

    return results
