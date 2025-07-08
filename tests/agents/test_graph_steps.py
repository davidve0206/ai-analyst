import re
import pytest
import pandas as pd

from langgraph.graph.state import CompiledStateGraph

from src.agents.utils import (
    PrompTypes,
    extract_graph_response_content,
    render_prompt_template,
)
from src.configuration.constants import DATA_PROVIDED
from src.configuration.kpis import SalesReportRequest
from src.configuration.settings import DATA_DIR, app_settings
from .helpers import test_temp_dir


@pytest.mark.asyncio
async def test_sales_retrieval_step(
    spain_sales_history_df: pd.DataFrame,
    default_request: SalesReportRequest,
    quantitative_agent: CompiledStateGraph,
) -> None:
    """Test that replicates the sales retrieval step."""
    expected_file_path = test_temp_dir / "sales_history.csv"

    task_prompt = render_prompt_template(
        template_name="retrieve_sales_step_prompt.md",
        context={
            "date": app_settings.analysis_date,
            "periodicity": default_request.period,
            "grouping": default_request.grouping,
            "grouping_value": default_request.grouping_value,
            "input_location": str(DATA_DIR / DATA_PROVIDED.name),
            "data_description": DATA_PROVIDED.description,
            "output_location": str(expected_file_path),
        },
        type=PrompTypes.HUMAN,
    )

    response = await quantitative_agent.ainvoke({"messages": [task_prompt]})

    assert response is not None
    print(response)
    assert expected_file_path.exists(), (
        f"Expected file {expected_file_path} was not created."
    )

    try:
        # Load the created file and check its content
        # The file should contain the sales history for Spain
        retrieved_sales_df = pd.read_csv(expected_file_path)
        assert not retrieved_sales_df.empty, "Retrieved sales data is empty."

        # Check that the expected data is present somewhere in the retrieved data
        # We don't care about exact column names, just that the values exist

        # Get all expected values we need to find
        expected_sales_amounts = set(spain_sales_history_df["GROSS_AMOUNT"].values)

        # Collect all numeric values from the retrieved data
        retrieved_values = set()
        for col in retrieved_sales_df.columns:
            if retrieved_sales_df[col].dtype in ["int64", "float64"]:
                retrieved_values.update(retrieved_sales_df[col].values)

        # Check that we have enough overlap to be confident the data is there
        # We expect to find at least some percentage of our expected values
        found_values = expected_sales_amounts.intersection(retrieved_values)
        coverage_ratio = len(found_values) / len(expected_sales_amounts)

        assert coverage_ratio >= 0.7, (
            f"Only found {len(found_values)}/{len(expected_sales_amounts)} expected values "
            f"({coverage_ratio:.1%} coverage). Missing values: {expected_sales_amounts - found_values}. "
        )

        # Additional sanity check: ensure we have a reasonable number of rows
        assert len(retrieved_sales_df) >= 30, (
            f"Retrieved data has {len(retrieved_sales_df)} rows, but expected at least 30."
        )
    finally:
        # Clean up the temp file
        if expected_file_path.exists():
            expected_file_path.unlink()


@pytest.mark.asyncio
async def test_sales_analysis_step(
    spain_sales_history_df: pd.DataFrame,
    default_request: SalesReportRequest,
    quantitative_agent: CompiledStateGraph,
) -> None:
    """Test that replicates the sales analysis step."""

    # Store the sales history as a file in the temp directory
    sales_history_file = (
        test_temp_dir
        / f"sales_analysis_{default_request.grouping_value}_sales_history.csv"
    )
    spain_sales_history_df.to_csv(sales_history_file, index=False)

    task_prompt = render_prompt_template(
        template_name="analyse_sales_step_prompt.md",
        context={
            "grouping": default_request.grouping,
            "grouping_value": default_request.grouping_value,
            "input_location": str(sales_history_file),
        },
        type=PrompTypes.HUMAN,
    )

    response = await quantitative_agent.ainvoke({"messages": [task_prompt]})
    assert response is not None

    response_content = extract_graph_response_content(response)
    print(response_content)

    # Use regex to find .png or .csv files mentioned in the response_content
    file_pattern = r"\b[\w\-_]+\.(?:png|csv)\b"
    found_files: list[str] = re.findall(file_pattern, response_content)

    print(f"Found files: {found_files}")
    assert found_files, "No output files were generated in the response."

    # Check that the files mentioned exist in the temp directory
    for file in found_files:
        file_path = test_temp_dir / file
        assert file_path.exists(), f"Expected output file {file} does not exist."
    # TODO: consider adding an LLM as a judge to validate the analysis
    # For now, we just check that the response contains some output files

    # Clean up the temp files
    sales_history_file.unlink(missing_ok=True)
    for file in found_files:
        file_path = test_temp_dir / file
        file_path.unlink(missing_ok=True)
