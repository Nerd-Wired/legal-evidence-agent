import sys
import types

import pytest

# Replace the heavy modules BEFORE the agent code imports them, so tests never
# load the embedding model or open the on-disk Qdrant store.
_embedder = types.ModuleType("backend.embedder")
_embedder.generate_embeddings = lambda texts: [[0.0, 0.0, 0.0] for _ in texts]
sys.modules["backend.embedder"] = _embedder

_vector_store = types.ModuleType("backend.vector_store")
_vector_store.search_chunks = lambda *args, **kwargs: []
_vector_store.close_vector_store = lambda: None
sys.modules["backend.vector_store"] = _vector_store

import backend.agent.nodes as nodes  # noqa: E402


@pytest.fixture(autouse=True)
def clean_store():
    """Every test starts and ends with an empty in-memory document store."""
    nodes.set_document_store([])
    yield
    nodes.set_document_store([])