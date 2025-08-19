import pytest

from src.configuration.db_models import (
    KpiPeriodsEnum,
    SalesGroupingsEnum,
    SalesReportRequestCreateDto,
    SalesReportRequestUpdateDto,
    RecipientEmail,
)

default_recipients = [RecipientEmail(email="test@example.com", name="Test User")]


def test_sales_report_create_grouping_with_value_valid():
    """Test that grouping and grouping_value can both be provided."""
    report = SalesReportRequestCreateDto(
        grouping=SalesGroupingsEnum.CITY,
        grouping_value="Los Angeles",
        period=KpiPeriodsEnum.MONTHLY,
        recipients=default_recipients,
    )
    assert report.grouping == SalesGroupingsEnum.CITY
    assert report.grouping_value == "Los Angeles"


def test_sales_report_create_no_grouping_valid():
    """Test that grouping and grouping_value can both be None."""
    report = SalesReportRequestCreateDto(
        grouping=None,
        grouping_value=None,
        period=KpiPeriodsEnum.MONTHLY,
        recipients=default_recipients,
    )
    assert report.grouping is None
    assert report.grouping_value is None


def test_sales_report_create_grouping_without_value_invalid():
    """Test that providing grouping without grouping_value raises error."""
    with pytest.raises(ValueError, match="grouping.*grouping_value"):
        SalesReportRequestCreateDto(
            grouping=SalesGroupingsEnum.CITY,
            grouping_value=None,
            period=KpiPeriodsEnum.MONTHLY,
            recipients=default_recipients,
        )


def test_sales_report_create_value_without_grouping_invalid():
    """Test that providing grouping_value without grouping raises error."""
    with pytest.raises(ValueError, match="grouping.*grouping_value"):
        SalesReportRequestCreateDto(
            grouping=None,
            grouping_value="California",
            period=KpiPeriodsEnum.MONTHLY,
            recipients=default_recipients,
        )


def test_sales_report_create_successful():
    """Test successful create instance."""
    recipients = [RecipientEmail(email="test@example.com", name="Test User")]

    create_request = SalesReportRequestCreateDto(
        period=KpiPeriodsEnum.MONTHLY,
        grouping=SalesGroupingsEnum.CITY,
        grouping_value="Los Angeles",
        recipients=recipients,
    )

    assert create_request.period == KpiPeriodsEnum.MONTHLY
    assert create_request.grouping == SalesGroupingsEnum.CITY
    assert create_request.grouping_value == "Los Angeles"
    assert len(create_request.recipients) == 1
    assert create_request.name == "Sales Report - City - Los Angeles"


def test_sales_report_create_empty_recipients_invalid():
    """Test create fails with empty recipients list."""
    with pytest.raises(ValueError, match="recipient"):
        SalesReportRequestCreateDto(
            period=KpiPeriodsEnum.MONTHLY,
            recipients=[],
        )


def test_sales_report_update_successful():
    """Test successful update instance."""
    recipients = [RecipientEmail(email="update@example.com", name="Update User")]

    update_request = SalesReportRequestUpdateDto(
        id=1,
        period=KpiPeriodsEnum.MONTHLY,
        grouping=SalesGroupingsEnum.COUNTRY,
        grouping_value="Spain",
        recipients=recipients,
    )

    assert update_request.id == 1
    assert update_request.grouping == SalesGroupingsEnum.COUNTRY
    assert update_request.grouping_value == "Spain"
    assert len(update_request.recipients) == 1
