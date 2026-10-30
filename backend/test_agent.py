
from pathlib import Path

from backend.pdf_loader import load_pdf
from backend.chunker import chunk_pages
from backend.agent.nodes import set_document_store
from backend.agent.graph import build_agent
from backend.vector_store import close_vector_store


def main():
    try:
        # Load the PDF
        pdf_path = Path("data/documents/sample_contract.pdf")
        pages = load_pdf(str(pdf_path))

        # Generate chunks
        chunks = chunk_pages(pages)

        for i, chunk in enumerate(chunks):
            chunk["chunk_id"] = i
            chunk["source"] = pdf_path.name

        # Initialize BM25
        set_document_store(chunks)

        # Build LangGraph agent
        agent = build_agent()

        # Execute query
        result = agent.invoke({
            "question": "What is the total contract value?",
            "retrieved_chunks": [],
            "answer": "",
            "evidence_sufficient": False,
            "citations_valid": False,
            "retry_count": 0,
            "error": ""
        })

        print("\nQUESTION:")
        print(result["question"])

        print("\nANSWER:")
        print(result["answer"])

        print("\nERROR:")
        print(result["error"])

    finally:
        # Explicitly close Qdrant
        close_vector_store()


if __name__ == "__main__":
    main()
