"""Start the Streamlit client."""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "ui/streamlit_app.py"],
        cwd=PROJECT_ROOT,
        check=True,
    )
