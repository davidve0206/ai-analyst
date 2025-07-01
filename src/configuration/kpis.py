from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker

from src.configuration.db import (
    KpiDirectionsEnum,
    KpiPeriodsEnum,
    KpiRequestModel,
    SalesGroupingsEnum,
    SalesReportRequestModel,
)


class KpiRequest(BaseModel):
    name: str
    description: str
    direction: str
    period: str


class SalesReportRequest(BaseModel):
    grouping: str
    grouping_value: str
    period: str

    @property
    def name(self) -> str:
        return f"Sales Report - {self.grouping} - {self.grouping_value}"


def add_kpi_request(session_maker: sessionmaker, kpi: KpiRequest):
    session = session_maker()
    try:
        # Remove all existing KPI entries
        session.query(KpiRequestModel).delete()

        # Add new KPI
        new_kpi = KpiRequestModel(
            name=kpi.name,
            description=kpi.description,
            direction=KpiDirectionsEnum(kpi.direction),
            period=KpiPeriodsEnum(kpi.period),
        )
        session.add(new_kpi)
        session.commit()
    finally:
        session.close()


def get_kpi_requests(session_maker: sessionmaker) -> KpiRequest | None:
    session = session_maker()
    try:
        result = session.query(KpiRequestModel).first()
        if result:
            return KpiRequest(
                name=result.name,
                description=result.description,
                direction=result.direction,
                period=result.period,
            )
        return None
    finally:
        session.close()


def add_sales_report_request(session_maker: sessionmaker, report: SalesReportRequest):
    session = session_maker()
    try:
        # Remove all existing sales report entries
        session.query(SalesReportRequestModel).delete()

        # Add new sales report request
        new_report = SalesReportRequestModel(
            period=KpiPeriodsEnum(report.period),
            grouping=SalesGroupingsEnum(report.grouping),
            grouping_value=report.grouping_value,
        )
        session.add(new_report)
        session.commit()
    finally:
        session.close()


def get_sales_report_request(session_maker: sessionmaker) -> SalesReportRequest | None:
    session = session_maker()
    try:
        result = session.query(SalesReportRequestModel).first()
        if result:
            return SalesReportRequest(
                grouping=result.grouping,
                grouping_value=result.grouping_value,
                period=result.period,
            )
        return None
    finally:
        session.close()
