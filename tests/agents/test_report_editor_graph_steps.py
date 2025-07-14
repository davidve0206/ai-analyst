"""
This module contains high-level tests for the report editor graph steps.

It does not intend to be a comprehensive test or evaluation suite, but
rather to ensure that the graph steps can be executed and produce
reasonable results when provided with the correct data and context.
"""

import pytest
from pathlib import Path

from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from src.agents.report_editor_graph import (
    ReportEditorGraphState,
    create_report_editor_graph,
)
from src.agents.utils.output_utils import get_all_files_mentioned_in_response
from .helpers import test_temp_dir


# Test data fixtures
report_editor_png_file_name = "test_chart.png"
report_editor_csv_file_name = "test_data.csv"


@pytest.fixture()
def patch_editor_graph_environment(
    monkeypatch: pytest.MonkeyPatch,
    data_visualization_agent: CompiledStateGraph,
) -> None:
    """
    Fixture to patch the environment for the report editor graph tests.
    This ensures that the TEMP_DIR is set correctly and files are created in test directory.
    """
    # Patch the TEMP_DIR where it's actually used - in prompt_utils
    monkeypatch.setattr("src.agents.utils.prompt_utils.TEMP_DIR", test_temp_dir)

    # Patch the data visualization agent getter
    def patched_get_data_visualization_agent(models) -> CompiledStateGraph:
        """Patched version that returns the data visualization agent for testing."""
        return data_visualization_agent

    monkeypatch.setattr(
        "src.agents.report_editor_graph.get_data_visualization_agent",
        patched_get_data_visualization_agent,
    )

    # Patch the helper that gets full path to temp files
    def patched_get_full_path_to_temp_file(file_name: str) -> Path:
        """Patched version that returns test temp directory paths."""
        return test_temp_dir / file_name

    monkeypatch.setattr(
        "src.agents.report_editor_graph.get_full_path_to_temp_file",
        patched_get_full_path_to_temp_file,
    )


@pytest.fixture()
def base_report_request() -> ReportEditorGraphState:
    """
    Base report request fixture for testing.
    """
    return ReportEditorGraphState(
        messages=[
            HumanMessage(
                content="Please generate a report for the sales data; we have already generated Spain_sales_history_fixture.csv which contains the sales history for Spain."
            )
        ],
        report="",
        next_speaker="",
    )


@pytest.mark.asyncio
async def test_report_editor_workflow(
    base_report_request: ReportEditorGraphState,
    patch_editor_graph_environment: None,
) -> None:
    """
    Test the complete report editor workflow.
    Ensures we get a report and that it contains at least one plot.
    """
    # Create the report editor graph
    graph = await create_report_editor_graph()

    # Run the graph
    result = await graph.ainvoke(base_report_request)
    assert "report" in result

    output_report = result["report"]
    assert output_report != ""
    assert len(output_report) > 0

    # Check that the report mentions at least one plot file
    files_mentioned = get_all_files_mentioned_in_response(output_report)
    plot_files = [f for f in files_mentioned if f.endswith((".png"))]
    assert len(plot_files) > 0, (
        f"Expected at least one plot file in report, but found: {files_mentioned}"
    )

    try:
        # Check that the files mentioned exist in the temp directory
        for file in files_mentioned:
            file_path = test_temp_dir / file
            assert file_path.exists(), f"Expected output file {file} does not exist."

    finally:
        # Clean up the temp files
        for file in files_mentioned:
            file_path = test_temp_dir / file
            file_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_loop_avoidance_logic(
    base_report_request: ReportEditorGraphState,
    patch_editor_graph_environment: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Test that the loop avoidance logic prevents infinite loops.
    This test forces the LLM to always choose the same agent and verifies
    that the real supervisor logic terminates the graph after max_loops iterations.
    """
    from unittest.mock import AsyncMock

    # Set max_loops to 2 for faster testing
    base_report_request.max_loops = 2

    # Track how many times document_writing_agent is called
    document_agent_call_count = 0

    # Mock the document_writing_agent to count calls and return quickly
    async def mock_document_writing_agent(state):
        nonlocal document_agent_call_count
        document_agent_call_count += 1

        from langgraph.types import Command

        return Command(
            update={
                "report": f"Document iteration {document_agent_call_count}",
            },
            goto="supervisor",
        )

    monkeypatch.setattr(
        "src.agents.report_editor_graph.document_writing_agent",
        mock_document_writing_agent,
    )

    # Mock the LLM to always return the same agent choice to force a loop
    class MockRouter:
        def __init__(self):
            self.next_speaker = "document_writing_agent"
            self.next_speaker_task = "Keep writing the document"

    # Create a proper mock for the LLM chain
    from unittest.mock import MagicMock

    mock_structured_output = AsyncMock()
    mock_structured_output.ainvoke = AsyncMock(return_value=MockRouter())

    mock_model = MagicMock()
    mock_model.with_structured_output.return_value = mock_structured_output

    # Patch the specific model attribute in models_client
    monkeypatch.setattr(
        "src.agents.report_editor_graph.models_client.gpt_o4_mini", mock_model
    )

    # Create the report editor graph
    graph = await create_report_editor_graph()

    # Run the graph
    result = await graph.ainvoke(base_report_request)

    # Verify that the loop was terminated by the supervisor logic
    assert "report" in result

    # The document agent should be called exactly max_loops times:
    # - First call (loop_count = 0, next_speaker = "")
    # - Second call (loop_count = 1, same speaker chosen again)
    # - Third supervisor call detects loop_count would be >= max_loops and terminates
    expected_calls = base_report_request.max_loops
    assert document_agent_call_count == expected_calls, (
        f"Expected document_writing_agent to be called {expected_calls} times, "
        f"but it was called {document_agent_call_count} times"
    )

    # Verify the final state shows the loop was detected
    assert result["loop_count"] >= base_report_request.max_loops

    # Verify the LLM was called the expected number of times
    # Should be called once per supervisor invocation
    # The supervisor is called: initial + per loop iteration + final termination check
    assert (
        mock_structured_output.ainvoke.call_count >= base_report_request.max_loops + 1
    ), (
        f"Expected at least {base_report_request.max_loops + 1} LLM calls, "
        f"but got {mock_structured_output.ainvoke.call_count}"
    )
