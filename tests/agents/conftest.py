import pytest
import pandas as pd

from src.agents.models import default_models, AppChatModels
from src.configuration.kpis import SalesReportRequest
from src.configuration.settings import DATA_DIR
from .helpers import test_temp_dir


@pytest.fixture(scope="session")
def models_client() -> AppChatModels:
    return default_models


@pytest.fixture(scope="function")
def patch_get_quantitative_agent(models_client: AppChatModels, monkeypatch):
    """
    Fixture to get the quantitative agent for testing, with a patched
    temporary directory for file creation.
    """
    monkeypatch.setattr("src.agents.quant_agent.TEMP_DIR", test_temp_dir)

    from src.agents.quant_agent import get_quantitative_agent

    return get_quantitative_agent(models_client)


@pytest.fixture(scope="session")
def default_request() -> SalesReportRequest:
    return SalesReportRequest(
        grouping="country",
        grouping_value="Spain",
        period="monthly",
    )


@pytest.fixture(scope="session")
def financials_df() -> pd.DataFrame:
    df_path = DATA_DIR / "financials_final.csv"
    df = pd.read_csv(df_path, encoding="ISO-8859-1", low_memory=False)
    return df


@pytest.fixture(scope="session")
def spain_sales_history_df(financials_df: pd.DataFrame) -> pd.DataFrame:
    spain_sales = financials_df[financials_df["SOLD_TO_COUNTRY"] == "SPAIN"]
    total_gross_amount = (
        spain_sales.groupby(["INVOICE_MONTH", "INVOICE_YEAR"])
        .agg(
            GROSS_AMOUNT=("GROSS_AMOUNT", "sum"),
            INVOICE_COUNT=("INVOICED_QUANTITY", "sum"),
        )
        .reset_index()
    )

    # sort by INVOICE_YEAR and INVOICE_MONTH
    total_gross_amount = total_gross_amount.sort_values(
        by=["INVOICE_YEAR", "INVOICE_MONTH"]
    )

    return total_gross_amount
