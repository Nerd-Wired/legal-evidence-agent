
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.8-flash"


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:

    context = ""

    for i, chunk in enumerate(retrieved_chunks, start=1):
        context += f"""
[Source {i} | Page {chunk['page_number']}]
{chunk['text']}
"""

    prompt = f"""
You are a precise legal document analysis assistant.

Answer the user's question using ONLY the provided document evidence.

Rules:
1. Never invent facts, legal provisions, or case details.
2. Cite factual claims using [Page X].
3. Only cite page numbers present in the supplied sources.
4. If evidence is insufficient, explicitly say so.
5. Distinguish documented facts from interpretations.
6. Do not present your response as professional legal advice.
7. If sources conflict, identify the conflict instead of choosing
   one without justification.

DOCUMENT EVIDENCE:
{context}

USER QUESTION:
{query}

Provide a clear, structured answer.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")

    return response.text
