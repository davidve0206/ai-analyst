import streamlit as st

from src.frontend import crontab_setup_ui, sales_report_setup_ui, recipients_setup_ui
from agent_main import main as agent_main


def main():
    st.set_page_config(page_title="AI Analyst Setup", page_icon="🤖")

    st.title("AI Analyst Setup")

    if st.button("Run Now", type="primary"):
        with st.spinner("Running AI Analyst..."):
            try:
                agent_main()
                st.success("Analyst run completed successfully!")
            except Exception as e:
                st.error(f"Error running AI Analyst: {str(e)}")

    # Setup sections
    crontab_setup_ui()
    sales_report_setup_ui()
    recipients_setup_ui()


if __name__ == "__main__":
    main()
