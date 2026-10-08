import gradio as gr

from app.evidence import get_benchmark_results, transport_improvement


def build_backtest_section():
    results = get_benchmark_results()
    improvement = transport_improvement()

    return gr.Column(
        [
            gr.Markdown("## 24-hour backtest evidence"),
            gr.Dataframe(
                value=results,
                interactive=False,
                label="October 2025 chronological holdout",
            ),
            gr.Markdown(
                f"""
### Key result

Transport-weighted fire exposure reduced 24-hour PM2.5 MAE from
**54.482 → 44.363 µg/m³**, a **{improvement:.2f}% improvement**
over the weather + lagged-PM baseline.

This is a single October 2025 historical evaluation and should not be
interpreted as proof of generalization.
"""
            ),
        ]
    )


def build_replay_table(results):
    """Build a compact historical replay table."""
    import gradio as gr

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

    return gr.Dataframe(
        value=display,
        headers=list(display.columns),
        interactive=False,
        label="October 2025 held-out replay",
    )
