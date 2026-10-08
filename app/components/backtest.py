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
