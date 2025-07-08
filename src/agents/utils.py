import base64
from enum import Enum
from pathlib import Path

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


def create_prompt_parts_from_file_list(file_list: list[Path]) -> list[dict]:
    """
    Create a list of parts from a list of file names.

    Args:
        file_list (list[str]): List of file names.

    Returns:
        list[dict]: List of parts with file names.
    """
    prompt_parts = []
    for file in file_list:
        if file.is_file():
            if file.suffix.lower() == ".png":
                prompt_parts.append(
                    {
                        "type": "text",
                        "text": f"Contents of file {file.name}:",
                    }
                )
                prompt_parts.append(
                    {
                        "type": "image",
                        "source_type": "base64",
                        "mime_type": "image/png",  # or image/png, etc.
                        "data": base64.b64encode(file.read_bytes()).decode(
                            "utf-8"
                        ),  # Encode the file content to base64
                    }
                )
            elif file.suffix.lower() == ".csv":
                prompt_parts.append(
                    {
                        "type": "text",
                        "text": f"Contents of file {file.name}: \n\n {file.read_text()}",
                    }
                )
        else:
            prompt_parts.append(
                {
                    "type": "text",
                    "text": f"File {file.name} was not found.",
                }
            )

    return prompt_parts
