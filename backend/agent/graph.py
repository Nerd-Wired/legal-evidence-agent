from langgraph.graph import StateGraph, END

from backend.agent.state import AgentState
from backend.agent.nodes import (
    retrieve_evidence,
    evaluate_evidence,
    generate_response
)


def build_agent():
    workflow = StateGraph(AgentState)

    # Register nodes
    workflow.add_node("retrieve", retrieve_evidence)
    workflow.add_node("evaluate", evaluate_evidence)
    workflow.add_node("generate", generate_response)

    # Define workflow sequence
    workflow.set_entry_point("retrieve")

    workflow.add_edge("retrieve", "evaluate")

    workflow.add_conditional_edges(
        "evaluate",
        lambda state: (
            "generate" if state["evidence_sufficient"] else END
        ),
        {
            "generate": "generate",
            END: END
        }
    )

    workflow.add_edge("generate", END)

    return workflow.compile()