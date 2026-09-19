# Agentic AI Book RAG

A retrieval-augmented generation pipeline built from `Ebook-Agentic-AI.pdf`.
The source is extracted into text and table records, enriched with chapter,
section, PDF-page, and in-book-page provenance, then chunked and indexed in
Pinecone.

## Project layout

```text
src/agentic_rag/   reusable retrieval and generation code
scripts/           extraction, chunking, and Pinecone ingestion commands
data/raw/          source PDF
data/processed/    extracted artifacts and JSONL chunks
tests/             future pipeline tests
```

## Current pipeline

```text
PDF -> text/table extraction -> cleanup -> structured chunks
    -> Gemini embeddings -> Pinecone -> retrieval -> Gemini answer
```

## Setup

```powershell
.\myenv\Scripts\activate
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the provider settings. Never commit
`.env` or API keys.

## Run the data pipeline

```powershell
python .\scripts\Extract_Page.py
python .\scripts\Find_Table.py
python .\scripts\chunk_documents.py
python .\scripts\pinecone_ingest.py
```

## Test retrieval and generation directly

```powershell
$env:PYTHONPATH = "$(Get-Location)\src"
python -m agentic_rag.retrieve "What are the capabilities of Agentic AI?"
python -m agentic_rag.ask "What are the capabilities of Agentic AI?"
```

FastAPI endpoints and a Streamlit interface will be added after retrieval and
generation behavior is stable.
