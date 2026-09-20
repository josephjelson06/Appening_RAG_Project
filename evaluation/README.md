# Retrieval evaluation

`questions.json` is a manually verified evaluation set. It includes direct
questions, section questions, table questions, cross-page questions, and one
question that should not be answerable from the book.

Run from the project root after Pinecone and the embedding configuration are
available:

```powershell
$env:PYTHONPATH = "$(Get-Location)\src"
python .\scripts\evaluate_retrieval.py
```

The report is written to `evaluation/retrieval_report.json`.

## Generation evaluation

After retrieval evaluation, run the full RAG answer path:

```powershell
$env:PYTHONPATH = "$(Get-Location)\src"
python .\scripts\evaluate_generation.py
```

This writes `generation_report.json`. The answer-point coverage and refusal
rate are heuristics; every generated answer should still be manually reviewed
for factual accuracy, grounding, and citation correctness.

## LangGraph workflow

The generation path is implemented as a compiled graph:

```text
START -> retrieve -> generate -> validate -> END
```

The validation result is returned by the API as `grounded` and
`validation_note`.
