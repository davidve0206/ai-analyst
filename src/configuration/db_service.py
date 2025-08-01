import os

from typing import Optional

from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from .db_models import SalesReportRequestCreate, SalesReportRequest, RecipientEmail


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

    def create_sales_report_request(
        self, request_data: SalesReportRequestCreate
    ) -> SalesReportRequest:
        """Create a new sales report request in the database.

        Args:
            request_data: The sales report request data to create

        Returns:
            The created SalesReportRequest with ID and populated recipients
        """
        with Session(self.engine) as session:
            # Create the main sales report request
            db_request = SalesReportRequest(
                period=request_data.period,
                grouping=request_data.grouping,
                grouping_value=request_data.grouping_value,
                currency=request_data.currency,
            )

            # Create recipient emails and establish relationship directly
            db_request.recipients = [
                RecipientEmail(email=recipient.email, name=recipient.name)
                for recipient in request_data.recipients
            ]

            # Add to session and commit
            session.add(db_request)
            session.commit()

            # Refresh and load relationships explicitly
            session.refresh(db_request)
            # Access recipients to ensure they're loaded before session closes
            _ = db_request.recipients

            return db_request
