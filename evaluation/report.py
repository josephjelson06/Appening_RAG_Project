"""Build a reviewer-friendly Markdown summary from evaluation JSON outputs."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _percent(value: Any) -> str:
    if value is None:
        return "N/A"
    return f"{float(value) * 100:.1f}%"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(
    retrieval_path: Path,
    generation_path: Path,
    output_path: Path,
) -> None:
    """Create a concise Markdown report from retrieval and generation reports."""
    retrieval = _load_json(retrieval_path)
    generation = _load_json(generation_path)

    retrieval_results = retrieval.get("results", [])
    retrieval_misses = [
        item["id"]
        for item in retrieval_results
        if item.get("answerable") and not item.get("hit_at_k")
    ]
    generation_results = generation.get("results", [])
    generation_errors = [
        item["id"] for item in generation_results if item.get("error")
    ]

    lines = [
        "# Evaluation Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "This report summarizes the current fixed-question evaluation set. "
        "The JSON files beside this report contain per-question evidence and sources.",
        "",
        "## Retrieval",
        "",
        "| Metric | Result |",
        "| --- | ---: |",
        f"| Total questions | {retrieval.get('total_questions', 'N/A')} |",
        f"| Answerable questions | {retrieval.get('answerable_questions', 'N/A')} |",
        f"| Answerable hit@k | {_percent(retrieval.get('answerable_hit_at_k'))} |",
        f"| Answerable page hit@k | {_percent(retrieval.get('answerable_page_hit_at_k'))} |",
        f"| Answerable evidence hit@k | {_percent(retrieval.get('answerable_evidence_hit_at_k'))} |",
        f"| Relevant top result accuracy | {_percent(retrieval.get('answerable_top_result_accuracy'))} |",
        "",
        "`hit@k` means that at least one relevant chunk appeared in the retrieved top-k. "
        "The individual result scores are Pinecone similarity scores; they are not calibrated confidence probabilities.",
        "",
        f"Known answerable retrieval misses: {', '.join(retrieval_misses) if retrieval_misses else 'None'}.",
        "",
        "## Generation",
        "",
        "| Metric | Result |",
        "| --- | ---: |",
        f"| Average answer-point coverage | {_percent(generation.get('average_answer_point_coverage'))} |",
        f"| Unanswerable refusal rate | {_percent(generation.get('unanswerable_refusal_rate'))} |",
        f"| Generation errors | {len(generation_errors)} |",
        "",
        "Answer-point coverage is a heuristic evaluator metric: it measures how many "
        "manually defined expected concepts were detected in an answer. It is not a truth guarantee or model confidence score.",
        "",
        f"Generation errors: {', '.join(generation_errors) if generation_errors else 'None'}.",
        "",
        "## Interpretation and limitations",
        "",
        "- Retrieval and generation are evaluated separately so failures can be diagnosed as retrieval, generation, or both.",
        "- The evaluation set is intentionally small and should be expanded with more section, table, boundary, and unanswerable questions before making production claims.",
        "- Scores and heuristic coverage should be reviewed alongside the returned source chunks and page metadata.",
        "- The generation evaluator uses the configured Groq model, so transient provider errors can affect a run.",
        "",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

