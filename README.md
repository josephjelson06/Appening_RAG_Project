# Agentic AI Book RAG

A Python RAG application grounded in the *Agentic AI for Executives* ebook.
The system uses PyMuPDF for extraction, Gemini embeddings, Pinecone for vector
search, Groq for generation, LangGraph for orchestration, FastAPI for the API,
and Streamlit for the user interface.

This README is the starting point for a fresh clone. The smaller guides in
`evaluation/`, `ui/`, and the artifact folders provide focused details after
the main setup is complete.

For a complete onboarding walkthrough, read the guides in [`docs/`](docs/):

- [Quick Start](docs/QUICKSTART.md) — environment, ingestion, API, UI, and evaluation setup.
- [Prompt and Question Catalog](docs/PROMPTS_AND_QUESTIONS.md) — supported, unsupported, page, and table prompts.
- [Preprocessing Decisions](docs/PREPROCESSING_DECISIONS.md) — cleaning, exclusions, and table transformations.
- [Technical Methods](docs/TECHNICAL_METHODS.md) — extraction, chunking, embeddings, retrieval, LangGraph, and evaluation.

## Architecture

```text
PDF
 |
 +--> page-text extractor --> cleaner --+
 |                                      |
 +--> table extractor ------------------+--> chunker --> Gemini --> Pinecone
                                                               |
                                                               v
                         FastAPI <-- LangGraph: retrieve -> generate -> validate
                            ^
                            |
                       Streamlit UI
```

The page and table extractors are deliberately separate. Page extraction
removes accepted table regions so table content is not duplicated in text
chunks. Table extraction preserves rows, table numbers, color-coded readiness
labels, and source metadata.

## Repository layout

```text
run_pipeline.py             build the complete RAG index
run_server.py               start the FastAPI application

rag/                        reusable application package
  config.py                 project paths and environment settings
  ingestion/
    extractor.py            separate page and table extraction functions
    cleaner.py              source-specific cleanup rules
    chunker.py              provenance-aware text/table chunks
    metadata.py             chapter, section, and page metadata
    indexer.py              embeddings and Pinecone upsert
  retrieval/retriever.py   Pinecone retrieval
  generation/generator.py  public generation entry point
  workflow/rag_graph.py    LangGraph workflow
  api/
    app.py                 FastAPI application
    routes.py              HTTP route handlers
    schemas.py             request/response models

evaluation/                 evaluation code and question set
scripts/                    optional evaluation command wrappers
ui/                         Streamlit client
data/raw/                   source PDF
data/artifacts/             extraction and chunking outputs
data/evaluation_results/    evaluation JSON and Markdown reports
```

## Setup

### Prerequisites

- Python 3.10 or newer
- A Gemini API key for embeddings
- A Pinecone account and API key
- A Groq API key for answer generation
- The source PDF placed at `data/raw/Ebook-Agentic-AI.pdf`

Clone the repository and enter its root directory:

```powershell
git clone https://github.com/josephjelson06/Appening_RAG_Project.git
cd Appening_RAG_Project
```

From the repository root, create the environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Fill `.env` with valid credentials. Never commit `.env` or API keys. The
`.env.example` file documents the required settings without containing secrets.

Required provider settings include:

```text
GOOGLE_API_KEY
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIMENSION=3072
PINECONE_API_KEY
PINECONE_INDEX_NAME=agentic-ai-book
PINECONE_NAMESPACE=agentic-ai-book
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
GROQ_API_KEY
GENERATION_MODEL=qwen/qwen3.8-27b
```

## 1. Build the RAG index

Place the source book at:

```text
data/raw/Ebook-Agentic-AI.pdf
```

Run one command:

```powershell
python .\run_pipeline.py
```

Run this once before using the API or evaluation scripts. It makes external
Gemini and Pinecone calls, so it requires valid provider credentials and an
available network connection.

This executes, in order:

1. page-text extraction and cleanup;
2. table extraction and color-label decoding;
3. structure-aware chunk creation;
4. embedding and Pinecone indexing.

Inspect local artifacts under `data/artifacts/`. The Pinecone index manifest is
written to `data/artifacts/04_index_manifest/` after a successful indexing run.

The local chunk artifact is the inspectable source of truth for indexing:
`data/artifacts/03_chunked/chunks.jsonl`. Re-running the pipeline regenerates
these artifacts and upserts the resulting records into the configured Pinecone
namespace.

## 2. Run the application

Start FastAPI:

```powershell
python .\run_server.py
```

Swagger documentation:

```text
http://127.0.0.1:18000/docs
```

Routes:

```text
GET  /health
POST /retrieve
POST /generate
```

In a second terminal, start Streamlit:

```powershell
streamlit run ui/streamlit_app.py
```

The UI defaults to `http://127.0.0.1:18000`. Set `RAG_API_URL` in `.env` or
the terminal if the API runs elsewhere.

Keep the API terminal running while using Streamlit. To verify the API before
opening the UI, visit `/docs` and call `/health` in Swagger.

## 3. Evaluate the system

Run the complete evaluation:

```powershell
python .\scripts\run_evaluation.py
```

Run individual evaluations when needed:

```powershell
python .\scripts\evaluate_retrieval.py
python .\scripts\evaluate_generation.py
```

Reports are written to:

```text
data/evaluation_results/outputs/retrieval_report.json
data/evaluation_results/outputs/generation_report.json
data/evaluation_results/outputs/evaluation_report.md
```

The retrieval score is a Pinecone similarity score, not a calibrated confidence
probability. Answer-point coverage is a transparent heuristic and does not
replace manual factuality review.

The committed reports are previous evaluation artifacts. Run the evaluation
again after rebuilding or changing the index if you want current results.

## Provider responsibilities

| Provider | Purpose | Used by |
| --- | --- | --- |
| Gemini | Generate document and query embeddings | ingestion, retrieval |
| Pinecone | Store and search embedded chunks | ingestion, retrieval |
| Groq | Generate the final grounded answer | LangGraph generation node |

## Troubleshooting

- Run commands from the repository root so the `rag` package can be imported.
- If `/generate` returns a provider error, check `GROQ_API_KEY` and
  `GENERATION_MODEL` in `.env`.
- If `/retrieve` fails, check Gemini credentials, Pinecone credentials, the
  index name, namespace, and whether `run_pipeline.py` completed successfully.
- If port `18000` is unavailable, set `API_PORT` in `.env` and set the same
  base URL in `RAG_API_URL` before starting Streamlit.
- If the PDF is missing, place the exact source file at the documented path;
  the pipeline will stop before making indexing calls.

## Sample questions

- What is Agentic AI?
- How does Agentic AI differ from other AI systems?
- What are the capabilities of Agentic AI?
- What are the types of atomic agents?
- What challenges affect multi-agent systems?
- What parameters assess organizational readiness for Agentic AI?

## Limitations

- External Gemini, Pinecone, and Groq services are required for live operation.
- Generated answers are model outputs and should be reviewed with their source chunks.
- Page-level provenance can be broader than section-level content when a page contains multiple sections.
- Evaluation reports are diagnostic evidence, not a guarantee of production quality.
