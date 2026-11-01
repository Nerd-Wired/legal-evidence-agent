from typing import TypedDict


class AgentState(TypedDict):

    # User input
    question: str

    # Retrieved evidence
    retrieved_chunks: list[dict]

    # Generated response
    answer: str

    # Evidence evaluation
    evidence_sufficient: bool

    # Citation validation
    citations_valid: bool

    # Retry tracking
    retry_count: int

    citation_feedback: str

    # Error tracking
    error: str