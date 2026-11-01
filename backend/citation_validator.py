import re

# Strict format: [filename.pdf, Page 3]
CITATION_PATTERN = re.compile(r"\[([^\[\],]+?),\s*Page\s+(\d+)\]")

# Anything bracketed that mentions "Page", well-formed or not
ANY_PAGE_BRACKET = re.compile(r"\[[^\[\]]*\bPages?\b[^\[\]]*\]", re.IGNORECASE)


def validate_citations(answer: str, chunks: list[dict]) -> dict:
    allowed = {
        (chunk["source"], chunk["page_number"])
        for chunk in chunks
    }

    cited = [
        (source.strip(), int(page))
        for source, page in CITATION_PATTERN.findall(answer)
    ]

    malformed = len(ANY_PAGE_BRACKET.findall(answer)) - len(cited)
    invalid = sorted({c for c in cited if c not in allowed})

    return {
        "valid": bool(cited) and not invalid and malformed == 0,
        "cited": cited,
        "invalid": invalid,
        "malformed": malformed
    }


def build_feedback(result: dict) -> str:
    problems = []

    if not result["cited"] and not result["malformed"]:
        problems.append("Your answer contained no citations.")

    if result["malformed"]:
        problems.append(
            f"{result['malformed']} citation(s) were not in the exact format "
            "[filename, Page N], with one source per bracket."
        )

    if result["invalid"]:
        bad = ", ".join(f"[{s}, Page {p}]" for s, p in result["invalid"])
        problems.append(
            f"These citations do not match any supplied source: {bad}."
        )

    return " ".join(problems)