"""Run the generation evaluation utility."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.generation import main


if __name__ == "__main__":
    main()
