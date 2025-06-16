from src.configuration.crontab import (
    CrontabFrequency,
    JobFrequency,
    Weekday,
    Month,
    set_crontab,
)


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
