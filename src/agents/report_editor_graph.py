from enum import Enum
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command

from langchain_core.messages import AnyMessage, HumanMessage

from src.agents.models import default_models as models_client
from src.agents.data_visualization_agent import get_data_visualization_agent
from src.agents.utils.output_utils import (
    get_all_files_mentioned_in_response,
    get_all_temp_files,
    get_full_path_to_temp_file,
)
from src.agents.utils.prompt_utils import (
    MessageTypes,
    create_human_message_from_parts,
    extract_graph_response_content,
    render_prompt_template,
)
from src.configuration.kpis import SalesReportRequest
from src.configuration.logger import default_logger
from src.configuration.settings import BASE_DIR


class ReportEditorGraphState(BaseModel):
    request: SalesReportRequest
    messages: Annotated[list[AnyMessage], add_messages]
    report: str = ""
    next_speaker: str = ""
    loop_count: int = 0
    max_writer_loops: int = 3  # End if the writer is repeated this many times in a row
    # Example: if the writing agent is chosen 3 times in a row (once first time, two repeated), we return the current report
    max_visualization_loops: int = 5  # Similar logic for visualization agent
    # This is much higher as we expect the visualization agent to be called multiple times for different charts

    def current_report_message(self) -> HumanMessage:
        """
        Returns the last human message in the conversation.
        """
        temp_file_list = get_all_temp_files(self.request)
        temp_file_str = [file.name for file in temp_file_list]

        return HumanMessage(
            f"{'No report has been generated yet.' if not self.report else f'This is the current report: \n\n {self.report}'} \n\n The following files are available: {', '.join(temp_file_str)} \n\n Last speaker: {self.next_speaker}",
        )


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
        context={
            "writing_agent_name": GraphNodeNames.DOCUMENT_WRITING_AGENT.value,
            "data_visualization_agent_name": GraphNodeNames.DATA_VISUALIZATION_AGENT.value,
            "complete_value": COMPLETE_VALUE,
        },
        type=MessageTypes.SYSTEM,
    )

    next_speaker_options = [
        COMPLETE_VALUE,
        GraphNodeNames.DATA_VISUALIZATION_AGENT.value,
        GraphNodeNames.DOCUMENT_WRITING_AGENT.value,
    ]

    class Router(BaseModel):
        """Next speaker and task routing model.

        Always fill the reasoning field with a brief explanation of why the next speaker was chosen.
        Including the necessary changes to the report that trigger this choice.
        """

        reasoning: str = Field(
            description="Reasoning for the next speaker choice. Explain why this speaker is chosen based on the current report state.",
        )
        next_speaker: str = Field(
            description=f"The next speaker to handle the request. Choose from: {', '.join(next_speaker_options)}; if the report is complete, use '{COMPLETE_VALUE}'",
        )
        next_speaker_task: str = Field(
            description="The task to be performed by the next speaker. State the task as if you were talking directly to them, with as much detail as necessary.",
        )

    messages = [system_message] + state.messages + [state.current_report_message()]
    response: Router = await models_client.default_model.with_structured_output(
        Router
    ).ainvoke(messages)

    goto = response.next_speaker

    # Check if we are looping back to the same speaker
    new_loop_count = state.loop_count
    if goto == state.next_speaker:
        new_loop_count += 1
    else:
        new_loop_count = 0

    # Determine the max loops based on which agent is being chosen
    max_loops = 0
    if goto == GraphNodeNames.DOCUMENT_WRITING_AGENT.value:
        max_loops = state.max_writer_loops
    elif goto == GraphNodeNames.DATA_VISUALIZATION_AGENT.value:
        max_loops = state.max_visualization_loops

    if new_loop_count >= max_loops or goto == COMPLETE_VALUE:
        goto = END

    return Command(
        goto=goto,
        update={
            "next_speaker": goto,
            "loop_count": new_loop_count,
            "messages": [HumanMessage(response.next_speaker_task)],
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
    agent = get_data_visualization_agent(models_client, request=state.request)
    response = await agent.ainvoke({"messages": state.messages})

    # Extract the content and files from the response
    response = extract_graph_response_content(response)
    files = get_all_files_mentioned_in_response(response)
    img_paths = [
        get_full_path_to_temp_file(file, state.request)
        for file in files
        if file.endswith(".png")
    ]

    # Create the updated message with the generated charts
    message = create_human_message_from_parts(
        text_parts=[response],
        file_list=img_paths,
    )

    return Command(
        update={
            "messages": [message],
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
        template_name="editing_writer_system_prompt.md",
        context={},
        type=MessageTypes.SYSTEM,
    )

    messages = [system_message] + state.messages + [state.current_report_message()]

    result = await models_client.default_model.ainvoke(messages)
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

    workflow = StateGraph(ReportEditorGraphState)

    # Define the nodes in the graph
    workflow.add_node(GraphNodeNames.SUPERVISOR.value, supervisor)
    workflow.add_node(
        GraphNodeNames.DATA_VISUALIZATION_AGENT.value, data_visualization_agent
    )
    workflow.add_node(
        GraphNodeNames.DOCUMENT_WRITING_AGENT.value, document_writing_agent
    )

    # Define the transitions between nodes
    workflow.add_edge(START, GraphNodeNames.SUPERVISOR.value)

    # Compile the state graph
    chain = workflow.compile()
    default_logger.info("Report editor graph created successfully.")

    if store_diagram:
        # Store the graph diagram as a PNG file
        default_logger.info("Storing the report editor graph diagram as a PNG file.")
        chain.get_graph().draw_mermaid_png(
            output_file_path=(BASE_DIR / "documentation" / "report_editor_graph.png")
        )

    return chain
