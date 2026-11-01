import re
from rank_bm25 import BM25Okapi

from backend.embedder import generate_embeddings
from backend.vector_store import search_chunks


# Plain function words only. Legal-meaning words (shall, may, not, no, any,
# all, unless, except, if, either, neither) are intentionally NOT listed.
STOPWORDS = {
    "a", "an", "the", "of", "to", "in", "on", "at", "by", "for", "from",
    "with", "and", "or", "is", "are", "was", "were", "be", "been", "being",
    "it", "its", "this", "that", "these", "those", "as", "what", "which",
    "who", "whom", "how", "do", "does", "did", "i", "you", "we", "they",
    "he", "she", "there", "their", "his", "her"
}


def tokenize(text):
    tokens = re.findall(r"\b\w+\b", text.lower())
    return [token for token in tokens if token not in STOPWORDS]

def build_bm25_index(chunks):
    tokenized_chunks = [
        tokenize(chunk["text"]) for chunk in chunks
    ]

    return BM25Okapi(tokenized_chunks)

def hybrid_search(query, chunks, bm25, limit=5):

    query_tokens = tokenize(query)

    bm25_scores = bm25.get_scores(query_tokens)

    # Keyword ranking: ignore chunks with no keyword match at all
    keyword_results = [
        i for i in sorted(
            range(len(bm25_scores)),
            key=lambda i: bm25_scores[i],
            reverse=True
        )[:limit]
        if bm25_scores[i] > 0
    ]

    query_embedding = generate_embeddings([query])[0]

    semantic_results = search_chunks(
        query_embedding,
        limit=limit
    )

    semantic_scores = {
        result.payload["chunk_id"]: float(result.score)
        for result in semantic_results
    }

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
            "score": score,
            "bm25_score": float(bm25_scores[chunk_id]),
            "semantic_score": semantic_scores.get(chunk_id, 0.0)
        }
        for chunk_id, score in ranked_chunks[:limit]
    ]

