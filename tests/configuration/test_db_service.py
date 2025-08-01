import pytest
from sqlmodel import Session, select

from src.configuration.db_service import SalesReportsDB
from src.configuration.db_models import (
    SalesReportRequestCreate,
    SalesReportRequestUpdate,
    SalesReportRequest,
    RecipientEmailBase,
    KpiPeriodsEnum,
    SalesGroupingsEnum,
    SalesCurrencyEnum,
    RecipientEmail,
)


@pytest.fixture
def test_db():
    """Create an in-memory database for testing."""
    return SalesReportsDB(db_url="sqlite:///:memory:")


def test_create_sales_report_request_basic(test_db: SalesReportsDB):
    """Test creating a basic sales report request with all data persisted correctly."""
    # Arrange
    recipients = [
        RecipientEmailBase(email="test1@example.com", name="Test User 1"),
        RecipientEmailBase(email="test2@example.com", name="Test User 2"),
    ]

    request_data = SalesReportRequestCreate(
        period=KpiPeriodsEnum.MONTHLY,
        grouping=SalesGroupingsEnum.COUNTRY,
        grouping_value="Spain",
        currency=SalesCurrencyEnum.FUNCTIONAL,
        recipients=recipients,
    )

    # Act
    result = test_db.create_sales_report_request(request_data)

    # Assert - Check the returned object
    assert isinstance(result, SalesReportRequest)
    assert result.id is not None
    assert result.period == KpiPeriodsEnum.MONTHLY
    assert result.grouping == SalesGroupingsEnum.COUNTRY
    assert result.grouping_value == "Spain"
    assert result.currency == SalesCurrencyEnum.FUNCTIONAL
    assert len(result.recipients) == 2

    # Check recipients
    assert result.recipients[0].email == "test1@example.com"
    assert result.recipients[0].name == "Test User 1"
    assert result.recipients[1].email == "test2@example.com"
    assert result.recipients[1].name == "Test User 2"

    # Assert - Verify data is actually in the database
    with Session(test_db.engine) as session:
        # Check sales report request is in database
        db_request = session.get(SalesReportRequest, result.id)
        assert db_request is not None
        assert db_request.period == KpiPeriodsEnum.MONTHLY
        assert db_request.grouping == SalesGroupingsEnum.COUNTRY
        assert db_request.grouping_value == "Spain"
        assert db_request.currency == SalesCurrencyEnum.FUNCTIONAL

        # Check recipients are in database
        db_recipients = session.exec(
            select(RecipientEmail).where(RecipientEmail.parent_id == result.id)
        ).all()
        assert len(db_recipients) == 2

        emails = [r.email for r in db_recipients]
        names = [r.name for r in db_recipients]
        assert "test1@example.com" in emails
        assert "test2@example.com" in emails
        assert "Test User 1" in names
        assert "Test User 2" in names


def test_create_sales_report_request_without_grouping(test_db: SalesReportsDB):
    """Test creating a sales report request without grouping (total sales)."""
    # Arrange
    recipients = [RecipientEmailBase(email="admin@example.com", name="Admin User")]

    request_data = SalesReportRequestCreate(
        period=KpiPeriodsEnum.QUARTERLY,
        grouping=None,
        grouping_value=None,
        currency=SalesCurrencyEnum.REPORTING,
        recipients=recipients,
    )

    # Act
    result = test_db.create_sales_report_request(request_data)

    # Assert
    assert isinstance(result, SalesReportRequest)
    assert result.id is not None
    assert result.period == KpiPeriodsEnum.QUARTERLY
    assert result.grouping is None
    assert result.grouping_value is None
    assert result.currency == SalesCurrencyEnum.REPORTING
    assert len(result.recipients) == 1
    assert result.recipients[0].email == "admin@example.com"
    assert result.recipients[0].name == "Admin User"

    # Verify in database
    with Session(test_db.engine) as session:
        db_request = session.get(SalesReportRequest, result.id)
        assert db_request is not None
        assert db_request.grouping is None
        assert db_request.grouping_value is None


def test_update_sales_report_request_with_email_changes(test_db: SalesReportsDB):
    """Test updating a sales report request with changes to recipient emails."""
    # Arrange - Create initial request
    initial_recipients = [
        RecipientEmailBase(email="user1@example.com", name="User One"),
        RecipientEmailBase(email="user2@example.com", name="User Two"),
    ]

    initial_request = SalesReportRequestCreate(
        period=KpiPeriodsEnum.MONTHLY,
        grouping=SalesGroupingsEnum.CITY,
        grouping_value="Madrid",
        currency=SalesCurrencyEnum.FUNCTIONAL,
        recipients=initial_recipients,
    )

    created_request = test_db.create_sales_report_request(initial_request)

    # Arrange - Prepare update with different recipients
    updated_recipients = [
        RecipientEmailBase(
            email="user1@example.com", name="User One Updated"
        ),  # Updated name
        RecipientEmailBase(email="user3@example.com", name="User Three"),  # New user
        # Note: user2@example.com is removed
    ]

    update_data = SalesReportRequestUpdate(
        id=created_request.id,
        period=KpiPeriodsEnum.QUARTERLY,  # Changed
        grouping=SalesGroupingsEnum.CITY,
        grouping_value="Barcelona",  # Changed
        currency=SalesCurrencyEnum.REPORTING,  # Changed
        recipients=updated_recipients,
    )

    # Act
    result = test_db.update_sales_report_request(update_data)

    # Assert - Check the returned object
    assert isinstance(result, SalesReportRequest)
    assert result.id == created_request.id
    assert result.period == KpiPeriodsEnum.QUARTERLY
    assert result.grouping == SalesGroupingsEnum.CITY
    assert result.grouping_value == "Barcelona"
    assert result.currency == SalesCurrencyEnum.REPORTING
    assert len(result.recipients) == 2

    # Check recipients are correctly updated
    emails = [r.email for r in result.recipients]
    names = [r.name for r in result.recipients]
    assert "user1@example.com" in emails
    assert "user3@example.com" in emails
    assert "user2@example.com" not in emails  # Should be removed
    assert "User One Updated" in names
    assert "User Three" in names

    # Assert - Verify data is correctly updated in the database
    with Session(test_db.engine) as session:
        # Check sales report request is updated in database
        db_request = session.get(SalesReportRequest, result.id)
        assert db_request is not None
        assert db_request.period == KpiPeriodsEnum.QUARTERLY
        assert db_request.grouping == SalesGroupingsEnum.CITY
        assert db_request.grouping_value == "Barcelona"
        assert db_request.currency == SalesCurrencyEnum.REPORTING

        # Check recipients are correctly updated in database
        db_recipients = session.exec(
            select(RecipientEmail).where(RecipientEmail.parent_id == result.id)
        ).all()
        assert len(db_recipients) == 2

        db_emails = [r.email for r in db_recipients]
        db_names = [r.name for r in db_recipients]
        assert "user1@example.com" in db_emails
        assert "user3@example.com" in db_emails
        assert "user2@example.com" not in db_emails
        assert "User One Updated" in db_names
        assert "User Three" in db_names


def test_update_sales_report_request_basic_fields_only(test_db: SalesReportsDB):
    """Test updating basic fields while keeping the same recipients."""
    # Arrange - Create initial request
    initial_recipients = [
        RecipientEmailBase(email="admin@example.com", name="Admin User"),
    ]

    initial_request = SalesReportRequestCreate(
        period=KpiPeriodsEnum.YEARLY,
        grouping=SalesGroupingsEnum.PRODUCT_FAMILY,
        grouping_value="Electronics",
        currency=SalesCurrencyEnum.FUNCTIONAL,
        recipients=initial_recipients,
    )

    created_request = test_db.create_sales_report_request(initial_request)

    # Arrange - Prepare update with same recipients but different other fields
    update_data = SalesReportRequestUpdate(
        id=created_request.id,
        period=KpiPeriodsEnum.MONTHLY,  # Changed
        grouping=None,  # Changed to no grouping
        grouping_value=None,  # Changed to no grouping
        currency=SalesCurrencyEnum.REPORTING,  # Changed
        recipients=initial_recipients,  # Same recipients
    )

    # Act
    result = test_db.update_sales_report_request(update_data)

    # Assert - Check the returned object
    assert isinstance(result, SalesReportRequest)
    assert result.id == created_request.id
    assert result.period == KpiPeriodsEnum.MONTHLY
    assert result.grouping is None
    assert result.grouping_value is None
    assert result.currency == SalesCurrencyEnum.REPORTING
    assert len(result.recipients) == 1
    assert result.recipients[0].email == "admin@example.com"
    assert result.recipients[0].name == "Admin User"

    # Assert - Verify data is correctly updated in the database
    with Session(test_db.engine) as session:
        db_request = session.get(SalesReportRequest, result.id)
        assert db_request is not None
        assert db_request.period == KpiPeriodsEnum.MONTHLY
        assert db_request.grouping is None
        assert db_request.grouping_value is None
        assert db_request.currency == SalesCurrencyEnum.REPORTING

        # Check that recipients are still correct in database
        db_recipients = session.exec(
            select(RecipientEmail).where(RecipientEmail.parent_id == result.id)
        ).all()
        assert len(db_recipients) == 1
        assert db_recipients[0].email == "admin@example.com"
        assert db_recipients[0].name == "Admin User"


def test_update_sales_report_request_nonexistent(test_db: SalesReportsDB):
    """Test updating a non-existent sales report request raises ValueError."""
    update_data = SalesReportRequestUpdate(
        id=99999,  # Non-existent ID
        period=KpiPeriodsEnum.MONTHLY,
        grouping=None,
        grouping_value=None,
        currency=SalesCurrencyEnum.FUNCTIONAL,
        recipients=[RecipientEmailBase(email="test@example.com", name="Test User")],
    )

    # Act & Assert - Try to update a request that doesn't exist
    with pytest.raises(ValueError):
        test_db.update_sales_report_request(update_data)


def test_delete_sales_report_request_with_recipients(test_db: SalesReportsDB):
    """Test deleting a sales report request removes it and all associated recipients."""
    # Arrange - Create a request with multiple recipients
    recipients = [
        RecipientEmailBase(email="user1@example.com", name="User One"),
        RecipientEmailBase(email="user2@example.com", name="User Two"),
        RecipientEmailBase(email="user3@example.com", name="User Three"),
    ]

    request_data = SalesReportRequestCreate(
        period=KpiPeriodsEnum.MONTHLY,
        grouping=SalesGroupingsEnum.COUNTRY,
        grouping_value="France",
        currency=SalesCurrencyEnum.FUNCTIONAL,
        recipients=recipients,
    )

    created_request = test_db.create_sales_report_request(request_data)
    request_id = created_request.id

    # Act - Delete the request
    deleted_request = test_db.delete_sales_report_request(request_id)

    # Assert - Check the returned deleted object (simplified)
    assert deleted_request.id == request_id
    assert len(deleted_request.recipients) == 3

    # Assert - Verify both request and recipients are deleted from database
    with Session(test_db.engine) as session:
        # Check that the request is deleted
        db_request = session.get(SalesReportRequest, request_id)
        assert db_request is None

        # Check that all associated recipients are also deleted
        db_recipients = session.exec(
            select(RecipientEmail).where(RecipientEmail.parent_id == request_id)
        ).all()
        assert len(db_recipients) == 0


def test_delete_sales_report_request_nonexistent(test_db: SalesReportsDB):
    """Test deleting a non-existent sales report request raises ValueError."""
    # Act & Assert - Try to delete a request that doesn't exist
    with pytest.raises(ValueError):
        test_db.delete_sales_report_request(99999)


def test_get_all_sales_report_requests(test_db: SalesReportsDB):
    """Test retrieving all sales report requests from the database."""
    # Arrange - Create multiple requests
    request1_data = SalesReportRequestCreate(
        period=KpiPeriodsEnum.MONTHLY,
        grouping=SalesGroupingsEnum.COUNTRY,
        grouping_value="Spain",
        currency=SalesCurrencyEnum.FUNCTIONAL,
        recipients=[RecipientEmailBase(email="user1@example.com", name="User One")],
    )

    request2_data = SalesReportRequestCreate(
        period=KpiPeriodsEnum.QUARTERLY,
        grouping=None,
        grouping_value=None,
        currency=SalesCurrencyEnum.REPORTING,
        recipients=[RecipientEmailBase(email="user2@example.com", name="User Two")],
    )

    request3_data = SalesReportRequestCreate(
        period=KpiPeriodsEnum.YEARLY,
        grouping=SalesGroupingsEnum.CITY,
        grouping_value="Madrid",
        currency=SalesCurrencyEnum.FUNCTIONAL,
        recipients=[
            RecipientEmailBase(email="user3@example.com", name="User Three"),
            RecipientEmailBase(email="user4@example.com", name="User Four"),
        ],
    )

    # Create the requests
    created1 = test_db.create_sales_report_request(request1_data)
    created2 = test_db.create_sales_report_request(request2_data)
    created3 = test_db.create_sales_report_request(request3_data)

    # Act - Retrieve all requests
    all_requests = test_db.get_all_sales_report_requests()

    # Assert - Check we got all 3 requests with their IDs
    assert len(all_requests) == 3

    request_ids = [r.id for r in all_requests]
    assert created1.id in request_ids
    assert created2.id in request_ids
    assert created3.id in request_ids

    # Check that recipients are properly loaded
    for request in all_requests:
        assert len(request.recipients) > 0


def test_get_all_sales_report_requests_empty(test_db: SalesReportsDB):
    """Test retrieving all sales report requests when database is empty."""
    # Act - Retrieve all requests from empty database
    all_requests = test_db.get_all_sales_report_requests()

    # Assert - Should return empty list
    assert isinstance(all_requests, list)
    assert len(all_requests) == 0
