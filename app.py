import gradio as gr

from app.dashboard import build_dashboard
from app.components.theme import DASHBOARD_CSS


demo = build_dashboard()


if __name__ == "__main__":
    demo.launch(
        css=DASHBOARD_CSS,
        theme=gr.themes.Base(
            primary_hue=gr.themes.colors.emerald,
            neutral_hue=gr.themes.colors.gray,
            font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"],
        ),
    )
