import os
from backend.agent.state import AgentState
from backend.hybrid_retriever import hybrid_search, build_bm25_index
from backend.answer_generator import generate_answer
from backend.chunk_store import load_chunks
from backend.citation_validator import validate_citations, build_feedback

MIN_SEMANTIC_SCORE = float(os.getenv("MIN_SEMANTIC_SCORE", "0.39"))

NO_EVIDENCE_MESSAGE = (
    "I could not find relevant evidence in the indexed documents "
    "to answer this question."
)
MAX_CITATION_RETRIES = 1

# In-memory copy of the indexed chunks, loaded lazily from disk
document_chunks = []
bm25_index = None


def set_document_store(chunks):
    global document_chunks, bm25_index

    document_chunks = chunks
    bm25_index = build_bm25_index(chunks) if chunks else None


def ensure_document_store():
    """Load the chunks saved at indexing time and build BM25 once per process."""
    if document_chunks and bm25_index is not None:
        return

    chunks = load_chunks()

    if chunks:
        set_document_store(chunks)


def retrieve_evidence(state: AgentState):
    ensure_document_store()

    if not document_chunks or bm25_index is None:
        return {
            "retrieved_chunks": [],
            "error": "No documents have been indexed. Run: python -m backend.index_documents"
        }

    results = hybrid_search(
        query=state["question"],
        chunks=document_chunks,
        bm25=bm25_index,
        limit=5
    )

    return {
        "retrieved_chunks": results,
        "retry_count": state.get("retry_count", 0)
    }


def evaluate_evidence(state: AgentState):
    # Keep an upstream failure (e.g. nothing indexed) visible instead of masking it
    if state.get("error"):
        return {"evidence_sufficient": False}

    usable_chunks = [
        chunk for chunk in state.get("retrieved_chunks", [])
        if chunk.get("text", "").strip()
    ]

    best_score = max(
        (chunk.get("semantic_score", 0.0) for chunk in usable_chunks),
        default=0.0
    )

    if best_score < MIN_SEMANTIC_SCORE:
        return {
            "evidence_sufficient": False,
            "answer": NO_EVIDENCE_MESSAGE,
            "error": ""
        }

    return {
        "evidence_sufficient": True,
        "error": ""
    }


def generate_response(state: AgentState):
    try:
        answer = generate_answer(
            query=state["question"],
            retrieved_chunks=state["retrieved_chunks"],
            feedback=state.get("citation_feedback", "")
        )

        return {
            "answer": answer,
            "error": ""
        }

    except Exception as e:
        return {
            "answer": "",
            "error": str(e)
        }


def validate_response(state: AgentState):
    # Generation failed, so there is nothing to validate
    if state.get("error"):
        return {"citations_valid": False}

    result = validate_citations(state["answer"], state["retrieved_chunks"])

    if result["valid"]:
        return {
            "citations_valid": True,
            "citation_feedback": ""
        }

    feedback = build_feedback(result)
    failures = state.get("retry_count", 0) + 1

    if failures <= MAX_CITATION_RETRIES:
        # The graph routes back to generate with this feedback
        return {
            "citations_valid": False,
            "citation_feedback": feedback,
            "retry_count": failures
        }

    # Out of retries: return the answer, but flag it clearly
    return {
        "citations_valid": False,
        "citation_feedback": feedback,
        "retry_count": failures,
        "answer": (
            state["answer"]
            + "\n\nWARNING: the automatic citation check failed ("
            + feedback
            + ") Verify this answer against the source documents."
        )
    }