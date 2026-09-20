# Technical Methods and Application Design

## 1. Loading and source-aware extraction

The source PDF is loaded from `data/raw/`. The extraction code is intentionally
split into two functions in `rag/ingestion/extractor.py`:

- `extract_pages()` extracts educational page text while excluding accepted
  table regions.
- `extract_tables()` extracts validated tables, preserves table numbers, and
  decodes the color-coded readiness matrix.

This is source-aware preprocessing rather than generic PDF text dumping.

## 2. Cleaning and metadata

`rag/ingestion/cleaner.py` removes repeated headers, footers, QR promotions,
known promotional inserts, and other source-specific noise while preserving
paragraphs and headings.

`rag/ingestion/metadata.py` assigns provenance deterministically:

- chapter ranges are mapped from PDF page numbers;
- in-book page number is calculated as `PDF page - 6`;
- numbered headings such as `2.1 ...` are detected as sections;
- lettered headings such as `B. Industry-Wise Readiness` are also supported.

The section mapping is therefore based on the known book layout and extracted
headings, not on an LLM guessing a section after indexing.

## 3. Chunking

The chunker reads the cleaned page and table artifacts separately. Each chunk
contains text plus metadata including source, content type, PDF page, in-book
page, chapter, chapter title, section, chunk type, and part number.

Text is split using a structure-aware recursive fallback:

1. paragraph boundaries;
2. line boundaries;
3. sentence boundaries;
4. word boundaries when necessary.

Text chunks have a maximum size of 2,800 characters and a 300-character
overlap. Table chunks have a maximum size of 4,500 characters and no overlap,
because each table row is already a compact unit of evidence.

The output is `data/artifacts/03_chunked/chunks.jsonl`.

## 4. Embeddings and Pinecone indexing

Gemini creates embeddings for each chunk. The configured embedding dimension is
3072. Pinecone stores the vectors and metadata in the configured index and
namespace using cosine similarity.

The stored metadata includes the chunk text itself so retrieval can return both
the similarity score and the source evidence needed by generation.

## 5. Retrieval

For a query, the same Gemini embedding model embeds the question. Pinecone
returns the configured top-k matches. Results below `RELEVANCE_THRESHOLD` are
discarded.

Each returned match includes:

- chunk ID;
- similarity score;
- extracted text;
- chapter and section metadata;
- PDF and in-book page numbers;
- content type and table number when applicable.

The score is a vector-retrieval similarity score. It is not a confidence
probability and does not independently verify factual correctness.

## 6. LangGraph generation workflow

LangGraph is used as explicit workflow orchestration rather than as a claim
that the application is a multi-agent system. The compiled graph is:

```text
START -> retrieve -> generate -> validate -> END
```

- **retrieve:** obtains relevant book chunks from Pinecone;
- **generate:** sends the question and retrieved excerpts to Groq with strict
  book-grounding instructions;
- **validate:** performs a lightweight check that sources exist and the answer
  contains a source citation.

The API returns the answer, source references, `grounded`, and
`validation_note`.

## 7. API, UI, and evaluation

FastAPI exposes separate `/retrieve` and `/generate` routes. Streamlit is a
thin client of those routes, so provider integrations stay in the backend.

Evaluation is separated into retrieval and generation checks. Retrieval uses
manually verified expected pages, sections, and content types. Generation uses
manually defined answer points and refusal checks. The resulting JSON reports
and reviewer-facing Markdown report are stored under
`data/evaluation_results/outputs/`.
