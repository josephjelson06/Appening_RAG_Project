"""Public generation entry point backed by the LangGraph RAG workflow."""

import sys

from ..workflow.rag_graph import run_rag_graph


def answer(question):
    return run_rag_graph(question)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit('Usage: python -m agentic_rag.generation.generator "your question"')

    result = answer(question)
    print(result["answer"])
    print(f"\nGrounded: {result['grounded']}")
    print(f"Validation: {result['validation_note']}")
    print("\nSources:")
    for source in result["sources"]:
        metadata = source["metadata"]
        print(
            f"- {source['score']:.3f}: PDF page {metadata.get('pdf_page')}, "
            f"in-book page {metadata.get('in_book_page')}, "
            f"{metadata.get('chapter')}, {metadata.get('section')}"
        )
