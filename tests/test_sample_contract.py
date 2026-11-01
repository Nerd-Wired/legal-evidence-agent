from pathlib import Path

import pytest

from backend.chunker import chunk_pages
from backend.pdf_loader import load_pdf

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "documents" / "sample_contract.pdf"
EXPECTED_CLAUSES = 13
LIGATURES = set("\ufb00\ufb01\ufb02\ufb03\ufb04")


@pytest.fixture(scope="module")
def pages():
    return load_pdf(str(SAMPLE))


@pytest.fixture(scope="module")
def chunks(pages):
    return chunk_pages(pages)


def test_all_clauses_are_present_in_order(chunks):
    numbers = []

    for chunk in chunks:
        if chunk["clause"]:
            number = int(chunk["clause"].split(".")[0])

            # a clause split across chunks or pages repeats its number
            if not numbers or numbers[-1] != number:
                numbers.append(number)

    assert numbers == list(range(1, EXPECTED_CLAUSES + 1))


def test_every_clause_has_body_text(chunks):
    for chunk in chunks:
        if chunk["clause"]:
            body = chunk["text"][len(chunk["clause"]):].strip()

            assert len(body) > 20, f"clause looks empty: {chunk['clause']}"


def test_no_clipped_glyph_remnants(pages):
    for page in pages:
        for line in page["text"].splitlines():
            stripped = line.strip()

            assert not (len(stripped) == 1 and stripped.isalpha()), (
                f"stray character {stripped!r} on page {page['page_number']}"
            )


def test_no_ligature_characters_remain(chunks):
    assert not any(ch in LIGATURES for chunk in chunks for ch in chunk["text"])


def test_document_ends_with_a_complete_sentence(chunks):
    assert chunks[-1]["text"].rstrip().endswith((".", "!", "?", '"'))


def test_every_page_produces_chunks(pages, chunks):
    assert {c["page_number"] for c in chunks} == {p["page_number"] for p in pages}