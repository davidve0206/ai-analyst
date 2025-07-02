import streamlit as st
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
    st.markdown("---")
    st.header("Sales Report Setup")
    st.write(
        "Here you can update the scope the AI Analyst will consider when providing your report."
    )

    current_report = get_sales_report_request(default_config_db_sessionmaker)

    if current_report:
        st.subheader("Current Configuration")
        current_config_placeholder = st.empty()
        current_config_placeholder.info(display_request(current_report))
    else:
        st.warning("No configuration found. Please set up.")
        current_config_placeholder = st.empty()

    st.subheader("Update Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        grouping = st.selectbox(
            "Scope type",
            options=grouping_choices,
            help="Select the type of scope for your report (e.g., region, product, etc.)",
            key="sales_grouping",
        )

    with col2:
        grouping_value = st.text_input(
            "Scope value",
            help="Enter the specific value for the selected scope (e.g., North America, Electronics, etc.)",
            key="sales_grouping_value",
        )

    with col3:
        period = st.selectbox(
            "Periodicity you want to track",
            options=period_choices,
            key="sales_period",
        )

    if st.button("Update Report", key="update_sales_kpi"):
        if grouping and grouping_value and period:
            result = add_request(grouping, grouping_value, period)
            st.success("Configuration updated successfully!")
            # Replace the current configuration display
            current_config_placeholder.info(result)
        else:
            st.error("Please fill in all fields.")
