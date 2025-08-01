from fastapi import FastAPI

from src.frontend.routers import index, sales_report, cronjob

app = FastAPI(
    title="Sales Report Setup", description="FastAPI version of Sales Report Setup"
)

# Include routers
app.include_router(index.router, tags=["home"])
app.include_router(sales_report.router, prefix="/sales_report", tags=["sales_report"])
app.include_router(cronjob.router, prefix="/crontab", tags=["cronjob"])
