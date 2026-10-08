import gradio as gr

from app.config import APP_TITLE, FORECAST_HORIZON_HOURS
from app.evidence import get_conformal_evaluation
from app.data import (
    load_data,
    split_chronological,
    train_replay_model,
    replay_prediction,
    replay_all,
)
from app.components.snapshot import format_snapshot
from app.components.backtest import build_backtest_section, build_replay_table
from app.components.theme import hero_html


def build_dashboard() -> gr.Blocks:
    """Build the SmokeClock Gradio dashboard."""
    df = load_data()
    # Use the last row of the full dataset as the reference snapshot
    row = df.iloc[-1]
    _, test = split_chronological(df)

    # Train the historical replay model once and reuse it for all interactions.
    replay_model = train_replay_model(df)

    timestamps = [
        ts.strftime("%Y-%m-%d %H:%M IST")
        for ts in test["datetime"]
    ]

    def run_replay(timestamp_text: str) -> str:
        index = timestamps.index(timestamp_text)
        result = replay_prediction(df, index, replay_model)
        error = abs(result["prediction"] - result["observed"])
        forecast_time = result["datetime"].strftime("%Y-%m-%d %H:%M IST")

        return f"""
<div class="sc-replay-result">
  <h3>Held-out replay result
    <span class="sc-held-out-badge">Held-out replay</span>
  </h3>
  <div class="sc-replay-metrics">
    <div>
      <div class="sc-replay-item-label">Forecast issued</div>
      <div class="sc-replay-item-value" style="font-size:1rem;">{forecast_time}</div>
    </div>
    <div>
      <div class="sc-replay-item-label">Predicted PM2.5</div>
      <div class="sc-replay-item-value">{result['prediction']:.1f}</div>
      <div class="sc-replay-item-unit">µg/m³</div>
    </div>
    <div>
      <div class="sc-replay-item-label">Observed PM2.5 +{FORECAST_HORIZON_HOURS}h</div>
      <div class="sc-replay-item-value">{result['observed']:.1f}</div>
      <div class="sc-replay-item-unit">µg/m³</div>
    </div>
    <div>
      <div class="sc-replay-item-label">Absolute error</div>
      <div class="sc-replay-item-value">{error:.1f}</div>
      <div class="sc-replay-item-unit">µg/m³</div>
    </div>
  </div>
  <div class="sc-replay-notice">
    Model trained only on data before the selected test period.
    This is a historical replay — not a live forecast.
  </div>
</div>
"""

    uncertainty = get_conformal_evaluation()

    with gr.Blocks(title=APP_TITLE) as demo:

        # ── 1. Hero ──────────────────────────────────────────────────────
        gr.HTML(hero_html())

        # ── 2. Key Snapshot ──────────────────────────────────────────────
        gr.HTML("""
<div class="sc-section-heading">Key Snapshot &nbsp;·&nbsp; Latest historical record</div>
""")
        gr.HTML(format_snapshot(row))

        # ── 3. Historical Forecast Replay ────────────────────────────────
        gr.HTML("""
<div class="sc-section-heading" style="margin-top:24px;">
  Historical Forecast Replay
</div>
<p style="font-size:0.88rem; color:#555; margin:-8px 0 14px 0;">
  Select a timestamp from the held-out October 2025 test period to run
  a historical replay. The model was trained only on earlier data.
</p>
""")

        with gr.Row():
            with gr.Column(scale=3):
                timestamp_dropdown = gr.Dropdown(
                    choices=timestamps,
                    value=timestamps[0],
                    label="Held-out forecast timestamp  (October 2025 test period)",
                    info="All timestamps are from the chronological holdout set.",
                )
            with gr.Column(scale=1):
                replay_button = gr.Button(
                    "Run historical replay",
                    variant="primary",
                    size="lg",
                )

        replay_output = gr.HTML(
            value="<p style='color:#888; font-size:0.85rem; padding:8px 0;'>"
                  "Select a timestamp and click Run to see the replay result.</p>"
        )

        replay_button.click(
            fn=run_replay,
            inputs=timestamp_dropdown,
            outputs=replay_output,
        )

        # ── 4. Model Evidence ────────────────────────────────────────────
        gr.HTML("""
<div class="sc-section-heading" style="margin-top:28px;">
  Model Evidence &nbsp;·&nbsp; Does transport add predictive skill?
</div>
<p style="font-size:0.88rem; color:#555; margin:-8px 0 14px 0;">
  Four benchmark models evaluated on the same October 2025 chronological holdout.
</p>
""")
        build_backtest_section()

        # ── 5. Full Held-out Replay ──────────────────────────────────────
        gr.HTML("""
<div class="sc-section-heading" style="margin-top:28px;">
  Full Held-out Replay
</div>
<p style="font-size:0.88rem; color:#555; margin:-8px 0 14px 0;">
  All 167 held-out October 2025 test rows with predicted vs observed PM2.5.
</p>
""")
        replay_results = replay_all(df, replay_model)
        build_replay_table(replay_results)

        # ── 6. Uncertainty Evaluation ────────────────────────────────────
        gr.HTML(f"""
<div class="sc-section-heading" style="margin-top:28px;">
  Uncertainty Evaluation
</div>
<div class="sc-uncertainty">
  <div class="sc-uncertainty-badge">Research only — not operational confidence</div>

  <div class="sc-uncertainty-grid">
    <div>
      <div class="sc-uncertainty-item-label">Target coverage</div>
      <div class="sc-uncertainty-item-value">
        {uncertainty['target_coverage'] * 100:.0f}%
      </div>
      <div class="sc-uncertainty-item-unit">conformal target</div>
    </div>
    <div>
      <div class="sc-uncertainty-item-label">Observed test coverage</div>
      <div class="sc-uncertainty-item-value">
        {uncertainty['test_coverage'] * 100:.1f}%
      </div>
      <div class="sc-uncertainty-item-unit">on {uncertainty['test_rows']} test rows</div>
    </div>
    <div>
      <div class="sc-uncertainty-item-label">Average interval width</div>
      <div class="sc-uncertainty-item-value">
        {uncertainty['average_interval_width']:.2f}
      </div>
      <div class="sc-uncertainty-item-unit">µg/m³</div>
    </div>
    <div>
      <div class="sc-uncertainty-item-label">Conformal radius</div>
      <div class="sc-uncertainty-item-value">
        {uncertainty['radius']:.2f}
      </div>
      <div class="sc-uncertainty-item-unit">µg/m³ (±)</div>
    </div>
  </div>

  <div class="sc-uncertainty-note">
    An 80% conformal prediction interval was calibrated on
    <strong>{uncertainty['calibration_rows']}</strong> historical observations
    and evaluated on <strong>{uncertainty['test_rows']}</strong> held-out observations.
    Coverage exceeded the 80% target ({uncertainty['test_coverage'] * 100:.1f}%),
    but the intervals were too wide to be decision-useful for this October 2025 dataset.
    SmokeClock therefore does <strong>not</strong> present this interval as operational
    confidence.
  </div>
</div>
""")

        # ── 7. Method & Limitations Footer ──────────────────────────────
        gr.HTML("""
<div class="sc-footer" style="margin-top:28px;">
  <div class="sc-footer-heading">How SmokeClock works</div>
  <ol>
    <li>Detect agricultural fire activity from FIRMS satellite data</li>
    <li>Cluster fire detections spatially</li>
    <li>Estimate wind-aligned transport relevance using direction, speed and distance</li>
    <li>Combine the transport exposure index with weather and historical PM2.5 lags</li>
    <li>Evaluate a LightGBM forecast model against chronological held-out observations</li>
  </ol>

  <div class="sc-footer-heading" style="margin-top:14px;">Limitations</div>
  <ul>
    <li>Historical October 2025 evaluation only — results may not generalise to other seasons</li>
    <li>Satellite fire detections have observation-time and cloud-cover limitations</li>
    <li>Transport exposure is a weighted index, not a full atmospheric dispersion model</li>
    <li>Single chronological split — no cross-validation across seasons or years</li>
    <li>Not official health advice</li>
  </ul>

  <div class="sc-footer-caution">
    SmokeClock is a research prototype. Data sourced from FIRMS (NASA), OpenAQ, and
    Open-Meteo. Not affiliated with any government or health authority.
  </div>
</div>
""")

    return demo
