import sys
import enum
from pathlib import Path
from typing import Annotated, Self

from crontab import CronTab
from pydantic import BaseModel, Field, model_validator

from src.configuration.settings import BASE_DIR


class JobFrequency(enum.Enum):
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
    days_of_month: list[Annotated[int, Field(strict=True, ge=0, le=31)]] = Field(
        default_factory=list
    )
    months: list[Month] = Field(default_factory=list)
    days_of_week: list[Weekday] = Field(default_factory=list)
    frequency: JobFrequency

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.frequency == JobFrequency.DAY and not self.days_of_week:
            raise ValueError(
                "days_of_week cannot be empty when frequency is set to specific days"
            )
        if self.frequency == JobFrequency.MONTH and (
            not self.months or not self.days_of_month
        ):
            raise ValueError(
                "months and days_of_month cannot be empty when frequency is set to specific months"
            )
        return self

    def __str__(self) -> str:
        """
        Returns a string representation of the CrontabFrequency object.
        """
        if self.frequency == JobFrequency.DAY:
            return f"At {self.hour}:00 on {', '.join(str(day) for day in self.days_of_week)}"
        elif self.frequency == JobFrequency.MONTH:
            return f"At {self.hour}:00 on the {', '.join(str(day) for day in self.days_of_month)} of {', '.join(str(month) for month in self.months)}"
        else:
            return "Invalid frequency"


def set_crontab(config: CrontabFrequency, write: bool = True) -> CronTab:
    """
    Set the crontab for the application.

    Args:
        config (CrontabFrequency): The configuration for the cron job.
        write (bool): Whether to write the changes to the crontab file. Defaults to True.
    Returns:
        CronTab: The CronTab object representing the cron job.
    Raises:
        ValueError: If the frequency type is unsupported or if the configuration is invalid.
    """
    cron = CronTab(user=True)

    for job in cron:
        if "agent" in job.command:
            cron.remove(job)

    python_path = Path(sys.executable)
    agent_main_path = BASE_DIR / "agent_main.py"

    # Command in the form "python /path/to/agent_main.py"
    command = f"{python_path} {agent_main_path}"
    job = cron.new(command=command, comment="AI Agent Cron Job")

    if config.frequency == JobFrequency.DAY:
        job.setall(
            f"0 {config.hour} * * {','.join(str(day) for day in config.days_of_week)}"
        )
    elif config.frequency == JobFrequency.MONTH:
        job.setall(
            f"0 {config.hour} {','.join(str(day) for day in config.days_of_month)} {','.join(str(month) for month in config.months)} *"
        )
    else:
        raise ValueError("Unsupported frequency type")

    # This allows us to test the cron job without writing to the crontab file.
    if write:
        cron.write()

    return job
