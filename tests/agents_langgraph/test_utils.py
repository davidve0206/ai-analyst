import pytest

from src.agents_langgraph.utils import render_system_prompt_template
from src.configuration.settings import BASE_DIR


@pytest.mark.asyncio
async def test_render_system_prompt_template(monkeypatch):
    # Override SRC_DIR for testing
    monkeypatch.setattr("src.agents_langgraph.utils.SRC_DIR", BASE_DIR / "tests")

    context = {"language": "spanish"}
    template_name = "test_system_prompt.md"

    rendered_template = await render_system_prompt_template(template_name, context)
    assert rendered_template is not None
    assert (
        rendered_template.content
        == "You are a translator and your role is to translate the text sent by the user to spanish"
    )
