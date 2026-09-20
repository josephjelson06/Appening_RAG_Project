"""Start the FastAPI application."""

import os

import uvicorn

from rag.config import PATHS  # noqa: F401  # loads the project .env


if __name__ == "__main__":
    uvicorn.run(
        "rag.api.app:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "18000")),
        reload=True,
    )
