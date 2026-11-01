from pathlib import Path

from backend.pdf_loader import load_pdf
from backend.chunker import chunk_pages
from backend.embedder import generate_embeddings
from backend.vector_store import (
    reset_collection,
    store_chunks,
    close_vector_store
)
from backend.chunk_store import save_chunks

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "data" / "documents"


def index_documents():
    pdf_paths = sorted(DOCUMENTS_DIR.glob("*.pdf"))
    all_chunks = []

    for pdf_path in pdf_paths:
        print(f"Processing: {pdf_path.name}")

        pages = load_pdf(str(pdf_path))
        chunks = chunk_pages(pages)

        for chunk in chunks:
            chunk["chunk_id"] = len(all_chunks)
            chunk["source"] = pdf_path.name
            all_chunks.append(chunk)

    if not all_chunks:
        raise ValueError("No PDF documents or text chunks found.")

    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = generate_embeddings(texts)

    # Rebuild Qdrant from scratch so no stale points remain
    reset_collection()
    store_chunks(all_chunks, embeddings)

    # Persist the exact same chunks so BM25 can be rebuilt identically
    save_chunks(all_chunks)

    print(f"\nSuccessfully indexed {len(all_chunks)} chunks.")
    print(f"Documents processed: {len(pdf_paths)}")


if __name__ == "__main__":
    try:
        index_documents()
    finally:
        close_vector_store()