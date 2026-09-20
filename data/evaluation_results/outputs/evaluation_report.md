# Evaluation Report

Generated: 2026-09-20T13:37:10.156572+00:00

This report summarizes the current fixed-question evaluation set. The JSON files beside this report contain per-question evidence and sources.

## Retrieval

| Metric | Result |
| --- | ---: |
| Total questions | 15 |
| Answerable questions | 14 |
| Answerable hit@k | 85.7% |
| Answerable page hit@k | 100.0% |
| Answerable evidence hit@k | 92.9% |
| Relevant top result accuracy | 64.3% |

`hit@k` means that at least one relevant chunk appeared in the retrieved top-k. The individual result scores are Pinecone similarity scores; they are not calibrated confidence probabilities.

Known answerable retrieval misses: q03, q14.

## Generation

| Metric | Result |
| --- | ---: |
| Average answer-point coverage | 74.9% |
| Unanswerable refusal rate | 100.0% |
| Generation errors | 1 |

Answer-point coverage is a heuristic evaluator metric: it measures how many manually defined expected concepts were detected in an answer. It is not a truth guarantee or model confidence score.

Generation errors: q05.

## Interpretation and limitations

- Retrieval and generation are evaluated separately so failures can be diagnosed as retrieval, generation, or both.
- The evaluation set is intentionally small and should be expanded with more section, table, boundary, and unanswerable questions before making production claims.
- Scores and heuristic coverage should be reviewed alongside the returned source chunks and page metadata.
- The generation evaluator uses the configured Groq model, so transient provider errors can affect a run.
