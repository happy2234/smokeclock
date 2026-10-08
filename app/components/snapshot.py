import pandas as pd


def format_snapshot(row: pd.Series) -> str:
    """
    Return an HTML block for the historical snapshot metric cards.

    Renders four key metrics:
      - Observed PM2.5
      - Observed PM2.5 24h later
      - Fire detections
      - 24h transport exposure index

    The transport exposure index is clearly labelled as an index, not
    a measured PM2.5 concentration.
    """
    timestamp = row["datetime"].strftime("%d %b %Y · %H:%M IST")

    pm25_now = f"{row['pm25']:.1f}"
    pm25_24h = f"{row['target_pm25']:.1f}"
    fire_count = str(int(row["fire_count"]))
    transport = f"{row['transport_exposure_24h']:.4f}"

    return f"""
<div style="margin-bottom: 8px;">
  <p class="sc-timestamp">Historical replay snapshot &nbsp;·&nbsp; {timestamp}</p>

  <div class="sc-metric-grid">

    <div class="sc-metric-card">
      <div class="sc-metric-label">Observed PM2.5</div>
      <div class="sc-metric-value">{pm25_now}</div>
      <div class="sc-metric-unit">µg/m³</div>
    </div>

    <div class="sc-metric-card">
      <div class="sc-metric-label">Observed PM2.5 · 24h later</div>
      <div class="sc-metric-value">{pm25_24h}</div>
      <div class="sc-metric-unit">µg/m³</div>
    </div>

    <div class="sc-metric-card">
      <div class="sc-metric-label">Fire detections</div>
      <div class="sc-metric-value">{fire_count}</div>
      <div class="sc-metric-unit">satellite detections</div>
    </div>

    <div class="sc-metric-card">
      <div class="sc-metric-label">24h transport exposure index</div>
      <div class="sc-metric-value">{transport}</div>
      <div class="sc-metric-unit">index (dimensionless)</div>
    </div>

  </div>

  <div class="sc-metric-note">
    Transport exposure is an index derived from fire activity, wind direction
    and distance to Delhi-NCR. It is not a measured PM2.5 concentration.
  </div>
</div>
"""
