"""Build provenance-aware chunks from cleaned extraction artifacts."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from agentic_rag.ingestion.chunker import OUTPUT, build_chunks


def main():
    chunks = build_chunks()
    with OUTPUT.open("w", encoding="utf-8") as output_file:
        for chunk in chunks:
            output_file.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"Wrote {len(chunks)} chunks to {OUTPUT}")


if __name__ == "__main__":
    main()
