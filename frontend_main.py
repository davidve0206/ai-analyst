import gradio as gr

from src.frontend import crontab_setup_ui

demo = gr.Blocks()

with demo:
    crontab_setup_ui()

demo.launch()
