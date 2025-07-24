import pytest

from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import HumanMessage

from src.agents.code_agent_with_review import PreConfiguredCodeAgent
from src.agents.utils.output_utils import get_all_files_mentioned_in_response
from src.agents.utils.prompt_utils import extract_graph_response_content

from .helpers import (
    california_monthly_sales_in_db,
    test_temp_dir,
)


@pytest.mark.asyncio
async def test_task_with_intermediate_interpreter(
    quantitative_agent: PreConfiguredCodeAgent,
):
    """
    Test the agent with a task that requires basic code generation and execution.
    """
    query = """The company made the following revenue every year: 
    
    2021: 300, 2022: 325, 2023: 350, 2024: 325, 2025: 400.
    
    What is the compounded average growth rate (CAGR)?
    
    Calculate the CAGR but don't create any plots or graphs, just return the value as a string with two decimals.
    
    Remember you have to print the result to be able to see it."""
    expected = (
        "7.46"  # %, but might include more decimal places so we check for substring
    )

    response = await quantitative_agent.ainvoke(messages=[HumanMessage(content=query)])

    assert response is not None
    quant_agent_response = extract_graph_response_content(response)

    assert expected in quant_agent_response


@pytest.mark.asyncio
async def test_file_creation(quantitative_agent: PreConfiguredCodeAgent):
    """
    Test the agent creates at least one file in the temp directory.
    """

    query = f"""The company's sales for the last three years are as follows:' 
    
    {california_monthly_sales_in_db}
    
    Perform a detailed analysis of the sales data, including trends, patterns, and insights."""

    response = await quantitative_agent.ainvoke(messages=[HumanMessage(content=query)])
    response_content = extract_graph_response_content(response)

    files_created = get_all_files_mentioned_in_response(response_content)
    try:
        # Assert that there is at least one file created in the temp directory
        assert len(files_created) > 0, "No files were created in the temp directory."
        # Assert all files are csv files
        assert all(file.endswith(".csv") for file in files_created), (
            "Not all created files are CSV files."
        )
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
