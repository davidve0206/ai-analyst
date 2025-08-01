import os

from typing import Optional

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import selectinload
from sqlmodel import SQLModel, Session, select

from .db_models import (
    SalesReportRequestCreate,
    SalesReportRequestUpdate,
    SalesReportRequest,
    RecipientEmail,
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
            _ = db_request.recipients

            return db_request

    def update_sales_report_request(
        self, update_data: SalesReportRequestUpdate
    ) -> SalesReportRequest:
        """Update an existing sales report request in the database.

        Args:
            update_data: The sales report request update data

        Returns:
            The updated SalesReportRequest with populated recipients
        """
        with Session(self.engine) as session:
            # Get the existing request
            db_request = session.get(SalesReportRequest, update_data.id)
            if db_request is None:
                raise ValueError(
                    f"SalesReportRequest with id {update_data.id} not found"
                )

            # Update the basic fields
            db_request.period = update_data.period
            db_request.grouping = update_data.grouping
            db_request.grouping_value = update_data.grouping_value
            db_request.currency = update_data.currency

            # Handle recipients - delete existing ones first, then create new ones
            # This approach avoids constraint violations with NOT NULL parent_id

            # Bulk delete existing recipients
            session.exec(
                delete(RecipientEmail).where(RecipientEmail.parent_id == update_data.id)
            )

            # Flush to ensure deletions are processed before inserts
            session.flush()

            # Create new recipients and add them to the relationship
            db_request.recipients = [
                RecipientEmail(email=recipient.email, name=recipient.name)
                for recipient in update_data.recipients
            ]

            # Commit the changes
            session.commit()

            # Refresh and load relationships
            session.refresh(db_request)
            _ = db_request.recipients

            return db_request

    def delete_sales_report_request(self, request_id: int) -> SalesReportRequest:
        """Delete a sales report request and all its associated recipient emails.

        Args:
            request_id: The ID of the sales report request to delete

        Returns:
            The deleted SalesReportRequest object (before deletion)

        Raises:
            ValueError: If no request with the given ID exists
        """
        with Session(self.engine) as session:
            # Get the existing request
            db_request = session.get(SalesReportRequest, request_id)
            if db_request is None:
                raise ValueError(f"SalesReportRequest with id {request_id} not found")

            # Load the recipients before deletion to return them
            _ = db_request.recipients

            # Delete the request - cascade will handle recipients automatically
            session.delete(db_request)
            session.commit()

            return db_request

    def get_all_sales_report_requests(self) -> list[SalesReportRequest]:
        """Retrieve all sales report requests from the database.

        Returns:
            List of all SalesReportRequest objects with their recipients loaded
        """
        with Session(self.engine) as session:
            # Get all sales report requests with recipients eagerly loaded
            statement = select(SalesReportRequest).options(
                selectinload(SalesReportRequest.recipients)
            )
            requests = session.exec(statement).all()

            return list(requests)
