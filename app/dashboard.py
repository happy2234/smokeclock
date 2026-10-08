import gradio as gr

from app.config import APP_TITLE, FORECAST_HORIZON_HOURS
from app.data import latest_row
from app.components.snapshot import format_snapshot
from app.components.backtest import build_backtest_section


def build_dashboard() -> gr.Blocks:
    """Build the SmokeClock Gradio dashboard."""
    row = latest_row()

    with gr.Blocks(title=APP_TITLE) as demo:
        gr.Markdown(
            f"""
# SmokeClock

### Wind-aware smoke intelligence for Delhi-NCR

SmokeClock estimates how upwind agricultural-fire activity may affect
future PM2.5 using fire detections, weather, and historical air quality.

> **Historical replay / research prototype** — not official health advice.
"""
        )

        gr.Markdown(format_snapshot(row))

        build_backtest_section()

        gr.Markdown(
            f"""
### Evaluation horizon

The current evidence panel evaluates a **{FORECAST_HORIZON_HOURS}-hour**
forecast horizon using a chronological October 2025 holdout.

The historical outcome shown above is observed data, not a live forecast.
"""
        )

    return demo
