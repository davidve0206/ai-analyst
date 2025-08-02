from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from typing import List, Annotated

from src.configuration.crontab import (
    CrontabFrequency,
    JobFrequency,
    Month,
    Weekday,
    set_crontab,
)

router = APIRouter()


def setup_daily_crontab(
    hour: int, days_of_week: List[Weekday], write: bool = True
) -> str:
    """Set up a daily cron job with the specified hour and days of the week."""
    config = CrontabFrequency(
        hour=hour, days_of_week=days_of_week, frequency=JobFrequency.DAY
    )
    set_crontab(config, write)
    return f"Agent set up to run: {config}."


def setup_monthly_crontab(
    hour: int, days_of_month: List[int], months: List[Month], write: bool = True
) -> str:
    """Set up a monthly cron job with the specified hour, days of the month, and months."""
    config = CrontabFrequency(
        hour=hour,
        days_of_month=days_of_month,
        months=months,
        frequency=JobFrequency.MONTH,
    )
    set_crontab(config, write)
    return f"Agent set up to run: {config}."


@router.post("/daily")
async def setup_daily_cron(
    request: Request,
    hour: Annotated[int, Form()],
    days_of_week: Annotated[List[str], Form()] = [],
):
    """Set up daily crontab schedule."""
    try:
        if not days_of_week:
            return RedirectResponse(
                url="/?error=Please select at least one day of the week",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        # Convert string days to Weekday enums
        try:
            weekday_enums = [Weekday(day) for day in days_of_week]
        except ValueError as e:
            return RedirectResponse(
                url=f"/?error=Invalid day selection: {str(e)}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        result = setup_daily_crontab(hour, weekday_enums)
        return RedirectResponse(
            url=f"/?success={result}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/?error=Error setting up daily cron: {str(e)}",
            status_code=status.HTTP_303_SEE_OTHER,
        )


@router.post("/monthly")
async def setup_monthly_cron(
    request: Request,
    hour: Annotated[int, Form()],
    days_of_month: Annotated[List[int], Form()] = [],
    months: Annotated[List[str], Form()] = [],
):
    """Set up monthly crontab schedule."""
    try:
        if not days_of_month or not months:
            return RedirectResponse(
                url="/?error=Please select at least one day of the month and one month",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        # Convert string months to Month enums
        try:
            month_enums = [Month(month) for month in months]
        except ValueError as e:
            return RedirectResponse(
                url=f"/?error=Invalid month selection: {str(e)}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        result = setup_monthly_crontab(hour, days_of_month, month_enums)
        return RedirectResponse(
            url=f"/?success={result}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/?error=Error setting up monthly cron: {str(e)}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
