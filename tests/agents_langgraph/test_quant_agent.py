import pytest

from langgraph.graph.state import CompiledStateGraph

from src.agents_langgraph.models import AppChatModels
from src.agents_langgraph.utils import extract_graph_response_content

from .helpers import california_monthly_sales_in_db, test_temp_dir


@pytest.fixture(scope="function")
def quantitative_agent(models_client: AppChatModels, monkeypatch):
    """
    Fixture to get the quantitative agent for testing, with a patched
    temporary directory for file creation.
    """
    monkeypatch.setattr("src.configuration.settings.TEMP_DIR", test_temp_dir)

    from src.agents_langgraph.quant_agent import get_quantitative_agent

    return get_quantitative_agent(models_client)


@pytest.mark.asyncio
async def test_task_with_intermediate_interpreter(
    quantitative_agent: CompiledStateGraph,
):
    """
    Test the agent with a task that requires basic code generation and execution.
    """
    query = """The company made the following revenue every year: 
    
    2021: 300, 2022: 325, 2023: 350, 2024: 325, 2025: 400.
    
    What is the average growth rate (CAGR)?"""
    expected = (
        "7.46"  # %, but might include more decimal places so we check for substring
    )

    response = await quantitative_agent.ainvoke({"messages": [("user", query)]})

    assert response is not None
    response_content = extract_graph_response_content(response)
    assert expected in response_content


@pytest.mark.asyncio
async def test_file_creation(quantitative_agent: CompiledStateGraph):
    """
    Test the agent creates at least one file in the temp directory.
    """

    query = f"""The company's sales for the last three years are as follows:' 
    
    {california_monthly_sales_in_db}
    
    Perform a detailed analysis of the sales data, including trends, patterns, and insights."""

    response = await quantitative_agent.ainvoke({"messages": [("user", query)]})

    assert response is not None
    response_content = extract_graph_response_content(response)

    temp_dir_files = test_temp_dir.glob("*")
    files_created = [file for file in temp_dir_files if file.is_file()]
    # Assert that there is at least one file created in the temp directory
    assert len(files_created) > 0, "No files were created in the temp directory."
    # Assert that the response contains the names of the files created
    for file in files_created:
        assert file.name in response_content, (
            f"File {file.name} not found in response content."
        )

    # Clean up the temp directory after the test
    for file in files_created:
        file.unlink(missing_ok=True)
