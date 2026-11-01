import pytest

import backend.agent.nodes as nodes
from backend.agent.graph import build_agent

CHUNK = {
    "chunk_id": 0,
    "source": "a.pdf",
    "page_number": 1,
    "clause": "1. Fees",
    "text": "1. Fees\nThe fee is 5."
}

# Scores relative to the configured threshold, so the tests survive retuning
LOW = nodes.MIN_SEMANTIC_SCORE - 0.01
HIGH = nodes.MIN_SEMANTIC_SCORE + 0.2


def retrieved(semantic_score):
    return [{
        **CHUNK,
        "score": 0.03,
        "bm25_score": 1.0,
        "semantic_score": semantic_score
    }]


def initial_state():
    return {
        "question": "What is the fee?",
        "retrieved_chunks": [],
        "answer": "",
        "evidence_sufficient": False,
        "citations_valid": False,
        "retry_count": 0,
        "citation_feedback": "",
        "error": ""
    }


@pytest.fixture
def indexed(monkeypatch):
    """Put one chunk in the store and fix what retrieval returns."""
    nodes.set_document_store([CHUNK])

    def set_score(score):
        monkeypatch.setattr(
            nodes, "hybrid_search", lambda **kwargs: retrieved(score)
        )

    return set_score


def fake_generator(monkeypatch, behavior):
    """Replace the Gemini call; returns the list of feedback strings it received."""
    calls = []

    def fake(query, retrieved_chunks, feedback=""):
        calls.append(feedback)
        return behavior(feedback)

    monkeypatch.setattr(nodes, "generate_answer", fake)
    return calls


# ---------- evaluate_evidence ----------

def test_score_below_threshold_is_refused():
    state = {**initial_state(), "retrieved_chunks": retrieved(LOW)}

    result = nodes.evaluate_evidence(state)

    assert result["evidence_sufficient"] is False
    assert result["answer"] == nodes.NO_EVIDENCE_MESSAGE
    assert result["error"] == ""


def test_score_above_threshold_passes():
    state = {**initial_state(), "retrieved_chunks": retrieved(HIGH)}

    assert nodes.evaluate_evidence(state)["evidence_sufficient"] is True


def test_score_exactly_at_threshold_passes():
    state = {
        **initial_state(),
        "retrieved_chunks": retrieved(nodes.MIN_SEMANTIC_SCORE)
    }

    assert nodes.evaluate_evidence(state)["evidence_sufficient"] is True


def test_upstream_error_is_not_masked():
    state = {**initial_state(), "error": "No documents have been indexed."}

    assert nodes.evaluate_evidence(state) == {"evidence_sufficient": False}


# ---------- retrieve_evidence ----------

def test_retrieve_without_an_index_explains_how_to_fix_it(monkeypatch):
    monkeypatch.setattr(nodes, "load_chunks", lambda: [])

    result = nodes.retrieve_evidence(initial_state())

    assert result["retrieved_chunks"] == []
    assert "index_documents" in result["error"]


# ---------- full graph ----------

def run_agent():
    return build_agent().invoke(initial_state())


def test_irrelevant_question_is_refused_without_calling_the_model(indexed, monkeypatch):
    indexed(LOW)
    calls = fake_generator(monkeypatch, lambda feedback: "must never run")

    result = run_agent()

    assert calls == []
    assert result["answer"] == nodes.NO_EVIDENCE_MESSAGE


def test_valid_answer_needs_no_retry(indexed, monkeypatch):
    indexed(HIGH)
    calls = fake_generator(monkeypatch, lambda feedback: "Fee is 5 [a.pdf, Page 1].")

    result = run_agent()

    assert len(calls) == 1
    assert result["citations_valid"] is True
    assert result["retry_count"] == 0


def test_bad_citation_triggers_one_retry_with_feedback(indexed, monkeypatch):
    indexed(HIGH)
    calls = fake_generator(
        monkeypatch,
        lambda feedback: "Fee is 5 [a.pdf, Page 1]." if feedback else "Fee is 5 [Page 1]."
    )

    result = run_agent()

    assert len(calls) == 2
    assert calls[0] == ""
    assert "exact format" in calls[1]
    assert result["citations_valid"] is True
    assert result["retry_count"] == 1


def test_persistent_bad_citations_return_answer_with_warning(indexed, monkeypatch):
    indexed(HIGH)
    calls = fake_generator(monkeypatch, lambda feedback: "Fee is 5 [a.pdf, Page 9].")

    result = run_agent()

    assert len(calls) == 2
    assert result["citations_valid"] is False
    assert result["retry_count"] == 2
    assert "WARNING" in result["answer"]


def test_generation_error_is_reported_without_retry(indexed, monkeypatch):
    indexed(HIGH)

    def explode(feedback):
        raise RuntimeError("Gemini exploded")

    calls = fake_generator(monkeypatch, explode)

    result = run_agent()

    assert len(calls) == 1
    assert "Gemini exploded" in result["error"]
    assert result["citations_valid"] is False