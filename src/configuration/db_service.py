import os

from typing import Optional

from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from src.configuration.db_models import (
    KpiPeriodsEnum,
    RecipientEmail,
    RecipientEmailBase,
    SalesCurrencyEnum,
    SalesGroupingsEnum,
    SalesReportRequest,
    SalesReportRequestBase,
)


class SalesReportsDB:
    """Database manager for sales reports with integrated business logic."""

    def __init__(self, db_url: Optional[str] = None):
        """Initialize the database manager.

        Args:
            db_url: Database URL. If None, uses default SQLite file.
        """
        if db_url is None:
            db_path = os.path.join(os.path.dirname(__file__), "configuration.db")
            db_url = f"sqlite:///{db_path}"

        self.engine = create_engine(db_url, echo=False)

        # Create tables if they don't exist
        SQLModel.metadata.create_all(self.engine)

    def add_sales_report_request(
        self, report: SalesReportRequestBase
    ) -> SalesReportRequest:
        """Add a single sales report request to the database.

        Args:
            report: Sales report request to add (base model with validation).

        Returns:
            The created sales report request with database ID included.
        """
        with Session(self.engine) as session:
            # Convert from base model to table model
            db_report = SalesReportRequest(
                period=report.period,
                grouping=report.grouping,
                grouping_value=report.grouping_value,
                currency=report.currency,
            )

            # Handle recipients if they exist
            if hasattr(report, "recipients") and report.recipients:
                for recipient_base in report.recipients:
                    db_recipient = RecipientEmail(
                        email=recipient_base.email,
                        name=recipient_base.name,
                    )
                    db_report.recipients.append(db_recipient)

            session.add(db_report)
            session.commit()
            session.refresh(db_report)
            return db_report

    def get_sales_report_requests(self) -> list[SalesReportRequest]:
        """Get all sales report requests from the database.

        Returns:
            List of sales report requests.
        """
        with Session(self.engine) as session:
            results = session.query(SalesReportRequest).all()
            return results

    def get_sales_report_request(self) -> Optional[SalesReportRequest]:
        """Get the first sales report request from the database (for backward compatibility).

        Returns:
            First sales report request or None if no reports exist.
        """
        reports = self.get_sales_report_requests()
        return reports[0] if reports else None

    def create_report(
        self,
        period: KpiPeriodsEnum,
        grouping: Optional[SalesGroupingsEnum] = None,
        grouping_value: Optional[str] = None,
        currency: SalesCurrencyEnum = SalesCurrencyEnum.FUNCTIONAL,
        recipients: Optional[list[RecipientEmailBase]] = None,
    ) -> SalesReportRequest:
        """Create a new sales report request with validation.

        Args:
            period: The reporting period (monthly, quarterly, yearly).
            grouping: Optional grouping dimension.
            grouping_value: Value for the grouping dimension.
            currency: Currency type for the report.
            recipients: List of email recipients.

        Returns:
            The created sales report request.

        Raises:
            ValueError: If grouping and grouping_value don't match (both None or both provided).
        """
        # Create base model (this will trigger validation)
        report = SalesReportRequestBase(
            period=period,
            grouping=grouping,
            grouping_value=grouping_value,
            currency=currency,
        )

        # Add recipients to the base model for conversion
        if recipients:
            report = report.model_copy()
            report.recipients = recipients

        return self.add_sales_report_request(report)

    def add_recipient_to_report(
        self, report_id: int, email: str, name: str
    ) -> RecipientEmail:
        """Add a recipient to an existing report.

        Args:
            report_id: ID of the sales report.
            email: Recipient email address.
            name: Recipient name.

        Returns:
            The created recipient.
        """
        recipient = RecipientEmail(email=email, name=name, parent_id=report_id)

        with Session(self.engine) as session:
            session.add(recipient)
            session.commit()
            session.refresh(recipient)
            return recipient

    def get_reports_by_grouping(
        self, grouping: SalesGroupingsEnum
    ) -> list[SalesReportRequest]:
        """Get all reports for a specific grouping type.

        Args:
            grouping: The grouping type to filter by.

        Returns:
            List of reports with the specified grouping.
        """
        with Session(self.engine) as session:
            results = (
                session.query(SalesReportRequest)
                .filter(SalesReportRequest.grouping == grouping)
                .all()
            )
            return results

    def get_reports_by_period(self, period: KpiPeriodsEnum) -> list[SalesReportRequest]:
        """Get all reports for a specific period.

        Args:
            period: The period to filter by.

        Returns:
            List of reports with the specified period.
        """
        with Session(self.engine) as session:
            results = (
                session.query(SalesReportRequest)
                .filter(SalesReportRequest.period == period)
                .all()
            )
            return results
