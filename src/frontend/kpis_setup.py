""" NOTE: For now this isn't used, as the MVP only allows Sales Reports, but
the logic might be useful when expanding the system."""

import gradio as gr
from src.configuration.db import (
    default_config_db_sessionmaker,
    KpiPeriodsEnum,
    KpiDirectionsEnum,
)
from src.configuration.kpis import KpiRequest, add_kpi_request, get_kpi_requests

period_choices = [period.value for period in KpiPeriodsEnum]
direction_choices = [direction.value for direction in KpiDirectionsEnum]


def display_kpi(kpi: KpiRequest):
    return f"""
    - **Name**: {kpi.name}
    - **Description**: {kpi.description}
    - **Direction**: {kpi.direction}
    - **Period**: {kpi.period}
    """


def add_kpi(
    name: str,
    description: str,
    direction: str,
    period: str,
) -> str:
    """
    Adds a new KPI configuration to the database.

    Args:
        name (str): The name of the KPI.
        description (str): A description of the KPI.
        direction (str): The direction of the KPI (e.g., "up", "down").
        period (str): The period of the KPI (e.g., "daily", "monthly").

    Returns:
        str: Confirmation message indicating success or failure.
    """
    kpi = KpiRequest(
        name=name, description=description, direction=direction, period=period
    )

    add_kpi_request(default_config_db_sessionmaker, kpi)

    return display_kpi(kpi)


def kpis_setup_ui():
    gr.Markdown(
        """
        # KPI Setup

        Here you can update the KPI's the AI Analyst will consider when providing your report.
        """
    )

    current_kpi = get_kpi_requests(default_config_db_sessionmaker)

    if current_kpi:
        gr.Markdown("## Current KPI Configuration")
        current_kpi_output = gr.Markdown(display_kpi(current_kpi))
    else:
        gr.Markdown("No KPI configuration found. Please set up a new KPI.")

    gr.Markdown("## Update KPI Configuration")

    name_input = gr.Textbox(
        label="KPI Name",
        placeholder="Enter the name of the KPI",
    )
    description_input = gr.Textbox(
        label="KPI Description",
        placeholder="Enter a description of the KPI",
        info="Please any information that might help the agent understand how to calculate this from your Database, such as the tables and columns that that contain useful information.",
    )
    direction_dropdown = gr.Dropdown(
        choices=direction_choices,
        label="Direction of the values KPI",
    )
    period_dropdown = gr.Dropdown(
        choices=period_choices,
        label="Periodicity of the KPI you want to track",
    )
    submit_button = gr.Button("Update KPI")

    submit_button.click(
        add_kpi,
        inputs=[
            name_input,
            description_input,
            direction_dropdown,
            period_dropdown,
        ],
        trigger_mode="once",
        outputs=current_kpi_output,
    )
