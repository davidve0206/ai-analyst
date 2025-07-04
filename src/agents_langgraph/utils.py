from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.messages import SystemMessage
from src.configuration.settings import SRC_DIR

# TODO: update this path to the correct location if this becomes the main prompt utility file
PROMPTS_PATH = SRC_DIR / "agents_langgraph" / "prompts"


async def render_system_prompt_template(
    template_name: str, context: dict[str, str | int | float]
) -> SystemMessage:
    """
    Render a system prompt template from the specified file.

    Args:
        template_name (str): The name of the template file without extension.

    Returns:
        SystemMessagePromptTemplate: The rendered system prompt template.
    """
    template_path = PROMPTS_PATH / template_name

    template = SystemMessagePromptTemplate.from_template_file(
        template_path,
        input_variables=[],  # input_variables is deprecated but still required for compatibility
    )
    return await template.aformat(**context)
