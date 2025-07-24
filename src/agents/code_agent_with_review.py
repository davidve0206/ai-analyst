"""
This module is similar to LangGraph's react agent, allowing
for the creation of agents that can interact with a code interpreter,
with a few key differences:

    TODO: Complete the docstring

This is useful for ensuring that the agent does not get stuck in an
infinite loop or execute harmful code.
"""

from enum import Enum
from pathlib import Path
from typing import Annotated, Literal
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command
from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage

from src.agents.models import AppChatModels
from src.agents.tools.python_interpreter import create_python_repl_tool
from src.agents.utils.output_utils import store_graph_as_png
from src.agents.utils.prompt_utils import (
    MessageTypes,
    render_prompt_template,
)
from src.configuration.logger import default_logger


class CodeAgentState(BaseModel):
    """State for the code agent with review.

    Max iterations default to 25 in line with langgaraph's default,
    be sure to set a recursion_limit if you want a larger number of iterations.
    """

    messages: Annotated[list[AnyMessage], add_messages] = Field(default_factory=list)
    system_prompt: SystemMessage | None = None
    max_errors: int = 5  # Maximum number of errors before stopping
    errors_counter: int = 0
    max_iterations: int = 25  # Maximum number of iterations before stopping
    iterations_counter: int = 0


class GraphNodeNames(Enum):
    AGENT = "agent"
    CODE_REVIEW = "code_review"
    TOOLS = "tools"
    TOOL_RESULT_ASSESSMENT = "tool_result_assessment"


def is_invalid_code_tool_message(message: ToolMessage) -> bool:
    """
    Validates that the message is a valid ToolMessage for code execution.

    Args:
        message: The ToolMessage to validate

    Returns:
        bool: True if valid, False otherwise

    Raises:
        ValueError: If message is not a ToolMessage
    """
    if not isinstance(message, ToolMessage):
        raise ValueError(
            "The last message must be a ToolMessage for progress assessment."
        )

    if message.status == "error":
        default_logger.debug("Received an error status in the tool message.")
        return True

    if message.content == "":
        default_logger.debug("Received an empty string as the last message content.")
        return True

    if "Error" in message.content or "Exception" in message.content:
        default_logger.debug("Received an error message in the last tool call output.")
        return True

    return False


def create_code_agent_with_review(models: AppChatModels) -> CompiledStateGraph:
    """
    Creates a code agent with review capabilities.

    Args:
        models (AppChatModels): The models to use for the agent.

    Returns:
        CompiledStateGraph: The compiled state graph for the agent.
    """
    # Create the tool for code execution and bind it to the model and tools node
    python_repl_tool = create_python_repl_tool()
    llm_with_tools = models.default_model.bind_tools(tools=[python_repl_tool])
    tool_node = ToolNode(tools=[python_repl_tool])

    async def agent(state: CodeAgentState) -> dict:
        """
        Basic call to the LLM model with tools bound.
        """
        messages = [state.system_prompt] if state.system_prompt else []
        messages += state.messages
        result = await llm_with_tools.ainvoke(messages)
        return {"messages": [result]}

    async def tool_result_assessment(
        state: CodeAgentState,
    ) -> Command[Literal["agent", "code_review"]]:
        """
        Uses an LLM to assess if progress is being made or if we're stuck in a loop.
        """

        last_response = state.messages[-1] if state.messages else None
        is_error = is_invalid_code_tool_message(last_response)

        # First, update the error counter if we have an error
        # and always increment the iteration counter
        state.iterations_counter += 1
        if is_error:
            state.errors_counter += 1
        else:
            state.errors_counter = 0  # Reset error counter if no error

        if (
            state.errors_counter >= state.max_errors
            or state.iterations_counter >= state.max_iterations
        ):
            # Add message to diagnose the situation and stop calling tools
            diagnose_message = render_prompt_template(
                "code_agent/diagnose_progress_prompt.md",
                context={},
                type=MessageTypes.AI,
            )
            state.messages.append(diagnose_message)

            # Jump directly to the agent node for the final output
            goto = GraphNodeNames.AGENT.value
        elif is_error:
            # Add message to let the agent know there was an error
            # Add message to diagnose the situation and stop calling tools
            diagnose_message = render_prompt_template(
                "code_agent/tool_error_prompt.md",
                context={},
                type=MessageTypes.HUMAN,
            )
            state.messages.append(diagnose_message)
            # If we have an error, we want to go to code review for further analysis
            goto = GraphNodeNames.CODE_REVIEW.value
        else:
            # In any other case, we want to go to the agent for further action
            goto = GraphNodeNames.AGENT.value

        return Command(
            goto=goto,
            update={
                "messages": state.messages,
                "iterations_counter": state.iterations_counter,
                "errors_counter": state.errors_counter,
            },
        )

    async def code_review(state: CodeAgentState) -> dict:
        """
        Reviews the proposed code before execution using LLM.
        """
        # Create code review prompt with the code to review
        system_message = render_prompt_template(
            "code_agent/code_review_system_prompt.md",
            context={},
            type=MessageTypes.SYSTEM,
        )

        # Build context for code review, ignore the last message
        # as it is just to give the main agent some context
        review_context = [system_message] + state.messages[:-1]

        # Get LLM review
        review_response = await models.default_non_reasoning_model.ainvoke(
            review_context
        )

        return {"messages": [review_response]}

    workflow = StateGraph(CodeAgentState)
    workflow.add_node(
        GraphNodeNames.AGENT.value,
        agent,
    )
    workflow.add_node(
        GraphNodeNames.TOOLS.value,
        tool_node,
    )
    workflow.add_node(
        GraphNodeNames.TOOL_RESULT_ASSESSMENT.value,
        tool_result_assessment,
    )
    workflow.add_node(
        GraphNodeNames.CODE_REVIEW.value,
        code_review,
    )

    workflow.add_edge(START, GraphNodeNames.AGENT.value)
    workflow.add_conditional_edges(GraphNodeNames.AGENT.value, tools_condition)
    workflow.add_edge(
        GraphNodeNames.TOOLS.value,
        GraphNodeNames.TOOL_RESULT_ASSESSMENT.value,
    )
    workflow.add_edge(
        GraphNodeNames.CODE_REVIEW.value,
        GraphNodeNames.AGENT.value,
    )

    return workflow.compile()


class PreConfiguredCodeAgent:
    """
    A preconfigured code agent that wraps the code agent with review functionality.

    This class provides a convenient interface for using the code agent with review
    capabilities, allowing for preset configuration and easy invocation.
    """

    _agent: CompiledStateGraph
    _preset_state: CodeAgentState
    _nodes_count: int = 2

    def __init__(
        self,
        preset_state: CodeAgentState,
        models: AppChatModels,
        name: str = "pre_configured_code_agent",
    ):
        """
        Initialize the preconfigured code agent.

        Args:
            preset_state (CodeAgentState): The preset state configuration for the agent
            models (AppChatModels): The models to use for the agent
        """
        self._agent = create_code_agent_with_review(models)
        self._preset_state = preset_state
        self._nodes_count = len(self._agent.nodes)
        self._name = name

    def store_graph_as_png(self) -> Path:
        return store_graph_as_png(graph=self._agent, file_name=self._name)

    def update_system_prompt(self, system_prompt: SystemMessage | None) -> None:
        """
        Update the system prompt in the preset state.

        Args:
            system_prompt (SystemMessage | None): The new system prompt
        """
        self._preset_state.system_prompt = system_prompt

    def update_max_iterations(self, max_iterations: int) -> None:
        """
        Update the maximum number of iterations in the preset state.

        Args:
            max_iterations (int): The new maximum number of iterations
        """
        self._preset_state.max_iterations = max_iterations

    def update_max_errors(self, max_errors: int) -> None:
        """
        Update the maximum number of errors in the preset state.

        Args:
            max_errors (int): The new maximum number of errors
        """
        self._preset_state.max_errors = max_errors

    def _prepare_state_and_config(
        self, messages: list[AnyMessage]
    ) -> tuple[CodeAgentState, dict]:
        """
        Prepare the state copy and configuration for agent invocation.

        Args:
            messages (list[AnyMessage]): The messages to add to the preset state

        Returns:
            tuple[CodeAgentState, dict]: The prepared state and configuration
        """
        state_copy = self._preset_state.model_copy(
            deep=True, update={"messages": self._preset_state.messages + messages}
        )
        config = {"recursion_limit": state_copy.max_iterations * self._nodes_count}
        return state_copy, config

    async def ainvoke(self, messages: list[AnyMessage]) -> dict:
        """
        Asynchronously invoke the code agent with the given messages.

        Args:
            messages (list[AnyMessage]): The messages to process

        Returns:
            dict: The result from the agent invocation
        """
        state_copy, config = self._prepare_state_and_config(messages)
        return await self._agent.ainvoke(state_copy, config)

    def invoke(self, messages: list[AnyMessage]) -> dict:
        """
        Synchronously invoke the code agent with the given messages.

        Args:
            messages (list[AnyMessage]): The messages to process

        Returns:
            dict: The result from the agent invocation
        """
        state_copy, config = self._prepare_state_and_config(messages)
        return self._agent.invoke(state_copy, config)
