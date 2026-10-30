import re
from rank_bm25 import BM25Okapi

from backend.embedder import generate_embeddings
from backend.vector_store import search_chunks


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def build_bm25_index(chunks):
    tokenized_chunks = [
        tokenize(chunk["text"]) for chunk in chunks
    ]

    return BM25Okapi(tokenized_chunks)


def hybrid_search(query, chunks, bm25, limit=5):

    query_tokens = tokenize(query)

    bm25_scores = bm25.get_scores(query_tokens)

    keyword_results = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True
    )[:limit]

    query_embedding = generate_embeddings([query])[0]

    semantic_results = search_chunks(
        query_embedding,
        limit=limit
    )

    rrf_scores = {}
    k = 60

    for rank, chunk_id in enumerate(keyword_results):
        rrf_scores[chunk_id] = (
            rrf_scores.get(chunk_id, 0) + 1 / (k + rank + 1)
        )

    for rank, result in enumerate(semantic_results):
        chunk_id = result.payload["chunk_id"]

        rrf_scores[chunk_id] = (
            rrf_scores.get(chunk_id, 0) + 1 / (k + rank + 1)
        )

    ranked_chunks = sorted(
        rrf_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return [
        {
            **chunks[chunk_id],
            "score": score
        }
        for chunk_id, score in ranked_chunks[:limit]
    ]