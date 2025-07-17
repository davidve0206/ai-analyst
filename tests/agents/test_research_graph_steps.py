from unittest.mock import AsyncMock, patch

import pytest
from langchain_core.messages import BaseMessage

from src.agents.research_graph import (
    ResearchGraphState,
    create_or_update_task_ledger,
    create_or_update_task_plan,
)
from src.agents.utils.prompt_utils import PrompTypes


@pytest.fixture()
def base_research_request() -> ResearchGraphState:
    """
    Base research request fixture for testing.
    """
    return ResearchGraphState(
        task="Analyze the impact of AI on financial markets.",
    )


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
            context={
                "team": "\n- quantitative_analysis_agent: Can load files, run code, and perform quantitative analysis."
            },
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
            context={
                "team": "\n- quantitative_analysis_agent: Can load files, run code, and perform quantitative analysis."
            },
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
