import gradio as gr
import pandas as pd

from app.evidence import get_benchmark_results, transport_improvement


def build_backtest_section() -> None:
    """
    Render the model evidence section inside the current gr.Blocks context.

    Shows:
      - A callout with the key headline result (18.57% MAE improvement)
      - A clean benchmark table with all four models
      - Footnotes about evaluation scope

    Does not modify benchmark numbers.
    """
    results = get_benchmark_results()
    improvement = transport_improvement()

    # Format the improvement callout as HTML
    callout_html = f"""
<div class="sc-evidence-callout">
  <div class="sc-evidence-number">{improvement:.2f}%</div>
  <div class="sc-evidence-label">
    lower 24-hour MAE vs weather + lagged PM baseline
    (Weather + PM + transport vs Weather + lagged PM)
  </div>
  <div class="sc-evidence-footnote">
    October 2025 chronological holdout &nbsp;·&nbsp;
    Single historical evaluation — not evidence of generalization.
  </div>
</div>
"""
    gr.HTML(callout_html)

    # Benchmark table — display with a highlight note
    gr.Dataframe(
        value=results,
        interactive=False,
        label="Four-model comparison · October 2025 chronological holdout",
        wrap=True,
    )

    gr.HTML("""
<div class="sc-evidence-footnote" style="padding: 8px 0 4px 0; color: #2c2c2c;">
  <strong>Weather + PM + transport</strong> is the M3 model that incorporates the
  transport exposure index. All models are evaluated on the same chronological
  held-out test period. MAE and RMSE are in µg/m³.
</div>
""")


def build_replay_table(results: pd.DataFrame) -> None:
    """
    Render a compact, scrollable historical replay table inside the current
    gr.Blocks context.

    Columns shown:
      Forecast time | Predicted PM2.5 | Observed PM2.5 +24h | Absolute error
    """
    display = results.copy()
    display["datetime"] = display["datetime"].dt.strftime("%Y-%m-%d %H:%M")
    display["predicted_pm25"] = display["predicted_pm25"].round(1)
    display["target_pm25"] = display["target_pm25"].round(1)
    display["absolute_error"] = display["absolute_error"].round(1)

    display = display.rename(
        columns={
            "datetime": "Forecast time",
            "predicted_pm25": "Predicted PM2.5",
            "target_pm25": "Observed PM2.5 +24h",
            "absolute_error": "Absolute error",
        }
    )

    gr.Dataframe(
        value=display,
        headers=list(display.columns),
        interactive=False,
        label=f"October 2025 held-out replay · {len(display)} rows",
        wrap=False,
        max_height=380,
    )
