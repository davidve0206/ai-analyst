def test_can_add_sales_report_request(test_session_maker):
    report = SalesReportRequest(
        grouping=SalesGroupingsEnum.CITY,
        grouping_value="Los Angeles",
        period=KpiPeriodsEnum.MONTHLY,
    )

    created_report = add_sales_report_request(test_session_maker, report)

    # Verify the function returns the created report with ID
    assert created_report.id is not None
    assert created_report.grouping == report.grouping
    assert created_report.grouping_value == report.grouping_value
    assert created_report.period == report.period


def test_can_add_sales_report_with_no_grouping(test_session_maker):
    """Test adding a sales report with None grouping values."""
    report = SalesReportRequest(
        grouping=None,
        grouping_value=None,
        period=KpiPeriodsEnum.YEARLY,
    )

    created_report = add_sales_report_request(test_session_maker, report)

    assert created_report.id is not None
    assert created_report.grouping is None
    assert created_report.grouping_value is None
    assert created_report.name == "Sales Report - Total Sales"


def test_can_add_retrieve_sales_report_requests(test_session_maker):
    report = SalesReportRequest(
        grouping=SalesGroupingsEnum.COUNTRY,
        grouping_value="United States",
        period=KpiPeriodsEnum.QUARTERLY,
    )

    add_sales_report_request(test_session_maker, report)
    retrieved_report = get_sales_report_request(test_session_maker)
    assert retrieved_report.grouping == report.grouping
    assert retrieved_report.grouping_value == report.grouping_value
    assert retrieved_report.period == report.period


def test_adding_multiple_sales_reports_allows_multiple(test_session_maker):
    """Test that multiple sales reports can now coexist."""
    from src.configuration.db_models import get_sales_report_requests

    report1 = SalesReportRequest(
        grouping=SalesGroupingsEnum.CITY,
        grouping_value="Los Angeles",
        period=KpiPeriodsEnum.MONTHLY,
    )
    report2 = SalesReportRequest(
        grouping=SalesGroupingsEnum.COUNTRY,
        grouping_value="United States",
        period=KpiPeriodsEnum.YEARLY,
    )

    add_sales_report_request(test_session_maker, report1)
    add_sales_report_request(test_session_maker, report2)

    all_reports = get_sales_report_requests(test_session_maker)
    assert len(all_reports) == 2


def test_sales_report_name_property(test_session_maker):
    """Test the name property of SalesReportRequest."""
    report = SalesReportRequest(
        grouping=SalesGroupingsEnum.PRODUCT_FAMILY,
        grouping_value="Electronics",
        period=KpiPeriodsEnum.QUARTERLY,
    )

    expected_name = "Sales Report - Product Family - Electronics"
    assert report.name == expected_name

    # Test that it works after adding to database
    add_sales_report_request(test_session_maker, report)
    retrieved_report = get_sales_report_request(test_session_maker)
    assert retrieved_report.name == expected_name


def test_can_add_sales_report_with_recipients(test_session_maker):
    """Test adding a sales report with recipient emails."""
    recipients = [
        RecipientEmail(email="user1@example.com", name="User One"),
        RecipientEmail(email="user2@example.com", name="User Two"),
    ]

    report = SalesReportRequest(
        grouping=SalesGroupingsEnum.COUNTRY,
        grouping_value="Spain",
        period=KpiPeriodsEnum.QUARTERLY,
        recipients=recipients,
    )

    created_report = add_sales_report_request(test_session_maker, report)

    # Verify recipients were saved and have IDs
    assert len(created_report.recipients) == 2
    assert all(recipient.id is not None for recipient in created_report.recipients)
    assert created_report.recipients[0].email == "user1@example.com"
    assert created_report.recipients[1].name == "User Two"
