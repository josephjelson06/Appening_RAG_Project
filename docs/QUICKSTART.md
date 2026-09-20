# Quick Start Guide

This guide is for a new developer who has cloned the repository and wants to
run the complete application.

## 1. Prepare the project

From the repository root:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
```

Use Python 3.10 or newer. Open `.env` and replace the placeholder values with
valid credentials. The providers have separate responsibilities:

| Setting | Purpose |
| --- | --- |
| `GOOGLE_API_KEY` | Gemini document and query embeddings |
| `PINECONE_API_KEY` | Vector storage and retrieval |
| `PINECONE_INDEX_NAME` | Pinecone index to create/use |
| `PINECONE_NAMESPACE` | Logical namespace inside that index |
| `GROQ_API_KEY` | Final answer generation |
| `GENERATION_MODEL` | Groq generation model |

Never commit `.env` or paste live keys into source files.

## 2. Add the source document

Place the source PDF at:

```text
data/raw/Ebook-Agentic-AI.pdf
```

## 3. Build the index

Run the single ingestion command:

```powershell
python .\run_pipeline.py
```

It extracts page text and tables, cleans them, creates metadata-rich chunks,
embeds the chunks with Gemini, and upserts them to Pinecone. This step requires
network access and valid Gemini/Pinecone credentials.

Inspect the local outputs under `data/artifacts/` before moving on.

## 4. Start the API

In the same environment:

```powershell
python .\run_server.py
```

Open Swagger at:

```text
http://127.0.0.1:18000/docs
```

Use `/health` first. Then test `/retrieve` and `/generate` with a question from
the prompt catalog.

## 5. Start the UI

Keep the API terminal running and open a second terminal:

```powershell
cd C:\path\to\Appening_RAG_Project
.\.venv\Scripts\activate
streamlit run ui\streamlit_app.py
```

Open the URL printed by Streamlit, normally `http://localhost:8501`.

## 6. Run evaluation

After ingestion and indexing:

```powershell
python .\scripts\run_evaluation.py
```

Reports are written to `data/evaluation_results/outputs/`. They are diagnostic
reports and should be reviewed alongside the retrieved source chunks.

## Common setup problems

- `ModuleNotFoundError: rag`: run commands from the repository root.
- Retrieval errors: confirm the Pinecone index name, namespace, embedding model,
  and that ingestion completed.
- Generation errors: confirm `GROQ_API_KEY` and `GENERATION_MODEL`.
- Port conflict: change `API_PORT` and `RAG_API_URL` together in `.env`.
