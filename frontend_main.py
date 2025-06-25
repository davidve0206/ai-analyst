import gradio as gr

from src.frontend import crontab_setup_ui, kpis_setup_ui, recipients_setup_ui
from agent_main import main as agent_main

demo = gr.Blocks()

with demo:
    with gr.Row():
        gr.Markdown("# AI Analyst Setup")
        gr.Button("Run Now", variant="primary").click(agent_main)

    crontab_setup_ui()
    kpis_setup_ui()
    recipients_setup_ui()

if __name__ == "__main__":
    demo.launch()
