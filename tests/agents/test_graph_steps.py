"""
This module contains high-level tests for the sales research graph steps.

It does not intend to be a comprehensive test or evaluation suite, but
rather to ensure that the graph steps can be executed and produce
reasonable results when provided with the correct data and context.
"""

from pathlib import Path
import pytest
import pandas as pd

from langgraph.graph.state import CompiledStateGraph

from src.configuration.kpis import SalesReportRequest
from .helpers import (
    get_all_files_mentioned_in_response,
    test_temp_dir,
    png_file_name,
    csv_file_name,
    sales_history_code_sample,
    sales_analysis_declining_yoy,
    sales_analysis_declining_trend,
    sales_analysis_no_special_case,
)


@pytest.fixture()
def patch_graph_environment(
    monkeypatch: pytest.MonkeyPatch,
    quantitative_agent: CompiledStateGraph,
) -> None:
    """
    Fixture to patch the environment for the graph tests.
    This is used to ensure that the TEMP_DIR is set correctly.
    """
    # Patch the TEMP_DIR and quant_agent
    monkeypatch.setattr("src.configuration.settings.TEMP_DIR", test_temp_dir)
    monkeypatch.setattr("src.agents.graph.quant_agent", quantitative_agent)

    # Patch the helper that retrieves all temp files
    def patched_get_all_temp_files() -> list[Path]:
        """Patched version that returns fixture filenames for testing."""
        return [
            test_temp_dir / csv_file_name,
            test_temp_dir / png_file_name,
        ]

    monkeypatch.setattr(
        "src.agents.graph.get_all_temp_files",
        patched_get_all_temp_files,
    )


@pytest.fixture()
def patch_graph_environment_with_fixture_csv(
    monkeypatch: pytest.MonkeyPatch,
    patch_graph_environment: None,
) -> None:
    """
    Fixture to patch the environment for the graph tests with a specific CSV fixture.
    This is used to ensure that the sales history retrieval step uses a fixture file.
    It patches the `get_sales_history_location` helper to return a fixture file path
    based on the grouping value, which is used in the sales retrieval step.
    """

    # Patch the helper that returns fixture filenames for testing
    def patched_get_sales_history_location(grouping_value: str) -> Path:
        """Patched version that uses fixture filenames for testing."""
        return test_temp_dir / f"{grouping_value}_sales_history_fixture.csv"

    # Patch just the helper function in the graph module (since it's imported there)
    monkeypatch.setattr(
        "src.agents.graph.get_sales_history_location",
        patched_get_sales_history_location,
    )


@pytest.fixture()
def patch_graph_environment_with_temp_csv(
    monkeypatch: pytest.MonkeyPatch,
    patch_graph_environment: None,
) -> None:
    """
    Fixture to patch the environment for the graph tests with a temporary CSV file.
    This is used to ensure that the sales history retrieval step uses a temporary file
    that can be created during the test.
    """

    # Patch the helper that returns fixture filenames for testing
    def patched_get_sales_history_location(grouping_value: str) -> Path:
        """Patched version that uses a temporary file for testing."""
        return test_temp_dir / f"{grouping_value}_sales_history_temp.csv"

    # Patch just the helper function in the graph module (since it's imported there)
    monkeypatch.setattr(
        "src.agents.graph.get_sales_history_location",
        patched_get_sales_history_location,
    )


@pytest.mark.asyncio
async def test_sales_retrieval_step(
    spain_sales_history_df: pd.DataFrame,
    default_request: SalesReportRequest,
    patch_graph_environment_with_temp_csv: None,
) -> None:
    """Test that replicates the sales retrieval step."""
    from src.agents.graph import retrieve_sales_history, SalesResearchGraphState

    test_state = SalesResearchGraphState(
        request=default_request,
    )
    expected_file_path = (
        test_temp_dir / f"{default_request.grouping_value}_sales_history_temp.csv"
    )

    step_result = await retrieve_sales_history(test_state)
    try:
        assert step_result is not None
        assert "sales_history" in step_result, (
            "Step result does not contain 'sales_history' key."
        )
        assert "sales_history_code" in step_result, (
            "Step result does not contain 'sales_history_code' key."
        )
        assert step_result["sales_history_code"], (
            "Expected sales history code to be non-empty."
        )
        assert expected_file_path.exists(), (
            f"Expected file {expected_file_path} was not created."
        )

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
    default_request: SalesReportRequest,
    patch_graph_environment_with_fixture_csv: None,
) -> None:
    """Test that replicates the sales analysis step."""
    from src.agents.graph import process_sales_data, SalesResearchGraphState

    test_state = SalesResearchGraphState(
        request=default_request,
        sales_history="The data has been retrieved successfully.",
    )

    # Now call the actual process_sales_data function which will use our patched helper
    step_result = await process_sales_data(test_state)

    assert step_result is not None
    assert "sales_analysis" in step_result, (
        "Step result does not contain 'sales_analysis' key."
    )

    response_content = step_result["sales_analysis"]
    print(response_content)  # Debugging output
    found_files = get_all_files_mentioned_in_response(response_content)

    print(f"Found files: {found_files}")
    assert found_files, "No output files were generated in the response."

    try:
        # Check that the files mentioned exist in the temp directory
        for file in found_files:
            file_path = test_temp_dir / file
            assert file_path.exists(), f"Expected output file {file} does not exist."

        # TODO: consider adding an LLM as a judge to validate the analysis
        # For now, we just check that the response contains some output files

    finally:
        # Clean up the temp files
        for file in found_files:
            file_path = test_temp_dir / file
            file_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_operational_data_retrieval_step(
    default_request: SalesReportRequest,
    patch_graph_environment_with_fixture_csv: None,
):
    """Test that replicates the operational data retrieval step."""
    from src.agents.graph import retrieve_operational_data, SalesResearchGraphState

    test_state = SalesResearchGraphState(
        request=default_request,
        sales_history="The data has been retrieved successfully.",
        sales_history_code=sales_history_code_sample,
    )

    step_result = await retrieve_operational_data(test_state)
    assert step_result is not None
    assert "sales_operational_data" in step_result, (
        "Step result does not contain 'sales_operational_data' key."
    )
    data = step_result["sales_operational_data"]

    # TODO: if we improve this step to get a proper analysis of the operational data,
    # we need to evaluate it gets the right data; for now, we just check that
    # the response contains some output files
    found_files = get_all_files_mentioned_in_response(data)
    print(f"Found files: {found_files}")
    assert found_files, "No output files were generated in the response."
    try:
        # Check that the files mentioned exist in the temp directory
        for file in found_files:
            file_path = test_temp_dir / file
            assert file_path.exists(), f"Expected output file {file} does not exist."
    finally:
        for file in found_files:
            file_path = test_temp_dir / file
            file_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_review_special_cases_declining_yoy_sales(
    default_request: SalesReportRequest,
    patch_graph_environment_with_fixture_csv: None,
):
    """Test that replicates the special case review step for declining YoY sales."""
    from src.agents.graph import review_special_cases, SalesResearchGraphState

    test_state = SalesResearchGraphState(
        request=default_request,
        sales_history="The data has been retrieved successfully.",
        sales_analysis=sales_analysis_declining_yoy,
    )

    step_result = await review_special_cases(test_state)
    assert step_result is not None
    assert "is_special_case" in step_result, (
        "Step result does not contain 'is_special_case' key."
    )
    assert step_result["is_special_case"] is True, (
        "Expected the special case to be identified as True."
    )


@pytest.mark.asyncio
async def test_review_special_cases_declining_trend_sales(
    default_request: SalesReportRequest,
    patch_graph_environment_with_fixture_csv: None,
):
    """Test that replicates the special case review step for declining trend sales."""
    from src.agents.graph import review_special_cases, SalesResearchGraphState

    test_state = SalesResearchGraphState(
        request=default_request,
        sales_history="The data has been retrieved successfully.",
        sales_analysis=sales_analysis_declining_trend,
    )

    step_result = await review_special_cases(test_state)
    assert step_result is not None
    assert "is_special_case" in step_result, (
        "Step result does not contain 'is_special_case' key."
    )
    assert step_result["is_special_case"] is True, (
        "Expected the special case to be identified as True."
    )


@pytest.mark.asyncio
async def test_review_special_cases_no_special_case(
    default_request: SalesReportRequest,
    patch_graph_environment_with_fixture_csv: None,
):
    """Test that replicates the special case review step for no special case."""
    from src.agents.graph import review_special_cases, SalesResearchGraphState

    test_state = SalesResearchGraphState(
        request=default_request,
        sales_history="The data has been retrieved successfully.",
        sales_analysis=sales_analysis_no_special_case,
    )

    step_result = await review_special_cases(test_state)
    assert step_result is not None
    assert "is_special_case" in step_result, (
        "Step result does not contain 'is_special_case' key."
    )
    assert step_result["is_special_case"] is False, (
        "Expected the special case to be identified as False."
    )


@pytest.mark.asyncio
async def test_sales_report_generation(
    default_request: SalesReportRequest,
    patch_graph_environment_with_fixture_csv: None,
):
    """Test that replicates the sales report generation step."""

    from src.agents.graph import generate_report, SalesResearchGraphState

    test_state = SalesResearchGraphState(
        request=default_request,
        sales_history="The data has been retrieved successfully.",
        sales_analysis="Sales are decreasing in the last month, by 10% compared to the previous month.",
    )

    step_result = await generate_report(test_state)
    assert step_result is not None
    assert "report" in step_result, "Step result does not contain 'report' key."

    response_content = step_result["report"]
    print(f"Generated report content: {response_content}")
    assert f"({png_file_name})" in response_content, (
        f"Expected output file {png_file_name} not mentioned in the report."
    )
    # TODO: consider adding an LLM as a judge to validate the report
    # For now, we just check that the response contains the image file
