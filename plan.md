# Project Plan and Status

## Completed architecture

The repository is organized into four concerns:

1. **Ingestion** — extract page text and tables, clean source-specific noise,
   attach chapter/section/page metadata, create chunks, embed, and index them.
2. **Application** — retrieve Pinecone context and generate grounded answers
   through the LangGraph workflow.
3. **Evaluation** — run retrieval and generation evaluations and create JSON and
   Markdown reports.
4. **Presentation** — expose the application through FastAPI and Streamlit.

## Primary commands

```powershell
python .\run_pipeline.py
python .\run_server.py
streamlit run ui/streamlit_app.py
python .\scripts\run_evaluation.py
```

## Current workflow

```text
data/raw/Ebook-Agentic-AI.pdf
        |
        +--> rag.ingestion.extractor.extract_pages()
        |       educational text, without accepted table regions
        |
        +--> rag.ingestion.extractor.extract_tables()
                validated tables, page-52 color labels
                         |
                         v
                  rag.ingestion.chunker
                         |
                         v
                  rag.ingestion.indexer
                         |
                         v
                       Pinecone
```

The application path is:

```text
FastAPI -> LangGraph -> retrieve -> generate -> validate -> sources
```

## Verification status

- Local extraction and chunking produce 59 non-empty chunks.
- Page and table content remain separate.
- API routes are `/health`, `/retrieve`, and `/generate`.
- Evaluation artifacts are stored under `data/evaluation_results/outputs/`.
- Live Pinecone and Groq calls are intentionally not part of local smoke checks.

## Deliberately out of scope

Authentication, accounts, conversation memory, background jobs, deployment
infrastructure, and complex external tools are not required for this interview
project.
