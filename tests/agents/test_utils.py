from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.utils import PrompTypes
from src.configuration.settings import BASE_DIR
from .helpers import test_temp_dir


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


def test_create_prompt_parts_from_file_list():
    # Import just for this test to avoid overriding monkeypatches on other tests
    from src.agents.utils import create_prompt_parts_from_file_list

    csv_file_name = "sales_analysis_Spain_sales_fixture.csv"
    png_file_name = "sales_projection_spain_fixture.png"
    file_list = [
        test_temp_dir / csv_file_name,
        test_temp_dir / png_file_name,
    ]
    parts = create_prompt_parts_from_file_list(file_list)

    assert len(parts) == 3
    assert parts[0]["type"] == "text"
    assert csv_file_name in parts[0]["text"]
    assert parts[1]["type"] == "text"
    assert png_file_name in parts[1]["text"]
    assert parts[2]["type"] == "image"
    assert parts[2]["source_type"] == "base64"
    assert parts[2]["mime_type"] == "image/png"
    assert parts[2]["data"]  # make sure data is not empty
