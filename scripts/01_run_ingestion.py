"""Run the complete ingestion and Pinecone indexing pipeline in order."""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = PROJECT_ROOT / "data" / "raw" / "Ebook-Agentic-AI.pdf"
STEPS = (
    "01_extract_pages.py",
    "02_extract_tables.py",
    "03_build_chunks.py",
    "04_index_pinecone.py",
)


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"Source PDF not found at {PDF_PATH}. Place the book there first."
        )

    for step in STEPS:
        print(f"\n=== Running {step} ===")
        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / step)],
            cwd=PROJECT_ROOT,
            check=True,
        )

    print("\nIngestion pipeline completed successfully.")


if __name__ == "__main__":
    main()
