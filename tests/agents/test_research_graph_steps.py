import pytest
from unittest.mock import AsyncMock, patch, ANY

from langchain_core.messages import BaseMessage, HumanMessage

from src.agents.quant_agent import QuantitativeAgentResponse
from src.agents.research_graph import (
    ProgressLedger,
    ResearchGraphState,
    create_or_update_task_ledger,
    create_or_update_task_plan,
    progress_ledger_gate,
    quantitative_analysis_agent,
    update_progress_ledger,
)
from src.agents.utils.prompt_utils import PrompTypes


@pytest.fixture()
def base_research_request() -> ResearchGraphState:
    """
    Base research request fixture for testing.
    """
    return ResearchGraphState(
        task_id="test_task_id",
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
            type=PrompTypes.HUMAN,
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
            type=PrompTypes.HUMAN,
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
            type=PrompTypes.HUMAN,
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
            type=PrompTypes.HUMAN,
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
async def test_progress_ledger_gate_summarize_findings(
    base_research_request: ResearchGraphState,
):
    """
    Test that the gate returns 'summarize_findings' when the request is satisfied.
    """
    base_research_request.progress_ledger.is_request_satisfied.answer = True
    result = await progress_ledger_gate(base_research_request)
    assert result == "summarize_findings"


@pytest.mark.asyncio
async def test_progress_ledger_gate_create_or_update_task_ledger(
    base_research_request: ResearchGraphState,
):
    """
    Test that the gate returns 'create_or_update_task_ledger' when stall count exceeds limit and no progress is being made.
    """
    base_research_request.stall_count = base_research_request.stall_count_limit + 1
    base_research_request.progress_ledger.is_progress_being_made.answer = False
    result = await progress_ledger_gate(base_research_request)
    assert result == "create_or_update_task_ledger"


@pytest.mark.asyncio
async def test_progress_ledger_gate_handover_to_team_member(
    base_research_request: ResearchGraphState,
):
    """
    Test that the gate returns 'handover_to_team_member' when neither of the other conditions are met.

    The test assumes that the model will only return a valid next_speaker.
    """
    base_research_request.stall_count = 0
    base_research_request.progress_ledger.is_progress_being_made.answer = True
    base_research_request.progress_ledger.next_speaker.answer = (
        "handover_to_team_member"
    )
    result = await progress_ledger_gate(base_research_request)
    assert result == "handover_to_team_member"


@pytest.mark.asyncio
async def test_progress_ledger_gate_progress_made_despite_stall(
    base_research_request: ResearchGraphState,
):
    """
    Test that the gate returns 'handover_to_team_member' when stall count exceeds limit but progress is being made.
    """
    base_research_request.stall_count = base_research_request.stall_count_limit + 1
    base_research_request.progress_ledger.is_progress_being_made.answer = True
    base_research_request.progress_ledger.next_speaker.answer = (
        "handover_to_team_member"
    )
    result = await progress_ledger_gate(base_research_request)
    assert result == "handover_to_team_member"


@pytest.mark.asyncio
async def test_quantitative_agent_calls_with_different_messages(monkeypatch):
    """
    Test that the quantitative_analysis_agent calls the quantitative agent
    with "messages" that are different from state.messages.
    """
    # Mock the quantitative agent
    mock_agent = AsyncMock()
    mock_agent.ainvoke.return_value = {
        "structured_response": QuantitativeAgentResponse(
            content="Mocked response content",
            code="Mocked code",
        )
    }
    monkeypatch.setattr(
        "src.agents.research_graph.get_quantitative_agent", lambda _: mock_agent
    )

    # Create a mock state
    state = ResearchGraphState(
        task_id="test_task",
        task="Analyze sales data",
        messages=[HumanMessage("message1"), HumanMessage("message2")],
    )
    state.progress_ledger.instruction_or_question.answer = "What is the sales trend?"

    # Call the function
    await quantitative_analysis_agent(state)

    # Assert that the agent was called with different messages
    mock_agent.ainvoke.assert_called_once()
    called_args = mock_agent.ainvoke.call_args[0][0]
    assert called_args["messages"] != state.messages, (
        "Expected messages to differ from state.messages."
    )


@pytest.mark.asyncio
async def test_quantitative_analysis_agent():
    """
    Test that the values returned by the function as "quant_agent_context"
    and "messages" are different.
    """

    # Create a mock state
    state = ResearchGraphState(
        task_id="test_task",
        task="Analyze sales data",
        messages=[HumanMessage("message1"), HumanMessage("message2")],
    )
    state.progress_ledger.instruction_or_question.answer = (
        "The company has made sales for 100, 120, 110 and 140. What is the sales trend?"
    )

    # Call the function
    result = await quantitative_analysis_agent(state)

    # Assert that the returned values are different
    assert result["quant_agent_context"] != result["messages"], (
        "Expected quant_agent_context and messages to differ."
    )
    assert (
        result["quant_agent_context"][-1].content != result["messages"][-1].content
    ), (
        "Expected the last message in quant_agent_context to differ from the last message in messages."
    )
