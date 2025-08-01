import base64
from enum import Enum
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages.content_blocks import (
    BaseDataContentBlock,
    PlainTextContentBlock,
    Base64ContentBlock,
)
from langchain_core.prompts import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
)
from langchain_core.prompt_values import ChatPromptValue
from openai import BaseModel

from src.configuration.settings import SRC_DIR

PROMPTS_PATH = SRC_DIR / "agents" / "prompts"


class MessageTypes(Enum):
    """
    Enum for prompt types.
    """

    SYSTEM = "system"
    HUMAN = "human"
    AI = "ai"


def render_prompt_template(
    template_name: str,
    context: dict[str, str | int | float],
    type: MessageTypes = MessageTypes.SYSTEM,
) -> SystemMessage | HumanMessage | AIMessage:
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

    if type == MessageTypes.SYSTEM:
        template = SystemMessagePromptTemplate.from_template_file(
            template_path,
            input_variables=[],  # input_variables is deprecated but still required for compatibility
        )
    elif type == MessageTypes.HUMAN:
        template = HumanMessagePromptTemplate.from_template_file(
            template_path,
            input_variables=[],  # input_variables is deprecated but still required for compatibility
        )
    elif type == MessageTypes.AI:
        template = AIMessagePromptTemplate.from_template_file(
            template_path,
            input_variables=[],  # input_variables is deprecated but still required for compatibility
        )
    else:
        raise ValueError(f"Unexpected promp type: {type}.")
    return template.format(**context)


def extract_graph_response_content(response: dict) -> str | dict | BaseModel:
    """
    Extract the content of the last message from a list of messages.

    Args:
        messages (list[dict]): List of message dictionaries.

    Returns:
        str: Content of the last message.
    """
    if "structured_response" in response:
        # If the response contains a structured response, return it directly.
        return response["structured_response"]

    messages: list[dict] = response.get("messages", [])
    if not messages:
        return ""

    last_message = messages[-1]
    return last_message.content


def create_content_blocks_from_file_list(
    file_list: list[Path],
) -> list[BaseDataContentBlock]:
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
                    PlainTextContentBlock(
                        type="text", text=f"Contents of file {file.name}:"
                    )
                )
                prompt_parts.append(
                    Base64ContentBlock(
                        type="image",
                        source_type="base64",
                        data=base64.b64encode(file.read_bytes()).decode("utf-8"),
                        mime_type="image/png",
                    )
                )
            elif file.suffix.lower() == ".csv":
                prompt_parts.append(
                    PlainTextContentBlock(
                        type="text",
                        text=f"Contents of file {file.name}: \n\n {file.read_text()}",
                    )
                )
        else:
            prompt_parts.append(
                PlainTextContentBlock(
                    type="text",
                    text=f"File {file.name} was not found.",
                )
            )

    return prompt_parts


def create_human_message_from_parts(
    text_parts: str | list[str] | None = None, file_list: list[Path] | None = None
) -> HumanMessage:
    """
    Create a human message from text parts and files.
    Args:
        text_parts (str | list[str]): The text parts to include in the message.
        file_list (list[Path]): List of files to include in the message."""
    message_blocks = []
    if isinstance(text_parts, str):
        message_blocks.append(PlainTextContentBlock(type="text", text=text_parts))
    elif isinstance(text_parts, list):
        for part in text_parts:
            message_blocks.append(PlainTextContentBlock(type="text", text=part))
    elif text_parts is None:
        pass
    else:
        raise ValueError("text_parts must be a string or a list of strings.")

    if file_list:
        file_blocks = create_content_blocks_from_file_list(file_list)
        message_blocks.extend(file_blocks)

    return HumanMessage(content=message_blocks)


def create_multimodal_prompt(
    text_parts: str | list[str] | None = None,
    file_list: list[Path] | None = None,
    system_message: SystemMessage | None = None,
    human_message: HumanMessage | None = None,
) -> ChatPromptValue:
    """Creates a prompt with (optionally) a system message, and a single
    user message that can contain text and files.

    NOTE: This only works with an OpenAI model (because of LangChain's
    implementation of the multimodal ContentBlock, which uses "image";
    google's, at least, uses "media"). If you want to use a different

    Args:
        text_parts (str | list[str]): The text parts to include in the prompt,
            always added before the file_list.
        file_list (list[Path]): List of files to include in the prompt.
        system_message (SystemMessage | None): Optional system message to include;
            if provided, it will be added first to the messages.
        human_message (HumanMessage | None): Optional human message to include;
            if provided, it will be added after system_message but before the text parts.
    """
    message_from_parts = create_human_message_from_parts(
        text_parts=text_parts, file_list=file_list
    )

    messages = []
    if system_message:
        messages.append(system_message)

    if human_message:
        messages.append(human_message)

    messages.append(message_from_parts)

    return ChatPromptValue(messages=messages)
