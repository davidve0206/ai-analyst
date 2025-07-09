import pytest

from langgraph.graph.state import CompiledStateGraph

from src.agents.utils.prompt_utils import extract_graph_response_content

from .helpers import (
    california_monthly_sales_in_db,
    get_all_files_mentioned_in_response,
    test_temp_dir,
)


@pytest.mark.asyncio
async def test_task_with_intermediate_interpreter(
    quantitative_agent: CompiledStateGraph,
):
    """
    Test the agent with a task that requires basic code generation and execution.
    """
    query = """The company made the following revenue every year: 
    
    2021: 300, 2022: 325, 2023: 350, 2024: 325, 2025: 400.
    
    What is the compounded average growth rate (CAGR)?
    
    Calculate the CAGR but don't create any plots or graphs, just return the value as a string.
    
    Remember you have to print the result to be able to see it."""
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

    files_created = get_all_files_mentioned_in_response(response_content)
    try:
        # Assert that there is at least one file created in the temp directory
        assert len(files_created) > 0, "No files were created in the temp directory."
        # Assert that the file actually exists
        for file_name in files_created:
            file_path = test_temp_dir / file_name
            assert file_path.exists(), f"File {file_name} does not exist at {file_path}"
    finally:
        # Clean up the temp directory after the test
        for file in files_created:
            file_path = test_temp_dir / file
            if file_path.exists():
                file_path.unlink(missing_ok=True)
