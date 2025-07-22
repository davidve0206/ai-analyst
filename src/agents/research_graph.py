from enum import Enum
from typing import Annotated, Literal
from pydantic import BaseModel, Field
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage

from src.agents.models import default_models as models_client
from src.agents.quant_agent import get_quantitative_agent
from src.agents.utils.prompt_utils import (
    MessageTypes,
    extract_graph_response_content,
    render_prompt_template,
)
from src.configuration.logger import default_logger
from src.configuration.settings import BASE_DIR

# TODO: This file is a bit convoluted and could be refactored.
#       Think about separating the graph logic from class definitions.


class BooleanProgressLedgerItem(BaseModel):
    """A progress ledger item."""

    reason: str = Field(
        description="Reason for the answer, providing context or explanation."
    )
    answer: bool = Field(
        description="The answer to the question, which should be a boolean value."
    )


class StringProgressLedgerItem(BaseModel):
    """A progress ledger item with a string answer."""

    reason: str = Field(
        description="Reason for the answer, providing context or explanation."
    )
    answer: str = Field(
        description="The answer to the question, which should be a string."
    )


class ProgressLedger(BaseModel):
    """To make progress on the request, please answer the following questions,
    including necessary reasoning"""

    is_request_satisfied: BooleanProgressLedgerItem = Field(
        description="Is the request fully satisfied? (True if complete or if there is NOT ENOUGH INFORMATION to proceed, False if the original request has yet to be SUCCESSFULLY addressed)",
        default_factory=lambda: BooleanProgressLedgerItem(
            reason="",
            answer=False,
        ),
    )
    is_in_loop: BooleanProgressLedgerItem = Field(
        description="Are we in a loop where we are repeating very similar requests and/or getting very similar responses as before? Loops can span multiple turns, and can include repeated actions like requesting the same or very similar information in a row.",
        default_factory=lambda: BooleanProgressLedgerItem(
            reason="",
            answer=False,
        ),
    )
    is_progress_being_made: BooleanProgressLedgerItem = Field(
        description="Are we making significant forward progress? (True if just starting, or recent messages are adding significant value. False if recent messages show evidence of being stuck in a loop or if there is evidence of significant barriers to success such as the inability to read from a required file. Be very strict, the analysis should be making significant progress, not just adding small bits of information.)",
        default_factory=lambda: BooleanProgressLedgerItem(
            reason="",
            answer=True,
        ),
    )
    next_speaker: StringProgressLedgerItem = Field(
        description="Who should speak next? (select from: the names of the team members)",
        default_factory=lambda: StringProgressLedgerItem(
            reason="",
            answer="",
        ),
    )
    instruction_or_question: StringProgressLedgerItem = Field(
        description="What instruction or question would you give this team member? (Phrase as if speaking directly to them, and include any specific information they may need)",
        default_factory=lambda: StringProgressLedgerItem(
            reason="",
            answer="",
        ),
    )


class ResearchGraphState(BaseModel):
    """
    Internal state model for the research Agent's graph.
    """

    task_id: str
    task: str
    task_output: str = ""
    task_facts: str = ""
    task_plan: str = ""
    task_output: str = ""
    stall_count: int = 0
    stall_count_limit: int = 3
    reset_count: int = 0
    reset_count_limit: int = 3
    messages: Annotated[list[AnyMessage], add_messages] = Field(default_factory=list)
    quant_agent_context: list[AnyMessage] = Field(
        default_factory=list
    )  # Note this doesn't auto add messages, this gives me more fine-grained control
    progress_ledger: ProgressLedger = ProgressLedger()


class GraphNodeNames(Enum):
    CREATE_OR_UPDATE_TASK_LEDGER = "create_or_update_task_ledger"
    CREATE_OR_UPDATE_TASK_PLAN = "create_or_update_task_plan"
    UPDATE_PROGRESS_LEDGER = "update_progress_ledger"
    EVALUATE_PROGRESS_LEDGER = "evaluate_progress_ledger"
    QUANTITATIVE_ANALYSIS_AGENT = "quantitative_analysis_agent"
    SUMMARIZE_FINDINGS = "summarize_findings"


class TeamMember(BaseModel):
    """
    Represents a team member in the research graph.
    """

    name: str  # Note: this should be the value of the GraphNodeNames enum (e.g. "quantitative_analysis_agent")
    role: str


class Team(BaseModel):
    members: list[TeamMember]

    @property
    def member_names(self) -> list[str]:
        """
        Returns a list of names of the team members.
        """
        return [member.name for member in self.members]

    @property
    def member_strings(self) -> list[str]:
        """
        Returns a list of strings representing the team members.
        """
        return [f"{member.name}: {member.role}" for member in self.members]

    @property
    def members_string(self) -> str:
        """
        Returns a string representation of the team members.
        """
        return "\n- " + "\n- ".join(self.member_strings)


DEFAULT_TEAM = Team(
    members=[
        TeamMember(
            name=GraphNodeNames.QUANTITATIVE_ANALYSIS_AGENT.value,
            role="Can load files, run code, and perform quantitative analysis. Only has access to files mentioned in the task, not to the general internet. Should not perform any complex statistical analysis; only simple regression analysis is allowed.",
        ),
    ]
)


async def create_or_update_task_ledger(state: ResearchGraphState):
    """
    Function to create or update the task ledger.
    This function is called when the task is first created or when the task facts are updated.
    """
    default_logger.info(f"Creating or updating ledger for task: {state.task_id}")

    task_prompt: HumanMessage
    if not state.task_facts:
        task_prompt = render_prompt_template(
            template_name="magentic_one/task_ledger_facts_prompt.md",
            context={"task": state.task},
            type=MessageTypes.HUMAN,
        )
    else:
        task_prompt = render_prompt_template(
            template_name="magentic_one/task_ledger_facts_update_prompt.md",
            context={"task": state.task, "old_facts": state.task_facts},
            type=MessageTypes.HUMAN,
        )

    messages = state.messages + [task_prompt]
    response = await models_client.default_model.ainvoke(messages)
    return {
        "task_facts": response.content,
        "messages": [response],
    }


async def create_or_update_task_plan(state: ResearchGraphState):
    """
    Function that creates or updates a task plan and sets the stall count to zero.
    This function is called when the task is first created or when the task plan is updated.
    """
    default_logger.info(f"Creating or updating task plan for task: {state.task_id}")

    if not state.task_plan:
        task_plan_prompt = render_prompt_template(
            template_name="magentic_one/task_ledger_plan_prompt.md",
            context={"team": DEFAULT_TEAM.members_string},
            type=MessageTypes.HUMAN,
        )
    else:
        task_plan_prompt = render_prompt_template(
            template_name="magentic_one/task_ledger_plan_update_prompt.md",
            context={"team": DEFAULT_TEAM.members_string},
            type=MessageTypes.HUMAN,
        )

    messages = state.messages + [task_plan_prompt]
    response = await models_client.default_model.ainvoke(messages)
    return {
        "task_plan": response.content,
        "messages": [response],
        "stall_count": 0,  # Reset stall count when task plan is created or updated
    }


async def update_progress_ledger(state: ResearchGraphState):
    """
    Function that updates the progress ledger.
    """
    default_logger.info(f"Updating progress ledger for task: {state.task_id}")
    task_message = render_prompt_template(
        "magentic_one/progress_ledger_prompt.md",
        context={
            "task": state.task,
            "team": DEFAULT_TEAM.members_string,
            "team_names": DEFAULT_TEAM.member_names,
        },
        type=MessageTypes.HUMAN,
    )
    progress_ledger_context = state.messages + [task_message]

    structured_response_model = models_client.default_model.with_structured_output(
        ProgressLedger
    )
    response: ProgressLedger = await structured_response_model.ainvoke(
        progress_ledger_context
    )

    return {
        "progress_ledger": response,
    }


async def quantitative_analysis_agent(state: ResearchGraphState):
    """
    Function that performs quantitative analysis.

    The context of the quant agent only includes the messages that
    have been sent to it and its own responses, while the conversation
    history excludes the quant agent's code.
    """
    default_logger.info(f"Performing quantitative analysis for task: {state.task_id}")

    #
    agent = get_quantitative_agent(models_client)
    updated_context = state.quant_agent_context + [
        HumanMessage(state.progress_ledger.instruction_or_question.answer)
    ]
    response = await agent.ainvoke({"messages": updated_context})

    # Extract the content and files from the response
    response = extract_graph_response_content(response)
    updated_context.append(AIMessage(response.content))

    return {
        "quant_agent_context": updated_context,
        "messages": [AIMessage(response.content)],
    }


async def summarize_findings(state: ResearchGraphState):
    """
    Summarize findings to return to the user.
    """
    default_logger.info(f"Summarizing findings for task: {state.task_id}")

    summary_message = render_prompt_template(
        template_name="magentic_one/summarize_findings_prompt.md",
        context={
            "task": state.task,
        },
        type=MessageTypes.HUMAN,
    )
    summary_context = state.messages + [summary_message]

    response = await models_client.default_model.ainvoke(summary_context)
    return {
        "task_output": response.content,
    }


async def evaluate_progress_ledger(
    state: ResearchGraphState,
) -> Command[
    Literal[
        "create_or_update_task_ledger",
        "summarize_findings",
        "quantitative_analysis_agent",
    ]
]:
    """
    Placeholder for a gate function that checks the progress ledger.
    """
    default_logger.info(f"Checking progress ledger for task: {state.task_id}")

    # Before anything else, update the stall count
    if (
        state.progress_ledger.is_in_loop.answer
        or not state.progress_ledger.is_progress_being_made.answer
    ):
        state.stall_count += 1

    # Then, determine the next step based on the progress ledger
    if (
        state.progress_ledger.is_request_satisfied.answer
        or state.reset_count >= state.reset_count_limit
    ):
        goto = GraphNodeNames.SUMMARIZE_FINDINGS.value
    elif (
        state.stall_count >= state.stall_count_limit
        and not state.progress_ledger.is_progress_being_made.answer
    ):
        goto = GraphNodeNames.CREATE_OR_UPDATE_TASK_LEDGER.value
        state.reset_count += 1  # Count the reset
    else:
        goto = state.progress_ledger.next_speaker.answer

    return Command(
        goto=goto,
        update={
            "next_speaker": goto,
            "stall_count": state.stall_count,
            "reset_count": state.reset_count,
        },
    )


async def create_research_graph(
    store_diagram: bool = False,
) -> CompiledStateGraph[ResearchGraphState]:
    workflow = StateGraph(ResearchGraphState)

    workflow.add_node(
        GraphNodeNames.CREATE_OR_UPDATE_TASK_LEDGER.value,
        create_or_update_task_ledger,
    )
    workflow.add_node(
        GraphNodeNames.CREATE_OR_UPDATE_TASK_PLAN.value,
        create_or_update_task_plan,
    )
    workflow.add_node(
        GraphNodeNames.UPDATE_PROGRESS_LEDGER.value,
        update_progress_ledger,
    )
    workflow.add_node(
        GraphNodeNames.EVALUATE_PROGRESS_LEDGER.value,
        evaluate_progress_ledger,
    )
    workflow.add_node(
        GraphNodeNames.QUANTITATIVE_ANALYSIS_AGENT.value,
        quantitative_analysis_agent,
    )
    workflow.add_node(
        GraphNodeNames.SUMMARIZE_FINDINGS.value,
        summarize_findings,
    )

    workflow.add_edge(START, GraphNodeNames.CREATE_OR_UPDATE_TASK_LEDGER.value)
    workflow.add_edge(
        GraphNodeNames.CREATE_OR_UPDATE_TASK_LEDGER.value,
        GraphNodeNames.CREATE_OR_UPDATE_TASK_PLAN.value,
    )
    workflow.add_edge(
        GraphNodeNames.CREATE_OR_UPDATE_TASK_PLAN.value,
        GraphNodeNames.UPDATE_PROGRESS_LEDGER.value,
    )
    workflow.add_edge(
        GraphNodeNames.UPDATE_PROGRESS_LEDGER.value,
        GraphNodeNames.EVALUATE_PROGRESS_LEDGER.value,
    )
    workflow.add_edge(
        GraphNodeNames.QUANTITATIVE_ANALYSIS_AGENT.value,
        GraphNodeNames.UPDATE_PROGRESS_LEDGER.value,
    )
    workflow.add_edge(
        GraphNodeNames.SUMMARIZE_FINDINGS.value,
        END,
    )

    chain = workflow.compile()
    print(chain)
    if store_diagram:
        # Store the graph diagram as a PNG file
        default_logger.info("Storing the research graph diagram as a PNG file.")
        chain.get_graph().draw_mermaid_png(
            output_file_path=(BASE_DIR / "documentation" / "sales_research_graph.png")
        )

    return chain
