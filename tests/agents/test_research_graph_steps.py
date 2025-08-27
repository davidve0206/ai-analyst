import pytest
from unittest.mock import AsyncMock, patch, ANY

from langchain_core.messages import BaseMessage, HumanMessage

from src.agents.research_graph import (
    ProgressLedger,
    ResearchGraphState,
    create_or_update_task_ledger,
    create_or_update_task_plan,
    evaluate_progress_ledger,
    update_progress_ledger,
    summarize_findings,
    create_research_graph,
    GraphNodeNames,
)
from src.agents.utils.prompt_utils import MessageTypes
from src.configuration.db_models import SalesReportRequest
from tests.agents.helpers import test_temp_dir


@pytest.fixture(scope="session")
def ai_sales_request() -> SalesReportRequest:
    """
    Fixture to create a sales report request for testing.
    """
    return SalesReportRequest(
        id=1,
        grouping="Product Family",
        grouping_value="AI",
        period="Yearly",
        recipients=[],
    )


@pytest.fixture()
def base_research_request(ai_sales_request: SalesReportRequest) -> ResearchGraphState:
    """
    Base research request fixture for testing.
    """
    return ResearchGraphState(
        task_id="test_task_id",
        request=ai_sales_request,
        task="Analyze the impact of AI on financial markets.",
    )


test_plan = """
•	Gather Background Information
    •	Summarize key ways AI is currently used in financial markets (e.g., algorithmic trading, risk modeling, fraud detection)
    •	Identify notable AI-driven developments or trends
•	Call quantitative_analysis_agent
    •	Task: Analyze historical market data to identify correlations or trends that may be linked to increased AI adoption
    •	Suggested metrics: volatility, liquidity, trading frequency, market efficiency
    •	Suggested datasets: major stock indices, algorithmic trading volume, AI adoption rates by financial firms
•	Interpret Results
    •	Review and summarize the agent’s findings
    •	Highlight any statistically significant trends or anomalies
•	Draw Conclusions
    •	Discuss implications of AI’s impact based on evidence
    •	Address limitations or assumptions in the analysis
•	Prepare Final Output
    •	Format findings into a clear, structured report or presentation
"""


@pytest.mark.asyncio
async def test_create_or_update_task_ledger_correct_prompt_selection(
    base_research_request: ResearchGraphState,
):
    """
    Test that the correct prompt is selected based on the current state.
    """
    with (
        patch(
            "src.agents.research_graph.render_prompt_template",
        ) as mock_render,
        patch("src.agents.research_graph.models_client") as mock_models,
    ):
        mock_render.return_value = "Mocked prompt content"
        mock_models.default_model.ainvoke = AsyncMock(
            return_value=BaseMessage(content="Mocked LLM response", type="mock")
        )

        result = await create_or_update_task_ledger(base_research_request)

        mock_render.assert_called_once_with(
            template_name="magentic_one/task_ledger_facts_prompt.md",
            context={"task": base_research_request.task},
            type=MessageTypes.HUMAN,
        )
        mock_models.default_model.ainvoke.assert_called_once()
        assert result is not None


@pytest.mark.asyncio
async def test_create_or_update_task_ledger_correct_prompt_selection_for_update(
    base_research_request: ResearchGraphState,
):
    """
    Test that the correct prompt is selected when the task is an update.
    """
    base_research_request.task_facts = (
        "GIVEN OR VERIFIED FACTS: Existing facts.\n"
        "FACTS TO LOOK UP: Facts to look up.\n"
        "FACTS TO DERIVE: Facts to derive.\n"
        "EDUCATED GUESSES: Educated guesses."
    )

    with (
        patch(
            "src.agents.research_graph.render_prompt_template",
        ) as mock_render,
        patch("src.agents.research_graph.models_client") as mock_models,
    ):
        mock_render.return_value = "Mocked update prompt content"
        mock_models.default_model.ainvoke = AsyncMock(
            return_value=BaseMessage(content="Mocked LLM response", type="mock")
        )

        result = await create_or_update_task_ledger(base_research_request)

        mock_render.assert_called_once_with(
            template_name="magentic_one/task_ledger_facts_update_prompt.md",
            context={
                "task": base_research_request.task,
                "old_facts": base_research_request.task_facts,
            },
            type=MessageTypes.HUMAN,
        )
        mock_models.default_model.ainvoke.assert_called_once()
        assert result is not None


@pytest.mark.asyncio
async def test_create_or_update_task_ledger_result_contains_required_headers(
    base_research_request: ResearchGraphState,
):
    """
    Test that the result contains the required headers from the actual LLM response.
    """
    updated_state = await create_or_update_task_ledger(base_research_request)
    result = updated_state.get("task_facts", "")

    assert "GIVEN OR VERIFIED FACTS" in result
    assert "FACTS TO LOOK UP" in result
    assert "FACTS TO DERIVE" in result
    assert "EDUCATED GUESSES" in result


@pytest.mark.asyncio
async def test_create_or_update_task_plan_correct_prompt_selection(
    base_research_request: ResearchGraphState,
):
    """
    Test that the correct prompt is selected based on the current state.
    """
    with (
        patch(
            "src.agents.research_graph.render_prompt_template",
        ) as mock_render,
        patch("src.agents.research_graph.models_client") as mock_models,
    ):
        mock_render.return_value = "Mocked prompt content"
        mock_models.default_model.ainvoke = AsyncMock(
            return_value=BaseMessage(content="Mocked LLM response", type="mock")
        )

        result = await create_or_update_task_plan(base_research_request)

        mock_render.assert_called_once_with(
            template_name="magentic_one/task_ledger_plan_prompt.md",
            context={"team": ANY},
            type=MessageTypes.HUMAN,
        )
        mock_models.default_model.ainvoke.assert_called_once()
        assert result is not None


@pytest.mark.asyncio
async def test_create_or_update_task_plan_correct_prompt_selection_for_update(
    base_research_request: ResearchGraphState,
):
    """
    Test that the correct prompt is selected when the task plan is an update.
    """
    base_research_request.task_plan = "Existing task plan."

    with (
        patch(
            "src.agents.research_graph.render_prompt_template",
        ) as mock_render,
        patch("src.agents.research_graph.models_client") as mock_models,
    ):
        mock_render.return_value = "Mocked update prompt content"
        mock_models.default_model.ainvoke = AsyncMock(
            return_value=BaseMessage(content="Mocked LLM response", type="mock")
        )

        result = await create_or_update_task_plan(base_research_request)

        mock_render.assert_called_once_with(
            template_name="magentic_one/task_ledger_plan_update_prompt.md",
            context={"team": ANY},
            type=MessageTypes.HUMAN,
        )
        mock_models.default_model.ainvoke.assert_called_once()
        assert result is not None


@pytest.mark.asyncio
async def test_create_or_update_task_plan_result_is_not_empty(
    base_research_request: ResearchGraphState,
):
    """
    Test that the result contains a non-empty task plan from the actual LLM response.
    """
    # TODO: This tests only checks that we get a response
    #       Consider alternatives such as LLM as a judge
    result = await create_or_update_task_plan(base_research_request)
    assert result.get("task_plan", "") != ""


@pytest.mark.asyncio
async def test_update_progress_ledger(
    base_research_request: ResearchGraphState,
):
    """
    Test that the return type is ProgressLedger and validate all fields.

    TODO: Consider creating a set of scenarios to test the progress ledger
    based on different states of the ResearchGraphState. Particularly,
    we should test that it only returns valid team members as next_speaker.
    """
    base_research_request.task_plan = test_plan
    result = await update_progress_ledger(base_research_request)

    progress_ledger = result["progress_ledger"]

    # Check is_request_satisfied
    assert isinstance(progress_ledger, ProgressLedger)
    assert progress_ledger.is_request_satisfied.reason != ""
    assert progress_ledger.is_request_satisfied.answer is False

    # Check is_in_loop
    assert progress_ledger.is_in_loop.reason != ""
    assert progress_ledger.is_in_loop.answer is False

    # Check is_progress_being_made
    assert progress_ledger.is_progress_being_made.reason != ""
    # At this point, the value of is_progress_being_made is irrelevant

    # Check next_speaker
    assert progress_ledger.next_speaker.reason != ""
    assert progress_ledger.next_speaker.answer != ""

    # Check instruction_or_question
    assert progress_ledger.instruction_or_question.reason != ""
    assert progress_ledger.instruction_or_question.answer != ""


@pytest.mark.asyncio
async def test_evaluate_progress_ledger_summarize_findings(
    base_research_request: ResearchGraphState,
):
    """
    Test that the gate returns 'summarize_findings' when the request is satisfied.
    """
    base_research_request.progress_ledger.is_request_satisfied.answer = True
    result = await evaluate_progress_ledger(base_research_request)

    assert result.goto == GraphNodeNames.SUMMARIZE_FINDINGS.value
    assert result.update["stall_count"] == base_research_request.stall_count
    assert result.update["reset_count"] == base_research_request.reset_count


@pytest.mark.asyncio
async def test_evaluate_progress_ledger_create_or_update_task_ledger(
    base_research_request: ResearchGraphState,
):
    """
    Test that the gate returns 'create_or_update_task_ledger' when stall count exceeds limit and no progress is being made.
    """
    base_research_request.stall_count = base_research_request.stall_count_limit - 1
    base_research_request.reset_count = 0
    base_research_request.progress_ledger.is_in_loop.answer = True
    base_research_request.progress_ledger.is_progress_being_made.answer = False
    result = await evaluate_progress_ledger(base_research_request)

    assert result.goto == GraphNodeNames.CREATE_OR_UPDATE_TASK_LEDGER.value
    assert result.update["stall_count"] == base_research_request.stall_count_limit, (
        "Stall count should be increased by 1"
    )
    assert result.update["reset_count"] == 1, "Reset count should be increased by 1"


@pytest.mark.asyncio
async def test_evaluate_progress_ledger_handover_to_team_member(
    base_research_request: ResearchGraphState,
):
    """
    Test that the gate returns 'handover_to_team_member' when neither of the other conditions are met.

    The test assumes that the model will only return a valid next_speaker.
    """
    base_research_request.stall_count = 0
    base_research_request.progress_ledger.is_progress_being_made.answer = True
    base_research_request.progress_ledger.next_speaker.answer = (
        GraphNodeNames.QUANTITATIVE_ANALYSIS_AGENT.value
    )
    result = await evaluate_progress_ledger(base_research_request)

    assert result.goto == GraphNodeNames.QUANTITATIVE_ANALYSIS_AGENT.value
    assert result.update["stall_count"] == base_research_request.stall_count
    assert result.update["reset_count"] == base_research_request.reset_count


@pytest.mark.asyncio
async def test_evaluate_progress_ledger_progress_made_despite_stall(
    base_research_request: ResearchGraphState,
):
    """
    Test that the gate returns 'handover_to_team_member' when stall count exceeds limit but progress is being made.
    """
    base_research_request.stall_count = base_research_request.stall_count_limit
    base_research_request.progress_ledger.is_in_loop.answer = True
    base_research_request.progress_ledger.is_progress_being_made.answer = True
    base_research_request.progress_ledger.next_speaker.answer = (
        GraphNodeNames.QUANTITATIVE_ANALYSIS_AGENT.value
    )
    result = await evaluate_progress_ledger(base_research_request)

    assert result.goto == GraphNodeNames.QUANTITATIVE_ANALYSIS_AGENT.value
    assert (
        result.update["stall_count"] == base_research_request.stall_count_limit + 1
    ), "The stall count should be increased by 1"
    assert result.update["reset_count"] == base_research_request.reset_count


@pytest.mark.asyncio
async def test_summarize_findings_with_csv_context(
    ai_sales_request: SalesReportRequest,
):
    """
    Test that the summarize_findings function correctly processes a context
    containing a message with a CSV file and mentions the file and the 10% figure.
    """
    # Create a mock state
    state = ResearchGraphState(
        task_id="test_task",
        task="Analyze the impact of AI on financial markets.",
        request=ai_sales_request,
        messages=[
            HumanMessage(
                "The file 'market_analysis.csv' contains market data showing that AI increased the market value by 10%."
            )
        ],
    )

    # Call the function
    result = await summarize_findings(state)

    # Assert that the task_output is not empty
    assert result["task_output"] != "", "Expected task_output to be non-empty."

    # Assert that the task_output mentions the file
    assert "market_analysis.csv" in result["task_output"], (
        "Expected task_output to mention the file."
    )

    # Assert that the task_output mentions the 10% figure
    assert "10%" in result["task_output"], (
        "Expected task_output to mention the 10% figure."
    )


@pytest.mark.asyncio
async def test_summarize_findings_with_extended_context(
    ai_sales_request: SalesReportRequest,
):
    """
    Test that the summarize_findings function correctly processes a context
    containing multiple messages, including a CSV file, a facts request, and a plan.
    """
    # Create a mock state
    state = ResearchGraphState(
        task_id="test_task",
        task="Analyze the impact of AI on financial markets.",
        request=ai_sales_request,
        messages=[
            HumanMessage(
                "GIVEN OR VERIFIED FACTS:\n- AI adoption rates have increased by 20% in the last 5 years.\nFACTS TO LOOK UP:\n- Historical market data for AI-driven companies.\nFACTS TO DERIVE:\n- Correlation between AI adoption and market value growth."
            ),
            HumanMessage(
                "PLAN:\n- Gather historical market data.\n- Analyze correlations between AI adoption and market trends.\n- Summarize findings in a structured report."
            ),
            HumanMessage(
                "The file 'market_analysis.csv' contains marked data showing that AI increased the market value by 10%."
            ),
        ],
    )

    # Call the function
    result = await summarize_findings(state)

    # Assert that the task_output is not empty
    assert result["task_output"] != "", "Expected task_output to be non-empty."

    # Assert that the task_output mentions the file
    assert "market_analysis.csv" in result["task_output"], (
        "Expected task_output to mention the file."
    )

    # Assert that the task_output mentions the 10% figure
    assert "10%" in result["task_output"], (
        "Expected task_output to mention the 10% figure."
    )

    # Assert that the task_output mentions facts
    assert "20%" in result["task_output"], "Expected task_output to mention the facts."


@pytest.mark.asyncio
async def test_run_research_graph(
    monkeypatch, ai_sales_request, patched_get_request_temp_dir
):
    """
    Test that runs the entire research graph.
    """
    monkeypatch.setattr(
        "src.agents.internal_data_agent.get_request_temp_dir",
        patched_get_request_temp_dir,
    )
    monkeypatch.setattr(
        "src.agents.quant_agent.get_request_temp_dir",
        patched_get_request_temp_dir,
    )

    # Create a research graph
    workflow = await create_research_graph()

    # Define the task with detailed context
    task_context = (
        "Analyze the impact of AI on financial markets."
        "\nAI has revolutionized algorithmic trading, risk modeling, and fraud detection. "
        "Recent trends show increased adoption of AI-driven strategies by major financial firms, "
        "leading to notable changes in market volatility and liquidity. "
        "\nThe value of the market were: 2015: 62.27T USD; 2016: 65.12T USD; 2017: 79.50T USD; 2018: 68.89T USD; 2019: 78.83T USD; 2020: 93.69T USD; 2021: 111.16T USD; 2022: 93.69T USD; 2023: 115.0T USD; 2024: 128.21T USD; 2025 (as of June): 134T USD"
        "\nHistorical data indicates correlations between AI adoption rates and trading frequency."
        "\nYour team does not have access to the internet or any other data, so you will need to use the provided data and your knowledge to analyze the impact of AI on financial markets. Do not make use of the internal data agent, as it is not available in this task."
    )

    state = ResearchGraphState(
        task_id="test_task_id",
        task=task_context,
        request=ai_sales_request,
    )

    # Run the graph with a high recursion limit to avoid recursion errors
    result = await workflow.ainvoke(state, {"recursion_limit": 150})

    # Assert the task_output is not empty
    assert "task_output" in result
    output = result["task_output"]

    assert output != ""
    from src.agents.utils.output_utils import get_all_files_mentioned_in_response

    files_mentioned = get_all_files_mentioned_in_response(output)
    try:
        assert "AI" in output, "Expected output to mention AI."
        assert ("financial markets" in output) or ("Financial Markets" in output), (
            "Expected output to mention financial markets."
        )
        assert "134" in output, "Expected output to mention the latest market value."
    finally:
        # Clean up the temp files
        for file in files_mentioned:
            file_path = test_temp_dir / file
            if file_path.exists() and "fixture" not in file:
                file_path.unlink(missing_ok=True)
