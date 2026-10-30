from backend.pdf_loader import load_pdf

pages = load_pdf("data/documents/sample.pdf")

print(f"Total pages extracted: {len(pages)}")

for page in pages[:2]:
    print(f"\nPage {page['text']}:")
    print(page["text"][:500])