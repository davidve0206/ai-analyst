from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, model_validator, ConfigDict
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# SQLAlchemy Base
class Base(DeclarativeBase):
    pass


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


# Pydantic Models for API/validation
class RecipientEmail(BaseModel):
    """Base model for recipient emails with validation."""

    model_config = ConfigDict(from_attributes=True)

    email: str
    name: str


class SalesReportRequestBase(BaseModel):
    """Base model for sales report requests without validation."""

    period: KpiPeriodsEnum
    grouping: Optional[SalesGroupingsEnum] = None
    grouping_value: Optional[str] = None
    currency: SalesCurrencyEnum = SalesCurrencyEnum.FUNCTIONAL
    recipients: list[RecipientEmail]


class SalesReportRequestCreateDto(SalesReportRequestBase):
    """Model for creating a new sales report request with all validations."""

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

    @model_validator(mode="after")
    def validate_recipients(self):
        """Validate that at least one recipient is provided."""
        if not self.recipients or len(self.recipients) == 0:
            raise ValueError("At least one recipient must be provided")
        return self

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


class SalesReportRequestUpdateDto(SalesReportRequestBase):
    """Model for updating an existing sales report request."""

    id: int


class SalesReportRequest(SalesReportRequestBase):
    """Base model for sales report requests without validation after DB retrieval."""

    model_config = ConfigDict(from_attributes=True)

    id: int


# SQLAlchemy Models for database
class RecipientEmailModel(Base):
    """Database table model for recipient emails."""

    __tablename__ = "recipient_emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    request_id: Mapped[int] = mapped_column(ForeignKey("sales_report_requests.id"))

    # Relationship back to the sales report
    sales_report_request: Mapped["SalesReportRequestModel"] = relationship(
        back_populates="recipients"
    )


class SalesReportRequestModel(Base):
    """Database table model for sales report requests."""

    __tablename__ = "sales_report_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    period: Mapped[KpiPeriodsEnum] = mapped_column(SQLEnum(KpiPeriodsEnum))
    grouping: Mapped[Optional[SalesGroupingsEnum]] = mapped_column(
        SQLEnum(SalesGroupingsEnum), nullable=True
    )
    grouping_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    currency: Mapped[SalesCurrencyEnum] = mapped_column(
        SQLEnum(SalesCurrencyEnum), default=SalesCurrencyEnum.FUNCTIONAL
    )

    # Relationship to recipients with cascade delete
    recipients: Mapped[List["RecipientEmailModel"]] = relationship(
        back_populates="sales_report_request", cascade="all, delete-orphan"
    )
