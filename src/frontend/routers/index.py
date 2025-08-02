from fastapi import APIRouter, Request, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import asyncio

from src.configuration.db_service import default_db
from src.configuration.db_models import (
    KpiPeriodsEnum,
    SalesGroupingsEnum,
    SalesCurrencyEnum,
)
from src.configuration.crontab import (
    CrontabFrequency,
    JobFrequency,
    Month,
    Weekday,
)
from src.frontend.templates_config import templates

router = APIRouter()


def get_last_crontab_config() -> Optional[CrontabFrequency]:
    """Get the last crontab configuration. TODO: Implement actual retrieval logic."""
    # TODO: Replace with actual logic to retrieve the last configuration
    return None


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page showing all sales report requests and crontab setup."""
    try:
        existing_requests = default_db.get_all_sales_report_requests()
        last_crontab_config = get_last_crontab_config()
    except Exception as e:
        existing_requests = []
        last_crontab_config = None
        error_message = f"Error loading existing requests: {str(e)}"
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "existing_requests": existing_requests,
                "error": error_message,
                "periods": list(KpiPeriodsEnum),
                "groupings": list(SalesGroupingsEnum),
                "currencies": list(SalesCurrencyEnum),
                "job_frequencies": list(JobFrequency),
                "weekdays": list(Weekday),
                "months": list(Month),
                "hours": list(range(0, 24)),
                "days_of_month": list(range(1, 32)),
                "last_crontab_config": last_crontab_config,
            },
        )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "existing_requests": existing_requests,
            "periods": list(KpiPeriodsEnum),
            "groupings": list(SalesGroupingsEnum),
            "currencies": list(SalesCurrencyEnum),
            "job_frequencies": list(JobFrequency),
            "weekdays": list(Weekday),
            "months": list(Month),
            "hours": list(range(0, 24)),
            "days_of_month": list(range(1, 32)),
            "last_crontab_config": last_crontab_config,
        },
    )


async def run_agent_background():
    """Background task to run the AI agent."""
    try:
        from agent_main import main as agent_main

        # Run the agent
        await agent_main()

    except Exception as e:
        # Log the error but don't raise it since this is a background task
        print(f"Error running AI Agent in background: {str(e)}")


@router.post("/run_now")
async def run_now(background_tasks: BackgroundTasks):
    """Execute the AI agent immediately in the background."""
    try:
        # Add the background task
        background_tasks.add_task(run_agent_background)

        return RedirectResponse(
            url="/?success=AI Agent execution started in the background! Check logs for progress.",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/?error=Error starting AI Agent: {str(e)}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
