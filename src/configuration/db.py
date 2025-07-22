import os
from enum import Enum as PyEnum

from sqlalchemy import Column, Enum, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


# Enum definitions matching your literals
class KpiDirectionsEnum(PyEnum):
    HIGHER = "Higher is better"
    LOWER = "Lower is better"
    NONE = "No direction"


class KpiPeriodsEnum(PyEnum):
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"


class SalesGroupingsEnum(PyEnum):
    COUNTRY = "Country"
    STATE = "State"
    CITY = "City"
    PRODUCT_CATEGORY = "Product Category"


class SalesCurrencyEnum(PyEnum):
    FUNCTIONAL = "Functional currency"
    REPORTING = "Reporting currency"


# SQLAlchemy model
class KpiRequestModel(Base):
    __tablename__ = "kpi_requests"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    direction = Column(Enum(KpiDirectionsEnum), nullable=False)
    period = Column(Enum(KpiPeriodsEnum), nullable=False)


class SalesReportRequestModel(Base):
    __tablename__ = "sales_report_requests"
    id = Column(Integer, primary_key=True)
    period = Column(Enum(KpiPeriodsEnum), nullable=False)
    grouping = Column(Enum(SalesGroupingsEnum), nullable=False)
    grouping_value = Column(String, nullable=False)
    currency = Column(Enum(SalesCurrencyEnum), nullable=False)


class RecipientEmail(Base):
    __tablename__ = "recipient_emails"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)


DB_PATH = os.path.join(os.path.dirname(__file__), "configuration.db")
DB_URL = f"sqlite:///{DB_PATH}"


def create_config_db_sessionmaker(url: str) -> sessionmaker:
    """
    Create a sessionmaker for the configuration database.

    :param path: Path to the SQLite database file.
    :return: A sessionmaker bound to the SQLite engine.
    """
    engine = create_engine(url, echo=False)

    # Create tables if they don't exist
    Base.metadata.create_all(engine)

    return sessionmaker(bind=engine)


default_config_db_sessionmaker = create_config_db_sessionmaker(DB_URL)
