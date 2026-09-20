"""Run retrieval and generation evaluation in sequence."""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agentic_rag.evaluation.report import build_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STEPS = ("05_evaluate_retrieval.py", "06_evaluate_generation.py")
RETRIEVAL_REPORT = PROJECT_ROOT / "evaluation" / "outputs" / "retrieval_report.json"
GENERATION_REPORT = PROJECT_ROOT / "evaluation" / "outputs" / "generation_report.json"
MARKDOWN_REPORT = PROJECT_ROOT / "evaluation" / "outputs" / "evaluation_report.md"


def main():
    for step in STEPS:
        print(f"\n=== Running {step} ===")
        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / step)],
            cwd=PROJECT_ROOT,
            check=True,
        )
    build_report(RETRIEVAL_REPORT, GENERATION_REPORT, MARKDOWN_REPORT)
    print(f"\nEvaluation completed. Reports are in {MARKDOWN_REPORT.parent}.")


if __name__ == "__main__":
    main()
