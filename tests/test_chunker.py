from backend.chunker import chunk_pages, is_heading


def page(number, text):
    return {"page_number": number, "text": text}


def test_numbered_titles_are_headings_but_list_items_are_not():
    assert is_heading("3. Contract Value and Payment Terms")
    assert not is_heading("1. Use Client data only for the agreed services.")
    assert not is_heading("30% advance payment upon signing: INR 72,000.")


def test_splits_into_one_chunk_per_clause():
    chunks = chunk_pages([
        page(1, "Preamble text\n1. Scope\nDo the work.\n2. Timeline\nBy October.")
    ])

    assert [c["clause"] for c in chunks] == ["", "1. Scope", "2. Timeline"]


def test_chunk_text_starts_with_its_clause_heading():
    chunks = chunk_pages([page(1, "1. Scope\nDo the work.")])

    assert chunks[0]["text"] == "1. Scope\nDo the work."


def test_clause_continuing_on_next_page_keeps_its_heading_and_page():
    chunks = chunk_pages([
        page(1, "9. Termination\nEither party may terminate."),
        page(2, "Confidentiality survives termination.\n10. Force Majeure\nEvents beyond control."),
    ])

    continuation = chunks[1]

    assert continuation["page_number"] == 2
    assert continuation["clause"] == "9. Termination"
    assert continuation["text"].startswith("9. Termination\n")


def test_repeated_footers_are_removed():
    pages = [
        page(1, "1. Scope\nDo the work.\nAcme Agreement\nPage 1 of 2"),
        page(2, "2. Timeline\nBy October.\nAcme Agreement\nPage 2 of 2"),
    ]

    text = " ".join(c["text"] for c in chunk_pages(pages))

    assert "Acme Agreement" not in text
    assert "Page 1 of 2" not in text
    assert "Do the work." in text


def test_long_clause_is_split_on_line_boundaries():
    lines = [f"Line {i} " + "x" * 40 for i in range(30)]

    chunks = chunk_pages(
        [page(1, "1. Big Clause\n" + "\n".join(lines))],
        max_chars=300
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert chunk["clause"] == "1. Big Clause"
        assert chunk["text"].startswith("1. Big Clause\n")

        for line in chunk["text"].splitlines()[1:]:
            assert line in lines