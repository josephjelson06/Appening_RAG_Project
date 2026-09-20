"""Central project paths and environment-backed runtime settings."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class ProjectPaths:
    root: Path = PROJECT_ROOT
    source_pdf: Path = PROJECT_ROOT / "data" / "raw" / "Ebook-Agentic-AI.pdf"
    cleaned_dir: Path = PROJECT_ROOT / "data" / "artifacts" / "02_cleaned"
    chunks_file: Path = PROJECT_ROOT / "data" / "artifacts" / "03_chunked" / "chunks.jsonl"
    index_manifest_dir: Path = PROJECT_ROOT / "data" / "artifacts" / "04_index_manifest"
    evaluation_dir: Path = PROJECT_ROOT / "evaluation"
    evaluation_results_dir: Path = PROJECT_ROOT / "data" / "evaluation_results"
    evaluation_outputs_dir: Path = evaluation_results_dir / "outputs"


PATHS = ProjectPaths()


def env_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def env_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))
