"""Retrieve relevant text/table chunks from the Pinecone index."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pinecone import Pinecone


def required(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def embed_query(client, query):
    response = client.models.embed_content(
        model=required("EMBEDDING_MODEL"),
        contents=query,
        config=types.EmbedContentConfig(
            output_dimensionality=int(os.getenv("EMBEDDING_DIMENSION", "3072")),
        ),
    )
    return response.embeddings[0].values


def retrieve(query):
    load_dotenv(".env")

    google_client = genai.Client(api_key=required("GOOGLE_API_KEY"))
    pinecone = Pinecone(api_key=required("PINECONE_API_KEY"))
    index = pinecone.Index(required("PINECONE_INDEX_NAME"))

    response = index.query(
        namespace=os.getenv("PINECONE_NAMESPACE", "agentic-ai-book"),
        vector=embed_query(google_client, query),
        top_k=int(os.getenv("TOP_K", "5")),
        include_metadata=True,
        include_values=False,
    )

    threshold = float(os.getenv("RELEVANCE_THRESHOLD", "0.35"))
    matches = []
    for match in response.matches:
        score = float(match.score or 0)
        if score < threshold:
            continue
        metadata = dict(match.metadata or {})
        matches.append(
            {
                "id": match.id,
                "score": score,
                "text": metadata.pop("text", ""),
                "metadata": metadata,
            }
        )

    return matches


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")

    question = " ".join(sys.argv[1:]).strip()
    if not question:
        raise SystemExit("Usage: python retrieve.py \"your question\"")

    for result in retrieve(question):
        metadata = result["metadata"]
        print(
            f"\n[{result['score']:.3f}] {result['id']} | "
            f"PDF page {metadata.get('pdf_page')} | "
            f"{metadata.get('chapter')} | {metadata.get('section')}"
        )
        print(result["text"])
