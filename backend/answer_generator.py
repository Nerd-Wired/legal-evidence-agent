import os
from functools import lru_cache

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")

    return genai.Client(api_key=api_key)


def generate_answer(
    query: str,
    retrieved_chunks: list[dict],
    feedback: str = ""
) -> str:

    context = ""

    for i, chunk in enumerate(retrieved_chunks, start=1):
        context += f"""
[Source {i} | File: {chunk['source']} | Page {chunk['page_number']}]
{chunk['text']}
"""

    retry_note = ""

    if feedback:
        retry_note = f"""
CORRECTION REQUIRED:
Your previous answer had citation problems: {feedback}
Rewrite the answer and fix them.
"""

    prompt = f"""
You are a precise legal document analysis assistant.

Answer the user's question using ONLY the provided document evidence.

Rules:
1. Never invent facts, legal provisions, or case details.
2. Cite every factual claim as [filename, Page N], copying the filename
   and page exactly from the source headers. Example: [contract.pdf, Page 2].
3. Use one bracket per citation. Write [a.pdf, Page 1] [a.pdf, Page 2],
   never [a.pdf, Page 1, 2] or [Page 1].
4. Only cite filename and page combinations present in the supplied sources.
5. If evidence is insufficient, explicitly say so.
6. Distinguish documented facts from interpretations.
7. Do not present your response as professional legal advice.
8. If sources conflict, identify the conflict instead of choosing
   one without justification.

DOCUMENT EVIDENCE:
{context}

USER QUESTION:
{query}
{retry_note}
Provide a clear, structured answer.
"""

    response = get_client().models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return response.text