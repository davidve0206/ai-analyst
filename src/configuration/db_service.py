import os
from typing import Optional

from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import selectinload, Session

from .db_models import (
    Base,
    SalesReportRequestCreateDto,
    SalesReportRequestUpdateDto,
    SalesReportRequest,
    SalesReportRequestModel,
    RecipientEmailModel,
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
        Base.metadata.create_all(self.engine)

    def create_sales_report_request(
        self, request_data: SalesReportRequestCreateDto
    ) -> SalesReportRequest:
        """Create a new sales report request in the database.

        Args:
            request_data: The sales report request data to create

        Returns:
            The created SalesReportRequest with ID and populated recipients
        """
        with Session(self.engine) as session:
            # Create the main sales report request
            db_request = SalesReportRequestModel(
                period=request_data.period,
                grouping=request_data.grouping,
                grouping_value=request_data.grouping_value,
                currency=request_data.currency,
            )

            # Create recipient emails and establish relationship directly
            db_request.recipients = [
                RecipientEmailModel(email=recipient.email, name=recipient.name)
                for recipient in request_data.recipients
            ]

            # Add to session and commit
            session.add(db_request)
            session.commit()

            # Refresh to ensure all relationships are loaded
            session.refresh(db_request)

            # Convert to Pydantic model for return
            return SalesReportRequest.model_validate(db_request)

    def update_sales_report_request(
        self, update_data: SalesReportRequestUpdateDto
    ) -> SalesReportRequest:
        """Update an existing sales report request in the database.

        Args:
            update_data: The sales report request update data

        Returns:
            The updated SalesReportRequest with populated recipients
        """
        with Session(self.engine) as session:
            # Get the existing request
            db_request = session.get(SalesReportRequestModel, update_data.id)
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
            session.execute(
                delete(RecipientEmailModel).where(
                    RecipientEmailModel.request_id == update_data.id
                )
            )
            session.flush()

            # Create new recipients and add them to the relationship
            db_request.recipients = [
                RecipientEmailModel(email=recipient.email, name=recipient.name)
                for recipient in update_data.recipients
            ]

            # Commit the changes
            session.commit()
            session.refresh(db_request)

            # Convert to Pydantic model for return
            return SalesReportRequest.model_validate(db_request)

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
            # Get the existing request with eager loading
            stmt = (
                select(SalesReportRequestModel)
                .options(selectinload(SalesReportRequestModel.recipients))
                .where(SalesReportRequestModel.id == request_id)
            )

            db_request = session.execute(stmt).scalar_one_or_none()
            if db_request is None:
                raise ValueError(f"SalesReportRequest with id {request_id} not found")

            # Convert to Pydantic model before deletion
            result = SalesReportRequest.model_validate(db_request)

            # Delete the request - cascade will handle recipients automatically
            session.delete(db_request)
            session.commit()

            return result

    def get_all_sales_report_requests(self) -> list[SalesReportRequest]:
        """Retrieve all sales report requests from the database.

        Returns:
            List of all SalesReportRequest objects with their recipients loaded
        """
        with Session(self.engine) as session:
            # Get all sales report requests with recipients eagerly loaded
            stmt = select(SalesReportRequestModel).options(
                selectinload(SalesReportRequestModel.recipients)
            )
            db_requests = session.execute(stmt).scalars().all()

            # Convert to Pydantic models for return
            return [
                SalesReportRequest.model_validate(request) for request in db_requests
            ]


default_db = SalesReportsDB()
