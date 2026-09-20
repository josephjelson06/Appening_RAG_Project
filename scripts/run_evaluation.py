"""Run retrieval and generation evaluation, then build the Markdown report."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.generation import main as evaluate_generation
from evaluation.report import build_report
from evaluation.retrieval import main as evaluate_retrieval
from rag.config import PATHS


def main():
    print("=== Evaluating retrieval ===")
    evaluate_retrieval()
    print("\n=== Evaluating generation ===")
    evaluate_generation()
    build_report(
        PATHS.evaluation_outputs_dir / "retrieval_report.json",
        PATHS.evaluation_outputs_dir / "generation_report.json",
        PATHS.evaluation_outputs_dir / "evaluation_report.md",
    )
    print(f"\nEvaluation completed. Reports are in {PATHS.evaluation_outputs_dir}.")


if __name__ == "__main__":
    main()
