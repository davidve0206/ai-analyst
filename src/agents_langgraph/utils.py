from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.messages import SystemMessage
from src.configuration.settings import SRC_DIR

# TODO: update this path to the correct location if this becomes the main prompt utility file
PROMPTS_PATH = SRC_DIR / "agents_langgraph" / "prompts"


def render_system_prompt_template(
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
    return template.format(**context)


def extract_graph_response_content(response: dict) -> str:
    """
    Extract the content of the last message from a list of messages.

    Args:
        messages (list[dict]): List of message dictionaries.

    Returns:
        str: Content of the last message.
    """
    messages: list[dict] = response.get("messages", [])
    if not messages:
        return ""

    last_message = messages[-1]
    return last_message.content
