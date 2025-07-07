import pytest

from src.agents_langgraph.models import AppChatModels
from src.agents_langgraph.tools.db import InternalDatabaseToolkit
from src.agents_langgraph.db_agent import get_database_agent
from src.agents_langgraph.utils import extract_graph_response_content
from .helpers import assert_numeric_value_in_str, california_monthly_sales_in_db


@pytest.mark.asyncio
async def test_internal_db_toolkit_creation(
    internal_db_toolkit: InternalDatabaseToolkit,
):
    """Test the creation of the InternalDatabaseToolkit."""
    assert internal_db_toolkit is not None
    assert internal_db_toolkit.dialect == "mssql"


@pytest.mark.asyncio
async def test_simple_internal_db_agent_request(
    models_client: AppChatModels, internal_db_toolkit: InternalDatabaseToolkit
):
    """Test the basic functionality of the database agent."""

    db_agent = get_database_agent(internal_db_toolkit, models_client)
    query = "What is the date of the most recent 'Invoice Date Key' in the Fact.Sale table? Respond in the format YYYY-MM-DD."
    response = await db_agent.ainvoke({"messages": [("user", query)]})

    assert response is not None
    response_content = extract_graph_response_content(response)
    assert "2025" in response_content
    assert "05" in response_content


@pytest.mark.asyncio
async def test_real_internal_db_agent_request(
    models_client: AppChatModels, internal_db_toolkit: InternalDatabaseToolkit
):
    """Test the basic functionality of the database agent."""

    db_agent = get_database_agent(internal_db_toolkit, models_client)
    query = "Retrieve the last three years of monthly total sales data for the State of California, excluding any collected taxes, available in the database. Include the month and year in the response, formatted as YYYY-MM."
    response = await db_agent.ainvoke({"messages": [("user", query)]})

    assert response is not None
    response_content = extract_graph_response_content(response)
    for month, sales in california_monthly_sales_in_db.items():
        assert_numeric_value_in_str(sales, response_content, None)
        assert month in response_content, f"Month {month} not found in response."
