"""Answer questions using retrieved context from the Agentic AI book."""

import os
import sys

from dotenv import load_dotenv
from groq import Groq

from .retrieve import retrieve


def format_context(results):
    sections = []
    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]
        citation = (
            f"Source {index}: PDF page {metadata.get('pdf_page')}, "
            f"in-book page {metadata.get('in_book_page')}, "
            f"{metadata.get('chapter')}, section {metadata.get('section')}"
        )
        if metadata.get("content_type") == "table":
            citation += f", table {metadata.get('table_number')}"
        sections.append(f"{citation}\n{result['text']}")
    return "\n\n---\n\n".join(sections)


def answer(question):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    load_dotenv(os.path.join(project_root, ".env"))
    results = retrieve(question)

    if not results:
        return {
            "answer": "I could not find sufficiently relevant information in the book.",
            "sources": [],
        }

    prompt = f"""You answer questions using only the provided excerpts from the book Agentic AI for Executives.

Rules:
- Do not use outside knowledge.
- If the excerpts do not support the answer, say so clearly.
- Explain the answer in plain language.
- Cite supporting sources using their exact labels, for example [Source 1].
- Do not invent page numbers, sections, or claims.

Question:
{question}

Book excerpts:
{format_context(results)}
"""

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=os.environ.get("GENERATION_MODEL", "qwen/qwen3.8-27b"),
        messages=[
            {
                "role": "system",
                "content": "You are a precise book-grounded RAG assistant.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=700,
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [
            {
                "id": result["id"],
                "score": result["score"],
                "metadata": result["metadata"],
            }
            for result in results
        ],
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit('Usage: python ask.py "your question"')

    result = answer(question)
    print(result["answer"])
    print("\nSources:")
    for source in result["sources"]:
        metadata = source["metadata"]
        print(
            f"- {source['score']:.3f}: PDF page {metadata.get('pdf_page')}, "
            f"in-book page {metadata.get('in_book_page')}, "
            f"{metadata.get('chapter')}, {metadata.get('section')}"
        )
