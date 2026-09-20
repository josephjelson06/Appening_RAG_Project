"""Build the complete RAG index from the source PDF."""

from rag.config import PATHS
from rag.ingestion.chunker import build_chunks, write_chunks
from rag.ingestion.extractor import extract_pages, extract_tables
from rag.ingestion.indexer import main as index_chunks


def main():
    if not PATHS.source_pdf.exists():
        raise FileNotFoundError(
            f"Source PDF not found at {PATHS.source_pdf}. Place the book there first."
        )

    print("=== Extracting page text ===")
    extract_pages()
    print("\n=== Extracting tables ===")
    extract_tables()
    print("\n=== Building chunks ===")
    chunks = build_chunks()
    write_chunks(chunks)
    print(f"Wrote {len(chunks)} chunks to {PATHS.chunks_file}")
    print("\n=== Indexing chunks in Pinecone ===")
    index_chunks()
    print("\nRAG pipeline completed successfully.")


if __name__ == "__main__":
    main()
