from src.configuration.db import KpiDirectionsEnum, KpiPeriodsEnum
from src.configuration.kpis import (
    KpiRequest,
    add_kpi_request,
    get_kpi_requests,
)


def test_can_add_kpi_request(test_session_maker):
    kpi = KpiRequest(
        name="Test KPI",
        description="This is a test KPI",
        direction=KpiDirectionsEnum.HIGHER.value,
        period=KpiPeriodsEnum.MONTHLY.value,
    )

    add_kpi_request(test_session_maker, kpi)
    retrieved_kpi = get_kpi_requests(test_session_maker)
    assert retrieved_kpi is not None


def test_can_add_retrieve_kpi_request(test_session_maker):
    kpi = KpiRequest(
        name="Test KPI",
        description="This is a test KPI",
        direction=KpiDirectionsEnum.HIGHER.value,
        period=KpiPeriodsEnum.MONTHLY.value,
    )

    add_kpi_request(test_session_maker, kpi)
    retrieved_kpi = get_kpi_requests(test_session_maker)
    assert retrieved_kpi.name == kpi.name
    assert retrieved_kpi.description == kpi.description
    assert retrieved_kpi.direction == kpi.direction
    assert retrieved_kpi.period == kpi.period


def test_adding_multiple_kpis_overwrites_previous(test_session_maker):
    """Temporary; this should change when the functionality is updated to allow multiple KPIs."""
    kpi1 = KpiRequest(
        name="KPI 1",
        description="First KPI",
        direction=KpiDirectionsEnum.HIGHER.value,
        period=KpiPeriodsEnum.MONTHLY.value,
    )
    kpi2 = KpiRequest(
        name="KPI 2",
        description="Second KPI",
        direction=KpiDirectionsEnum.LOWER.value,
        period=KpiPeriodsEnum.QUARTERLY.value,
    )

    add_kpi_request(test_session_maker, kpi1)
    add_kpi_request(test_session_maker, kpi2)

    retrieved_kpi = get_kpi_requests(test_session_maker)
    assert retrieved_kpi is not None
    assert retrieved_kpi.name == kpi2.name
    assert retrieved_kpi.description == kpi2.description
    assert retrieved_kpi.direction == kpi2.direction
    assert retrieved_kpi.period == kpi2.period
