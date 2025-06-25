from pydantic import BaseModel
from sqlalchemy.orm import sessionmaker

from src.configuration.db import KpiDirectionsEnum, KpiPeriodsEnum, KpiRequestModel


class KpiRequest(BaseModel):
    name: str
    description: str
    direction: str
    period: str


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
