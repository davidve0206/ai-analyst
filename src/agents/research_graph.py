from enum import Enum
from typing import Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.configuration.logger import default_logger
from src.configuration.settings import BASE_DIR


class ResearchGraphState(BaseModel):
    """
    State model for the research Agent's graph.
    """

    task: str


class InternalResearchGraphState(BaseModel):
    """
    Internal state model for the research Agent's graph.
    """

    task: str
    stall_count: int = 0
    stall_count_limit: int = 3

    def reset_stall_count(self):
        """
        Reset the stall count to zero.
        """
        self.stall_count = 0

    def increment_stall_count(self):
        """
        Increment the stall count by one.
        """
        self.stall_count += 1


class ProgressLedgerItem(BaseModel):
    """A progress ledger item."""

    reason: str
    answer: str | bool


class ProgressLedger(BaseModel):
    """A progress ledger."""

    is_request_satisfied: ProgressLedgerItem
    is_in_loop: ProgressLedgerItem
    is_progress_being_made: ProgressLedgerItem
    next_speaker: ProgressLedgerItem
    instruction_or_question: ProgressLedgerItem


class GraphNodeNames(Enum):
    CREATE_OR_UPDATE_TASK_LEDGER = "create_or_update_task_ledger"
    CREATE_OR_UPDATE_TASK_PLAN = "create_or_update_task_plan"
    UPDATE_PROGRESS_LEDGER = "update_progress_ledger"
    HANDOVER_TO_TEAM_MEMBER = "handover_to_team_member"
    SUMMARIZE_FINDINGS = "summarize_findings"


async def create_or_update_task_ledger(state: ResearchGraphState):
    """
    Placeholder for a function that creates or updates a ledger.
    """
    default_logger.info(f"Creating or updating ledger for task: {state.task}")
    # Implementation goes here


async def create_or_update_task_plan(state: ResearchGraphState):
    """
    Placeholder for a function that creates or updates a task plan.
    """
    default_logger.info(f"Creating or updating task plan for: {state.task}")
    # Implementation goes here


async def update_progress_ledger(state: ResearchGraphState):
    """
    Placeholder for a function that updates the progress ledger.
    """
    default_logger.info(f"Updating progress ledger for task: {state.task}")
    # Implementation goes here


async def handover_to_team_member(state: ResearchGraphState):
    """
    Placeholder for a function that hands over the task to a team member.
    """
    default_logger.info(f"Handover task: {state.task} to team member")
    # Implementation goes here


async def summarize_findings(state: ResearchGraphState):
    """
    Placeholder for a function that summarizes findings.
    """
    default_logger.info(f"Summarizing findings for task: {state.task}")
    # Implementation goes here


async def progress_ledger_gate(
    state: ResearchGraphState,
) -> Literal[
    "create_or_update_task_ledger", "summarize_findings", "handover_to_team_member"
]:
    """
    Placeholder for a gate function that checks the progress ledger.
    """
    default_logger.info(f"Checking progress ledger for task: {state.task}")
    # Implementation goes here


async def create_research_graph(
    store_diagram: bool = False,
) -> CompiledStateGraph[ResearchGraphState]:
    graph = StateGraph(ResearchGraphState)

    graph.add_node(
        GraphNodeNames.CREATE_OR_UPDATE_TASK_LEDGER.value,
        create_or_update_task_ledger,
    )
    graph.add_node(
        GraphNodeNames.CREATE_OR_UPDATE_TASK_PLAN.value,
        create_or_update_task_plan,
    )
    graph.add_node(
        GraphNodeNames.UPDATE_PROGRESS_LEDGER.value,
        update_progress_ledger,
    )
    graph.add_node(
        GraphNodeNames.HANDOVER_TO_TEAM_MEMBER.value,
        handover_to_team_member,
    )
    graph.add_node(
        GraphNodeNames.SUMMARIZE_FINDINGS.value,
        summarize_findings,
    )

    graph.add_edge(START, GraphNodeNames.CREATE_OR_UPDATE_TASK_LEDGER.value)
    graph.add_edge(
        GraphNodeNames.CREATE_OR_UPDATE_TASK_LEDGER.value,
        GraphNodeNames.CREATE_OR_UPDATE_TASK_PLAN.value,
    )
    graph.add_edge(
        GraphNodeNames.CREATE_OR_UPDATE_TASK_PLAN.value,
        GraphNodeNames.UPDATE_PROGRESS_LEDGER.value,
    )
    graph.add_conditional_edges(
        GraphNodeNames.UPDATE_PROGRESS_LEDGER.value, progress_ledger_gate
    )
    graph.add_edge(
        GraphNodeNames.HANDOVER_TO_TEAM_MEMBER.value,
        GraphNodeNames.UPDATE_PROGRESS_LEDGER.value,
    )
    graph.add_edge(
        GraphNodeNames.SUMMARIZE_FINDINGS.value,
        END,
    )

    chain = graph.compile()
    print(chain)
    if store_diagram:
        # Store the graph diagram as a PNG file
        default_logger.info("Storing the research graph diagram as a PNG file.")
        chain.get_graph().draw_mermaid_png(
            output_file_path=(BASE_DIR / "documentation" / "sales_research_graph.png")
        )

    return chain
