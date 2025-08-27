import pytest

from langgraph.graph.state import CompiledStateGraph

from .helpers import (
    test_temp_dir,
    csv_file_name,
)


@pytest.mark.asyncio
async def test_file_creation(data_visualization_agent: CompiledStateGraph):
    """
    Test the agent creates at least one file in the temp directory.
    """
    from src.agents.utils.prompt_utils import extract_graph_response_content
    from src.agents.utils.output_utils import get_all_files_mentioned_in_response

    query = f"""The company's sale history is provided in the CSV file: {csv_file_name}.
    Create a plot that shows the sales trends over the last three years, including a trend line."""

    response = await data_visualization_agent.ainvoke({"messages": [("user", query)]})

    assert response is not None
    response = extract_graph_response_content(response)

    files_mentioned = get_all_files_mentioned_in_response(response)
    try:
        # Assert that there is at least one file created in the temp directory
        assert len(files_mentioned) > 0, "No files were created in the temp directory."
        # Assert all files are csv files
        assert all(file.endswith(".png") for file in files_mentioned), (
            "Not all created files are CSV files."
        )
        # Assert that the file actually exists
        for file_name in files_mentioned:
            file_path = test_temp_dir / file_name
            assert file_path.exists(), f"File {file_name} does not exist at {file_path}"
    finally:
        # Clean up the temp directory after the test
        for file in files_mentioned:
            file_path = test_temp_dir / file
            if file_path.exists() and "fixture" not in file:
                file_path.unlink(missing_ok=True)
