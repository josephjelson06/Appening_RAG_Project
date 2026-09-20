"""Embed chunked documents and upsert them into Pinecone."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pinecone import Pinecone, ServerlessSpec


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNKS_PATH = PROJECT_ROOT / "data" / "artifacts" / "03_chunked" / "chunks.jsonl"


def required(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_chunks():
    with CHUNKS_PATH.open(encoding="utf-8") as source:
        return [json.loads(line) for line in source if line.strip()]


def embedder():
    return genai.Client(api_key=required("GOOGLE_API_KEY"))


def embed_documents(client, texts):
    response = client.models.embed_content(
        model=required("EMBEDDING_MODEL"),
        contents=texts,
        config=types.EmbedContentConfig(
            output_dimensionality=int(os.getenv("EMBEDDING_DIMENSION", "3072"))
        ),
    )
    return [embedding.values for embedding in response.embeddings]


def ensure_index(pc, index_name, dimension):
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric=os.getenv("PINECONE_METRIC", "cosine"),
            spec=ServerlessSpec(
                cloud=os.getenv("PINECONE_CLOUD", "aws"),
                region=required("PINECONE_REGION"),
            ),
        )
    return pc.Index(index_name)


def main():
    load_dotenv(PROJECT_ROOT / ".env")
    chunks = load_chunks()
    if not chunks:
        raise RuntimeError("No chunks found. Run chunk_documents.py first.")

    batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "64"))
    embedding_client = embedder()
    pinecone = Pinecone(api_key=required("PINECONE_API_KEY"))
    index_name = required("PINECONE_INDEX_NAME")
    namespace = os.getenv("PINECONE_NAMESPACE", "agentic-ai-book")

    first_batch = chunks[:batch_size]
    first_embeddings = embed_documents(
        embedding_client, [item["text"] for item in first_batch]
    )
    index = ensure_index(pinecone, index_name, len(first_embeddings[0]))

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        embeddings = (
            first_embeddings
            if start == 0
            else embed_documents(embedding_client, [item["text"] for item in batch])
        )
        vectors = [
            {
                "id": item["id"],
                "values": embedding,
                "metadata": {**item["metadata"], "text": item["text"]},
            }
            for item, embedding in zip(batch, embeddings)
        ]
        index.upsert(vectors=vectors, namespace=namespace)
        print(f"Upserted {min(start + batch_size, len(chunks))}/{len(chunks)} chunks")

    print(f"Completed Pinecone ingestion in namespace: {namespace}")


if __name__ == "__main__":
    main()
