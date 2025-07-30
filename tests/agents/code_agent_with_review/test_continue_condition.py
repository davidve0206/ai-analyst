import pytest

from src.agents.models import AppChatModels
from src.agents.utils.prompt_utils import MessageTypes, render_prompt_template

from . import continue_condition_helpers


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scenario,helper_attr,expected",
    [
        ("agent clearly finalizes", "finalized_text", "RESPOND"),
        ("agent returns introspection", "introspection_text", "RESPOND"),
        ("agent requests user input", "user_request_text", "RESPOND"),
        ("agent implicitly requests user input", "user_request_implicit", "RESPOND"),
        ("agent needs to proceed with task", "proceeding_text", "CONTINUE"),
        ("agent implicitly needs to proceed", "proceeding_implicit", "CONTINUE"),
    ],
)
async def test_continue_condition_scenarios(
    models_client: AppChatModels, scenario: str, helper_attr: str, expected: str
):
    """Test continue condition prompt correctly identifies when agent should continue vs respond."""
    test_message = getattr(continue_condition_helpers, helper_attr)
    assessment_message = render_prompt_template(
        "code_agent/continue_condition_prompt.md",
        context={
            "last_message": test_message,
        },
        type=MessageTypes.HUMAN,
    )
    review_response = await models_client.default_non_reasoning_model.ainvoke(
        [assessment_message]
    )

    actual = review_response.content
    assert actual == expected, f"Failed for scenario: {scenario}"
