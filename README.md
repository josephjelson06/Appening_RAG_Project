# Agentic AI Book RAG

A Python RAG chatbot grounded strictly in the *Agentic AI for Executives*
ebook. The project uses PyMuPDF for extraction, Gemini for embeddings, Pinecone
for vector search, Groq for generation, LangGraph for orchestration, FastAPI
for the API, and Streamlit for the UI.

## Architecture

```text
Source PDF
   |
   v
Numbered ingestion pipeline
   |-- extract text and tables
   |-- clean artifacts
   |-- build provenance-aware chunks
   |-- embed and index in Pinecone
   |
   v
LangGraph RAG workflow
   |-- retrieve
   |-- generate
   |-- validate
   |
   v
FastAPI (/retrieve, /generate)
   |
   v
Streamlit UI
```

## Repository layout

```text
data/raw/                          source PDF
data/artifacts/02_cleaned/         cleaned text/table artifacts
data/artifacts/03_chunked/         final chunks.jsonl
data/artifacts/04_index_manifest/  Pinecone indexing manifest
src/agentic_rag/                   reusable application modules
scripts/                           numbered pipeline and run commands
evaluation/                        question set and generated reports
ui/                                Streamlit client and instructions
```

The extraction scripts write the cleaned extraction artifacts directly to
`data/artifacts/02_cleaned/`; the empty `01_extracted` stage is intentionally
not required for this PDF because the source-specific extraction and cleanup
are performed together.

## Setup

Use the project virtual environment:

```powershell
.\myenv\Scripts\activate
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and provide valid credentials. Never commit
`.env` or API keys.

Required provider settings include:

```text
GOOGLE_API_KEY       Gemini embedding access
EMBEDDING_MODEL      gemini-embedding-001
EMBEDDING_DIMENSION  3072
PINECONE_API_KEY     Pinecone access
GROQ_API_KEY         Groq generation access
GENERATION_MODEL     qwen/qwen3.8-27b
```

## Part 1: ingestion and indexing

Place the source book at:

```text
data/raw/Ebook-Agentic-AI.pdf
```

Run the complete pipeline with one command:

```powershell
python .\scripts\01_run_ingestion.py
```

The steps run in this order:

```text
01_extract_pages.py
02_extract_tables.py
03_build_chunks.py
04_index_pinecone.py
```

Inspect the resulting artifacts under `data/artifacts/`.

## Part 2: API and UI

Start the API:

```powershell
python .\scripts\03_run_api.py
```

Swagger is available at:

```text
http://127.0.0.1:18000/docs
```

The main routes are:

```text
GET  /health
POST /retrieve
POST /generate
```

Start Streamlit in a second terminal:

```powershell
python .\scripts\04_run_streamlit.py
```

The UI defaults to the local API URL above. Set `RAG_API_URL` first only when
the API is running at a different address.

See [ui/README.md](ui/README.md) for UI-specific instructions.

## Part 3: evaluation

Run retrieval and generation evaluation in sequence:

```powershell
python .\scripts\02_run_evaluation.py
```

Reports are written to:

```text
evaluation/outputs/retrieval_report.json
evaluation/outputs/generation_report.json
evaluation/outputs/evaluation_report.md
```

The retrieval score is a Pinecone vector similarity score, not an LLM
confidence probability. Answer-point coverage is a transparent heuristic and
does not replace manual factuality review.

## Sample questions

- What is Agentic AI?
- How does Agentic AI differ from other AI systems?
- What are the capabilities of Agentic AI?
- What are the types of atomic agents?
- What challenges affect multi-agent systems?
- What parameters assess organizational readiness for Agentic AI?

## Current limitations

- Retrieval and generation depend on external Gemini, Pinecone, and Groq APIs.
- The `grounded` field is a lightweight citation/evidence signal, not a formal
  factuality guarantee.
- Some PDF pages contain multiple sections, so page-level provenance can be
  less precise than chunk-level content.
- Evaluation reports must be manually reviewed before making production claims.
