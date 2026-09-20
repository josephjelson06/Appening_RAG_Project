# Streamlit UI

The Streamlit app is a thin client of the FastAPI service. It does not call
Pinecone, Gemini, or Groq directly.

## Start the API first

From the repository root:

```powershell
python .\scripts\03_run_api.py
```

The default API URL is:

```text
http://127.0.0.1:18000
```

## Start Streamlit

Open a second terminal:

```powershell
python .\scripts\04_run_streamlit.py
```

The app reads `RAG_API_URL` from `.env` when present and otherwise uses the
default local API URL. Override it in the terminal for a different API host.

Open the URL printed by Streamlit, normally `http://localhost:8501`.

## UI modes

### Retrieve context

Shows the chunks returned by Pinecone, their similarity scores, and their
chapter, section, PDF-page, in-book-page, and table metadata.

### Generate answer

Runs the LangGraph workflow through FastAPI and displays the grounded answer
and its source references.

The displayed score is Pinecone retrieval similarity, not a probability that
the final answer is correct.
