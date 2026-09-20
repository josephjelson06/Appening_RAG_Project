"""Run retrieval and generation evaluation in sequence."""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STEPS = ("05_evaluate_retrieval.py", "06_evaluate_generation.py")


def main():
    for step in STEPS:
        print(f"\n=== Running {step} ===")
        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / step)],
            cwd=PROJECT_ROOT,
            check=True,
        )
    print("\nEvaluation completed. Reports are in evaluation/outputs.")


if __name__ == "__main__":
    main()
