from enum import Enum
from typing import Optional

from pydantic import model_validator
from sqlmodel import SQLModel, Field, Relationship


class KpiPeriodsEnum(Enum):
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"


class SalesGroupingsEnum(Enum):
    COUNTRY = "Country"
    CITY = "City"
    PRODUCT_FAMILY = "Product Family"


class SalesCurrencyEnum(Enum):
    FUNCTIONAL = "Functional currency"
    REPORTING = "Reporting currency"


class RecipientEmailBase(SQLModel):
    """Base model for recipient emails with validation."""

    email: str
    name: str


class RecipientEmail(RecipientEmailBase, table=True):
    """Database table model for recipient emails."""

    __tablename__ = "recipient_emails"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: int = Field(foreign_key="sales_report_requests.id")

    # Relationship back to the sales report
    sales_report_request: Optional["SalesReportRequest"] = Relationship(
        back_populates="recipients"
    )


class SalesReportRequestBase(SQLModel):
    """Base model for sales report requests with validation."""

    period: KpiPeriodsEnum
    grouping: Optional[SalesGroupingsEnum] = Field(default=None)
    grouping_value: Optional[str] = Field(default=None)
    currency: SalesCurrencyEnum = Field(default=SalesCurrencyEnum.FUNCTIONAL)

    @model_validator(mode="before")
    def validate_grouping_relationship(cls, values):
        """Validate that grouping and grouping_value are both provided or both None."""
        # Handle both dict and object inputs
        if isinstance(values, dict):
            grouping = values.get("grouping")
            grouping_value = values.get("grouping_value")
        else:
            # For object inputs, get attributes
            grouping = getattr(values, "grouping", None)
            grouping_value = getattr(values, "grouping_value", None)

        if (grouping is None) != (grouping_value is None):
            raise ValueError(
                "grouping and grouping_value must both be provided or both be None"
            )
        return values

    @property
    def name(self) -> str:
        if self.grouping is None:
            return "Sales Report - Total Sales"
        else:
            return f"Sales Report - {self.grouping.value} - {self.grouping_value}"

    @property
    def task_id(self) -> str:
        if self.grouping is None or self.grouping_value is None:
            return "sales_report_total_sales"
        return f"sales_report_{self.grouping.value.lower().replace(' ', '_')}_{self.grouping_value.lower().replace(' ', '_')}"


class SalesReportRequest(SalesReportRequestBase, table=True):
    """Database table model for sales report requests."""

    __tablename__ = "sales_report_requests"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationship to recipients with cascade delete
    recipients: list[RecipientEmail] = Relationship(
        back_populates="sales_report_request", cascade_delete=True
    )


class SalesReportRequestCreate(SalesReportRequestBase):
    """Model for creating a new sales report request."""

    recipients: list[RecipientEmailBase]

    @model_validator(mode="after")
    def validate_recipients(self):
        """Validate that at least one recipient is provided."""
        if not self.recipients or len(self.recipients) == 0:
            raise ValueError("At least one recipient must be provided")
        return self


class SalesReportRequestUpdate(SalesReportRequestCreate):
    """Model for updating an existing sales report request."""

    id: int
