import gradio as gr
from src.configuration.crontab import (
    CronFrequency,
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


def setup_crontab(frequency: CronFrequency) -> str:
    """
    Sets up the crontab with the specified frequency.

    Args:
        frequency (CronFrequency): The frequency at which the cron job should run.
    """

    if frequency == CronFrequency.DAY.value:
        # Set up daily cron job
        return "Setting up daily cron job..."
    elif frequency == CronFrequency.MONTH.value:
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
        hour=hour, days_of_week=days_of_week, frequency=CronFrequency.DAY
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
        frequency=CronFrequency.MONTH,
    )

    set_crontab(config, write)
    return f"Agent set up to run: {config}."


def crontab_setup_ui():
    gr.Markdown("# AI Analyst Setup")

    # TODO: Replace with actual logic to retrieve the last configuration
    last_config: CrontabFrequency | None = None

    if last_config:
        gr.Markdown(f"Update the frequency of the analyst's runs: {last_config}")
    else:
        gr.Markdown("Set up your how frequently the AI Analyst runs.")

        cron_frequency = gr.Radio(
            choices=[CronFrequency.DAY.value, CronFrequency.MONTH.value],
            label="Cron Frequency",
        )

        @gr.render(inputs=cron_frequency)
        def setup_crontab(frequency: str):
            if frequency == CronFrequency.DAY.value:
                # Set up daily cron job
                days_dropdown = gr.Dropdown(
                    choices=weekday_choices,
                    multiselect=True,
                    label="Days of the week the agent will run",
                )
                hour_dropdown = gr.Dropdown(
                    choices=hour_choices,
                    label="Hour of the day",
                )

                setup_button = gr.Button("Set Daily Execution")
                output_text = gr.Textbox(label="Result", interactive=False)

                setup_button.click(
                    fn=setup_daily_crontab,
                    inputs=[hour_dropdown, days_dropdown],
                    outputs=output_text,
                )

            elif frequency == CronFrequency.MONTH.value:
                month_dropdown = gr.Dropdown(
                    choices=month_choices,
                    multiselect=True,
                    label="Months the agent will run",
                )
                days_dropdown = gr.Dropdown(
                    choices=day_of_month_choices,
                    multiselect=True,
                    label="Days of the month the agent will run",
                )
                hour_dropdown = gr.Dropdown(
                    choices=hour_choices, label="Hour of the day"
                )

                setup_button = gr.Button("Set Monthly Execution")
                output_text = gr.Textbox(label="Result", interactive=False)

                setup_button.click(
                    fn=setup_monthly_crontab,
                    inputs=[hour_dropdown, days_dropdown, month_dropdown],
                    outputs=output_text,
                )

            else:
                return
