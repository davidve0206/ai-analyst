from src.configuration.db import KpiPeriodsEnum, SalesGroupingsEnum
from src.configuration.kpis import (
    SalesReportRequest,
    add_sales_report_request,
    get_sales_report_request,
)


def test_can_add_sales_report_request(test_session_maker):
    report = SalesReportRequest(
        grouping=SalesGroupingsEnum.STATE.value,
        grouping_value="California",
        period=KpiPeriodsEnum.MONTHLY.value,
    )

    add_sales_report_request(test_session_maker, report)
    retrieved_report = get_sales_report_request(test_session_maker)
    assert retrieved_report is not None


def test_can_add_retrieve_sales_report_request(test_session_maker):
    report = SalesReportRequest(
        grouping=SalesGroupingsEnum.COUNTRY.value,
        grouping_value="United States",
        period=KpiPeriodsEnum.QUARTERLY.value,
    )

    add_sales_report_request(test_session_maker, report)
    retrieved_report = get_sales_report_request(test_session_maker)
    assert retrieved_report.grouping == report.grouping
    assert retrieved_report.grouping_value == report.grouping_value
    assert retrieved_report.period == report.period


def test_adding_multiple_sales_reports_overwrites_previous(test_session_maker):
    """Temporary; this should change when the functionality is updated to allow multiple sales reports."""
    report1 = SalesReportRequest(
        grouping=SalesGroupingsEnum.STATE.value,
        grouping_value="California",
        period=KpiPeriodsEnum.MONTHLY.value,
    )
    report2 = SalesReportRequest(
        grouping=SalesGroupingsEnum.CITY.value,
        grouping_value="Los Angeles",
        period=KpiPeriodsEnum.YEARLY.value,
    )

    add_sales_report_request(test_session_maker, report1)
    add_sales_report_request(test_session_maker, report2)

    retrieved_report = get_sales_report_request(test_session_maker)
    assert retrieved_report is not None
    assert retrieved_report.grouping == report2.grouping
    assert retrieved_report.grouping_value == report2.grouping_value
    assert retrieved_report.period == report2.period


def test_sales_report_name_property(test_session_maker):
    """Test the name property of SalesReportRequest."""
    report = SalesReportRequest(
        grouping=SalesGroupingsEnum.PRODUCT_CATEGORY.value,
        grouping_value="Electronics",
        period=KpiPeriodsEnum.QUARTERLY.value,
    )

    expected_name = "Sales Report - Product Category - Electronics"
    assert report.name == expected_name

    # Test that it works after adding to database
    add_sales_report_request(test_session_maker, report)
    retrieved_report = get_sales_report_request(test_session_maker)
    assert retrieved_report.name == expected_name


def test_sales_report_with_different_groupings(test_session_maker):
    """Test sales reports with different grouping types."""
    test_cases = [
        (SalesGroupingsEnum.COUNTRY.value, "Canada", KpiPeriodsEnum.MONTHLY.value),
        (SalesGroupingsEnum.STATE.value, "Texas", KpiPeriodsEnum.QUARTERLY.value),
        (SalesGroupingsEnum.CITY.value, "New York", KpiPeriodsEnum.YEARLY.value),
        (
            SalesGroupingsEnum.PRODUCT_CATEGORY.value,
            "Clothing",
            KpiPeriodsEnum.MONTHLY.value,
        ),
    ]

    for grouping, grouping_value, period in test_cases:
        report = SalesReportRequest(
            grouping=grouping,
            grouping_value=grouping_value,
            period=period,
        )

        add_sales_report_request(test_session_maker, report)
        retrieved_report = get_sales_report_request(test_session_maker)

        assert retrieved_report is not None
        assert retrieved_report.grouping == grouping
        assert retrieved_report.grouping_value == grouping_value
        assert retrieved_report.period == period
