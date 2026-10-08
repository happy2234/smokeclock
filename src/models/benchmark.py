from pathlib import Path
import argparse

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


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


def train_lgbm(X_train, y_train, X_test):
    model = LGBMRegressor(
        objective="regression",
        n_estimators=300,
        learning_rate=0.03,
        num_leaves=15,
        max_depth=5,
        random_state=42,
        verbosity=-1,
    )

    model.fit(X_train, y_train)

    return model.predict(X_test)


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

    # Shared weather + lagged PM features.
    base_features = [
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m",
        "wind_direction_10m",
        "boundary_layer_height",
        "pm25_lag_1h",
        "pm25_lag_3h",
        "pm25_lag_6h",
    ]

    # M2 adds raw fire information.
    fire_features = [
        "fire_count",
        "fire_frp",
    ]

    # M3 adds transport-weighted fire exposure.
    transport_features = [
        "transport_exposure_6h",
        "transport_exposure_24h",
        "transport_exposure_48h",
        "transport_exposure_72h",
    ]

    results = []

    results.append(
        evaluate(
            "M0 Persistence",
            test[target],
            persistence_pred,
        )
    )

    # M1
    pred_m1 = train_lgbm(
        train[base_features],
        train[target],
        test[base_features],
    )

    results.append(
        evaluate(
            "M1 Weather + lagged PM",
            test[target],
            pred_m1,
        )
    )

    # M2
    m2_features = base_features + fire_features

    pred_m2 = train_lgbm(
        train[m2_features],
        train[target],
        test[m2_features],
    )

    results.append(
        evaluate(
            "M2 + raw fire",
            test[target],
            pred_m2,
        )
    )

    # M3
    m3_features = base_features + transport_features

    pred_m3 = train_lgbm(
        train[m3_features],
        train[target],
        test[m3_features],
    )

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
