from semantic_kernel.agents import Agent
from semantic_kernel.contents import FunctionCallContent, FunctionResultContent
from semantic_kernel.contents.chat_message_content import ChatMessageContent


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
            print(f"{message.role}: {message.content}")


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
