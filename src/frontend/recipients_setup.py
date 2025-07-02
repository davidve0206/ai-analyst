import streamlit as st

from src.configuration.db import default_config_db_sessionmaker
from src.configuration.recipients import (
    add_recipient_email,
    get_recipient_emails,
    remove_recipient_email,
)


def recipients_setup_ui():
    st.markdown("---")
    st.header("Recipients Setup")
    st.write(
        "Here you can update the emails that will receive the AI Analyst's reports."
    )

    # Get current recipients
    current_emails = get_recipient_emails(default_config_db_sessionmaker)

    st.subheader(f"Current Recipients ({len(current_emails)})")

    if current_emails:
        # Display current recipients with remove buttons
        for i, email in enumerate(current_emails):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(email)
            with col2:
                if st.button("Remove", key=f"remove_{i}_{email}"):
                    remove_recipient_email(default_config_db_sessionmaker, email)
                    st.success(f"Removed {email}")
                    st.rerun()
    else:
        st.info("No recipients configured yet.")

    st.subheader("Add New Recipient")

    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")

    with col1:
        new_email = st.text_input(
            "Email Address",
            placeholder="Enter the email address to receive reports",
            key="new_recipient_email",
        )

    with col2:
        st.write("")  # Add spacing
        if st.button("Add Email", key="add_recipient"):
            if new_email:
                if "@" in new_email and "." in new_email:  # Basic email validation
                    add_recipient_email(default_config_db_sessionmaker, new_email)
                    st.success(f"Added {new_email}")
                    st.rerun()
                else:
                    st.error("Please enter a valid email address.")
            else:
                st.error("Please enter an email address.")
