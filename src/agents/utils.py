from enum import Enum

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from src.configuration.settings import SRC_DIR

PROMPTS_PATH = SRC_DIR / "agents" / "prompts"


class PrompTypes(Enum):
    """
    Enum for prompt types.
    """

    SYSTEM = "system"
    HUMAN = "human"


def render_prompt_template(
    template_name: str,
    context: dict[str, str | int | float],
    type: PrompTypes = PrompTypes.SYSTEM,
) -> SystemMessage | HumanMessage:
    """
    Render a system prompt template from the specified file.

    Args:
        template_name (str): The name of the template file without extension.

    Returns:
        SystemMessagePromptTemplate: The rendered system prompt template.
    """
    template_path = PROMPTS_PATH / template_name

    if not template_path.exists():
        raise FileNotFoundError(f"Template file {template_path} does not exist.")
    if not template_path.is_file():
        raise ValueError(f"Template path {template_path} is not a file.")

    if type == PrompTypes.SYSTEM:
        template = SystemMessagePromptTemplate.from_template_file(
            template_path,
            input_variables=[],  # input_variables is deprecated but still required for compatibility
        )
    elif type == PrompTypes.HUMAN:
        template = HumanMessagePromptTemplate.from_template_file(
            template_path,
            input_variables=[],  # input_variables is deprecated but still required for compatibility
        )
    else:
        raise ValueError(f"Unexpected promp type: {type}.")
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
