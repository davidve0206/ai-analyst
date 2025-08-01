import pytest
from sqlmodel import Session

from src.configuration.db_service import SalesReportsDB
from src.configuration.db_models import (
    SalesReportRequestCreate,
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


def test_create_sales_report_request_basic(test_db):
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
        db_recipients = (
            session.query(RecipientEmail).filter_by(parent_id=result.id).all()
        )
        assert len(db_recipients) == 2

        emails = [r.email for r in db_recipients]
        names = [r.name for r in db_recipients]
        assert "test1@example.com" in emails
        assert "test2@example.com" in emails
        assert "Test User 1" in names
        assert "Test User 2" in names


def test_create_sales_report_request_without_grouping(test_db):
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
