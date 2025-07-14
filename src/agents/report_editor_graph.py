from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command
from langchain_core.messages import AnyMessage, HumanMessage

from src.agents.models import default_models as models_client
from src.agents.data_visualization_agent import get_data_visualization_agent
from src.agents.utils.output_utils import get_all_files_mentioned_in_response
from src.agents.utils.prompt_utils import (
    PrompTypes,
    create_human_message_from_parts,
    extract_graph_response_content,
    get_full_path_to_temp_file,
    render_prompt_template,
)
from src.configuration.logger import default_logger
from src.configuration.settings import BASE_DIR


class ReportEditorGraphState(BaseModel):
    messages: list[AnyMessage]
    report: str = ""
    next_speaker: str = ""


COMPLETE_VALUE = "report_complete"


class GraphNodeNames(Enum):
    SUPERVISOR = "supervisor"
    DATA_VISUALIZATION_AGENT = "data_visualization_agent"
    DOCUMENT_WRITING_AGENT = "document_writing_agent"


async def supervisor(
    state: ReportEditorGraphState,
) -> Command[Literal["__end__", "data_visualization_agent", "document_writing_agent"]]:
    """
    Supervisor node to handle the report editing process.
    """
    default_logger.info("Supervisor node is processing the report editing request.")

    system_message = render_prompt_template(
        template_name="editing_supervisor_system_prompt.md",
        context={},
        type=PrompTypes.SYSTEM,
    )
    llm = models_client.gpt_o4_mini

    next_speaker_options = [
        COMPLETE_VALUE,
        GraphNodeNames.DATA_VISUALIZATION_AGENT.value,
        GraphNodeNames.DOCUMENT_WRITING_AGENT.value,
    ]

    class Router(BaseModel):
        """Next speaker and task routing model."""

        next_speaker: str = Field(
            description=f"The next speaker to handle the request. Choose from: {', '.join(next_speaker_options)}; if the report is complete, use '{COMPLETE_VALUE}'",
            enum=next_speaker_options,
        )
        next_speaker_task: str = Field(
            description="The task to be performed by the next speaker. State the task as if you were talking directly to them.",
        )

    messages = (
        [system_message]
        + state.messages
        + HumanMessage(f"This is the current report: \n\n {state.report}")
    )
    response: Router = await llm.with_structured_output(Router).ainvoke(messages)

    goto = response.next_speaker
    if goto == COMPLETE_VALUE:
        default_logger.info("Report editing process is complete.")
        goto = END

    return Command(
        goto=goto,
        update={
            "next_speaker": goto,
            "messages": state.messages + HumanMessage(response.next_speaker_task),
        },
    )


async def data_visualization_agent(
    state: ReportEditorGraphState,
) -> Command[Literal["supervisor"]]:
    """
    Node to generate charts based on the report request.
    """
    default_logger.info("Generating charts for the report.")
    # Call the data visualization agent to generate charts
    agent = get_data_visualization_agent(models_client)
    response = await agent.ainvoke({"messages": state.messages})
    # Extract the content and files from the response
    response = extract_graph_response_content(response)
    files = get_all_files_mentioned_in_response(response)
    img_paths = [
        get_full_path_to_temp_file(file)
        for file in files
        if file.endswith(".png") or file.endswith(".jpg")
    ]

    # Create the updated message with the generated charts
    message = create_human_message_from_parts(
        text_parts=[response],
        file_list=img_paths,
    )

    return Command(
        update={
            "messages": state.messages + [message],
        },
        goto=GraphNodeNames.SUPERVISOR.value,
    )


async def document_writing_agent(
    state: ReportEditorGraphState,
) -> Command[Literal["supervisor"]]:
    """
    Node to write the document based on the report request.
    """
    default_logger.info("Writing the document for the report.")

    # Get the system prompt for the editor agent
    system_message = render_prompt_template(
        template_name="editor_agent_system_prompt.md",
        context={},
        type=PrompTypes.SYSTEM,
    )

    messages = [system_message] + state.messages

    system_message = render_prompt_template(
        template_name="editor_agent_system_prompt.md",
        context={},
        type=PrompTypes.SYSTEM,
    )

    result = await models_client.gpt_o4_mini.ainvoke(messages)
    return Command(
        update={
            "report": result.content,
        },
        goto=GraphNodeNames.SUPERVISOR.value,
    )


async def create_report_editor_graph(store_diagram: bool = False) -> CompiledStateGraph:
    """
    Create the report editor graph with the defined nodes and transitions.
    """
    default_logger.info("Creating the report editor graph.")

    graph = StateGraph(ReportEditorGraphState)

    # Define the nodes in the graph
    graph.add_node(GraphNodeNames.SUPERVISOR.value, supervisor)
    graph.add_node(
        GraphNodeNames.DATA_VISUALIZATION_AGENT.value, data_visualization_agent
    )
    graph.add_node(GraphNodeNames.DOCUMENT_WRITING_AGENT.value, document_writing_agent)

    # Define the transitions between nodes
    graph.add_edge(START, GraphNodeNames.SUPERVISOR.value)

    # Compile the state graph
    chain = graph.compile()
    default_logger.info("Report editor graph created successfully.")

    if store_diagram:
        # Store the graph diagram as a PNG file
        default_logger.info("Storing the report editor graph diagram as a PNG file.")
        chain.get_graph().draw_mermaid_png(
            output_file_path=(BASE_DIR / "documentation" / "report_editor_graph.png")
        )

    return chain
