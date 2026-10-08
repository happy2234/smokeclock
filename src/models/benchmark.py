from pathlib import Path
import argparse

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.models.forecast import BASE_FEATURES, TRANSPORT_FEATURES, create_model


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "features"
    / "october_2025_6h.csv"
)


def evaluate(name, y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    return {
        "model": name,
        "MAE": mae,
        "RMSE": rmse,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Path to feature CSV",
    )
    args = parser.parse_args()

    data_path = args.data
    if not data_path.is_absolute():
        data_path = PROJECT_ROOT / data_path

    df = pd.read_csv(data_path)
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Chronological split:
    # first ~75% for training, final ~25% for testing.
    split = int(len(df) * 0.75)

    train = df.iloc[:split].copy()
    test = df.iloc[split:].copy()

    target = "target_pm25"

    # M0: persistence
    persistence_pred = test["pm25"].to_numpy()

    # Shared model feature definitions.
    base_features = BASE_FEATURES

    # M2 adds raw fire information.
    fire_features = [
        "fire_count",
        "fire_frp",
    ]

    # M3 adds transport-weighted fire exposure.
    transport_features = TRANSPORT_FEATURES

    results = []

    results.append(
        evaluate(
            "M0 Persistence",
            test[target],
            persistence_pred,
        )
    )

    # M1
    model_m1 = create_model()
    model_m1.fit(train[base_features], train[target])
    pred_m1 = model_m1.predict(test[base_features])

    results.append(
        evaluate(
            "M1 Weather + lagged PM",
            test[target],
            pred_m1,
        )
    )

    # M2
    m2_features = base_features + fire_features

    model_m2 = create_model()
    model_m2.fit(train[m2_features], train[target])
    pred_m2 = model_m2.predict(test[m2_features])

    results.append(
        evaluate(
            "M2 + raw fire",
            test[target],
            pred_m2,
        )
    )

    # M3
    m3_features = base_features + transport_features

    model_m3 = create_model()
    model_m3.fit(train[m3_features], train[target])
    pred_m3 = model_m3.predict(test[m3_features])

    results.append(
        evaluate(
            "M3 + transport exposure",
            test[target],
            pred_m3,
        )
    )

    results_df = pd.DataFrame(results)

    print()
    horizon = data_path.stem.split("_")[-1]
    print(f"SmokeClock — {horizon} PM2.5 Benchmark")
    print("=" * 70)
    print(f"Train rows: {len(train)}")
    print(f"Test rows:  {len(test)}")
    print(
        f"Test period: "
        f"{test['datetime'].min()} → {test['datetime'].max()}"
    )
    print()

    print(
        results_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.3f}",
        )
    )

    print()

    baseline_mae = results_df.loc[
        results_df["model"] == "M1 Weather + lagged PM",
        "MAE",
    ].iloc[0]

    transport_mae = results_df.loc[
        results_df["model"] == "M3 + transport exposure",
        "MAE",
    ].iloc[0]

    improvement = (
        (baseline_mae - transport_mae)
        / baseline_mae
        * 100
    )

    print(
        f"M3 MAE change vs M1 (positive = improvement): "
        f"{improvement:+.2f}%"
    )


if __name__ == "__main__":
    main()
