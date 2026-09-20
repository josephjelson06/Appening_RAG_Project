"""Evaluate Pinecone retrieval against manually verified expected evidence."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from agentic_rag.retrieve import retrieve


QUESTIONS_PATH = PROJECT_ROOT / "evaluation" / "questions.json"
REPORT_PATH = PROJECT_ROOT / "evaluation" / "retrieval_report.json"


def evaluate_question(item):
    results = retrieve(item["question"])
    expected_pages = set(item.get("expected_pdf_pages", []))
    expected_types = set(item.get("expected_content_types", []))
    expected_sections = item.get("expected_sections", [])

    hits = []
    for result in results:
        metadata = result["metadata"]
        page_hit = metadata.get("pdf_page") in expected_pages
        type_hit = not expected_types or metadata.get("content_type") in expected_types
        section_text = str(metadata.get("section", ""))
        section_hit = not expected_sections or any(
            section_text.startswith(section_prefix)
            for section_prefix in expected_sections
        )
        hits.append(
            {
                "id": result["id"],
                "score": result["score"],
                "pdf_page": metadata.get("pdf_page"),
                "content_type": metadata.get("content_type"),
                "section": metadata.get("section"),
                "page_hit": page_hit,
                "type_hit": type_hit,
                "section_hit": section_hit,
                "relevant": page_hit and type_hit and section_hit,
            }
        )

    relevant = [hit for hit in hits if hit["relevant"]]
    page_relevant = [hit for hit in hits if hit["page_hit"]]
    evidence_relevant = [
        hit for hit in hits if hit["page_hit"] and hit["type_hit"]
    ]
    return {
        "id": item["id"],
        "question": item["question"],
        "answerable": item["answerable"],
        "retrieved_count": len(hits),
        "hit_at_k": bool(relevant),
        "page_hit_at_k": bool(page_relevant),
        "evidence_hit_at_k": bool(evidence_relevant),
        "top_result_relevant": bool(hits and hits[0]["relevant"]),
        "results": hits,
    }


def main():
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    report = []
    for index, question in enumerate(questions, start=1):
        print(f"[{index}/{len(questions)}] {question['id']}: {question['question']}")
        report.append(evaluate_question(question))

    answerable = [item for item in report if item["answerable"]]
    positive_hits = sum(item["hit_at_k"] for item in answerable)
    page_hits = sum(item["page_hit_at_k"] for item in answerable)
    evidence_hits = sum(item["evidence_hit_at_k"] for item in answerable)
    top_hits = sum(item["top_result_relevant"] for item in answerable)

    summary = {
        "total_questions": len(report),
        "answerable_questions": len(answerable),
        "answerable_hit_at_k": positive_hits / len(answerable) if answerable else 0,
        "answerable_page_hit_at_k": page_hits / len(answerable) if answerable else 0,
        "answerable_evidence_hit_at_k": evidence_hits / len(answerable) if answerable else 0,
        "answerable_top_result_accuracy": top_hits / len(answerable) if answerable else 0,
        "results": report,
    }
    REPORT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "results"}, indent=2))
    print(f"Saved report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
