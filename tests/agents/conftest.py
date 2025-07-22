from pathlib import Path
from typing import Callable
import pytest
import pandas as pd

from src.agents.models import default_models, AppChatModels
from src.configuration.kpis import SalesReportRequest
from .helpers import test_temp_dir


@pytest.fixture(scope="session")
def models_client() -> AppChatModels:
    return default_models


@pytest.fixture(scope="session")
def patched_get_request_temp_dir():
    """
    Fixture to get the temporary directory for a specific sales report request.
    """

    def _get_request_temp_dir(request: SalesReportRequest) -> Path:
        return test_temp_dir

    return _get_request_temp_dir


@pytest.fixture(scope="function")
def quantitative_agent(
    models_client: AppChatModels,
    patched_get_request_temp_dir: Callable,
    default_request: SalesReportRequest,
    monkeypatch,
):
    """
    Fixture to get the quantitative agent for testing, with a patched
    temporary directory for file creation.
    """
    # Patch the TEMP_DIR - ensure its patched wherever it's used
    monkeypatch.setattr(
        "src.agents.utils.output_utils.get_request_temp_dir",
        patched_get_request_temp_dir,
    )

    from src.agents.quant_agent import get_quantitative_agent

    return get_quantitative_agent(models=models_client, request=default_request)


@pytest.fixture(scope="function")
def data_visualization_agent(models_client: AppChatModels, monkeypatch):
    """
    Fixture to get the data visualization agent for testing, with a patched
    temporary directory for file creation.
    """
    monkeypatch.setattr("src.agents.data_visualization_agent.TEMP_DIR", test_temp_dir)

    from src.agents.data_visualization_agent import get_data_visualization_agent

    return get_data_visualization_agent(models_client)


@pytest.fixture(scope="session")
def default_request() -> SalesReportRequest:
    return SalesReportRequest(
        grouping="country",
        grouping_value="Spain",
        period="monthly",
        currency="Functional currency",
    )


@pytest.fixture(scope="session")
def spain_sales_history_df() -> pd.DataFrame:
    df_path = test_temp_dir / "Spain_sales_history_fixture.csv"
    spain_sales = pd.read_csv(df_path, encoding="ISO-8859-1", low_memory=False)

    return spain_sales
