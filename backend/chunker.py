import re
from collections import Counter

# A clause heading is a short numbered line with no sentence punctuation,
# e.g. "3. Contract Value and Payment Terms". List items such as
# "1. Use Client data only for the agreed services." end in a period,
# so they are not treated as headings.
HEADING_PATTERN = re.compile(r"^\d{1,2}\.\s+[A-Z][^.\n]{2,80}$")


def is_heading(line: str) -> bool:
    return bool(HEADING_PATTERN.match(line))


def normalize(line: str) -> str:
    # "Page 1 of 2" and "Page 2 of 2" must compare equal
    return re.sub(r"\d+", "#", line)


def page_lines(page: dict) -> list[str]:
    return [line.strip() for line in page["text"].splitlines() if line.strip()]


def strip_repeated_edges(pages: list[dict]) -> list[dict]:
    """Drop running headers/footers: lines near a page edge that repeat across pages."""
    if len(pages) < 2:
        return pages

    counts = Counter()

    for page in pages:
        lines = page_lines(page)
        counts.update({normalize(line) for line in lines[:2] + lines[-2:]})

    repeated = {line for line, n in counts.items() if n >= 2}

    cleaned = []

    for page in pages:
        lines = page_lines(page)
        total = len(lines)

        kept = [
            line for i, line in enumerate(lines)
            if not ((i < 2 or i >= total - 2) and normalize(line) in repeated)
        ]

        cleaned.append({**page, "text": "\n".join(kept)})

    return cleaned


def split_long_section(lines: list[str], max_chars: int) -> list[str]:
    """Pack whole lines into pieces of at most max_chars; never cuts mid-line."""
    pieces = []
    current = []
    size = 0

    for line in lines:
        if current and size + len(line) + 1 > max_chars:
            pieces.append("\n".join(current))
            current = []
            size = 0

        current.append(line)
        size += len(line) + 1

    if current:
        pieces.append("\n".join(current))

    return pieces


def chunk_pages(pages: list[dict], max_chars: int = 1200) -> list[dict]:
    chunks = []
    carried_heading = ""  # a clause that continues on the next page keeps its heading

    for page in strip_repeated_edges(pages):
        sections = []
        heading = carried_heading
        body = []

        for line in page_lines(page):
            if is_heading(line):
                sections.append((heading, body))
                heading = line
                body = []
            else:
                body.append(line)

        sections.append((heading, body))
        carried_heading = heading

        for section_heading, lines in sections:
            if not lines:
                continue

            for piece in split_long_section(lines, max_chars):
                text = f"{section_heading}\n{piece}" if section_heading else piece

                chunks.append({
                    "page_number": page["page_number"],
                    "text": text,
                    "clause": section_heading
                })

    return chunks