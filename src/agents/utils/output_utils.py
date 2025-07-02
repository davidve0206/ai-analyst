import re
from datetime import datetime
from pathlib import Path
from markdown_pdf import MarkdownPdf, Section
from semantic_kernel.agents import Agent
from semantic_kernel.contents import FunctionCallContent, FunctionResultContent
from semantic_kernel.contents.chat_message_content import ChatMessageContent

from src.configuration.settings import STORAGE_DIR, TEMP_DIR


async def invoke_agent_displaying_intermediate_steps(
    agent: Agent, messages: str | ChatMessageContent | list[str | ChatMessageContent]
):
    """
    Invoke the agent with the given messages and handle intermediate
    messages if provided.
    """
    async for response in agent.invoke(
        messages=messages,
        on_intermediate_message=handle_intermediate_steps,
    ):
        print(f"# {response.role}: {response}")


async def handle_intermediate_steps(message: ChatMessageContent) -> None:
    for item in message.items or []:
        if isinstance(item, FunctionCallContent):
            print(f"Function Call:> {item.name} with arguments: {item.arguments}")
        elif isinstance(item, FunctionResultContent):
            print(f"Function Result:> {item.result} for function: {item.name}")
        else:
            print(f"{message.role} - {message.name}: {message.content}")


async def invoke_agent_in_chat_mode(agent: Agent):
    """
    Invoke the agent in a chat mode, allowing for user input and displaying the response.
    This function simulates a chat interaction with the agent, where the user can input messages
    and receive responses from the agent, the application remains in a loop until the user decides to exit.

    Note that this does not include memory management, its just a simple
    chat interface to make it easier to test the agent's functionality.
    """
    while True:
        print("Type 'exit' to quit the chat.")
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        invoke_agent_displaying_intermediate_steps(agent, user_input)


def store_response_with_timestamp(
    response: str, file_name: str, temp: bool = True
) -> Path:
    """
    Store the agent's response in a file.
    """
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    if temp:
        file_path = TEMP_DIR / f"{timestamp} - {file_name}.md"
    else:
        file_path = STORAGE_DIR / f"{timestamp} - {file_name}.md"

    with open(file_path, "a") as file:
        file.write(response)

    return file_path


def convert_markdown_to_pdf(markdown_path: Path) -> Path:
    """
    Convert the given markdown content to a PDF file.
    If the file is in TEMP_DIR, convert absolute paths to relative paths.
    """
    if not markdown_path.exists() or not markdown_path.is_file():
        raise FileNotFoundError(f"The file {markdown_path} does not exist.")

    markdown_content = None
    with open(markdown_path, "r") as file:
        markdown_content = file.read()

    # Check if the file is in TEMP_DIR and convert absolute paths to relative
    if TEMP_DIR in markdown_path.parents or markdown_path.parent == TEMP_DIR:
        temp_dir_str = str(TEMP_DIR)
        patterns_to_remove = [
            r"sandbox:",  # Remove sandbox: prefix
            re.escape(temp_dir_str) + r"[/\\]?",  # Make TEMP_DIR paths relative
        ]

        for pattern in patterns_to_remove:
            markdown_content = re.sub(pattern, "", markdown_content)

    # By default, no table of content is generated in the PDF.
    pdf = MarkdownPdf(toc_level=0)
    pdf_path = markdown_path.with_suffix(".pdf")
    pdf.add_section(Section(text=markdown_content, toc=False, root=str(TEMP_DIR)))
    pdf.save(pdf_path)

    return pdf_path


def move_file_to_storage(file_path: Path) -> Path:
    """
    Move a file to the storage directory.
    """
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    storage_path = STORAGE_DIR / file_path.name
    file_path.rename(storage_path)

    return storage_path


def clean_temp_folder() -> None:
    """
    Clean the temporary folder by removing all files in TEMP_DIR.
    """
    if not TEMP_DIR.exists() or not TEMP_DIR.is_dir():
        return

    for item in TEMP_DIR.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            # Optionally, remove directories as well
            item.rmdir()  # This will only work if the directory is empty
