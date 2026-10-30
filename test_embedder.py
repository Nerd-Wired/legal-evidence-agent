from backend.pdf_loader import load_pdf
from backend.chunker import chunk_pages
from backend.embedder import generate_embeddings

pages = load_pdf("data/documents/sample.pdf")
chunks = chunk_pages(pages)

texts = [chunk["text"] for chunk in chunks]

embeddings = generate_embeddings(texts)

print("Total chunks:", len(chunks))
print("Total embeddings:", len(embeddings))
print("Embedding dimensions:", len(embeddings[0]))
print("First embedding:", embeddings[0][:5])