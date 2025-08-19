from src.configuration.crontab import (
    CrontabFrequency,
    JobFrequency,
    Weekday,
    Month,
    set_crontab,
    get_existing_agent_cronjob,
)
from crontab import CronTab


def test_daily_crontab():
    crontab = CrontabFrequency(
        hour=12,
        days_of_month=[],
        months=[],
        days_of_week=[Weekday.MONDAY, Weekday.WEDNESDAY],
        frequency=JobFrequency.DAY,
    )

    created_job = set_crontab(config=crontab, write=False)
    assert created_job.frequency(year=2023) == 104


def test_daily_crontab_order_of_days():
    crontab = CrontabFrequency(
        hour=12,
        days_of_month=[],
        months=[],
        days_of_week=[Weekday.WEDNESDAY, Weekday.MONDAY],
        frequency=JobFrequency.DAY,
    )

    created_job = set_crontab(config=crontab, write=False)
    assert created_job.frequency(year=2023) == 104


def test_monthly_crontab():
    crontab = CrontabFrequency(
        hour=12,
        days_of_month=[4],
        months=[Month.JANUARY, Month.APRIL, Month.JULY, Month.OCTOBER],
        days_of_week=[],
        frequency=JobFrequency.MONTH,
    )

    created_job = set_crontab(config=crontab, write=False)
    assert created_job.frequency() == 4


def test_monthly_crontab_order_of_months():
    crontab = CrontabFrequency(
        hour=12,
        days_of_month=[8, 4],
        months=[Month.OCTOBER, Month.JULY, Month.APRIL, Month.JANUARY],
        days_of_week=[],
        frequency=JobFrequency.MONTH,
    )

    created_job = set_crontab(config=crontab, write=False)
    assert created_job.frequency() == 8


def test_get_existing_agent_cronjob_daily():
    """Test parsing a daily cron job from a mock CronTab."""
    # Create a mock CronTab with a temporary file to avoid system crontab issues
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        # Write a sample crontab entry
        f.write("0 14 * * MON,WED python /path/to/agent_main.py\n")
        f.flush()

        try:
            # Create CronTab from the temporary file
            cron = CronTab(tabfile=f.name)

            # Test parsing
            result = get_existing_agent_cronjob(cron)

            assert result.hour == 14
            assert result.days_of_month == []
            assert result.months == []
            assert set(result.days_of_week) == {Weekday.MONDAY, Weekday.WEDNESDAY}
            assert result.frequency == JobFrequency.DAY
        finally:
            os.unlink(f.name)


def test_get_existing_agent_cronjob_monthly():
    """Test parsing a monthly cron job from a mock CronTab."""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        # Write a sample crontab entry
        f.write("0 9 4,15 JAN,APR,JUL,OCT * python /path/to/agent_main.py\n")
        f.flush()

        try:
            # Create CronTab from the temporary file
            cron = CronTab(tabfile=f.name)

            # Test parsing
            result = get_existing_agent_cronjob(cron)

            assert result.hour == 9
            assert set(result.days_of_month) == {4, 15}
            assert set(result.months) == {
                Month.JANUARY,
                Month.APRIL,
                Month.JULY,
                Month.OCTOBER,
            }
            assert result.days_of_week == []
            assert result.frequency == JobFrequency.MONTH
        finally:
            os.unlink(f.name)


def test_get_existing_agent_cronjob_no_agent_job():
    """Test that ValueError is raised when no agent job exists."""
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        # Write a non-agent crontab entry
        f.write("0 12 * * * python /path/to/other_script.py\n")
        f.flush()

        try:
            # Create CronTab from the temporary file
            cron = CronTab(tabfile=f.name)

            # Test that ValueError is raised
            try:
                get_existing_agent_cronjob(cron)
                assert False, "Expected ValueError to be raised"
            except ValueError as e:
                assert str(e) == "No existing cron job found for the AI agent."
        finally:
            os.unlink(f.name)
