# Evaluation

`questions.json` is a manually verified evaluation set containing direct
questions, section questions, table questions, cross-page questions, and one
intentionally unanswerable question.

Run the complete evaluation from the project root:

```powershell
python .\scripts\run_evaluation.py
```

Run only one evaluation when diagnosing a failure:

```powershell
python .\scripts\evaluate_retrieval.py
python .\scripts\evaluate_generation.py
```

Reports are written to `data/evaluation_results/outputs/`:

- `retrieval_report.json` contains per-question retrieval evidence.
- `generation_report.json` contains generated answers and heuristic metrics.
- `evaluation_report.md` is the reviewer-facing summary.

The generation path uses the LangGraph workflow:

```text
START -> retrieve -> generate -> validate -> END
```

The validation result is returned by the API as `grounded` and
`validation_note`. Evaluation metrics are diagnostic and require manual review.
