import gradio as gr

from src.frontend import crontab_setup_ui, kpis_setup_ui, recipients_setup_ui

demo = gr.Blocks()

with demo:
    crontab_setup_ui()
    kpis_setup_ui()
    recipients_setup_ui()

if __name__ == "__main__":
    demo.launch()
