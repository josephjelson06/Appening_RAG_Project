"""Embed chunks and upsert them into Pinecone."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from agentic_rag.ingestion.indexer import main


if __name__ == "__main__":
    main()
