
from backend.pdf_loader import load_pdf
from backend.chunker import chunk_pages
from backend.hybrid_retriever import (
    build_bm25_index,
    hybrid_search
)
from backend.answer_generator import generate_answer

pages = load_pdf("data/documents/sample.pdf")
chunks = chunk_pages(pages)

bm25 = build_bm25_index(chunks)

query = "What are the main legal provisions in this document?"

retrieved_chunks = hybrid_search(
    query,
    chunks,
    bm25,
    limit=5
)

answer = generate_answer(query, retrieved_chunks)

print("\nQUESTION:")
print(query)

print("\nGEMINI ANSWER:")
print(answer)
