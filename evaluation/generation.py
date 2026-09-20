"""Evaluate generated answers against the manual RAG evaluation set."""

import json
import re

from rag.config import PATHS
from rag.generation.generator import answer


QUESTIONS_PATH = PATHS.evaluation_dir / "questions.json"
REPORT_PATH = PATHS.evaluation_outputs_dir / "generation_report.json"

ALIASES = {
    "autonomous decision-making": ["autonom", "independent decision"],
    "acts toward goals": ["goal", "objective"],
    "proactive behavior": ["proactive", "anticipat"],
    "decision-making": ["decision", "choice"],
    "language understanding": ["language", "natural language"],
    "workflow optimization": ["workflow", "process optimization"],
    "data maturity": ["data maturity", "data infrastructure"],
    "technology infrastructure": ["technology infrastructure", "tech infrastructure"],
    "talent availability": ["talent", "skills"],
    "regulatory adaptability": ["regulatory", "regulation"],
}


def normalized(text):
    return re.sub(r"\s+", " ", text.lower())


def point_supported(answer_text, point):
    text = normalized(answer_text)
    candidates = ALIASES.get(point.lower(), [point.lower()])
    return any(candidate in text for candidate in candidates)


def evaluate_item(item):
    try:
        result = answer(item["question"])
    except Exception as exc:
        return {
            "id": item["id"],
            "question": item["question"],
            "answerable": item["answerable"],
            "error": f"{type(exc).__name__}: {exc}",
            "answer": "",
            "supported_answer_points": [],
            "answer_point_coverage": None,
            "refusal_detected": False,
            "sources": [],
        }

    answer_text = result["answer"] or ""
    points = item.get("answer_points", [])
    supported_points = [point for point in points if point_supported(answer_text, point)]
    refusal_text = normalized(answer_text)
    refusal = any(
        phrase in refusal_text
        for phrase in (
            "could not find",
            "not found in the book",
            "not covered in the book",
            "does not mention",
            "no information",
        )
    )

    return {
        "id": item["id"],
        "question": item["question"],
        "answerable": item["answerable"],
        "answer": answer_text,
        "supported_answer_points": supported_points,
        "answer_point_coverage": len(supported_points) / len(points) if points else None,
        "refusal_detected": refusal,
        "sources": result["sources"],
    }


def main():
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    results = []

    for index, item in enumerate(questions, start=1):
        print(f"[{index}/{len(questions)}] {item['id']}: {item['question']}")
        results.append(evaluate_item(item))

    answerable = [item for item in results if item["answerable"]]
    coverage_values = [
        item["answer_point_coverage"]
        for item in answerable
        if item["answer_point_coverage"] is not None
    ]
    unanswerable = [item for item in results if not item["answerable"]]

    report = {
        "total_questions": len(results),
        "answerable_questions": len(answerable),
        "average_answer_point_coverage": sum(coverage_values) / len(coverage_values) if coverage_values else 0,
        "unanswerable_refusal_rate": (
            sum(item["refusal_detected"] for item in unanswerable) / len(unanswerable)
            if unanswerable
            else 0
        ),
        "manual_review_required": True,
        "results": results,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, indent=2))
    print(f"Saved report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
