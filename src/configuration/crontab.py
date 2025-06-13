import sys
import enum
from pathlib import Path
from typing import Annotated, Self

from crontab import CronTab
from pydantic import BaseModel, Field, model_validator

from src.configuration.settings import BASE_DIR


class CronFrequency(enum.Enum):
    DAY = "On specific days of the week"
    MONTH = "On a specific days of the month"


class Weekday(enum.Enum):
    MONDAY = "MON"
    TUESDAY = "TUE"
    WEDNESDAY = "WED"
    THURSDAY = "THU"
    FRIDAY = "FRI"
    SATURDAY = "SAT"
    SUNDAY = "SUN"

    def __str__(self):
        return self.value


class Month(enum.Enum):
    JANUARY = "JAN"
    FEBRUARY = "FEB"
    MARCH = "MAR"
    APRIL = "APR"
    MAY = "MAY"
    JUNE = "JUN"
    JULY = "JUL"
    AUGUST = "AUG"
    SEPTEMBER = "SEP"
    OCTOBER = "OCT"
    NOVEMBER = "NOV"
    DECEMBER = "DEC"

    def __str__(self):
        return self.value


class CrontabFrequency(BaseModel):
    """
    Represents the frequency of a cron job.
    """

    hour: int
    days_of_month: list[Annotated[int, Field(strict=True, ge=0, le=31)]] = []
    months: list[Month] = []
    days_of_week: list[Weekday] = []
    frequency: CronFrequency

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.frequency == CronFrequency.DAY and not self.days_of_week:
            raise ValueError(
                "days_of_week cannot be empty when frequency is set to specific days"
            )
        if self.frequency == CronFrequency.MONTH and (
            not self.months or not self.days_of_month
        ):
            raise ValueError(
                "months and days_of_month cannot be empty when frequency is set to specific months"
            )
        return self


def set_crontab():
    """
    Set the crontab for the application.

    TODO: Implement variable to set the frequency of the cron job.
    """

    cron = CronTab(user="root")
    for job in cron:
        if "agent" in job.command:
            cron.remove(job)

    python_path = Path(sys.executable)
    agent_main_path = BASE_DIR / "agent_main.py"

    command = f"{python_path} {agent_main_path} >> /var/log/agent.log 2>&1"
    job = cron.new(command=command, comment="AI Agent Cron Job")
    job.minute.every(1)  # Set the job to run every minute

    cron.write()
