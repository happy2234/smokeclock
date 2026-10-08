from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

FEATURES_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "features"
)

FEATURES_24H_PATH = FEATURES_DIR / "october_2025_24h.csv"

APP_TITLE = "SmokeClock"
FORECAST_HORIZON_HOURS = 24
