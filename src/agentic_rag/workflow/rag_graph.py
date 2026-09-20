"""LangGraph workflow for retrieve -> generate -> validate RAG."""

import os
from typing import Any, TypedDict

from groq import Groq
from langgraph.graph import END, START, StateGraph

from ..retrieval.retriever import retrieve


class RAGState(TypedDict, total=False):
    question: str
    retrieved_chunks: list[dict[str, Any]]
    answer: str
    sources: list[dict[str, Any]]
    grounded: bool
    validation_note: str


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


def retrieve_node(state: RAGState) -> RAGState:
    return {"retrieved_chunks": retrieve(state["question"])}


def generate_node(state: RAGState) -> RAGState:
    results = state.get("retrieved_chunks", [])
    if not results:
        return {"answer": "I could not find sufficiently relevant information in the book.", "sources": []}

    prompt = f"""You answer questions using only the provided excerpts from the book Agentic AI for Executives.

Rules:
- Do not use outside knowledge.
- If the excerpts do not support the answer, say so clearly.
- Explain the answer in plain language.
- Cite supporting sources using their exact labels, for example [Source 1].
- Do not invent page numbers, sections, or claims.

Question:
{state['question']}

Book excerpts:
{format_context(results)}
"""
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=os.environ.get("GENERATION_MODEL", "qwen/qwen3.8-27b"),
        messages=[
            {"role": "system", "content": "You are a precise book-grounded RAG assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=700,
    )
    sources = [
        {"id": result["id"], "score": result["score"], "metadata": result["metadata"]}
        for result in results
    ]
    return {"answer": response.choices[0].message.content, "sources": sources}


def validate_node(state: RAGState) -> RAGState:
    answer = state.get("answer", "")
    sources = state.get("sources", [])
    grounded = bool(sources) and "[Source" in answer
    return {
        "grounded": grounded,
        "validation_note": (
            "Answer includes retrieved sources and source citations."
            if grounded else "No supported answer citation was detected."
        ),
    }


def build_graph():
    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("validate", validate_node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "validate")
    graph.add_edge("validate", END)
    return graph.compile()


rag_graph = build_graph()


def run_rag_graph(question: str) -> dict:
    state = rag_graph.invoke({"question": question})
    return {
        "answer": state.get("answer", ""),
        "sources": state.get("sources", []),
        "grounded": state.get("grounded", False),
        "validation_note": state.get("validation_note", ""),
    }
