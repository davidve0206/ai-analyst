from src.configuration.settings import BASE_DIR


def test_render_system_prompt_template(monkeypatch):
    # Patch SRC_DIR to be the tests directory
    monkeypatch.setattr("src.configuration.settings.SRC_DIR", BASE_DIR / "tests")

    # Import after patching
    from src.agents_langgraph.utils import render_system_prompt_template

    context = {"language": "spanish"}
    template_name = "test_system_prompt.md"

    rendered_template = render_system_prompt_template(template_name, context)
    assert rendered_template is not None
    assert (
        rendered_template.content
        == "You are a translator and your role is to translate the text sent by the user to spanish"
    )
