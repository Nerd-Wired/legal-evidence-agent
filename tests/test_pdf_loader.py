import pymupdf

from backend.pdf_loader import load_pdf


def make_pdf(path, page_texts):
    document = pymupdf.open()

    for text in page_texts:
        page = document.new_page()

        if text:
            page.insert_text((72, 72), text)

    document.save(str(path))
    document.close()


def test_pages_are_numbered_from_one(tmp_path):
    path = tmp_path / "two_pages.pdf"
    make_pdf(path, ["First page", "Second page"])

    pages = load_pdf(str(path))

    assert [p["page_number"] for p in pages] == [1, 2]
    assert "First page" in pages[0]["text"]


def test_blank_pages_are_skipped_but_numbering_is_kept(tmp_path):
    path = tmp_path / "gap.pdf"
    make_pdf(path, ["First page", "", "Third page"])

    pages = load_pdf(str(path))

    assert [p["page_number"] for p in pages] == [1, 3]