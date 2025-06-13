import gradio as gr
from src.frontend.crontab_setup import setup_crontab

# NOTE: Gradio requires the main "demo" variable to be defined
# and for it to be in the entry point of the script.

demo = gr.Interface(
    fn=setup_crontab,
    inputs=gr.Radio(
        choices=["On specific days of the week", "On a specific days of the month"],
        label="Cron Frequency",
    ),
    outputs="text",
    title="Cron Job Setup",
    description="Set up your cron job frequency.",
)

if __name__ == "__main__":
    demo.launch()
