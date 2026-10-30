from backend.agent.state import AgentState
from backend.hybrid_retriever import hybrid_search, build_bm25_index
from backend.answer_generator import generate_answer


# Temporary in-memory document storage
document_chunks = []
bm25_index = None


def set_document_store(chunks):
    global document_chunks, bm25_index

    document_chunks = chunks
    bm25_index = build_bm25_index(chunks)


def retrieve_evidence(state: AgentState):
    if not document_chunks or bm25_index is None:
        return {
            "retrieved_chunks": [],
            "error": "No documents have been indexed."
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
    retrieved_chunks = state.get("retrieved_chunks", [])

    usable_chunks = [
        chunk for chunk in retrieved_chunks
        if chunk.get("text", "").strip()
    ]

    if not usable_chunks:
        return {
            "evidence_sufficient": False,
            "error": "Insufficient evidence to answer the question."
        }

    return {
        "evidence_sufficient": True,
        "error": ""
    }


def generate_response(state: AgentState):
    try:
        answer = generate_answer(
            query=state["question"],
            retrieved_chunks=state["retrieved_chunks"]
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