from pathlib import Path

from backend.pdf_loader import load_pdf
from backend.chunker import chunk_pages
from backend.embedder import generate_embeddings
from backend.vector_store import create_collection, store_chunks
from backend.agent.nodes import set_document_store

DOCUMENTS_DIR = Path("data/documents")


def index_documents():
    all_chunks = []

    for pdf_path in DOCUMENTS_DIR.glob("*.pdf"):
        print(f"Processing: {pdf_path.name}")

        pages = load_pdf(str(pdf_path))
        chunks = chunk_pages(pages)

        for chunk in chunks:
            chunk["chunk_id"] = len(all_chunks)
            chunk["source"] = pdf_path.name
            all_chunks.append(chunk)

    if not all_chunks:
        raise ValueError("No PDF documents or text chunks found.")

    # Generate embeddings
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = generate_embeddings(texts)

    # Store in Qdrant
    create_collection()
    store_chunks(all_chunks, embeddings)

    # Initialize BM25
    set_document_store(all_chunks)

    print(f"\nSuccessfully indexed {len(all_chunks)} chunks.")
    print(f"Documents processed: {len(list(DOCUMENTS_DIR.glob('*.pdf')))}")


if __name__ == "__main__":
    index_documents()