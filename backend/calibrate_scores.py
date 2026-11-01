import backend.agent.nodes as nodes
from backend.hybrid_retriever import hybrid_search
from backend.vector_store import close_vector_store

QUESTIONS = [
    # Questions the contract should be able to answer
    "What is the total contract value?",
    "What are the payment terms?",
    "How can the contract be terminated?",
    # Questions it should NOT be able to answer
    "What is the capital of France?",
    "How do I bake a chocolate cake?",
    "Who won the 2018 football world cup?",
    # Legal-sounding but not in this document
    "What is the penalty for tax evasion in India?",
]


def main():
    try:
        nodes.ensure_document_store()

        print(f"{'semantic':>9} {'bm25':>7}  question")

        for question in QUESTIONS:
            results = hybrid_search(
                question,
                nodes.document_chunks,
                nodes.bm25_index,
                limit=5
            )

            best_semantic = max((r["semantic_score"] for r in results), default=0.0)
            best_bm25 = max((r["bm25_score"] for r in results), default=0.0)

            print(f"{best_semantic:9.3f} {best_bm25:7.2f}  {question}")

    finally:
        close_vector_store()


if __name__ == "__main__":
    main()