from src.configuration.crontab import (
    CrontabFrequency,
    CronFrequency,
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
        frequency=CronFrequency.DAY,
    )

    created_job = set_crontab(config=crontab, write=False)
    assert created_job.frequency(year=2023) == 104


def test_monthly_crontab():
    crontab = CrontabFrequency(
        hour=12,
        days_of_month=[4],
        months=[Month.JANUARY, Month.APRIL, Month.JULY, Month.OCTOBER],
        days_of_week=[],
        frequency=CronFrequency.MONTH,
    )

    created_job = set_crontab(config=crontab, write=False)
    assert created_job.frequency() == 4
