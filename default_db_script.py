"""Script to populate the default database with initial data."""

from src.configuration.db import (
    KpiPeriodsEnum,
    KpiDirectionsEnum,
    SalesGroupingsEnum,
    default_config_db_sessionmaker,
)
from src.configuration.recipients import add_recipient_email
from src.configuration.kpis import (
    KpiRequest,
    SalesReportRequest,
    add_kpi_request,
    add_sales_report_request,
)


def populate_default_db():
    """Populate the default database with initial data."""
    session_maker = default_config_db_sessionmaker

    # Add default recipient emails
    recipient_emails = ["test1@test.com", "test2@test.com"]
    kpi = KpiRequest(
        name="Gross Profit Margin",
        description="The percentage of revenue that exceeds the cost of the goods sold; it might be referred as profit in the Sales table.",
        direction=KpiDirectionsEnum.HIGHER.value,
        period=KpiPeriodsEnum.QUARTERLY.value,
    )
    sales = SalesReportRequest(
        grouping=SalesGroupingsEnum.STATE.value,
        grouping_value="California",
        period=KpiPeriodsEnum.MONTHLY.value,
    )

    for email in recipient_emails:
        add_recipient_email(session_maker, email)

    add_kpi_request(session_maker, kpi)
    add_sales_report_request(session_maker, sales)


if __name__ == "__main__":
    populate_default_db()
    print("Default database populated with initial data.")
