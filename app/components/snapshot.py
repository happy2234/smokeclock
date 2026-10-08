import pandas as pd


def format_snapshot(row: pd.Series) -> str:
    """Format a historical SmokeClock replay snapshot."""
    return (
        "### Delhi-NCR SmokeClock\n\n"
        f"**Observed PM2.5:** {row['pm25']:.1f} µg/m³\n\n"
        f"**Observed PM2.5 24h later:** {row['target_pm25']:.1f} µg/m³\n\n"
        f"**Fire detections:** {int(row['fire_count'])}\n\n"
        f"**24h transport exposure index:** "
        f"{row['transport_exposure_24h']:.4f}\n\n"
        f"**Historical timestamp:** {row['datetime']}"
    )
