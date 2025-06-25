import gradio as gr

from src.configuration.db import default_config_db_sessionmaker
from src.configuration.recipients import (
    add_recipient_email,
    get_recipient_emails,
    remove_recipient_email,
)


def add_and_rerender(email_input):
    """Add an email and re-render the list."""
    add_recipient_email(default_config_db_sessionmaker, email_input)
    # Returns the updated list of recipient emails and clears the input field
    return get_recipient_emails(default_config_db_sessionmaker), ""


def remove_and_rerender(email_to_remove):
    """Remove an email and re-render the list."""
    remove_recipient_email(default_config_db_sessionmaker, email_to_remove)
    return get_recipient_emails(default_config_db_sessionmaker)


def recipients_setup_ui():
    gr.Markdown(
        """
        # Recipients Setup

        Here you can update the emails that will receive the AI Analyst's reports.
        """
    )

    email_state = gr.State(get_recipient_emails(default_config_db_sessionmaker))

    @gr.render(inputs=email_state)
    def render_email_list(email_list):
        """Render the list of recipient emails."""
        gr.Markdown(f"## Current Recipients ({len(email_list)}):")
        for email in email_list:
            with gr.Row():
                gr.Textbox(email, show_label=False, container=False)
                delete_btn = gr.Button("Remove", scale=0, variant="stop")

                def remove(email=email):
                    return remove_and_rerender(email)

                delete_btn.click(remove, None, [email_state])

    gr.Markdown("## Add New Recipient:")

    email_input = gr.Textbox(
        label="Email Address",
        placeholder="Enter the email address to receive reports",
        type="email",
    )
    submit_button = gr.Button("Add Email")
    submit_button.click(
        add_and_rerender,
        inputs=[email_input],
        trigger_mode="once",
        outputs=[email_state, email_input],
    )
