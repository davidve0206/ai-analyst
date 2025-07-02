import gradio as gr
from src.configuration.db import (
    default_config_db_sessionmaker,
    KpiPeriodsEnum,
    SalesGroupingsEnum,
)
from src.configuration.kpis import (
    SalesReportRequest,
    add_sales_report_request,
    get_sales_report_request,
)

period_choices = [period.value for period in KpiPeriodsEnum]
grouping_choices = [direction.value for direction in SalesGroupingsEnum]


def display_request(
    request: SalesReportRequest,
) -> str:
    return f"""
    - **Scope**: {request.grouping} - {request.grouping_value}
    - **Period**: {request.period}
    """


def add_request(
    grouping: str,
    grouping_value: str,
    period: str,
) -> str:
    """
    Adds a new KPI configuration to the database.

    Args:
        grouping (str): The grouping of the KPI (e.g., "region", "product").
        grouping_value (str): The specific value for the grouping (e.g., "North America", "Electronics").
        period (str): The period of the KPI (e.g., "daily", "monthly").

    Returns:
        str: Confirmation message indicating success or failure.
    """
    request = SalesReportRequest(
        grouping=grouping,
        grouping_value=grouping_value,
        period=period,
    )

    add_sales_report_request(default_config_db_sessionmaker, request)

    return display_request(request)


def sales_report_setup_ui():
    gr.Markdown(
        """
        # Sales Report Setup

        Here you can update the scope the AI Analyst will consider when providing your report.
        """
    )

    current_report = get_sales_report_request(default_config_db_sessionmaker)

    if current_report:
        gr.Markdown("## Current Configuration")
        current_report_output = gr.Markdown(display_request(current_report))
    else:
        gr.Markdown("No configuration found. Please set up.")

    gr.Markdown("## Update Configuration")

    grouping_dropdown = gr.Dropdown(
        choices=grouping_choices,
        label="Scope type",
        info="Select the type of scope for your report (e.g., region, product, etc.)",
    )
    grouping_value_input = gr.Textbox(
        label="Scope value",
        info="Enter the specific value for the selected scope (e.g., North America, Electronics, etc.)",
    )
    period_dropdown = gr.Dropdown(
        choices=period_choices,
        label="Periodicity of the KPI you want to track",
    )
    submit_button = gr.Button("Update KPI")

    submit_button.click(
        add_request,
        inputs=[
            grouping_dropdown,
            grouping_value_input,
            period_dropdown,
        ],
        trigger_mode="once",
        outputs=current_report_output,
    )
