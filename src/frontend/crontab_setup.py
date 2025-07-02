import streamlit as st
from src.configuration.crontab import (
    JobFrequency,
    CrontabFrequency,
    Month,
    Weekday,
    set_crontab,
)

# Set the selectable choices
weekday_choices = [day.value for day in Weekday]
month_choices = [month.value for month in Month]
day_of_month_choices = list(range(1, 31))
hour_choices = list(range(0, 24))


def setup_crontab(frequency: JobFrequency) -> str:
    """
    Sets up the crontab with the specified frequency.

    Args:
        frequency (JobFrequency): The frequency at which the cron job should run.
    """

    if frequency == JobFrequency.DAY.value:
        # Set up daily cron job
        return "Setting up daily cron job..."
    elif frequency == JobFrequency.MONTH.value:
        # Set up monthly cron job
        return "Setting up monthly cron job..."
    else:
        raise ValueError("Unsupported frequency type for cron job setup")


def setup_daily_crontab(
    hour: int, days_of_week: list[Weekday], write: bool = True
) -> bool:
    """
    Sets up a daily cron job with the specified hour and days of the week.

    Args:
        hour (int): The hour at which the cron job should run.
        days_of_week (list[Weekday]): The days of the week on which the cron job should run.
        write (bool): Whether to write the changes to the crontab file. Defaults to True.

    Returns:
        bool: True if the setup was successful, False otherwise.
    """
    config = CrontabFrequency(
        hour=hour, days_of_week=days_of_week, frequency=JobFrequency.DAY
    )

    set_crontab(config, write)
    return f"Agent set up to run: {config}."


def setup_monthly_crontab(
    hour: int, days_of_month: list[int], months: list[Month], write: bool = True
) -> bool:
    """
    Sets up a monthly cron job with the specified hour, days of the month, and months.

    Args:
        hour (int): The hour at which the cron job should run.
        days_of_month (list[int]): The days of the month on which the cron job should run.
        months (list[Month]): The months in which the cron job should run.
        write (bool): Whether to write the changes to the crontab file. Defaults to True.

    Returns:
        bool: True if the setup was successful, False otherwise.
    """
    config = CrontabFrequency(
        hour=hour,
        days_of_month=days_of_month,
        months=months,
        frequency=JobFrequency.MONTH,
    )

    set_crontab(config, write)
    return f"Agent set up to run: {config}."


def crontab_setup_ui():
    # TODO: Replace with actual logic to retrieve the last configuration
    last_config: CrontabFrequency | None = None

    st.markdown("---")
    st.header("Cron Schedule Setup")

    if last_config:
        st.info(f"Update the frequency of the analyst's runs: {last_config}")
    else:
        st.write("Set up how frequently the AI Analyst runs.")

        frequency = st.radio(
            "When do you want the AI Analyst to run?",
            options=[JobFrequency.DAY.value, JobFrequency.MONTH.value],
            key="cron_frequency",
        )

        if frequency == JobFrequency.DAY.value:
            col1, col2 = st.columns(2)

            with col1:
                selected_days = st.multiselect(
                    "Days of the week the agent will run",
                    options=weekday_choices,
                    key="daily_days",
                )

            with col2:
                selected_hour = st.selectbox(
                    "Hour of the day",
                    options=hour_choices,
                    help="Hour in UTC (0-23); adjust for your timezone if necessary.",
                    key="daily_hour",
                )

            if st.button("Set Daily Execution", key="daily_setup"):
                if selected_days and selected_hour is not None:
                    # Convert string days back to Weekday enums
                    weekday_enums = [Weekday(day) for day in selected_days]
                    result = setup_daily_crontab(selected_hour, weekday_enums)
                    st.success(result)
                else:
                    st.error("Please select both days and hour.")

        elif frequency == JobFrequency.MONTH.value:
            col1, col2, col3 = st.columns(3)

            with col1:
                selected_months = st.multiselect(
                    "Months the agent will run",
                    options=month_choices,
                    key="monthly_months",
                )

            with col2:
                selected_days = st.multiselect(
                    "Days of the month the agent will run",
                    options=day_of_month_choices,
                    key="monthly_days",
                )

            with col3:
                selected_hour = st.selectbox(
                    "Hour of the day",
                    options=hour_choices,
                    help="Hour in UTC (0-23); adjust for your timezone if necessary.",
                    key="monthly_hour",
                )

            if st.button("Set Monthly Execution", key="monthly_setup"):
                if selected_months and selected_days and selected_hour is not None:
                    # Convert string months back to Month enums
                    month_enums = [Month(month) for month in selected_months]
                    result = setup_monthly_crontab(
                        selected_hour, selected_days, month_enums
                    )
                    st.success(result)
                else:
                    st.error("Please select months, days, and hour.")
