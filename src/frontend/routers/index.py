from fastapi import APIRouter, Request, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse

from src.configuration.db_service import default_db
from src.configuration.db_models import (
    KpiPeriodsEnum,
    SalesGroupingsEnum,
    SalesCurrencyEnum,
)
from src.configuration.crontab import (
    Month,
    get_existing_agent_cronjob,
)
from src.frontend.templates_config import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page showing all sales report requests and crontab setup."""
    try:
        existing_requests = default_db.get_all_sales_report_requests()
        last_crontab_config = get_existing_agent_cronjob()
        error_message = None
    except Exception as e:
        existing_requests = []
        last_crontab_config = None
        error_message = f"Error loading existing requests: {str(e)}"

    template_values = {
        "request": request,
        "existing_requests": existing_requests,
        "periods": list(KpiPeriodsEnum),
        "groupings": list(SalesGroupingsEnum),
        "currencies": list(SalesCurrencyEnum),
        "months": list(Month),
        "hours": list(range(0, 24)),
        "days_of_month": list(range(1, 32)),
        "last_crontab_config": last_crontab_config,
    }

    if error_message:
        template_values["error_message"] = error_message

    return templates.TemplateResponse(
        "index.html",
        context=template_values,
    )


@router.post("/run_now")
async def run_now(background_tasks: BackgroundTasks):
    """Execute the AI agent immediately in the background."""
    try:
        # Add the background task
        async def run_agent_background():
            """Background task to run the AI agent."""
            try:
                from agent_main import main as agent_main

                # Run the agent
                await agent_main()

            except Exception as e:
                # Log the error but don't raise it since this is a background task
                print(f"Error running AI Agent in background: {str(e)}")

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
