import unicodedata

import pymupdf


def load_pdf(file_path: str) -> list[dict]:
    document = pymupdf.open(file_path)
    pages = []

    for page_number, page in enumerate(document, start=1):
        # NFKC turns ligatures such as "ﬁ" into "fi", so keyword search can match them
        text = unicodedata.normalize("NFKC", page.get_text("text")).strip()

        if text:
            pages.append({
                "page_number": page_number,
                "text": text
            })

    document.close()

    return pages