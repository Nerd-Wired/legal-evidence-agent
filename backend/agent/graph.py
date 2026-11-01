from langgraph.graph import StateGraph, END

from backend.agent.state import AgentState
from backend.agent.nodes import (
    retrieve_evidence,
    evaluate_evidence,
    generate_response,
    validate_response,
    MAX_CITATION_RETRIES
)


def route_after_evaluation(state: AgentState):
    return "generate" if state["evidence_sufficient"] else END


def route_after_validation(state: AgentState):
    if state.get("citations_valid") or state.get("error"):
        return END

    if state.get("retry_count", 0) <= MAX_CITATION_RETRIES:
        return "generate"

    return END


def build_agent():
    workflow = StateGraph(AgentState)

    workflow.add_node("retrieve", retrieve_evidence)
    workflow.add_node("evaluate", evaluate_evidence)
    workflow.add_node("generate", generate_response)
    workflow.add_node("validate", validate_response)

    workflow.set_entry_point("retrieve")

    workflow.add_edge("retrieve", "evaluate")

    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {"generate": "generate", END: END}
    )

    workflow.add_edge("generate", "validate")

    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {"generate": "generate", END: END}
    )

    return workflow.compile()