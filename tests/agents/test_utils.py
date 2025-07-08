from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.utils import PrompTypes
from src.configuration.settings import BASE_DIR


def test_render_system_prompt_template(monkeypatch):
    # Patch PROMPTS_PATH to point to the test prompts directory
    test_prompts_path = BASE_DIR / "tests" / "agents" / "prompts"
    monkeypatch.setattr("src.agents.utils.PROMPTS_PATH", test_prompts_path)

    # Import after patching
    from src.agents.utils import render_prompt_template

    context = {"language": "spanish"}
    template_name = "test_render_prompt.md"

    rendered_template = render_prompt_template(
        template_name, context, type=PrompTypes.SYSTEM
    )
    assert rendered_template is not None
    assert type(rendered_template) is SystemMessage
    assert (
        rendered_template.content
        == "You are a translator and your role is to translate the text sent by the user to spanish"
    )


def test_render_human_prompt_template(monkeypatch):
    # Patch PROMPTS_PATH to point to the test prompts directory
    test_prompts_path = BASE_DIR / "tests" / "agents" / "prompts"
    monkeypatch.setattr("src.agents.utils.PROMPTS_PATH", test_prompts_path)

    # Import after patching
    from src.agents.utils import render_prompt_template

    context = {"language": "spanish"}
    template_name = "test_render_prompt.md"

    rendered_template = render_prompt_template(
        template_name, context, type=PrompTypes.HUMAN
    )
    assert rendered_template is not None
    assert type(rendered_template) is HumanMessage
    assert (
        rendered_template.content
        == "You are a translator and your role is to translate the text sent by the user to spanish"
    )
