"""Minimal unit tests for frontend routes to ensure they call correct configuration functions."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.frontend.routers import index, sales_report, cronjob
from src.configuration.db_models import (
    SalesReportRequest,
    RecipientEmail,
    KpiPeriodsEnum,
    SalesCurrencyEnum,
)
from src.configuration.crontab import CrontabFrequency, JobFrequency


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(index.router, tags=["home"])
    app.include_router(
        sales_report.router, prefix="/sales_report", tags=["sales_report"]
    )
    app.include_router(cronjob.router, prefix="/crontab", tags=["cronjob"])

    return TestClient(app)


class TestIndexRoutes:
    """Test index router calls correct configuration functions."""

    @patch("src.frontend.routers.index.templates")
    @patch("src.frontend.routers.index.default_db")
    @patch("src.frontend.routers.index.get_existing_agent_cronjob")
    def test_index_calls_db_and_crontab_functions(
        self, mock_crontab, mock_db, mock_templates, test_client
    ):
        """Test index route calls get_all_sales_report_requests and get_existing_agent_cronjob."""
        # Arrange
        mock_db.get_all_sales_report_requests.return_value = []
        mock_crontab.return_value = None
        mock_templates.TemplateResponse.return_value = "mocked_template"

        # Act
        test_client.get("/")

        # Assert - only check that the functions were called
        mock_db.get_all_sales_report_requests.assert_called_once()
        mock_crontab.assert_called_once()


class TestSalesReportRoutes:
    """Test sales_report router calls correct configuration functions."""

    @patch("src.frontend.routers.sales_report.default_db")
    def test_delete_request_calls_db_delete(self, mock_db, test_client):
        """Test delete_request route calls delete_sales_report_request."""
        # Arrange
        mock_result = SalesReportRequest(
            id=1,
            name="Deleted Report",
            period=KpiPeriodsEnum.MONTHLY,
            grouping=None,
            grouping_value=None,
            currency=SalesCurrencyEnum.FUNCTIONAL,
            recipients=[],
        )
        mock_db.delete_sales_report_request.return_value = mock_result

        # Act
        test_client.post("/sales_report/delete/1")

        # Assert - only check that the function was called
        mock_db.delete_sales_report_request.assert_called_once_with(1)

    @patch("src.frontend.routers.sales_report.templates")
    @patch("src.frontend.routers.sales_report.default_db")
    def test_edit_form_calls_db_get_all(self, mock_db, mock_templates, test_client):
        """Test edit_form route calls get_all_sales_report_requests."""
        # Arrange
        mock_request = SalesReportRequest(
            id=1,
            name="Test Report",
            period=KpiPeriodsEnum.MONTHLY,
            grouping=None,
            grouping_value=None,
            currency=SalesCurrencyEnum.FUNCTIONAL,
            recipients=[RecipientEmail(email="test@test.com", name="Test User")],
        )
        mock_db.get_all_sales_report_requests.return_value = [mock_request]
        mock_templates.TemplateResponse.return_value = "mocked_template"

        # Act
        test_client.get("/sales_report/edit/1")

        # Assert - only check that the function was called
        mock_db.get_all_sales_report_requests.assert_called_once()


class TestCronjobRoutes:
    """Test cronjob router calls correct configuration functions."""

    @patch("src.frontend.routers.cronjob.set_crontab")
    def test_setup_daily_cron_calls_set_crontab(self, mock_set_crontab, test_client):
        """Test setup_daily_cron route calls set_crontab with daily config."""
        # Act
        test_client.post(
            "/crontab/daily", data={"hour": 9, "days_of_week": ["MON", "WED", "FRI"]}
        )

        # Assert - only check that the function was called with correct parameters
        mock_set_crontab.assert_called_once()
        call_args = mock_set_crontab.call_args[0][0]
        assert isinstance(call_args, CrontabFrequency)
        assert call_args.hour == 9
        assert call_args.frequency == JobFrequency.DAY

    @patch("src.frontend.routers.cronjob.set_crontab")
    def test_setup_monthly_cron_calls_set_crontab(self, mock_set_crontab, test_client):
        """Test setup_monthly_cron route calls set_crontab with monthly config."""
        # Act
        test_client.post(
            "/crontab/monthly",
            data={"hour": 14, "days_of_month": [1, 15], "months": ["JAN", "JUL"]},
        )

        # Assert - only check that the function was called with correct parameters
        mock_set_crontab.assert_called_once()
        call_args = mock_set_crontab.call_args[0][0]
        assert isinstance(call_args, CrontabFrequency)
        assert call_args.hour == 14
        assert call_args.frequency == JobFrequency.MONTH
