from pathlib import Path

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor


BASE_FEATURES = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_direction_10m",
    "boundary_layer_height",
    "pm25_lag_1h",
    "pm25_lag_3h",
    "pm25_lag_6h",
]

TRANSPORT_FEATURES = [
    "transport_exposure_6h",
    "transport_exposure_24h",
    "transport_exposure_48h",
    "transport_exposure_72h",
]

M3_FEATURES = BASE_FEATURES + TRANSPORT_FEATURES


def create_model() -> LGBMRegressor:
    """Create the same LightGBM configuration used in the benchmark."""
    return LGBMRegressor(
        objective="regression",
        n_estimators=300,
        learning_rate=0.03,
        num_leaves=15,
        max_depth=5,
        random_state=42,
        verbosity=-1,
    )


def train_forecast(
    train: pd.DataFrame,
    target: str = "target_pm25",
) -> LGBMRegressor:
    """Train the M3 transport-aware PM2.5 model."""
    model = create_model()
    model.fit(train[M3_FEATURES], train[target])
    return model


def predict(model: LGBMRegressor, row: pd.DataFrame):
    """Generate an M3 PM2.5 prediction for one or more rows."""
    return model.predict(row[M3_FEATURES])


def conformal_radius(
    model: LGBMRegressor,
    calibration: pd.DataFrame,
    coverage: float = 0.80,
) -> float:
    """Estimate a symmetric conformal residual radius."""
    if not 0 < coverage < 1:
        raise ValueError("coverage must be between 0 and 1")

    residuals = (
        calibration["target_pm25"].to_numpy()
        - predict(model, calibration)
    )
    absolute_residuals = pd.Series(residuals).abs()

    n = len(absolute_residuals)
    rank = int(np.ceil((n + 1) * coverage))
    rank = min(rank, n)

    return float(absolute_residuals.sort_values().iloc[rank - 1])


def prediction_interval(
    prediction: float,
    radius: float,
) -> tuple[float, float]:
    """Return a symmetric conformal prediction interval."""
    return (
        max(0.0, prediction - radius),
        prediction + radius,
    )
