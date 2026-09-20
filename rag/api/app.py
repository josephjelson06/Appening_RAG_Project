"""FastAPI application for the Agentic AI book RAG system."""

from fastapi import FastAPI

from .routes import router


app = FastAPI(
    title="Agentic AI Book RAG API",
    description="Retrieve and answer questions from the Agentic AI book.",
    version="0.1.0",
)

app.include_router(router)
