import gradio as gr

from src.frontend import crontab_setup_ui, sales_report_setup_ui, recipients_setup_ui
from agent_main import main as agent_main

demo = gr.Blocks()

with demo:
    with gr.Row():
        with gr.Column(scale=4):
            gr.Markdown("# AI Analyst Setup")
        with gr.Column(scale=1):
            gr.Button("Run Now", variant="primary").click(agent_main)

    crontab_setup_ui()
    sales_report_setup_ui()
    recipients_setup_ui()

if __name__ == "__main__":
    demo.launch()
