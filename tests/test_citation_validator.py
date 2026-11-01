from backend.citation_validator import validate_citations, build_feedback

CHUNKS = [
    {"source": "a.pdf", "page_number": 1},
    {"source": "a.pdf", "page_number": 2},
]


def test_valid_citations_pass():
    result = validate_citations(
        "Fee is 5 [a.pdf, Page 1] and notice is 30 days [a.pdf, Page 2].",
        CHUNKS
    )

    assert result["valid"]
    assert result["cited"] == [("a.pdf", 1), ("a.pdf", 2)]


def test_citation_to_page_not_retrieved_is_invalid():
    result = validate_citations("Fee is 5 [a.pdf, Page 9].", CHUNKS)

    assert not result["valid"]
    assert result["invalid"] == [("a.pdf", 9)]


def test_citation_to_wrong_file_is_invalid():
    result = validate_citations("Fee is 5 [b.pdf, Page 1].", CHUNKS)

    assert not result["valid"]
    assert result["invalid"] == [("b.pdf", 1)]


def test_old_style_citation_is_malformed():
    result = validate_citations("Fee is 5 [Page 1].", CHUNKS)

    assert not result["valid"]
    assert result["malformed"] == 1


def test_grouped_citation_is_malformed():
    result = validate_citations("Fee is 5 [a.pdf, Page 1, Page 2].", CHUNKS)

    assert not result["valid"]
    assert result["malformed"] == 1


def test_answer_without_citations_is_invalid():
    result = validate_citations("The fee is 5.", CHUNKS)

    assert not result["valid"]
    assert result["cited"] == []


def test_feedback_describes_each_problem():
    result = validate_citations("x [a.pdf, Page 9] y [Page 1]", CHUNKS)
    feedback = build_feedback(result)

    assert "a.pdf, Page 9" in feedback
    assert "exact format" in feedback