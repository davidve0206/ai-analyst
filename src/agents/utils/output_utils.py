from datetime import datetime
from pathlib import Path
from markdown_pdf import MarkdownPdf, Section
from semantic_kernel.agents import Agent
from semantic_kernel.contents import FunctionCallContent, FunctionResultContent
from semantic_kernel.contents.chat_message_content import ChatMessageContent

from src.configuration.settings import BASE_DIR


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


def store_response_with_timestamp(response: str, file_name: str) -> Path:
    """
    Store the agent's response in a file.
    """
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    file_path = BASE_DIR / "outputs" / f"{timestamp}-{file_name}.md"

    with open(file_path, "a") as file:
        file.write(response)

    return file_path


def convert_markdown_to_pdf(markdown_path: Path) -> Path:
    """
    Convert the given markdown content to a PDF file.
    """
    if not markdown_path.exists() or not markdown_path.is_file():
        raise FileNotFoundError(f"The file {markdown_path} does not exist.")

    markdown_content = None
    with open(markdown_path, "r") as file:
        markdown_content = file.read()

    # By default, no table of content is generated in the PDF.
    pdf = MarkdownPdf(toc_level=0)
    pdf_path = markdown_path.with_suffix(".pdf")
    pdf.add_section(Section(text=markdown_content, toc=False))
    pdf.save(pdf_path)

    return pdf_path
